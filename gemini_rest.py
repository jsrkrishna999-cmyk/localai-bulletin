# gemini_rest.py — rotating Gemini key pool using the REST API via stdlib urllib only.
#
# Why REST (not google-genai): Streamlit in Snowflake only allows packages from Snowflake's
# Anaconda channel, and outbound calls go through an External Access Integration. urllib is
# always available, so we call the Generative Language REST API directly. Same rotation +
# quota/dead-key failover behaviour as the desktop version.
import json
import time
# NOTE: urllib is imported LAZILY inside the functions below. Importing network modules at
# module load can fail in the Streamlit-in-Snowflake sandbox ("bad argument type for built-in
# operation") before the External Access Integration context is active — so we defer it.

BASE = "https://generativelanguage.googleapis.com/v1beta"


class AllKeysExhausted(Exception):
    """Every key hit its quota (or is invalid)."""


def load_keys(raw):
    """Parse keys from a comma/whitespace separated string. Dedupe, keep order."""
    if not raw:
        return []
    seen, out = set(), []
    for part in str(raw).replace(",", " ").split():
        k = part.strip()
        if k and k not in seen:
            seen.add(k)
            out.append(k)
    return out


def mask(k):
    return (k[:6] + "…" + k[-4:]) if k and len(k) > 12 else (k or "")


def _post(url, payload, timeout=120):
    import urllib.request
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _get(url, timeout=60):
    import urllib.request
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def list_models(key):
    """Text models this key can call (ids without the 'models/' prefix)."""
    out = []
    data = _get(f"{BASE}/models?key={key}")
    for m in data.get("models", []):
        name = m.get("name", "").replace("models/", "")
        methods = m.get("supportedGenerationMethods", [])
        low = name.lower()
        if "generateContent" not in methods:
            continue
        if any(x in low for x in ("embedding", "aqa", "tts", "image", "imagen", "veo", "vision")):
            continue
        out.append(name)
    return sorted(set(out))


def _reason(body):
    """Pull a short human reason out of Google's error JSON: prefer error.status, then message."""
    if not body:
        return ""
    try:
        err = json.loads(body).get("error", {})
        status = err.get("status", "")
        msg = (err.get("message", "") or "").strip().replace("\n", " ")
        if status and msg:
            return f"{status}: {msg[:120]}"
        return status or msg[:140]
    except Exception:
        return body.strip().replace("\n", " ")[:140]


def _classify(code, body):
    b = (body or "").lower()
    if code in (400, 401, 403) and ("api_key_invalid" in b or "api key not valid" in b
                                     or "permission_denied" in b or "unauthenticated" in b):
        return "deadkey"
    if code == 429 or "resource_exhausted" in b or "quota" in b or "rate limit" in b:
        return "quota"
    if code in (500, 503) or "unavailable" in b or "overloaded" in b or "internal" in b:
        return "transient"
    return "fatal"


class KeyPool:
    def __init__(self, keys):
        self.keys = list(keys)
        self.idx = 0
        self.spent = set()

    def remaining(self):
        return len(self.keys) - len(self.spent)

    def status(self):
        out = []
        for i, k in enumerate(self.keys):
            state = "spent" if i in self.spent else ("active" if i == self.idx else "idle")
            out.append({"n": i + 1, "masked": mask(k), "state": state})
        return out

    def _next(self):
        for step in range(len(self.keys)):
            i = (self.idx + step) % len(self.keys)
            if i not in self.spent:
                self.idx = i
                return i
        return None

    def generate(self, model, prompt, on_event=None, transient_retries=2, transient_wait=6):
        import urllib.error                       # lazy (see note at top of file)
        log = on_event or (lambda *_a: None)
        if not self.keys:
            raise AllKeysExhausted("No API keys provided.")
        payload = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
        tried_transient = set()   # keys that hit a MODEL-overload this call — fine, just busy, don't spend
        while True:
            # pick next key that's neither spent nor already transient-skipped this call
            i = None
            for step in range(len(self.keys)):
                j = (self.idx + step) % len(self.keys)
                if j not in self.spent and j not in tried_transient:
                    i = j
                    break
            if i is None:
                if self.remaining() == 0:
                    raise AllKeysExhausted(
                        f"All {len(self.keys)} keys are out of quota / invalid. Add more and continue.")
                # every usable key hit the same overloaded model → it's Google's model, not your keys
                raise RuntimeError(
                    f"Model '{model}' is overloaded (503) on Google's side right now — all "
                    f"{self.remaining()} keys are fine, they just can't reach it. Try again in a "
                    f"minute, or pick a different model.")
            key = self.keys[i]
            url = f"{BASE}/models/{model}:generateContent?key={key}"
            for attempt in range(1, transient_retries + 1):
                try:
                    resp = _post(url, payload)
                    cands = resp.get("candidates", [])
                    parts = (cands[0].get("content", {}).get("parts", []) if cands else [])
                    text = "".join(p.get("text", "") for p in parts)
                    return text, i + 1
                except urllib.error.HTTPError as e:
                    body = ""
                    try:
                        body = e.read().decode("utf-8")
                    except Exception:
                        pass
                    reason = _reason(body) or e.reason or ""
                    kind = _classify(e.code, body)
                    if kind in ("deadkey", "quota"):
                        self.spent.add(i)
                        self.idx = (i + 1) % len(self.keys)
                        why = "INVALID" if kind == "deadkey" else "out of quota"
                        log(f"🔑 Key #{i+1} ({mask(key)}) {why} [{e.code} {reason}] → next key ({self.remaining()} left)")
                        break
                    if kind == "transient" and attempt < transient_retries:
                        log(f"⏳ Key #{i+1}: {e.code} {reason} → retry {attempt}/{transient_retries} in {transient_wait}s")
                        time.sleep(transient_wait)
                        continue
                    if kind == "transient":
                        tried_transient.add(i)          # DON'T spend — key is good, model is busy
                        self.idx = (i + 1) % len(self.keys)
                        log(f"⚠️ Key #{i+1}: {e.code} {reason} → model busy, trying next key (key NOT used up)")
                        break
                    raise RuntimeError(f"Gemini error {e.code}: {body[:300]}")
                except urllib.error.URLError as e:
                    # network/EAI problem — surface clearly (usually a missing External Access Integration)
                    raise RuntimeError(f"Network error calling Gemini: {e}. "
                                       "Check the External Access Integration is attached.")
