"""Supabase Auth and persistence. No service-role key; per-user clients only.

This module has no import-time network calls, making it suitable for offline tests.
"""
from __future__ import annotations

import re
from typing import Any

from core import CLASSES, POINTS_PER_ITEM


class SetupError(RuntimeError):
    """Missing database setup or connection details."""


def validate_nickname(value: str) -> str:
    name = str(value).strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]{3,24}", name):
        raise ValueError("Use 3–24 characters: letters, numbers, - or _ (no spaces).")
    return name


def clean_counts(counts: dict[str, Any]) -> dict[str, int]:
    """Mirror the DB trigger's item constraints for fast user feedback."""
    result: dict[str, int] = {}
    for label, raw in counts.items():
        if label not in CLASSES or isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError("Invalid waste category or count.")
        if raw < 0 or raw > 100:
            raise ValueError("Counts must be between 0 and 100.")
        if raw:
            result[label] = raw
    if not 1 <= sum(result.values()) <= 100:
        raise ValueError("Confirm between 1 and 100 items per photo.")
    return result


def create_client(url: str, publishable_key: str):
    """Fresh client per Streamlit browser session/rerun; never cache across users."""
    from supabase import create_client as new_client

    if not url.startswith("https://") or not publishable_key:
        raise SetupError("Set SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY in your .env file.")
    return new_client(url, publishable_key)


def attach_session(client, session_tokens: dict[str, str] | None):
    """Restores/refreshes JWTs. Returns authenticated user and rotated tokens."""
    if not session_tokens:
        return None, None
    response = client.auth.set_session(
        session_tokens["access_token"], session_tokens["refresh_token"]
    )
    if response.session is None or response.user is None:
        return None, None
    return response.user, {
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
    }


def profile_for(client, user_id: str) -> dict | None:
    response = client.table("profiles").select("id,nickname,created_at").eq("id", user_id).limit(1).execute()
    return response.data[0] if response.data else None


def create_profile(client, user_id: str, nickname: str) -> dict:
    name = validate_nickname(nickname)
    result = client.table("profiles").insert({"id": user_id, "nickname": name}).execute()
    return result.data[0]


def rename_profile(client, user_id: str, nickname: str) -> dict:
    name = validate_nickname(nickname)
    result = client.table("profiles").update({"nickname": name}).eq("id", user_id).execute()
    return result.data[0]


def submit_photo(client, user_id: str, photo_hash: str, ai_count: int, counts: dict) -> dict:
    """Database trigger calculates immutable points, even if a caller tampers with inputs."""
    if not re.fullmatch(r"[0-9a-f]{64}", photo_hash):
        raise ValueError("Invalid photo fingerprint.")
    accepted = clean_counts(counts)
    result = client.table("submissions").insert({
        "user_id": user_id, "photo_hash": photo_hash,
        "ai_count": int(ai_count), "counts": accepted,
    }).execute()
    if not result.data:
        raise RuntimeError("Submission was not saved.")
    return result.data[0]


def my_stats(client) -> dict[str, int]:
    result = client.rpc("natureclean_my_stats").execute()
    response = result.data or {}
    return {name: int(response.get(name, 0)) for name in (
        "total_points", "total_items", "month_points", "month_items", "photos"
    )}


def my_history(client) -> list[dict]:
    return client.rpc("natureclean_my_history").execute().data or []


def my_recent_submissions(client, user_id: str, count: int = 8) -> list[dict]:
    return (client.table("submissions")
            .select("created_at,points,confirmed_count,ai_count,counts")
            .eq("user_id", user_id).order("created_at", desc=True)
            .limit(count).execute().data or [])


def leaderboard(client, period: str = "month") -> list[dict]:
    if period not in ("month", "all"):
        raise ValueError("Invalid leaderboard period")
    return client.rpc("natureclean_leaderboard", {"p_period": period}).execute().data or []


def score_preview(counts: dict) -> int:
    return sum(clean_counts(counts).values()) * POINTS_PER_ITEM
