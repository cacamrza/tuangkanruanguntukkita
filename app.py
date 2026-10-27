import os
import uuid
from datetime import date, datetime
from typing import Optional

import streamlit as st
from supabase import create_client, Client

st.set_page_config(
    page_title="Roll of Us — A",
    page_icon="📷",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown("""
<style>
/* Label input: gunakan warna terang agar terbaca */
.stTextInput label,
.stTextInput label p,
.stForm label,
.stForm label p {
    color: #49372d !important;
    font-weight: 600 !important;
}
/* Vintage card: days counting */
.memory-counter {
    position: relative;
    overflow: hidden;
    border: 1px solid #c87858;
    border-radius: 18px;
    padding: 30px;
    min-height: 245px;
    color: #8f1e1e;
    background: linear-gradient(
        135deg,
        #b95738 0%,
        #8d3f2d 55%,
        #492c27 100%
    );
    box-shadow: 0 9px 22px rgba(95, 48, 32, 0.16);
}
.memory-counter::after {
    content: "♡";
    position: absolute;
    right: 22px;
    bottom: 5px;
    font-family: Georgia, serif;
    font-size: 76px;
    color: rgba(255, 235, 215, 0.13);
}
.memory-counter p {
    color: #912c3d;
    letter-spacing: 2px;
}
/* Vintage paper: notes */
.memory-quote {
    position: relative;
    border: 1px solid #e4c9aa;
    border-left: 5px solid #c76b4a;
    border-radius: 4px 16px 16px 4px;
    padding: 28px 30px;
    min-height: 180px;
    color: #49352e;
    background: linear-gradient(
        135deg,
        #fffaf1 0%,
        #f7e7d4 100%
    );
    box-shadow: 0 8px 20px rgba(95, 65, 45, 0.09);
}
.memory-quote p {
    color: #49352e;
    font-family: Georgia, serif;
    font-style: italic;
    line-height: 1.8;
}
.memory-quote strong {
    color: #b95738;
}
/* Teks di dalam kolom input */
.stTextInput input {
    color: #29211d !important;
    background-color: #fffdf8 !important;
}
/* Teks petunjuk di dalam kolom */
.stTextInput input::placeholder {
    color: #8b796c !important;
    opacity: 1 !important;
}
/* Smaller vintage diary photos */
div[data-testid="stImage"] {
    max-width: 280px !important;
    width: 100% !important;
    margin-top: 12px;
    margin-bottom: 16px;
}
div[data-testid="stImage"] img {
    width: 100% !important;
    height: 180px !important;
    object-fit: cover !important;
    border-radius: 10px !important;
    border: 1px solid #e5d4bf;
    box-shadow: 0 5px 14px rgba(69, 43, 28, 0.12);
}
/* Romantic letter section */
.ily-message {
    background: linear-gradient(135deg, #fffaf1, #f4e4d3);
    border: 1px solid #dfc3a5;
    border-left: 5px solid #c45b3c;
    border-radius: 14px;
    padding: 20px 24px;
    margin: 16px 0 22px 0;
    color: #49372f;
    font-family: Georgia, serif;
    font-size: 20px;
    line-height: 1.8;
    box-shadow: 0 5px 16px rgba(91, 57, 39, 0.08);
}

.ily-message::before {
    content: "♡  A LITTLE NOTE FOR YOU";
    display: block;
    color: #bd593c;
    font-family: sans-serif;
    font-size: 11px;
    letter-spacing: 2px;
    margin-bottom: 10px;
}

div[data-testid="stTextArea"] textarea {
    background: #fffaf4 !important;
    color: #49372f !important;
    border: 1px solid #dfc3a5 !important;
    border-radius: 12px !important;
    line-height: 1.8 !important;
    padding: 16px !important;
}

div[data-testid="stTextArea"] label {
    color: #a64f35 !important;
    font-weight: 600 !important;
}

div[data-testid="stButton"] button {
    border-radius: 10px !important;
    transition: all 0.2s ease;
}

div[data-testid="stButton"] button:hover {
    border-color: #c45b3c !important;
    color: #c45b3c !important;
}
</style>
""", unsafe_allow_html=True)

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
    # Runs only on Streamlit's server. Never use this service key in browser JavaScript.
    return create_client(url, key)

def config_values():
    url = get_secret("SUPABASE_URL")
    key = get_secret("SUPABASE_SERVICE_ROLE_KEY")
    pin = get_secret("SHARED_PIN")
    if not url or not key or not pin:
        st.error("Konfigurasi belum lengkap. Isi SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, dan SHARED_PIN di Streamlit Secrets.")
        st.code('SUPABASE_URL = "https://PROJECT-ID.supabase.co"\nSUPABASE_SERVICE_ROLE_KEY = "YOUR_SUPABASE_SERVICE_ROLE_KEY"\nSHARED_PIN = "26092026"')
        st.stop()
    return url, key, str(pin)

url, service_key, SHARED_PIN = config_values()
supabase = make_supabase(url, service_key)

# Session state is scoped to each visitor's Streamlit browser session.
if "unlocked" not in st.session_state:
    st.session_state.unlocked = False
if "show_add" not in st.session_state:
    st.session_state.show_add = False
if "edit_memory" not in st.session_state:
    st.session_state.edit_memory = None

# Fixed non-personal actor UUID. The SQL patch removes auth.users foreign keys because
# this app uses a server-verified shared PIN rather than individual Supabase Auth users.
SERVER_ACTOR_ID = "00000000-0000-0000-0000-000000000001"

def signed_photo(path: str) -> Optional[str]:
    if not path:
        return None
    try:
        result = supabase.storage.from_("memories").create_signed_url(path, 20 * 20)
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
        path = f"shared/{uuid.uuid4().hex}.{suffix}"
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
    <div class="eyebrow">▦ PRIVATE FILM DIARY · VOL. 01</div>
    <style>
    .pin-camera { background:#c18c60; border-radius:15px; padding:18px; max-width:420px; margin:1.5rem auto 0; box-shadow:0 18px 32px #715c3c25; transform:rotate(.5deg); }
    .pin-camera-top { background:#b98255; border-radius:10px; padding:18px; display:flex; align-items:center; justify-content:center; gap:20px; flex-wrap:wrap; }
    .pin-camera-label { width:100%; display:flex; justify-content:space-between; color:#60412c; font-family:'DM Mono',monospace; letter-spacing:.12em; font-size:.7rem; }
    .pin-lens { width:112px;height:112px;border:8px solid #3d342b;outline:2px dashed #e5d0aa;outline-offset:-15px;border-radius:50%;display:grid;place-items:center;background:radial-gradient(circle at 40% 35%,#64857b,#214c43 52%,#172a25 70%);color:#e9b578;font-size:28px;box-shadow:0 7px 10px #4e2e20aa; }
    .pin-date { display:grid;gap:5px;font-family:'DM Mono',monospace;font-size:.75rem; }
    .pin-date span { background:#ae7d54;border:1px solid #dfb88e;color:#fff4e3;padding:2px 9px;border-radius:3px; }
    .pin-paper { background:#fffdf8;border-radius:5px 5px 12px 12px;padding:22px;text-align:center;margin-top:0; }
    .pin-paper small { color:#8c8173; }
    </style>
    """, unsafe_allow_html=True)
    left, right = st.columns([1.05, .95], gap="large")
    with left:
        st.markdown(
            '<div class="hero"><h1>Every little thing<br><em>worth remembering.</em></h1>'
            '<p>A tiny archive of our ordinary magic. Cerita kita, frame by frame — kept here for whenever we need to remember.</p>'
            '<p style="font-family:Playfair Display,serif;font-style:italic;font-size:1.25rem">“Somewhere between hello and always.”</p>'
            '<div class="small-mono">our memories &nbsp; / &nbsp; A </div></div>',
            unsafe_allow_html=True
        )
    with right:
        st.markdown(
            '<div class="pin-camera"><div class="pin-camera-top">'
            '<div class="pin-camera-label"><span>ROLL OF US</span><span>●</span></div>'
            '<div class="pin-lens">♥</div><div class="pin-date"><span>26</span><span>09</span><span>26</span></div>'
            '</div><div class="pin-paper"><div class="eyebrow">♧ THE SECRET DATE</div></div></div>',
            unsafe_allow_html=True
        )
        with st.form("shared_pin_form", clear_on_submit=True):
            pin_entry = st.text_input("PIN bersama", placeholder="DDMMYYYY", max_chars=8, type="password", label_visibility="collapsed")
            submitted = st.form_submit_button("Open our archive ↗", use_container_width=True)
        st.caption("♧ private by design · just for us two")
        if submitted:
            # PIN is compared on the server; it is never placed in a URL or client-side script.
            if pin_entry.strip() == SHARED_PIN:
                st.session_state.unlocked = True
                st.rerun()
            else:
                st.error("PIN belum cocok. Coba lagi, ya ♡")
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
        location = st.text_input("Lokasi", value=(existing or {}).get("location", ""), max_chars=150, placeholder="Tujuan hari itu kemana?")
        story = st.text_area("Cerita kecil", value=(existing or {}).get("story", ""), height=130, placeholder="Produktivitas apa yang kalian lakukan?")
        favorite = st.text_input("Makanan / favorit hari itu", value=(existing or {}).get("mam", ""), max_chars=180)
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
                "created_by": SERVER_ACTOR_ID,
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
    st.markdown('<div class="small-mono">▦ A · PRIVATE ARCHIVE · VOL. 01</div>', unsafe_allow_html=True)
    a, b = st.columns([4, 1])
    with a:
        st.markdown('<div class="hero"><h1>Our little<br><em>analog diary.</em></h1><p>A collection of the days that felt like forever. Cerita kita, frame by frame — kept here for whenever we need to remember.</p><div class="small-mono">STARTED ON · 26 SEPTEMBER 2026</div></div>', unsafe_allow_html=True)
    with b:
        st.write("")
        st.write("")
        if st.button("↪ Lock diary", use_container_width=True):
            st.session_state.unlocked = False
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
                    st.markdown(f"☕ **anythings:** {memory['favorite']}")
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

    letter_text = st.text_area(
        "Tulis surat baru di sini ♡",
        value="",
        height=160,
        key="letter_text"
    )

    try:
        result = supabase.table("letters").select("*").limit(1).execute()
        saved_letter = result.data[0] if result.data else None
    except Exception as exc:
        saved_letter = None
        st.error(f"Gagal memuat surat: {exc}")

    latest_message = (saved_letter or {}).get("body", "ILY")

    with st.expander("Open the letter ♡"):
        st.markdown(
            f"<div class='ily-message'>{latest_message}</div>",
            unsafe_allow_html=True
        )

    
    if st.button("♡ Save new letter", key="save_new_letter"):
        new_text = st.session_state.get("letter_text", "").strip()

        if not new_text:
            st.warning("Tulis notes-nya dulu ya ♡")
        else:
            try:
                payload = {
                    "body": new_text,
                    "updated_by": SERVER_ACTOR_ID
                }

                if saved_letter:
                    supabase.table("letters").update(payload).eq(
                        "id", saved_letter["id"]
                    ).execute()
                else:
                    supabase.table("letters").insert(payload).execute()

                st.success("Little note berhasil diganti ♡")
                st.rerun()

            except Exception as exc:
                st.error(f"Gagal mengganti notes: {exc}")
    
    st.markdown("---")
    st.markdown("## Our kind of favorite")
    with st.form("favorite_form", clear_on_submit=True):
        cat = st.selectbox(
            "Kategori",
            ["FOOD", "INSIDE JOKES", "PLACES", "LITTLE THINGS"]
        )
        fav = st.text_input(
            "Favorit kecil kita",
            placeholder="Makanan, lelucon, atau detail kecil"
        )
        submitted = st.form_submit_button("Add favorite +")

        if submitted:
        if fav.strip():
            try:
                supabase.table("favorites").insert({
                    "category": cat,
                    "text": fav.strip()
                }).execute()

                st.success("Favorite berhasil ditambahkan ♡")
                st.rerun()

            except Exception as exc:
                st.error(f"Gagal menambahkan favorite: {exc}")
        else:
            st.warning("Isi favorit kecil kita dulu ya ♡")
    try:
        result = supabase.table("favorites").select("*").execute()
        favorites = result.data or []
    except Exception as exc:
        st.error(f"Gagal memuat favorite: {exc}")
        favorites = []

    if favorites:
        cols = st.columns(2)
        for i, item in enumerate(favorites):
            with cols[i % 2]:
                st.markdown(
                    f"""<div class="paper-card">
                    <div class="eyebrow">{item.get("category", "LITTLE THINGS")}</div>
                    <p>{item.get("text", "")}</p>
                    </div>""",
                    unsafe_allow_html=True
                )
                if st.button("Remove", key=f"favdel_{item['id']}"):
                    try:
                        supabase.table("favorites").delete().eq(
                            "id", item["id"]
                        ).execute()
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))

    st.markdown("---")
    st.caption("MADE OF LITTLE MOMENTS, KEPT WITH LOVE ·A ♡")

def main():
    if not st.session_state.unlocked:
        login_screen()
    else:
        archive_screen()

main()
