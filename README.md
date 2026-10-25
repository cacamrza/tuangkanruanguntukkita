# Roll of Us — Aca & Akmal (Streamlit + Supabase)

Vintage-style shared memory diary built with Streamlit, Supabase Auth, Postgres and private Storage.

## 1. Create the two accounts first
In Supabase Dashboard → Authentication → Users, create the accounts for Aca and Akmal. Use email/password sign-in.

## 2. Run the database SQL
Open SQL Editor, run `supabase-setup.sql`. Then copy each Auth user's UUID and email from Authentication → Users and run:
```sql
insert into public.couple_members (user_id, email) values
('ACTUAL-ACA-USER-UUID', 'aca@example.com'),
('ACTUAL-AKMAL-USER-UUID', 'akmal@example.com');
```
Replace placeholders with real values. Do not insert literal placeholder values. The allowlist controls access to shared memories and photos.

## 3. Configure secrets locally
Create `.streamlit/secrets.toml` (make `.streamlit` folder if needed) containing:
```toml
SUPABASE_URL = "https://YOUR-PROJECT-ID.supabase.co"
SUPABASE_ANON_KEY = "YOUR_PUBLISHABLE_OR_ANON_KEY"
```
Use the Project URL and publishable/anon key from Supabase. Never use a service_role/secret key in this app.

## 4. Run locally
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## 5. Publish online
1. Upload the project files to a private or public GitHub repository. Do not upload `.streamlit/secrets.toml`.
2. Open https://share.streamlit.io/ and deploy the repository, selecting `app.py` as the main file.
3. In App settings → Secrets, paste the same TOML config values.
4. Keep the Supabase project active and make sure Auth users and membership rows exist.

## Security notes
- The app uses Supabase Auth; shared data and the Storage bucket are guarded by RLS policies.
- The publishable/anon key is intended for client use when RLS is correctly configured. Never use a service-role key in Streamlit secrets for this app.
- This version relies on Supabase Auth login during the current Streamlit session. If the app restarts or session state is lost, users may need to log in again.
- Export/restore and migration from the old browser IndexedDB are not included. Old local browser data does not automatically migrate to cloud.
- Photo deletion on memory deletion is best-effort in this starter; if you need strict storage cleanup, implement a server-side transaction/workflow.
