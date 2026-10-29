"""NatureClean AI — student MVP: Supabase accounts, Roboflow V1, monthly leaderboards.

Start with: python -m streamlit run app.py
"""
from __future__ import annotations

import hashlib
import io
import os
import tempfile
from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

from cloud import (
    SetupError, attach_session, create_client, create_profile, leaderboard,
    my_history, my_recent_submissions, my_stats, profile_for, rename_profile,
    submit_photo, validate_nickname,
)
from core import CLASSES, LABELS, POINTS_PER_ITEM, clean_predictions, confirmed_counts, find_predictions

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
ROBOFLOW_API_KEY = os.getenv("ROBOFLOW_API_KEY", "").strip()
WORKSPACE = os.getenv("ROBOFLOW_WORKSPACE", "arbrs-workspace").strip()
WORKFLOW_ID = os.getenv(
    "ROBOFLOW_WORKFLOW_ID", "natureclean-ai-vnatureclean-ai-1-rfdetr-small-t1-logic"
).strip()
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY", "").strip()

st.set_page_config(page_title="NatureClean AI | Volunteer community", page_icon="🌱", layout="wide", initial_sidebar_state="collapsed")
st.markdown(f"<style>{(ROOT / 'style.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def api_client():
    """Construct an inference client only for an actual scan."""
    from inference_sdk import InferenceHTTPClient, InferenceConfiguration
    return InferenceHTTPClient(
        api_url="https://serverless.roboflow.com", api_key=ROBOFLOW_API_KEY
    ).configure(InferenceConfiguration(api_key_transport="header"))


def analyze(image: Image.Image) -> tuple[list[dict], dict]:
    with tempfile.TemporaryDirectory(prefix="natureclean_") as folder:
        path = Path(folder) / "upload.jpg"
        image.save(path, format="JPEG", quality=92)
        response = api_client().run_workflow(
            workspace_name=WORKSPACE,
            workflow_id=WORKFLOW_ID,
            images={"image": str(path)},
            use_cache=False,
        )
    raw, metadata = find_predictions(response)
    return clean_predictions(raw), metadata


def load_photo(data: bytes) -> tuple[Image.Image, str]:
    if len(data) > 12 * 1024 * 1024:
        raise ValueError("Please choose a photo smaller than 12 MB.")
    try:
        img = Image.open(io.BytesIO(data))
        if img.format not in {"JPEG", "PNG"}:
            raise ValueError("Only JPG and PNG files are supported.")
        img = ImageOps.exif_transpose(img)
        if img.width * img.height > 25_000_000:
            raise ValueError("Please use a photo under 25 megapixels.")
        img = img.convert("RGB")
        fingerprint = hashlib.sha256(
            f"{img.width}x{img.height}:".encode() + img.tobytes()
        ).hexdigest()
        return img, fingerprint
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Could not open photo. Please upload a JPG or PNG.") from exc


def font_for(image: Image.Image):
    size = max(18, min(50, int(image.width * 0.023)))
    for candidate in ("DejaVuSans.ttf", "arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


COLORS = {
    "plastic_bottle": "#7cd8c8", "plastic_bag": "#ccb0f7", "plastic_packaging": "#f2be78",
    "beverage_can": "#8eb8ff", "paper_cardboard": "#d6ad92", "glass_bottle": "#9fdc92",
    "pen": "#f6a5b7", "other_litter": "#f3d58a",
}


def draw_boxes(image: Image.Image, detections: list[dict], metadata: dict) -> Image.Image:
    output = image.copy()
    pen = ImageDraw.Draw(output)
    font = font_for(image)
    source_w = float(metadata.get("width") or image.width)
    source_h = float(metadata.get("height") or image.height)
    if source_w <= 0 or source_h <= 0:
        source_w, source_h = image.size
    sx, sy = image.width / source_w, image.height / source_h
    thickness, pad = max(3, image.width // 320), max(4, image.width // 370)
    for det in detections:
        x, y, w, h = (det[k] for k in ("x", "y", "width", "height"))
        x1 = max(0, min(image.width - 1, int((x - w / 2) * sx)))
        y1 = max(0, min(image.height - 1, int((y - h / 2) * sy)))
        x2 = max(0, min(image.width - 1, int((x + w / 2) * sx)))
        y2 = max(0, min(image.height - 1, int((y + h / 2) * sy)))
        if x2 <= x1 or y2 <= y1:
            continue
        color = COLORS.get(det["class"], "#a9f5c6")
        pen.rectangle([x1, y1, x2, y2], outline=color, width=thickness)
        label = f"{LABELS.get(det['class'], det['class'])} · {det['confidence'] * 100:.1f}%"
        bbox = pen.textbbox((0, 0), label, font=font)
        width, height = bbox[2] - bbox[0] + 2 * pad, bbox[3] - bbox[1] + 2 * pad
        tx, ty = min(x1, max(0, image.width - width)), y1 - height if y1 >= height else min(y2, image.height - height)
        pen.rectangle([tx, ty, tx + width, ty + height], fill="#12231e")
        pen.text((tx + pad, ty + pad - bbox[1]), label, fill=color, font=font)
    return output


def hint(text: str) -> None:
    st.markdown(f'<div class="sectionhint">{escape(text)}</div>', unsafe_allow_html=True)


def display_date(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            ZoneInfo("Europe/Amsterdam")
        ).strftime("%d %b %Y · %H:%M")
    except (ValueError, TypeError):
        return "—"


def clear_personal_state():
    for name in list(st.session_state):
        if name == "main_nav" or name.startswith((
            "scan_", "review_", "edit_", "missed_", "verify_", "photo_",
            "auth_", "signup_", "nickname_",
        )):
            del st.session_state[name]


def go_to(page: str):
    """Streamlit callbacks run before widgets render, avoiding session-state errors."""
    st.session_state["main_nav"] = page


def show_brand():
    st.markdown(
        '<div class="brandbar"><div class="brand"><span class="brandmark">✳</span>'
        'NatureClean AI</div><span class="tinybadge">SDG 15 · Life on Land</span></div>',
        unsafe_allow_html=True,
    )


show_brand()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase is not configured yet. Complete the README setup and add the URL and publishable key to .env.")
    st.code("SUPABASE_URL=https://YOUR_PROJECT.supabase.co\nSUPABASE_PUBLISHABLE_KEY=YOUR_PUBLISHABLE_OR_ANON_KEY", language="dotenv")
    st.stop()

try:
    # A fresh client is used per rerun; do NOT cache a signed-in Supabase client globally.
    sb = create_client(SUPABASE_URL, SUPABASE_KEY)
except (ValueError, SetupError):
    st.error("Supabase configuration is invalid. Check .env.")
    st.stop()

user = None
if st.session_state.get("auth_tokens"):
    try:
        user, updated = attach_session(sb, st.session_state["auth_tokens"])
        if updated:
            st.session_state["auth_tokens"] = updated
    except Exception:
        st.session_state.pop("auth_tokens", None)
        st.warning("Your session has expired. Please sign in again.")

if user is None:
    st.markdown(
        '<section class="hero"><div class="eyebrow">THE HAGUE · COMMUNITY CLEANUPS</div>'
        '<h1>Small cleanups.<br><em>Big impact.</em></h1>'
        '<p>Find litter, review your AI scan, collect participation points, '
        'and see how your community is doing this month.</p>'
        '</section>', unsafe_allow_html=True,
    )
    left, right = st.columns([1.12, 0.88], gap="large")
    with left:
        st.markdown('<div class="featurebox"><div class="sectionhint">HOW NATURECLEAN WORKS</div>'
                    '<h3>Turn a cleanup into visible progress</h3>'
                    '<p>Upload a photo → review the detection → save your points. Your monthly '
                    'score resets automatically, while lifetime points stay on your profile.</p>'
                    '<div class="pillline"><span class="pill">AI-assisted detection</span>'
                    '<span class="pill">Human confirmation</span>'
                    '<span class="pill">Monthly leaderboard</span></div></div>', unsafe_allow_html=True)
    with right:
        st.subheader("Welcome to the community")
        login_tab, register_tab = st.tabs(["Sign in", "Create account"])
        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", key="auth_email")
                password = st.text_input("Password", type="password", key="auth_password")
                submit_login = st.form_submit_button("Sign in", use_container_width=True, type="primary")
            if submit_login:
                try:
                    response = sb.auth.sign_in_with_password({"email": email.strip(), "password": password})
                    if not response.session:
                        raise ValueError("No session returned")
                    clear_personal_state()
                    st.session_state["auth_tokens"] = {
                        "access_token": response.session.access_token,
                        "refresh_token": response.session.refresh_token,
                    }
                    st.rerun()
                except Exception:
                    st.error("Could not sign in. Check your email/password and email verification.")
        with register_tab:
            with st.form("registration_form"):
                name = st.text_input("Public nickname", placeholder="GreenExplorer", max_chars=24, key="nickname_registration")
                signup_email = st.text_input("Email address", key="signup_email")
                signup_password = st.text_input("Password (minimum 8 characters)", type="password", key="signup_password")
                submit_signup = st.form_submit_button("Create account", use_container_width=True, type="primary")
            if submit_signup:
                try:
                    preferred = validate_nickname(name)
                    if len(signup_password) < 8:
                        raise ValueError("Use at least 8 characters for your password.")
                    answer = sb.auth.sign_up({
                        "email": signup_email.strip(), "password": signup_password,
                        "options": {"data": {"nickname": preferred}},
                    })
                    if answer.session:
                        clear_personal_state()
                        st.session_state["auth_tokens"] = {
                            "access_token": answer.session.access_token,
                            "refresh_token": answer.session.refresh_token,
                        }
                        st.rerun()
                    else:
                        st.success("Check your inbox to confirm your email, then come back and sign in.")
                except ValueError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Registration failed. Check your details or try a different email.")
    st.markdown('<div class="footline">Student project · AI for Good · Scores are self-reported, not proof of cleanup.</div>', unsafe_allow_html=True)
    st.stop()

user_id = str(user.id)
try:
    profile = profile_for(sb, user_id)
except Exception:
    st.error("Database unavailable. In Supabase, run supabase/setup.sql in the SQL Editor first.")
    st.stop()

if profile is None:
    hint("Welcome · one last step")
    st.title("Choose your volunteer nickname")
    st.write("Your nickname appears on the leaderboard. Email addresses stay private.")
    preferred = (getattr(user, "user_metadata", None) or {}).get("nickname", "")
    with st.form("first_profile"):
        nickname = st.text_input("Nickname", value=preferred, max_chars=24)
        create = st.form_submit_button("Join NatureClean", type="primary")
    if create:
        try:
            create_profile(sb, user_id, nickname)
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))
        except Exception:
            st.error("Could not save nickname. It may already be taken, or setup.sql has not been run.")
    if st.button("Sign out"):
        try:
            sb.auth.sign_out()
        except Exception:
            pass
        clear_personal_state()
        st.rerun()
    st.stop()

# Shared top navigation; every view is rendered only when selected.
nav, signout = st.columns([5.5, 1], vertical_alignment="center")
with nav:
    page = st.radio(
        "Navigation", ["Dashboard", "Detect Waste", "Leaderboard", "My Profile"],
        horizontal=True, label_visibility="collapsed", key="main_nav",
    )
with signout:
    if st.button("Sign out", use_container_width=True):
        try:
            sb.auth.sign_out()
        except Exception:
            pass
        clear_personal_state()
        st.rerun()


def read_stats() -> dict:
    try:
        return my_stats(sb)
    except Exception:
        st.error("Could not load profile statistics. Check that supabase/setup.sql has been run.")
        st.stop()


def show_leaderboard(period: str, limit: int = 50):
    try:
        rows = leaderboard(sb, period)
    except Exception:
        st.error("Could not load the leaderboard. Check the Supabase SQL setup.")
        return
    if not rows:
        st.info("No submissions for this period yet. Be the first volunteer!")
        return
    for index, row in enumerate(rows[:limit], start=1):
        nickname = escape(row["nickname"])
        note = " · You" if row["nickname"].lower() == profile["nickname"].lower() else ""
        st.markdown(
            f'<div class="rankrow"><div class="ranknumber">{index:02}</div>'
            f'<div class="rankname">{nickname}<span class="youmark">{note}</span></div>'
            f'<div class="rankpoints">{int(row["points"]):,} <span>pts</span></div></div>',
            unsafe_allow_html=True,
        )


if page == "Dashboard":
    st.markdown(
        '<section class="hero compact"><div class="eyebrow">YOUR VOLUNTEER HUB</div>'
        f'<h1>Welcome back, <em>{escape(profile["nickname"])}.</em></h1>'
        '<p>Every verified-by-you count makes your progress visible. '
        'Check your points, contribute a cleanup, and join this month’s community ranking.</p></section>',
        unsafe_allow_html=True,
    )
    info = read_stats()
    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("Points this month", f'{info["month_points"]:,}')
    m2.metric("All-time points", f'{info["total_points"]:,}')
    m3.metric("Items registered", f'{info["total_items"]:,}')
    m4.metric("Photo submissions", f'{info["photos"]:,}')
    st.write("")
    left, right = st.columns([1.05, 0.95], gap="large")
    with left:
        hint("YOUR NEXT CLEANUP")
        st.markdown('<div class="featurebox"><h3>Take a photo. Make it count.</h3>'
                    '<p>Scan collected waste with our Roboflow model. Check the result yourself '
                    'before adding points to your account.</p>'
                    '<div class="pillline"><span class="pill">01 Upload</span>'
                    '<span class="pill">02 Review</span><span class="pill">03 Earn</span></div></div>', unsafe_allow_html=True)
        st.button("Go to Detect Waste", type="primary", use_container_width=True,
                  on_click=go_to, args=("Detect Waste",))
        st.caption("10 participation points per confirmed item. Photo uploads alone do not verify physical cleanup.")
    with right:
        hint("MONTHLY COMMUNITY RANKING")
        show_leaderboard("month", limit=5)
        st.button("See full leaderboard", use_container_width=True,
                  on_click=go_to, args=("Leaderboard",))

elif page == "Detect Waste":
    hint("01 · YOUR CLEANUP PHOTO")
    st.title("Scan your litter")
    st.write("Upload a photo of collected waste. AI detection starts automatically; you can correct the results before earning points.")
    upload = st.file_uploader("Upload a JPG or PNG (max 12 MB)", type=["jpg", "jpeg", "png"])
    with st.expander("Or take a photo with your camera"):
        camera = st.camera_input("Take a cleanup photo")
    upload = upload if upload is not None else camera
    if not upload:
        st.markdown('<div class="infobox"><strong>Tip:</strong> Spread the collected litter so '
                    'each item is visible. Avoid including faces or private information.</div>', unsafe_allow_html=True)
    elif not ROBOFLOW_API_KEY:
        st.error("ROBOFLOW_API_KEY is missing from .env. Add your V1 Roboflow key.")
    else:
        try:
            image, photo_hash = load_photo(upload.getvalue())
        except ValueError as exc:
            st.error(str(exc))
        else:
            scan_key = f"{user_id}:{photo_hash}"
            if st.session_state.get("scan_key") != scan_key:
                st.session_state["scan_key"] = scan_key
                st.session_state.pop("scan_predictions", None)
                st.session_state.pop("scan_metadata", None)
                st.session_state.pop("scan_error", None)
                st.session_state.pop("scan_success", None)
            try:
                existing = (sb.table("submissions").select("points,created_at")
                            .eq("user_id", user_id).eq("photo_hash", photo_hash).limit(1)
                            .execute().data or [])
            except Exception:
                existing = []
            if existing:
                st.success(f'This photo is already in your history. It earned {existing[0]["points"]} points.')
                st.image(image, caption="Previously submitted photo", use_container_width=True)
            else:
                if "scan_predictions" not in st.session_state and "scan_error" not in st.session_state:
                    with st.spinner("Detecting litter with Roboflow..."):
                        try:
                            preds, metadata = analyze(image)
                            st.session_state["scan_predictions"] = preds
                            st.session_state["scan_metadata"] = metadata
                        except Exception:
                            st.session_state["scan_error"] = True
                if "scan_error" in st.session_state:
                    st.error("Roboflow detection failed. Check your model V1 workflow, API key and internet connection.")
                    if st.button("Try detection again"):
                        st.session_state.pop("scan_error", None)
                        st.rerun()
                    st.image(image, use_container_width=True)
                else:
                    preds = st.session_state["scan_predictions"]
                    columns = st.columns([1.35, 0.65], gap="large")
                    with columns[0]:
                        hint("02 · AI DETECTION")
                        st.image(draw_boxes(image, preds, st.session_state.get("scan_metadata", {})), use_container_width=True)
                        st.caption("Boxes and confidence scores are AI guesses, not verified results.")
                    with columns[1]:
                        hint("SCAN SUMMARY")
                        st.metric("AI suggested items", len(preds))
                        if preds:
                            for key, n in Counter(p["class"] for p in preds).most_common():
                                st.markdown(f'**{LABELS.get(key, key)}** · {n}')
                            st.caption(f'Highest confidence: {max(p["confidence"] for p in preds)*100:.1f}%')
                        else:
                            st.warning("The AI found no objects. You can still add missed litter manually.")
                        st.markdown('<div class="infobox">Our V1 model can miss objects or classify them '
                                    'incorrectly. Human review is essential.</div>', unsafe_allow_html=True)
                    st.divider()
                    hint("03 · HUMAN REVIEW")
                    st.subheader("Does the AI count look correct?")
                    decision = st.radio(
                        "Choose how to review", ["Yes, accept its count", "No, I want to correct it"],
                        index=1 if not preds else 0,
                        key=f"verify_{scan_key}", horizontal=True,
                    )
                    edit = decision.startswith("No")
                    with st.form(key=f"review_{scan_key}"):
                        if edit:
                            st.markdown("**1. Keep or change the AI predictions**")
                            st.caption("Untick items that aren't litter. Change the category if it is wrong.")
                            if preds:
                                rows = [
                                    {"Keep": True, "Category": p["class"], "AI confidence (%)": round(p["confidence"] * 100, 1)}
                                    for p in preds
                                ]
                                revised = st.data_editor(
                                    pd.DataFrame(rows), num_rows="fixed", hide_index=True,
                                    key=f"edit_{scan_key}", use_container_width=True,
                                    disabled=["AI confidence (%)"],
                                    column_config={
                                        "Keep": st.column_config.CheckboxColumn("Keep"),
                                        "Category": st.column_config.SelectboxColumn("Category", options=list(CLASSES), required=True),
                                        "AI confidence (%)": st.column_config.NumberColumn("AI confidence (%)", format="%.1f"),
                                    },
                                )
                                checked_rows = revised.to_dict(orient="records")
                            else:
                                checked_rows = []
                            st.markdown("**2. Add items the AI missed**")
                            st.caption("Only add *extra* objects not already kept above.")
                            missed: dict[str, int] = {}
                            c1, c2 = st.columns(2)
                            for index, label in enumerate(CLASSES):
                                with (c1 if index % 2 == 0 else c2):
                                    missed[label] = st.number_input(
                                        LABELS[label], 0, 100, 0, 1,
                                        key=f"missed_{scan_key}_{label}",
                                    )
                        else:
                            checked_rows = [{"Keep": True, "Category": p["class"]} for p in preds]
                            missed = {}
                            st.info(f"You are accepting {len(preds)} AI suggestions. To correct a mistake, choose ‘No, I want to correct it’ above.")
                        st.markdown("**3. Confirm your cleanup**")
                        confirmed = st.checkbox("I checked this submission and confirm it is my cleanup.")
                        st.caption(f"You earn {POINTS_PER_ITEM} points per confirmed item. These are self-reported participation points.")
                        send = st.form_submit_button("Confirm & earn points", type="primary", use_container_width=True)
                    if send:
                        try:
                            if not confirmed:
                                raise ValueError("Please check the confirmation box first.")
                            final_counts = confirmed_counts(checked_rows, missed)
                            saved = submit_photo(sb, user_id, photo_hash, len(preds), final_counts)
                            st.session_state["scan_success"] = int(saved.get("points", sum(final_counts.values()) * POINTS_PER_ITEM))
                            st.success(f'Submission saved · +{st.session_state["scan_success"]} points!')
                            st.rerun()
                        except ValueError as exc:
                            st.error(str(exc))
                        except Exception as exc:
                            if "23505" in str(exc) or "duplicate key" in str(exc).lower():
                                st.warning("This photo is already on the platform. Duplicate points are blocked.")
                            else:
                                st.error("Could not save submission. Check your Supabase SQL setup or connection.")
                    st.caption("AI confidence is not a guarantee. Please review carefully before confirming.")

elif page == "Leaderboard":
    hint("THE NATURECLEAN COMMUNITY")
    st.title("Leaderboard")
    st.write("See who's contributing to cleanup activities. Scores are self-reported participation points.")
    period = st.radio("Ranking period", ["This month", "All time"], horizontal=True)
    selected = "month" if period == "This month" else "all"
    if selected == "month":
        now = datetime.now(ZoneInfo("Europe/Amsterdam"))
        st.caption(f"Showing {now.strftime('%B %Y')} · Europe/Amsterdam. Monthly points start at zero each month; all-time points never reset.")
        st.markdown(
            '<div class="rewardidea"><span class="rewardmark">★</span><div>'
            '<span class="rewardtag">FUTURE REWARD IDEA · NOT ACTIVE</span>'
            '<h3>Monthly cleanup champion</h3>'
            '<p>We hope to offer a gift card to the top eligible volunteer once a local '
            'organizer or sponsor confirms a prize and fair verification rules. '
            'No prize is currently promised or awarded.</p>'
            '</div></div>', unsafe_allow_html=True,
        )
    show_leaderboard(selected)
    st.markdown('<div class="infobox">Leaderboard positions measure volunteer-reported activity, '
                'not independently verified environmental impact. Correcting an AI detection does not '
                'prove that an item was collected.</div>', unsafe_allow_html=True)

elif page == "My Profile":
    hint("YOUR NATURECLEAN ACCOUNT")
    st.title("My Profile")
    st.markdown(f'<div class="profileheadline"><span class="avatar">✳</span>'
                f'<div><h2>{escape(profile["nickname"])}</h2><p>NatureClean volunteer · Personal activity history</p></div></div>', unsafe_allow_html=True)
    info = read_stats()
    m1, m2, m3, m4 = st.columns(4, gap="small")
    m1.metric("This month", f'{info["month_points"]:,} pts')
    m2.metric("Lifetime", f'{info["total_points"]:,} pts')
    m3.metric("Items reported", f'{info["total_items"]:,}')
    m4.metric("Cleanup photos", f'{info["photos"]:,}')
    st.write("")
    left, right = st.columns([1.12, 0.88], gap="large")
    with left:
        hint("MONTHLY PROGRESS")
        try:
            history = my_history(sb)
        except Exception:
            history = []
            st.warning("Monthly history is unavailable. Check the database setup.")
        if history:
            rows = pd.DataFrame(history).sort_values("month")
            st.bar_chart(rows.set_index("month")["points"], color="#9ce8b9")
            st.dataframe(
                rows.iloc[::-1].rename(columns={"month": "Month", "points": "Points", "items": "Items"}),
                hide_index=True, use_container_width=True,
            )
        else:
            st.info("No monthly history yet. Upload your first cleanup photo!")
        hint("RECENT ACTIVITY")
        try:
            recent = my_recent_submissions(sb, user_id)
            for item in recent:
                st.markdown('<div class="activityrow"><span>'
                            f'{escape(display_date(item["created_at"]))} · {int(item["confirmed_count"])} items'
                            f'</span><strong>+{int(item["points"])} pts</strong></div>', unsafe_allow_html=True)
            if not recent:
                st.caption("No photos submitted yet.")
        except Exception:
            st.caption("Recent activity unavailable.")
    with right:
        hint("ACCOUNT DETAILS")
        st.markdown('<div class="featurebox"><h3>Make your impact personal.</h3>'
                    '<p>Your identity is linked to your account. Your nickname is visible '
                    'on the leaderboard; your email is not.</p></div>', unsafe_allow_html=True)
        with st.form("rename_account"):
            new_name = st.text_input("Change nickname", value=profile["nickname"], max_chars=24)
            update = st.form_submit_button("Save nickname", use_container_width=True)
        if update:
            try:
                rename_profile(sb, user_id, new_name)
                st.success("Nickname updated.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Nickname unavailable or already taken.")
        st.caption("Monthly progress uses the Europe/Amsterdam calendar month. Your all-time points remain saved in Supabase.")

st.markdown('<div class="footline">NatureClean AI · Hackathon 7 · SDG 15 — Life on Land · '
            'Roboflow V1 + Streamlit + Supabase · Student prototype</div>', unsafe_allow_html=True)
