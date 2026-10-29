import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from cloud import validate_nickname, clean_counts, submit_photo, score_preview, leaderboard


def test_nickname_rule():
    assert validate_nickname(" GreenExplorer ") == "GreenExplorer"
    for nickname in ("a", "Jane Doe", " x'--", "a" * 25):
        with pytest.raises(ValueError):
            validate_nickname(nickname)


def test_counts_and_preview():
    assert clean_counts({"plastic_bag": 2, "plastic_bottle": 0}) == {"plastic_bag": 2}
    assert score_preview({"plastic_bag": 2}) == 20
    for value in (-1, 101, True, 2.5):
        with pytest.raises(ValueError):
            clean_counts({"plastic_bag": value})
    with pytest.raises(ValueError):
        clean_counts({"bad_label": 1})
    with pytest.raises(ValueError):
        clean_counts({"plastic_bag": 0})
    with pytest.raises(ValueError):
        clean_counts({"plastic_bag": 70, "plastic_bottle": 40})


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeInsert:
    def __init__(self):
        self.payload = None
    def insert(self, data):
        self.payload = data
        return self
    def execute(self):
        return FakeResponse([dict(self.payload, points=20, confirmed_count=2)])


class FakeClient:
    def __init__(self):
        self.query = FakeInsert()
        self.called_table = None
    def table(self, name):
        self.called_table = name
        return self.query


def test_scores_not_sent_by_client():
    client = FakeClient()
    data = submit_photo(client, "123", "a" * 64, 1, {"plastic_bag": 2})
    assert data["points"] == 20
    assert client.called_table == "submissions"
    assert "points" not in client.query.payload
    assert "confirmed_count" not in client.query.payload
    assert client.query.payload["counts"] == {"plastic_bag": 2}


def test_invalid_hash_blocked_without_database():
    with pytest.raises(ValueError):
        submit_photo(FakeClient(), "123", "abc", 1, {"plastic_bag": 1})


def test_invalid_leaderboard_period_blocked():
    with pytest.raises(ValueError):
        leaderboard(FakeClient(), "yesterday")
