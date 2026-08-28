#!/usr/bin/env python3
"""drive_post.py — send the day's files to a Google Apps Script web app.

No service account, no Cloud project: the Apps Script runs inside the user's own
Google account and writes to their Drive. GitHub only needs the URL and a shared
secret. Files go up in batches so one huge POST can't time out.
"""
import datetime, json, os, ssl, sys, urllib.request, urllib.error

IST  = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.environ.get("OUT_DIR") or os.path.join(HERE, "Gemini_outs")
SECTIONS = [("dist", "dist"), ("city", "city"),
            ("headlines/dist", "headlines-dist"), ("headlines/city", "headlines-city")]
BATCH = 12                      # files per POST — keeps each request small


def ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def post(url, payload, tries=3):
    for a in range(tries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180, context=ctx()) as r:
                return r.read().decode()[:120]
        except Exception as e:
            if a == tries - 1:
                return f"ERROR {str(e)[:90]}"
            import time; time.sleep(4 * (a + 1))


def main():
    url = os.environ.get("GAS_URL", "").strip()
    sec = os.environ.get("GAS_SECRET", "").strip()
    if not url or not sec:
        print("  GAS_URL / GAS_SECRET not set — skipping Drive upload")
        return 0
    day = datetime.datetime.now(IST).strftime("%d-%m-%Y")
    print(f"  uploading to Drive as {day}")
    total = 0
    for src, label in SECTIONS:
        d = os.path.join(OUT, src)
        if not os.path.isdir(d):
            continue
        names = sorted(f for f in os.listdir(d) if f.endswith(".txt"))
        sent = 0
        for i in range(0, len(names), BATCH):
            chunk = names[i:i + BATCH]
            files = []
            for n in chunk:
                try:
                    files.append({"dir": label, "name": n,
                                  "text": open(os.path.join(d, n), encoding="utf-8").read()})
                except Exception as e:
                    print(f"    ⚠️ {n}: {e}")
            r = post(url, {"secret": sec, "day": day, "files": files})
            if str(r).startswith("ERROR"):
                print(f"    ❌ {label} batch {i//BATCH+1}: {r}")
            else:
                sent += len(files)
        print(f"    {label}: {sent}/{len(names)} uploaded")
        total += sent
    print(f"  Drive upload done — {total} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
