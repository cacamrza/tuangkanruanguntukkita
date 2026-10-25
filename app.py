import os
import uuid
from datetime import date, datetime
from typing import Optional

import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Roll of Us — Aca & Akmal",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- Vintage editorial styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&display=swap');
:root { --paper:#f7f1e6; --ink:#211d19; --muted:#786e62; --rust:#bd5736; --green:#28584f; --line:#dfd2bd; }
.stApp { background: #f7f1e6; color: #211d19; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
h1,h2,h3 { font-family:'Playfair Display',Georgia,serif !important; font-weight:400 !important; letter-spacing:-.035em; color:#211d19; }
.eyebrow { font-family:'DM Mono',monospace; letter-spacing:.13em; text-transform:uppercase; color:#bd5736; font-size:.72rem; }
.hero { padding:2.2rem 0 1.5rem; }
.hero h1 { font-size:clamp(3rem,7vw,6rem); line-height:.98; margin:.4rem 0 1.1rem; }
.hero em { color:#bd5736; }
.hero p { color:#786e62; line-height:1.85; max-width:42rem; }
.paper-card { background:#fffdf8; border:1px solid #dfd2bd; padding:1.2rem; border-radius:4px; }
.polaroid { background:#fffdf8; padding:10px 10px 18px; border:1px solid #e8dfd1; box-shadow:0 10px 25px #57452d15; }
.polaroid img { width:100%; height:260px; object-fit:cover; }
.small-mono { font-family:'DM Mono',monospace; font-size:.72rem; letter-spacing:.1em; color:#bd5736; text-transform:uppercase; }
div.stButton > button, div.stFormSubmitButton > button { background:#28584f; color:white; border:0; border-radius:7px; min-height:2.7rem; }
div.stButton > button:hover, div.stFormSubmitButton > button:hover { background:#356b60; color:white; border:0; }
input, textarea { background:#fffdf8 !important; }
hr { border-color:#dfd2bd; }
footer { visibility:hidden; }
[data-testid="stSidebar"] { background:#eee3d0; }
div[data-testid="stFileUploader"] { background:#fffdf8; padding:.5rem; border:1px dashed #cdbda7; border-radius:8px; }
</style>
""", unsafe_allow_html=True)

def get_secret(name: str, default: Optional[str] = None):
    try:
        return st.secrets.get(name, default)
    except Exception:
        return os.environ.get(name, default)

def make_supabase(url: str, key: str) -> Client:
    # Do not cache an authenticated Supabase client globally: Streamlit serves many users.
    # Each browser session must have its own client to avoid sharing auth state.
    return create_client(url, key)

def config_values():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        st.error("Konfigurasi belum lengkap. Isi `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, dan `APP_PIN` di Streamlit Secrets.")
        st.code('SUPABASE_URL = "https://PROJECT-ID.supabase.co"\nSUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"\nAPP_PIN = "26092026"')
        st.stop()
    return url, key

url, anon_key = config_values()
if not get_secret("APP_PIN"):
    st.error("APP_PIN belum diatur di Streamlit Secrets. Isi dengan PIN bersama 26092026.")
    st.stop()
supabase = make_supabase(url, anon_key)

if "pin_authenticated" not in st.session_state:
    st.session_state.pin_authenticated = False
if "show_add" not in st.session_state:
    st.session_state.show_add = False
if "edit_memory" not in st.session_state:
    st.session_state.edit_memory = None

class SharedDiaryUser:
    # Minimal identity used only for ownership/audit fields in the app.
    id = "aca-akmal-shared-diary"

st.session_state.user = SharedDiaryUser() if st.session_state.pin_authenticated else None

if "show_add" not in st.session_state:
    st.session_state.show_add = False
if "edit_memory" not in st.session_state:
    st.session_state.edit_memory = None

def user_email():
    return None


def signed_photo(path: str) -> Optional[str]:
    if not path:
        return None
    try:
        result = supabase.storage.from_("memories").create_signed_url(path, 60 * 60)
        return result.get("signedURL") or result.get("signedUrl")
