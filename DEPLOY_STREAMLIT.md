# Deploy the Bulletin Generator to Streamlit Community Cloud (free)

Everything in this folder is ready. You do the GitHub + deploy steps (I can't log into your accounts).

## Files
| File | Role |
|---|---|
| `streamlit_app.py` | the app (main file) |
| `gemini_rest.py` | Gemini via REST (stdlib urllib) |
| `prompts.py`, `headlines_local.py` | prompts + offline headline parser |
| `requirements.txt` | just `streamlit` (everything else is stdlib) |
| `.streamlit/secrets.toml.example` | template for your keys |
| `.gitignore` | keeps real secrets out of git |

## Steps

**1. Put this folder in a GitHub repo**
- Create a **new repo** on github.com (public is free). Name it e.g. `localai-bulletin`.
- Upload the **contents of this `streamlit_cloud/` folder** to the repo (drag-drop in the GitHub web UI, or `git push`).
- ⚠️ Do NOT upload `secrets.toml` (only the `.example`). The `.gitignore` already blocks the real one.

**2. Deploy on Streamlit Cloud**
- Go to **share.streamlit.io** → sign in with GitHub → **New app**.
- Repo: your `localai-bulletin` · Branch: `main` · Main file path: `streamlit_app.py`.
- Click **Deploy**.

**3. Add your keys as Secrets** (NOT in the code)
- In the app's **⋮ → Settings → Secrets**, paste:
  ```
  GEMINI_API_KEYS = "AQ.key1,AQ.key2,AQ.key3,AQ.key4,AQ.key5,AQ.key6,AQ.key7"
  ```
- Save → the app reboots and reads them.

**4. Use it from any phone/browser**
- You get a public URL like `https://localai-bulletin.streamlit.app`.
- Sidebar should show **"N keys"**; click **Detect models**, then generate.

## Good to know
- **Free**: yes. Public repo required on the free tier. Keys live in Secrets (private), not the repo.
- **Output**: scripts/headlines **download as a ZIP** (no server disk like your Mac).
- **Sleeps when idle**: first visit after a while takes ~30s to wake — normal.
- **Only text**: the bulletin + headlines app fits the free tier. The **video generator can't** go here (too heavy).
