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
    st.markdown("""
    <style>
    .block-container {max-width: 1180px; padding-top: 2rem;}
    .camera-shell {background:#d5a477;border-radius:18px;padding:15px;max-width:360px;margin:0 auto;
        transform:rotate(1deg);box-shadow:0 18px 30px #715c3c25;}
    .camera-top {background:#c18c60;border-radius:12px;padding:16px;display:flex;align-items:center;
        justify-content:center;gap:18px;flex-wrap:wrap;}
    .camera-label {width:100%;font:9px 'DM Mono',monospace;letter-spacing:.13em;color:#60412c;
        display:flex;justify-content:space-between;}
    .camera-lens {width:112px;height:112px;border:8px solid #3d342b;outline:2px dashed #e5d0aa;
        outline-offset:-15px;border-radius:50%;display:grid;place-items:center;
        background:radial-gradient(circle at 40% 35%,#64857b,#214c43 52%,#172a25 70%);
        color:#e9b578;font-size:24px;box-shadow:0 7px 10px #4e2e20aa;}
    .date-stack {display:grid;gap:5px;font:9px 'DM Mono',monospace;}
    .date-stack span {background:#ae7d54;border:1px solid #dfb88e;color:#fff4e3;padding:2px 8px;border-radius:3px;}
    .pin-card {background:#fffdf8;border-radius:5px 5px 12px 12px;text-align:center;padding:22px 18px 20px;}
    .lock-icon {margin:0 auto 10px;border-radius:50%;width:34px;height:34px;display:grid;place-items:center;
        background:#e5eee7;color:#28584f;}
    .pin-caption {font:9px 'DM Mono',monospace;letter-spacing:.13em;color:#bd5736;}
    .private-note {display:block;color:#8c8173;font-size:10px;margin-top:12px;}
    div[data-testid="stForm"] {border:0;padding:0;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="eyebrow">▦ PRIVATE FILM DIARY · VOL. 01</div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, .9], gap="large")
    with left:
        st.markdown(
            '<div class="hero"><p class="eyebrow">A LITTLE PLACE FOR OUR MEMORIES</p>'
            '<h1>Every little thing<br><em>worth remembering.</em></h1>'
            '<p>A tiny archive of our ordinary magic. Cerita kita, frame by frame — '
            'masukkan PIN rahasia untuk membuka gulungan film ini.</p>'
            '<p style="font-family:Playfair Display,serif;font-style:italic;font-size:1.25rem">'
            '“Somewhere between hello and always.”</p>'
            '<div class="small-mono">26 · 09 · 26 &nbsp; / &nbsp; A + A</div></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown("""
        <div class="camera-shell">
          <div class="camera-top">
            <div class="camera-label"><span>ROLL OF US</span><span>●</span></div>
            <div class="camera-lens">♥</div>
            <div class="date-stack"><span>26</span><span>09</span><span>26</span></div>
          </div>
          <div class="pin-card">
            <div class="lock-icon">♧</div>
            <p class="pin-caption">THE SECRET DATE</p>
        """, unsafe_allow_html=True)
        with st.form("shared_pin_form", clear_on_submit=False):
            pin = st.text_input(
                "PIN rahasia",
                placeholder="D D M M Y Y Y Y",
                type="password",
                max_chars=8,
                label_visibility="collapsed",
            )
            submitted = st.form_submit_button("Open our archive ↗", use_container_width=True)
        st.markdown('<span class="private-note">♧ private by design · just for us two</span></div></div>', unsafe_allow_html=True)
        if submitted:
            expected_pin = str(get_secret("APP_PIN", ""))
            if expected_pin and pin.strip() == expected_pin:
                st.session_state.pin_authenticated = True
                st.session_state.pin_auth_time = datetime.now().isoformat()
                st.rerun()
            else:
                st.error("PIN belum cocok. Coba tanggal rahasia kita lagi, ya ♡")
    st.markdown("---")
    st.caption("KEEP THIS LITTLE WORLD CLOSE · ♡")



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
        if st.button("↪ Lock diary", use_container_width=True):
            st.session_state.pin_authenticated = False
            st.session_state.user = None
            st.session_state.show_add = False
            st.session_state.edit_memory = None
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
                payload = {"body": letter_text}
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
                supabase.table("favorites").insert({"category": cat, "text": fav.strip()}).execute()
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
    if not st.session_state.get("pin_authenticated", False):
        login_screen()
    else:
        archive_screen()

main()
