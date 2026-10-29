# NatureClean AI — Community Cleanup Platform

A polished Streamlit app for **AI for Good · Hackathon 7 · SDG 15 (Life on Land)**.
Volunteers create accounts, upload photos of collected litter, review a Roboflow **Model V1** prediction, confirm the counts, earn participation points, and see **monthly** and **all-time** leaderboards. Photos are processed for predictions but **are not stored** by this application.

## 1. What is included

- **Dashboard:** current-month points, lifetime points, items logged, community ranking.
- **Detect Waste:** automatic AI scan on JPG/PNG upload or camera photo; bounding boxes with confidence; simple “Yes, correct / No, edit” review. In edit mode users can remove detections, change their class or add missed objects.
- **Leaderboard:** This Month and All Time. Month boundaries are calculated in **Europe/Amsterdam** time. Past months don't reset or disappear from profiles.
- **My Profile:** personal score history, past submissions, and editable nickname.
- **Accounts:** email/password authentication using Supabase Auth (email confirmation may be required).
- **Durable database:** Supabase Postgres with Row Level Security (RLS), duplicate-photo hash constraint, and points calculated by a database trigger.

**Scoring:** 10 participation points per confirmed item. Scores are *self-reported*, not independently verified cleanup impact. The leaderboard shows a proposed future gift-card reward; no contest, sponsor or payout is active.

## 2. Getting started (Windows, VS Code)

Requires Python 3.11+ and an internet connection.

1. Extract the ZIP and open the **NatureClean_AI_V2** folder in VS Code.
2. Create and activate a virtual environment (recommended):
   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```
3. Install libraries:
   ```powershell
   python -m pip install -r requirements.txt
   ```
4. Create a free **Supabase** project at https://supabase.com/dashboard.
5. In your project, open **SQL Editor → New query**. Paste **the entire contents** of `supabase/setup.sql`, then **Run**. You only need to do this once for a new project. Do not run this SQL against unrelated tables with the same names.
6. In Supabase **Project Settings → Data API**, copy the **Project URL**. In **Project Settings → API Keys**, copy the **publishable** key (legacy **anon** key also works). **Never** use a `service_role`/secret key.
7. Copy `.env.example` to `.env` in the project root:
   ```powershell
   Copy-Item .env.example .env
   ```
   Edit `.env`:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_PUBLISHABLE_KEY=your_publishable_key
   ROBOFLOW_API_KEY=your_roboflow_key
   ROBOFLOW_WORKSPACE=arbrs-workspace
   ROBOFLOW_WORKFLOW_ID=natureclean-ai-vnatureclean-ai-1-rfdetr-small-t1-logic
   ```
   Your Roboflow key is under your Roboflow account/workspace settings. **Rotate** any key that was shared in chats or public files.
8. Start the app:
   ```powershell
   python -m streamlit run app.py
   ```
   Or double-click `START_WINDOWS.bat` after installing dependencies.
9. Create an account in the app. If Supabase **Authentication → Providers → Email → Confirm email** is enabled (normally the default), confirm the email message and return to the app to sign in. Complete your nickname on first login. The email verification redirect does not need to go through Streamlit for this flow.

**Note:** This is a real Supabase integration, not a preconfigured hosted account. Accounts and live leaderboards only work after you create the Supabase project, run the SQL, and configure `.env`. The archive contains **no API keys or passwords**.

## 3. Demo flow

1. Register two email accounts (or use one and another test account). Choose distinct nicknames.
2. Sign in with the first, open **Detect Waste** and upload an unseen litter photo.
3. Confirm AI predictions or choose **No, I want to correct it**. Add missed objects as needed.
4. Tick the cleanup confirmation and submit. Points appear on **Dashboard**, **My Profile**, and the **Leaderboard**.
5. Sign out, sign in with the other account, and submit another image; both nicknames appear on the same leaderboard.
6. Switch **This month / All time**. `My Profile` keeps month-by-month history; scores from earlier calendar months remain in lifetime totals.
7. Try the identical image again: the database rejects duplicate scoring. This is **not** robust against crops/edited images or fraudulent claims.

## 4. Model and integration details

This release uses the **original Model V1 Roboflow Workflow**. Its configured workflow ID is:

`natureclean-ai-vnatureclean-ai-1-rfdetr-small-t1-logic`

