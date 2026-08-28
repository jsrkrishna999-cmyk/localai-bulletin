#!/usr/bin/env python3
"""daily_scripts.py — generate every bulletin script + headline, headless.

Runs the same work as the Streamlit app but with no UI, so launchd can call it
at 00:01. Safe to re-run: anything already written for today is skipped, so a
retry after a failure only does what's missing.

    python3 daily_scripts.py            # city + district scripts, then headlines
    python3 daily_scripts.py --headlines-only
"""
import datetime, json, os, ssl, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
# On GitHub the repo IS the working dir; locally the app lives one level up.
ROOT = HERE if os.path.isfile(os.path.join(HERE, "prompts.py")) else os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import prompts

OUT   = os.environ.get("OUT_DIR") or os.path.join(ROOT, "Gemini_outs")
API   = "https://generativelanguage.googleapis.com/v1beta"
MODEL = os.environ.get("DAILY_MODEL", "gemini-flash-lite-latest")
IST   = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def log(m):
    print(f"{datetime.datetime.now(IST):%H:%M:%S}  {m}", flush=True)


def _ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


class Pool:
    def __init__(self):
        raw = os.environ.get("GEMINI_API_KEYS", "")
        self.ks = [k.strip() for k in raw.replace(",", " ").split() if k.strip()]
        if not self.ks:
            raise SystemExit("No GEMINI_API_KEYS — launchd needs it in the plist env")
        self.i = 0

    def ask(self, prompt, tries=None):
        tries = tries or len(self.ks) * 3
        last = ""
        for _ in range(tries):
            k = self.ks[self.i % len(self.ks)]; self.i += 1
            try:
                req = urllib.request.Request(
                    f"{API}/models/{MODEL}:generateContent?key={k}",
                    data=json.dumps({"contents": [{"parts": [{"text": prompt}]}]},
                                    ensure_ascii=False).encode(),
                    headers={"Content-Type": "application/json"})
                with urllib.request.urlopen(req, timeout=240, context=_ctx()) as r:
                    d = json.loads(r.read().decode())
                return "".join(p.get("text", "")
                               for p in d["candidates"][0]["content"]["parts"])
            except urllib.error.HTTPError as e:
                last = f"HTTP {e.code}"
                if e.code in (429, 500, 503):
                    time.sleep(4); continue
                raise RuntimeError(f"{last}: {e.read().decode()[:150]}")
            except Exception as e:
                last = str(e)[:60]; time.sleep(4)
        raise RuntimeError(f"all keys failed ({last})")


def fresh(path):
    """Already written today and non-empty?"""
    try:
        return (os.path.getsize(path) > 0 and
                datetime.date.fromtimestamp(os.path.getmtime(path)) == datetime.date.today())
    except OSError:
        return False


def do_scripts(pool, kind, places, date):
    d = os.path.join(OUT, kind); os.makedirs(d, exist_ok=True)
    build = prompts.build_city_prompt if kind == "city" else prompts.build_dist_prompt
    made = skipped = failed = 0
    for n, place in enumerate(places, 1):
        p = os.path.join(d, f"{place}.txt")
        if fresh(p):
            skipped += 1; continue
        try:
            txt = pool.ask(build(place, date)).strip()
            if not txt:
                raise RuntimeError("empty response")
            open(p, "w", encoding="utf-8").write(txt)
            made += 1
            log(f"  [{n}/{len(places)}] {kind}/{place} ✅")
        except Exception as e:
            failed += 1
            log(f"  [{n}/{len(places)}] {kind}/{place} ❌ {str(e)[:70]}")
    log(f"{kind} scripts: {made} new · {skipped} already today · {failed} failed")
    return failed


def do_headlines(pool, kind):
    src = os.path.join(OUT, kind)
    dst = os.path.join(OUT, "headlines", kind); os.makedirs(dst, exist_ok=True)
    files = sorted(f for f in os.listdir(src) if f.endswith(".txt")) if os.path.isdir(src) else []
    made = skipped = failed = 0
    for n, f in enumerate(files, 1):
        out = os.path.join(dst, f)
        if fresh(out):
            skipped += 1; continue
        body = open(os.path.join(src, f), encoding="utf-8", errors="ignore").read()
        if not body.strip():
            continue
        base = prompts.build_headline_prompt(body)
        got = None
        for attempt in range(1, 4):                      # Telugu-only guard
            line = prompts.format_headlines(
                pool.ask(base if attempt == 1 else base + prompts.RETRY_TELUGU_NOTE))
            if prompts.is_telugu(line):
                got = line; break
        if got:
            open(out, "w", encoding="utf-8").write(got)
            made += 1
            log(f"  [{n}/{len(files)}] headlines/{kind}/{f[:-4]} ✅")
        else:
            failed += 1
            log(f"  [{n}/{len(files)}] headlines/{kind}/{f[:-4]} ❌ not Telugu after 3 tries")
    log(f"{kind} headlines: {made} new · {skipped} already today · {failed} failed")
    return failed


def notify(title, msg):
    try:
        import subprocess
        subprocess.run(["osascript", "-e",
                        f'display notification "{msg}" with title "{title}"'],
                       capture_output=True)
    except Exception:
        pass


def main():
    t0 = time.time()
    # today's date in India, recomputed on every run — nothing to update by hand
    date = datetime.datetime.now(IST).strftime("%d-%m-%Y")
    # alphabetical, so the run order matches the folder listing
    places = sorted({p.strip() for p in prompts.DEFAULT_PLACES.split(",") if p.strip()},
                    key=str.lower)
    log(f"═══ daily run · {date} (auto) · {len(places)} places, alphabetical ═══")
    log(f"    order: dist scripts → city scripts → dist headlines → city headlines")
    pool = Pool()
    bad = 0
    # Order matters: districts first, then city, then their headlines — headlines
    # read the scripts, so each stage must finish before the next begins.
    if "--headlines-only" not in sys.argv:
        bad += do_scripts(pool, "dist", places, date)      # 1. district scripts
        bad += do_scripts(pool, "city", places, date)      # 2. city scripts
    bad += do_headlines(pool, "dist")                      # 3. district headlines
    bad += do_headlines(pool, "city")                      # 4. city headlines
    mins = (time.time() - t0) / 60
    log(f"═══ finished in {mins:.1f} min · {bad} failure(s) ═══")
    notify("LocalAI TV — daily scripts",
           f"{'✅' if not bad else '⚠️'} done in {mins:.0f} min, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
