# streamlit_app.py — LocalAI TV Bulletin Generator, ported for Streamlit in Snowflake (SiS).
#
# Differences from the desktop app (studio_app.py):
#   • API keys come from a Snowflake SECRET (get_generic_secret_string), with an in-app override.
#   • Gemini is called over REST (gemini_rest.py) — no google-genai package needed.
#   • No local filesystem: generated scripts live in session state and download as a ZIP.
#   • Headlines run on in-session scripts OR uploaded .txt files (no folders).
#   • Google Drive option removed (not applicable in Snowflake).
import io
import zipfile

import streamlit as st

import prompts
import headlines_local
from gemini_rest import KeyPool, load_keys, mask, list_models, AllKeysExhausted

# gemini-2.5-flash & 2.0-flash were deprecated by Google (2026-08). '-latest' auto-updates.
DEFAULT_MODEL = "gemini-flash-latest"
MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-3.5-flash",
          "gemini-3.1-flash-lite", "gemini-2.5-pro"]

st.set_page_config(page_title="LocalAI TV — Bulletin Generator", page_icon="📺", layout="wide")


# ---------- keys ----------
def secret_keys():
    """Read the comma-separated keys. Works on Streamlit Cloud (st.secrets), Snowflake
    (_snowflake secret), and locally (GEMINI_API_KEYS env var) — first one that has a value wins."""
    # 1) Streamlit Cloud / local .streamlit/secrets.toml
    try:
        v = st.secrets.get("GEMINI_API_KEYS", "")
        if v:
            return v
    except Exception:
        pass
    # 2) Snowflake bound secret
    try:
        import _snowflake
        v = _snowflake.get_generic_secret_string("gemini_keys")
        if v:
            return v
    except Exception:
        pass
    # 3) local env var
    import os
    return os.environ.get("GEMINI_API_KEYS", "")


def current_keys():
    override = st.session_state.get("keys_override", "").strip()
    return load_keys(override) if override else load_keys(secret_keys())


def get_pool(keys):
    sig = tuple(keys)
    pool = st.session_state.get("pool")
    if pool is None or st.session_state.get("pool_sig") != sig:
        pool = KeyPool(keys)
        st.session_state["pool"] = pool
        st.session_state["pool_sig"] = sig
    return pool


def model_options():
    return st.session_state.get("detected_models") or MODELS


def model_index(opts):
    return opts.index(DEFAULT_MODEL) if DEFAULT_MODEL in opts else 0


