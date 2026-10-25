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
    key = get_secret("SUPABASE_ANON_KEY")
    if not url or not key:
        st.error("Konfigurasi Supabase belum ditemukan. Isi `SUPABASE_URL` dan `SUPABASE_ANON_KEY` di Streamlit Secrets.")
        st.code('SUPABASE_URL = "https://PROJECT-ID.supabase.co"\nSUPABASE_ANON_KEY = "sb_publishable_..."')
        st.stop()
    return url, key

url, anon_key = config_values()
supabase = make_supabase(url, anon_key)
# Restore the current browser session only into this per-session client.
if st.session_state.get("access_token") and st.session_state.get("refresh_token"):
    try:
        supabase.auth.set_session(st.session_state.access_token, st.session_state.refresh_token)
        if st.session_state.get("user") is None:
            st.session_state.user = supabase.auth.get_user().user
    except Exception:
        st.session_state.user = None
        st.session_state.access_token = None
        st.session_state.refresh_token = None

if "session" not in st.session_state:
    st.session_state.session = None
if "user" not in st.session_state:
    st.session_state.user = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "refresh_token" not in st.session_state:
    st.session_state.refresh_token = None
if "show_add" not in st.session_state:
    st.session_state.show_add = False
if "edit_memory" not in st.session_state:
    st.session_state.edit_memory = None

def user_email():
    user = st.session_state.user
    return getattr(user, "email", None) if user else None

def signed_photo(path: str) -> Optional[str]:
    if not path:
        return None
    try:
        result = supabase.storage.from_("memories").create_signed_url(path, 60 * 60)
        return result.get("signedURL") or result.get("signedUrl")
    except Exception:
        return None

def list_memories():
    response = (supabase.table("memories")
                .select("*")
                .order("memory_date", desc=True)
                .execute())
    return response.data or []

def list_favorites():
    response = supabase.table("favorites").select("*").order("created_at", desc=True).execute()
    return response.data or []

def save_uploaded_photos(files):
    paths = []
    for file in files or []:
        raw = file.getvalue()
        suffix = (file.name.rsplit(".", 1)[-1] if "." in file.name else "jpg").lower()
        if suffix not in {"jpg", "jpeg", "png", "webp", "gif"}:
            suffix = "jpg"
        path = f"{st.session_state.user.id}/{uuid.uuid4().hex}.{suffix}"
        content_type = file.type or "image/jpeg"
        supabase.storage.from_("memories").upload(
            path, raw,
            file_options={"content-type": content_type, "upsert": "false"}
        )
        paths.append(path)
    return paths

def delete_photo(path: str):
    try:
        supabase.storage.from_("memories").remove([path])
    except Exception:
        pass

