"""Tests for scheduler."""

from datetime import datetime, timedelta

from linkedin_poster.services.scheduler import Scheduler
from linkedin_poster.models.schedule import ScheduledPost
from linkedin_poster.models.post import PostContent


def _make_post(at: datetime) -> ScheduledPost:
    return ScheduledPost(
        post_content=PostContent(commentary="Test scheduled post"),
        scheduled_at=at,
        template_name="poc_showcase",
    )


class TestScheduler:
    def test_add_and_list(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        post = _make_post(datetime(2026, 4, 1, 10, 0))
        sched.add(post)
        pending = sched.list_pending()
        assert len(pending) == 1
        assert pending[0].id == post.id

    def test_empty_list(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        assert sched.list_pending() == []

    def test_get_due_past(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        past = _make_post(datetime(2020, 1, 1))
        sched.add(past)
        due = sched.get_due()
        assert len(due) == 1

    def test_get_due_future(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        future = _make_post(datetime(2099, 12, 31))
        sched.add(future)
        due = sched.get_due()
        assert len(due) == 0

    def test_mark_published(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        post = _make_post(datetime(2020, 1, 1))
        sched.add(post)
        sched.mark_published(post.id)
        pending = sched.list_pending()
        assert len(pending) == 0

    def test_remove(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        post = _make_post(datetime(2026, 4, 1))
        sched.add(post)
        assert sched.remove(post.id) is True
        assert sched.list_pending() == []

    def test_remove_nonexistent(self, tmp_json_path):
        sched = Scheduler(path=tmp_json_path)
        assert sched.remove("nonexistent") is False
