# Drive upload without a service account

You paste this into your own Google account, deploy it, and give GitHub the URL.
The script runs **as you**, so it can write to your Drive with no extra credentials.

## 1. Create the script
Go to **script.google.com** → **New project**. Delete what's there, paste this:

```javascript
// Receives files from GitHub and files them into Drive by date.
// Deployed "execute as me", so it writes with YOUR Drive permissions.
const ROOT_FOLDER_ID = 'PASTE_YOUR_FOLDER_ID_HERE';   // from the folder's URL
const SECRET         = 'PASTE_A_LONG_RANDOM_STRING';  // must match the GitHub secret

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    if (body.secret !== SECRET) {
      return ContentService.createTextOutput('bad secret');
    }
    const root = DriveApp.getFolderById(ROOT_FOLDER_ID);
    const day  = sub(root, body.day);            // e.g. 29-08-2026
    let n = 0;
    (body.files || []).forEach(f => {
      const dir = sub(day, f.dir);               // dist | city | headlines-dist | headlines-city
      // replace an existing file of the same name rather than duplicating
      const old = dir.getFilesByName(f.name);
      while (old.hasNext()) old.next().setTrashed(true);
      dir.createFile(f.name, f.text, MimeType.PLAIN_TEXT);
      n++;
    });
    return ContentService.createTextOutput('ok ' + n);
  } catch (err) {
    return ContentService.createTextOutput('error ' + err);
  }
}

function sub(parent, name) {
  const it = parent.getFoldersByName(name);
  return it.hasNext() ? it.next() : parent.createFolder(name);
}
```

## 2. Fill in the two values
* `ROOT_FOLDER_ID` — make a folder in your Drive, open it, copy the id from the URL:
  `drive.google.com/drive/folders/`**`1AbCdEf...`**
* `SECRET` — any long random string. It stops strangers posting to your URL.

## 3. Deploy
**Deploy → New deployment → Web app**
* Execute as: **Me**
* Who has access: **Anyone**    ← needed so GitHub can reach it; the SECRET is what protects it

Copy the **Web app URL** it gives you.

## 4. Two GitHub secrets
Repo → Settings → Secrets and variables → Actions:

| Name | Value |
|---|---|
| `GAS_URL` | the Web app URL |
| `GAS_SECRET` | the same random string |

That's all — no Cloud project, no service account, no JSON key.
