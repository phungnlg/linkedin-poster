"""Tests for history store."""

from datetime import datetime

from linkedin_poster.services.history import HistoryStore
from linkedin_poster.models.post import PostRecord


class TestHistoryStore:
    def test_empty_list(self, tmp_json_path):
        store = HistoryStore(path=tmp_json_path)
        assert store.list_records() == []

    def test_add_and_list(self, tmp_json_path):
        store = HistoryStore(path=tmp_json_path)
        record = PostRecord(
            post_urn="urn:li:share:123",
            poc_hash="hash1",
            text_preview="Test post",
        )
        store.add(record)
        records = store.list_records()
        assert len(records) == 1
        assert records[0].post_urn == "urn:li:share:123"

    def test_duplicate_detection(self, tmp_json_path):
        store = HistoryStore(path=tmp_json_path)
        record = PostRecord(
            post_urn="urn:li:share:456",
            poc_hash="unique_hash",
            text_preview="Test",
        )
        store.add(record)
        assert store.is_duplicate("unique_hash") is True
        assert store.is_duplicate("other_hash") is False

    def test_compute_hash(self, sample_poc_config):
        h = HistoryStore.compute_hash(sample_poc_config)
        assert len(h) == 16
        # Same file should produce same hash
        assert h == HistoryStore.compute_hash(sample_poc_config)

    def test_compute_hash_missing_file(self):
        h = HistoryStore.compute_hash("/nonexistent/file.json")
        assert len(h) == 16

    def test_multiple_records(self, tmp_json_path):
        store = HistoryStore(path=tmp_json_path)
        for i in range(3):
            record = PostRecord(
                post_urn=f"urn:li:share:{i}",
                poc_hash=f"hash_{i}",
                text_preview=f"Post {i}",
            )
            store.add(record)
        assert len(store.list_records()) == 3
