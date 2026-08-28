#!/usr/bin/env python3
"""drive_upload.py — push the day's scripts + headlines to Google Drive.

Runs after daily_scripts.py in the GitHub Action. Uses a SERVICE ACCOUNT, so no
browser login is involved and it works headless.

Layout is date-first because the point is reading them on a phone:

    <your shared folder>/
        29-08-2026/
            dist/            54 district scripts
            city/            54 city scripts
            headlines-dist/  54 district headlines
            headlines-city/  54 city headlines

Needs two env vars (GitHub secrets):
    GDRIVE_SA_JSON    the service-account key file, pasted whole
    GDRIVE_FOLDER_ID  id of a Drive folder you shared with the service account
"""
import datetime, json, os, sys

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "Gemini_outs")

SECTIONS = [("dist", "dist"), ("city", "city"),
            ("headlines/dist", "headlines-dist"), ("headlines/city", "headlines-city")]


def log(m): print(f"  {m}", flush=True)


def service():
    raw = os.environ.get("GDRIVE_SA_JSON", "").strip()
    if not raw:
        raise SystemExit("GDRIVE_SA_JSON is not set — add it as a GitHub secret")
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    info = json.loads(raw)
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=["https://www.googleapis.com/auth/drive"])
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def find_or_make(svc, name, parent):
    """One folder per name under `parent`, reused on later runs."""
    q = (f"name = '{name}' and '{parent}' in parents "
         f"and mimeType = 'application/vnd.google-apps.folder' and trashed = false")
    hit = svc.files().list(q=q, fields="files(id)", pageSize=1,
                           supportsAllDrives=True,
                           includeItemsFromAllDrives=True).execute().get("files", [])
    if hit:
        return hit[0]["id"]
    return svc.files().create(
        body={"name": name, "mimeType": "application/vnd.google-apps.folder",
              "parents": [parent]},
        fields="id", supportsAllDrives=True).execute()["id"]


def upload(svc, path, parent):
    """Create, or update in place if the same name is already there."""
    from googleapiclient.http import MediaFileUpload
    name = os.path.basename(path)
    media = MediaFileUpload(path, mimetype="text/plain", resumable=False)
    q = f"name = '{name}' and '{parent}' in parents and trashed = false"
    hit = svc.files().list(q=q, fields="files(id)", pageSize=1,
                           supportsAllDrives=True,
                           includeItemsFromAllDrives=True).execute().get("files", [])
    if hit:
        svc.files().update(fileId=hit[0]["id"], media_body=media,
                           supportsAllDrives=True).execute()
        return "updated"
    svc.files().create(body={"name": name, "parents": [parent]},
                       media_body=media, fields="id",
                       supportsAllDrives=True).execute()
    return "new"


def main():
    root = os.environ.get("GDRIVE_FOLDER_ID", "").strip()
    if not root:
        raise SystemExit("GDRIVE_FOLDER_ID is not set — add it as a GitHub secret")
    svc = service()
    day = datetime.datetime.now(IST).strftime("%d-%m-%Y")
    log(f"uploading to Drive · folder for {day}")
    day_id = find_or_make(svc, day, root)

    total = new = upd = 0
    for src, label in SECTIONS:
        d = os.path.join(OUT, src)
        if not os.path.isdir(d):
            log(f"  {label}: nothing to upload"); continue
        files = sorted(f for f in os.listdir(d) if f.endswith(".txt"))
        if not files:
            log(f"  {label}: empty"); continue
        sub = find_or_make(svc, label, day_id)
        n_new = n_upd = 0
        for f in files:
            try:
                r = upload(svc, os.path.join(d, f), sub)
                n_new += r == "new"; n_upd += r == "updated"
            except Exception as e:
                log(f"    ❌ {f}: {str(e)[:70]}")
        total += len(files); new += n_new; upd += n_upd
        log(f"  {label}: {n_new} new · {n_upd} updated  ({len(files)} files)")
    log(f"done — {total} file(s): {new} new, {upd} updated")
    log(f"open: https://drive.google.com/drive/folders/{day_id}")


if __name__ == "__main__":
    sys.exit(main())