def login_screen():
    st.markdown('<div class="eyebrow">▦ PRIVATE FILM DIARY · VOL. 01</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, .9], gap="large")
    with left:
        st.markdown('<div class="hero"><h1>Every little thing<br><em>worth remembering.</em></h1><p>A tiny archive of our ordinary magic. Cerita kita, frame by frame — kept here for whenever we need to remember.</p><p style="font-family:Playfair Display,serif;font-style:italic;font-size:1.25rem">“Somewhere between hello and always.”</p><div class="small-mono">26 · 09 · 26 &nbsp; / &nbsp; A + A</div></div>', unsafe_allow_html=True)
    with right:
        st.markdown('<div class="paper-card">', unsafe_allow_html=True)
        st.markdown("### ♧ Welcome to our little archive")
        st.caption("Login dengan akun privat Aca atau Akmal.")
        with st.form("login_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password", placeholder="Password akun")
            submitted = st.form_submit_button("Open our archive ↗", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        if submitted:
            try:
                auth = supabase.auth.sign_in_with_password({"email": email.strip(), "password": password})
                st.session_state.session = auth.session
                st.session_state.user = auth.user
                st.session_state.access_token = auth.session.access_token
                st.session_state.refresh_token = auth.session.refresh_token
                st.rerun()
            except Exception as exc:
                st.error("Login gagal. Periksa email/password dan pastikan akun sudah dibuat di Supabase Authentication.")
                st.caption(str(exc))
    st.markdown("---")
    st.caption("PRIVATE BY DESIGN · JUST FOR US TWO")

def add_or_edit_form(memories):
    editing = st.session_state.edit_memory
    existing = next((m for m in memories if m["id"] == editing), None) if editing else None
    st.markdown("### Edit a memory" if existing else "### Save a new memory")
    with st.form("memory_form", clear_on_submit=True):
        default_date = date.fromisoformat(existing["memory_date"]) if existing and existing.get("memory_date") else date.today()
        memory_date = st.date_input("Tanggal pertemuan", value=default_date)
        title = st.text_input("Judul kenangan", value=(existing or {}).get("title", ""), max_chars=100, placeholder="Contoh: Sushi after work")
        location = st.text_input("Lokasi", value=(existing or {}).get("location", ""), max_chars=150, placeholder="Di mana kalian bertemu?")
        story = st.text_area("Cerita kecil", value=(existing or {}).get("story", ""), height=130, placeholder="Apa yang paling berkesan hari itu?")
        favorite = st.text_input("Makanan / favorit hari itu", value=(existing or {}).get("favorite", ""), max_chars=180)
        note = st.text_input("Catatan tambahan", value=(existing or {}).get("note", ""), max_chars=180)
        uploads = st.file_uploader("Foto kenangan (pilih beberapa)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)
        if existing and existing.get("photo_paths"):
            st.caption(f"{len(existing['photo_paths'])} foto lama tetap disimpan. Upload foto baru untuk menambahkan foto.")
        submitted = st.form_submit_button("Update memory" if existing else "Save this memory", use_container_width=True)
    if submitted:
        if not title.strip() or not story.strip():
            st.warning("Isi judul dan cerita kenangan dulu, ya.")
            return
        try:
            paths = save_uploaded_photos(uploads)
            old_paths = (existing or {}).get("photo_paths") or []
            payload = {
                "title": title.strip(), "memory_date": memory_date.isoformat(),
                "location": location.strip(), "story": story.strip(),
                "favorite": favorite.strip(), "note": note.strip(),
                "photo_paths": old_paths + paths,
                "created_by": st.session_state.user.id,
            }
            if existing:
                supabase.table("memories").update(payload).eq("id", existing["id"]).execute()
                st.session_state.edit_memory = None
                st.success("Kenangan berhasil diperbarui ♡")
            else:
                supabase.table("memories").insert(payload).execute()
                st.success("Kenangan baru tersimpan ♡")
            st.session_state.show_add = False
            st.rerun()
        except Exception as exc:
            st.error("Gagal menyimpan kenangan. Periksa SQL, RLS, dan bucket `memories`.")
            st.caption(str(exc))

def archive_screen():
    st.markdown('<div class="small-mono">▦ A + A · PRIVATE ARCHIVE · VOL. 01</div>', unsafe_allow_html=True)
    a, b = st.columns([4, 1])
    with a:
        st.markdown('<div class="hero"><h1>Our little<br><em>analog diary.</em></h1><p>A collection of the days that felt like forever. Cerita kita, frame by frame — kept here for whenever we need to remember.</p><div class="small-mono">STARTED ON · 26 SEPTEMBER 2026</div></div>', unsafe_allow_html=True)
    with b:
        st.write("")
        st.write("")
        if st.button("↪ Logout", use_container_width=True):
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
            st.session_state.session = None
            st.session_state.user = None
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.rerun()
    try:
        memories = list_memories()
        favorites = list_favorites()
    except Exception as exc:
        st.error("Tidak bisa mengambil data cloud. Pastikan SQL setup sudah dijalankan dan user sudah ditambahkan ke couple_members.")
        st.caption(str(exc))
        return

    start = date(2026, 9, 26)
    days = max(0, (date.today() - start).days + 1)
    c1, c2 = st.columns([.8, 1.2])
    with c1:
        st.markdown(f'<div class="paper-card"><div class="eyebrow">OUR TIME TOGETHER</div><h1 style="font-size:4rem;margin:.4rem 0">{days:,}</h1><div class="small-mono">DAYS AND COUNTING</div><small>since 26 September 2026</small></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="paper-card"><div class="eyebrow">A NOTE FROM THE ARCHIVE</div><p style="font-family:Playfair Display,serif;font-size:1.35rem;font-style:italic">“Tidak semua hal kecil perlu jadi besar. Some memories are perfect just because they are ours.”</p><small>— keep looking for the soft light</small></div>', unsafe_allow_html=True)

    st.markdown("---")
    head, addcol = st.columns([4, 1])
    with head:
        st.markdown("## Frames we keep returning to.")
        st.caption(f"{len(memories)} LITTLE CHAPTERS")
    with addcol:
        if st.button("＋ Add a memory", use_container_width=True):
            st.session_state.show_add = not st.session_state.show_add
            st.session_state.edit_memory = None
    if st.session_state.show_add or st.session_state.edit_memory:
        add_or_edit_form(memories)
        st.markdown("---")

    if not memories:
        st.info("Every story starts somewhere. Tambahkan kenangan pertama kalian.")
    for idx, memory in enumerate(memories):
        with st.container(border=True):
            col_date, col_main = st.columns([1, 4], gap="large")
            with col_date:
                st.markdown(f'<div class="small-mono">{memory.get("memory_date","")}</div><p style="color:#bd5736">FRAME {len(memories)-idx:03d}</p>', unsafe_allow_html=True)
            with col_main:
                st.markdown(f"### {memory.get('title','Untitled memory')}")
                if memory.get("location"):
                    st.caption(f"♧ {memory['location']}")
                st.write(memory.get("story", ""))
                paths = memory.get("photo_paths") or []
                if paths:
                    cols = st.columns(min(3, len(paths)))
                    for i, path in enumerate(paths):
                        image_url = signed_photo(path)
                        if image_url:
                            cols[i % len(cols)].image(image_url, use_container_width=True)
                if memory.get("favorite"):
                    st.markdown(f"☕ **Favorite:** {memory['favorite']}")
                if memory.get("note"):
                    st.markdown(f"✧ {memory['note']}")
                e, d, _ = st.columns([1, 1, 5])
                if e.button("Edit", key=f"edit_{memory['id']}"):
                    st.session_state.edit_memory = memory["id"]
                    st.session_state.show_add = False
                    st.rerun()
                if d.button("Delete", key=f"delete_{memory['id']}"):
                    st.session_state.confirm_delete = memory["id"]
                if st.session_state.get("confirm_delete") == memory["id"]:
                    st.warning("Hapus kenangan ini? Foto terkait juga akan dihapus dari storage.")
                    yes, no = st.columns(2)
                    if yes.button("Ya, hapus", key=f"yes_{memory['id']}"):
                        try:
                            for p in paths:
                                delete_photo(p)
                            supabase.table("memories").delete().eq("id", memory["id"]).execute()
                            st.session_state.confirm_delete = None
                            st.success("Kenangan dihapus.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Gagal menghapus: {exc}")
                    if no.button("Batal", key=f"no_{memory['id']}"):
                        st.session_state.confirm_delete = None
                        st.rerun()
        st.write("")

    st.markdown("---")
    st.markdown("## A letter for us")
    try:
        result = supabase.table("letters").select("*").limit(1).execute()
        saved_letter = result.data[0] if result.data else None
    except Exception:
        saved_letter = None
    default_letter = (saved_letter or {}).get("body", "")
    with st.expander("Open the letter ♡"):
        st.markdown("Hai, Aca. Semoga kita selalu punya tempat untuk menyimpan hal-hal kecil, foto yang sedikit blur, makanan yang kita bagi, dan hari biasa yang terasa istimewa karena dijalani bersama.")
        letter_text = st.text_area("Tulis atau edit surat", value=default_letter, height=160, key="letter_text")
        if st.button("Save letter"):
            try:
                payload = {"body": letter_text, "updated_by": st.session_state.user.id}
                if saved_letter:
                    supabase.table("letters").update(payload).eq("id", saved_letter["id"]).execute()
                else:
                    supabase.table("letters").insert(payload).execute()
                st.success("Surat tersimpan ♡")
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menyimpan surat: {exc}")

    st.markdown("---")
    st.markdown("## Our kind of favorite")
    with st.form("favorite_form", clear_on_submit=True):
        cat = st.selectbox("Kategori", ["FOOD", "INSIDE JOKES", "PLACES", "LITTLE THINGS"])
        fav = st.text_input("Favorit kecil kita", placeholder="Makanan, lelucon, atau detail kecil")
        submitted = st.form_submit_button("Add favorite +")
    if submitted:
        if fav.strip():
            try:
                supabase.table("favorites").insert({"category": cat, "text": fav.strip(), "created_by": st.session_state.user.id}).execute()
                st.rerun()
            except Exception as exc:
                st.error(f"Gagal menyimpan favorit: {exc}")
    if favorites:
        cols = st.columns(2)
        for i, item in enumerate(favorites):
            with cols[i % 2]:
                st.markdown(f'<div class="paper-card"><div class="eyebrow">{item.get("category","LITTLE THINGS")}</div><p style="font-family:Playfair Display,serif;font-size:1.15rem">{item.get("text","")}</p></div>', unsafe_allow_html=True)
                if st.button("Remove", key=f"favdel_{item['id']}"):
                    try:
                        supabase.table("favorites").delete().eq("id", item["id"]).execute()
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

    st.markdown("---")
    st.caption("MADE OF LITTLE MOMENTS, KEPT WITH LOVE · ACA & AKMAL ♡")

def main():
    if st.session_state.user is None:
        login_screen()
    else:
        archive_screen()

main()