The model is **RF-DETR Small**, originally trained on 419 image assets with seven model categories. Historic test metrics: **mAP@50 20.8%, precision 34.2%, recall 20.5%, F1 24.5%**. These are weak scores; the model may miss most litter objects. The app allows human corrections and has an `other_litter` fallback for objects outside the trained classes.

The Roboflow API returns predictions under a nested `predictions` output. The app finds that output, renders predicted bounding boxes and confidence percentages, and normalizes photo orientation using EXIF metadata.

The model's **upstream confidence threshold still applies**. This app shows every prediction that the workflow *returns*, which may not include very low-confidence objects filtered in Roboflow. It does not manufacture missing predictions.

## 5. Database, privacy and security

The supplied `supabase/setup.sql` creates:
- `profiles` — account UUID, unique public nickname, creation date.
- `submissions` — user UUID, photo pixel fingerprint, AI count, confirmed counts, server-calculated points, timestamp.
- Policies: each signed-in user may only read their own raw records and profile, and may only edit their own nickname. They cannot directly update scores, delete score records, or set the score on insertion.
- Trigger: on submission, validates category names, count values and a maximum of 100 items; calculates `points = 10 × confirmed_count`.
- Leaderboard RPC: returns only **public nicknames + aggregated points/items/photo counts** (top 50), never emails or photo hashes.

**Security limits:** A signed-in user can still lie about how many objects they collected. Duplicate checks use identical normalized pixels; cropping or recompression can bypass them. This is a classroom prototype, not an audited anti-fraud system. Avoid uploading photos of people, addresses, or sensitive documents. The image itself is uploaded to Roboflow for inference; consult Roboflow's policies before public deployment. Accounts are handled through Supabase Auth. Streamlit keeps the login tokens in its per-browser session memory while connected, so refreshing a session after a full server restart can require login again.

**No automatic migration:** The previous version used a local SQLite leaderboard with nicknames. It does not contain real Supabase user IDs, so those old scores are not automatically transferred to new accounts. Keep your old ZIP if you need the local demo data.

## 6. Ethics / data card (hackathon requirement)

The dataset consists of self-collected Dutch litter photographs and video frames, including near-duplicate frames of the same objects. The data is limited in size, environment, lighting and class balance. Both false negatives (missed litter) and false positives/wrong categories are common; underrepresented types are particularly unreliable. This can distort rewards and community comparisons. A photo also does not prove an item was actually removed, and users can submit misleading counts or manipulated photos. Consequently the interface requires human confirmation and calls all points **self-reported participation points** rather than verified impact. It should not be used for public resource allocation or penalties without more evidence and oversight.

## 7. Troubleshooting

| Symptom | What to check |
|---|---|
| "Supabase is not configured" | `.env` is in the same folder as `app.py`; copy the URL and publishable key. |
| "Database unavailable" | Run `supabase/setup.sql` in your own Supabase project's SQL Editor. |
| Signup works but login doesn't | Confirm the verification email, then sign in. Check Supabase Auth email settings. |
| Cannot create nickname | Name must be 3–24 characters (letters, digits, `-`, `_`), and unique ignoring case. |
| "Roboflow detection failed" | Rotate/check API key, internet, original V1 workflow and workspace; test in Roboflow first. |
| No objects found | The AI has poor recall. Correct the count manually; remember its upstream confidence filtering. |
| Duplicate photo rejected | The same pixel-identical image has already earned points on any account. |
| Different scores in the leaderboard | Monthly ranking uses the Netherlands calendar month; All Time includes earlier months. |
| Old local scores not visible | SQLite V1 data is not linked to Supabase accounts. |

## 8. Files

```text
NatureClean_AI_V2/
├── app.py                     Streamlit UI and Roboflow workflow
├── cloud.py                   Supabase Auth/data helpers
├── core.py                    Prediction parsing and counting
├── style.css                  Dark/mint visual design
├── supabase/setup.sql         Schema, RLS, scoring and leaderboard functions
├── tests/                     Offline tests
├── .env.example               Placeholder configuration (no secrets)
├── requirements.txt
├── START_WINDOWS.bat
└── README.md
```

Run offline tests with `python -m pytest -q` (install `pytest` first if needed). These do not connect to Roboflow or Supabase. A real end-to-end test requires your own accounts and API configuration.