def zip_bytes(mapping):
    """mapping: {name: text} -> bytes of a .zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in mapping.items():
            z.writestr(f"{name}.txt", text)
    return buf.getvalue()


# ---------- batch ----------
def run_batch(kind, places, date, model, keys):
    pool = get_pool(keys)
    builder = prompts.build_city_prompt if kind == "city" else prompts.build_dist_prompt
    store = st.session_state.setdefault(f"scripts_{kind}", {})
    log_box, prog, res_box = st.empty(), st.progress(0.0), st.empty()
    logs, results = [], []

    def log(m):
        logs.append(str(m)); log_box.code("\n".join(logs[-14:]))

    def render():
        res_box.markdown("\n".join(
            f"- {'✅' if r['ok'] else '❌'} {r['place']} — {r['note']}" for r in results))

    for n, place in enumerate(places, 1):
        log(f"[{n}/{len(places)}] {place}: generating…")
        try:
            text, key_no = pool.generate(model, builder(place, date), on_event=log)
            if text.strip():
                store[place] = text
                results.append({"place": place, "ok": True, "note": f"done · key #{key_no}"})
            else:
                results.append({"place": place, "ok": False, "note": "empty response"})
        except AllKeysExhausted as e:
            results.append({"place": place, "ok": False, "note": str(e)})
            render(); prog.progress(n / len(places))
            st.error(f"⛔ Stopped at {place} ({n}/{len(places)}). {e}")
            break
        except Exception as e:
            results.append({"place": place, "ok": False, "note": f"{type(e).__name__}: {e}"})
        render(); prog.progress(n / len(places))

    ok = sum(1 for r in results if r["ok"])
    st.success(f"Done — ✅ {ok}/{len(places)} · 🔑 {pool.remaining()}/{len(keys)} keys left")


# ================= UI =================
st.title("📺 LocalAI TV — Telugu Bulletin Generator")
st.caption("Streamlit in Snowflake · Gemini REST · auto key-rotation")

with st.sidebar:
    st.header("🔑 API Keys")
    sk = load_keys(secret_keys())
    st.write(f"**{len(sk)}** key(s) from Snowflake secret `gemini_keys`."
             if sk else "No keys in secret `gemini_keys` yet — paste below or bind the secret.")
    st.text_area("Override keys for this session (one per line)", key="keys_override", height=110)
    keys = current_keys()
    if keys:
        pool = get_pool(keys)
        st.markdown("**Key status**")
        for s in pool.status():
            dot = {"active": "🟢", "idle": "⚪️", "spent": "🔴"}[s["state"]]
            st.write(f"{dot} #{s['n']} `{s['masked']}` · {s['state']}")
        if st.button("🔍 Detect models"):
            try:
                st.session_state["detected_models"] = list_models(keys[0])
                st.success(f"{len(st.session_state['detected_models'])} models")
                st.rerun()
            except Exception as e:
                st.error(f"{type(e).__name__}: {e}")
    else:
        st.warning("No usable keys.")

tab_city, tab_dist, tab_head = st.tabs(["🏙️ City", "🏛️ District", "📰 Headlines"])

for kind, tab in (("city", tab_city), ("dist", tab_dist)):
    with tab:
        c1, c2 = st.columns([2, 1])
        with c1:
            raw = st.text_area("Places (comma-separated)", prompts.DEFAULT_PLACES, height=90,
                               key=f"{kind}_places")
        with c2:
            date = st.text_input("Date (DD-MM-YYYY)", prompts.DEFAULT_DATE, key=f"{kind}_date")
            opts = model_options()
            model = st.selectbox("Model", opts, index=model_index(opts), key=f"{kind}_model")
        places = [p.strip() for p in raw.replace("\n", ",").split(",") if p.strip()]
        st.caption(f"{len(places)} place(s)")
        if st.button(f"✨ Generate {len(places)} {kind} scripts", type="primary", key=f"{kind}_go",
                     use_container_width=True):
            keys = current_keys()
            if not keys:
                st.error("Add API keys (secret or sidebar).")
            elif not places:
                st.error("Enter at least one place.")
            else:
                run_batch(kind, places, date.strip(), model, keys)
        store = st.session_state.get(f"scripts_{kind}", {})
        if store:
            st.download_button(f"⬇️ Download {len(store)} {kind} scripts (ZIP)",
                               zip_bytes(store), f"{kind}_scripts.txt.zip", "application/zip",
                               key=f"{kind}_dl", use_container_width=True)

with tab_head:
    st.markdown("Headlines from your generated scripts (this session) or uploaded `.txt` files.")
    src = st.radio("Source", ["This session's City scripts", "This session's District scripts",
                              "Upload .txt files"], key="h_src")
    method = st.radio("Method", ["🤖 AI — Gemini editor (recommended)",
                                 "🆓 Free — parse raw titles (no key)"], key="h_method")
    use_ai = method.startswith("🤖")
    opts = model_options()
    h_model = st.selectbox("Model (AI only)", opts, index=model_index(opts), key="h_model",
                           disabled=not use_ai)

    docs = {}
    if src == "This session's City scripts":
        docs = dict(st.session_state.get("scripts_city", {}))
    elif src == "This session's District scripts":
        docs = dict(st.session_state.get("scripts_dist", {}))
    else:
        ups = st.file_uploader("Upload script .txt files", type=["txt"], accept_multiple_files=True)
        for u in (ups or []):
            docs[u.name.rsplit(".", 1)[0]] = u.getvalue().decode("utf-8", "ignore")
    st.caption(f"{len(docs)} document(s) ready")

    if st.button("📰 Generate headlines", type="primary", key="h_go", use_container_width=True):
        keys = current_keys()
        if not docs:
            st.error("No documents — generate scripts or upload files first.")
        elif use_ai and not keys:
            st.error("AI method needs keys, or switch to Free.")
        else:
            pool = get_pool(keys) if use_ai else None
            out = {}
            prog, logbox, logs = st.progress(0.0), st.empty(), []
            def hlog(m): logs.append(str(m)); logbox.code("\n".join(logs[-10:]))
            items = list(docs.items())
            for n, (name, content) in enumerate(items, 1):
                hlog(f"[{n}/{len(items)}] {name}…")
                try:
                    if use_ai:
                        text, key_no = pool.generate(h_model, prompts.build_headline_prompt(content),
                                                     on_event=hlog)
                        line = prompts.format_headlines(text)
                        tag = f"key #{key_no}"
                    else:
                        line, _ = headlines_local.extract(content); tag = "free"
                    if line:
                        out[name] = line
                        st.markdown(f"**{name}** · {len(line.split(prompts.HEADLINE_SEP))} headlines · {tag}")
                        st.code(line, language=None)
                except AllKeysExhausted as e:
                    st.error(f"⛔ {name}: {e}"); break
                except Exception as e:
                    st.error(f"{name}: {type(e).__name__}: {e}")
                prog.progress(n / len(items))
            if out:
                st.download_button(f"⬇️ Download {len(out)} headline files (ZIP)", zip_bytes(out),
                                   "headlines.txt.zip", "application/zip", use_container_width=True)
