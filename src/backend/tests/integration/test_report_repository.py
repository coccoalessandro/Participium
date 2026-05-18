from __future__ import annotations

from datetime import datetime

import pytest
from sqlalchemy import text

from participium.models.enums import ReportStatus, Role
from participium.models.report import ReportFollower, ReportPhoto, ReportStatusHistory, Report
from participium.repositories.report_repository import ReportRepository
from datetime import datetime

pytestmark = pytest.mark.integration


def _set_created_at(db_session, report, timestamp: datetime) -> None:
    db_session.execute(
        text("UPDATE reports SET created_at = :ts WHERE id = :id"),
        {"ts": timestamp.isoformat(sep=" "), "id": report.id},
    )
    db_session.flush()



def test_add_persists_report_and_get_by_id_retrieves_it(db_session, make_category, make_report):
    cat = make_category(name="Roads")
    report = make_report(category_id=cat.id, title="Pothole on Via Roma")
    db_session.commit()

    repo = ReportRepository(db_session)
    result = repo.get_by_id(report.id)

    assert result is not None
    assert result.title == "Pothole on Via Roma"
    assert result.status == ReportStatus.PENDING_APPROVAL


def test_get_by_id_loads_category_relationship(db_session, make_category, make_report):
    cat = make_category(name="Waste")
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    result = repo.get_by_id(report.id)

    assert result.category is not None
    assert result.category.name == "Waste"


def test_get_by_id_loads_reporter_relationship(db_session, make_category, make_user, make_report):
    cat = make_category()
    user = make_user(username="reporter_user")
    report = make_report(category_id=cat.id, reporter_id=user.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    result = repo.get_by_id(report.id)

    assert result.reporter is not None
    assert result.reporter.username == "reporter_user"


def test_get_by_id_returns_none_when_report_does_not_exist(db_session):
    repo = ReportRepository(db_session)

    assert repo.get_by_id(9999) is None




def test_list_reports_returns_all_reports_with_no_filters(
    db_session, make_category, make_report
):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports()

    assert len(results) == 2


def test_list_reports_public_only_excludes_pending_and_rejected(
    db_session, make_category, make_report
):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=cat.id, status=ReportStatus.REJECTED)
    public_report = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(public_only=True)

    ids = {r.id for r in results}
    assert public_report.id in ids
    assert len(results) == 1


def test_list_reports_public_only_includes_assigned_and_in_progress(
    db_session, make_category, make_report
):
    cat = make_category()
    r_assigned = make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    r_in_progress = make_report(category_id=cat.id, status=ReportStatus.IN_PROGRESS)
    make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(public_only=True)

    ids = {r.id for r in results}
    assert r_assigned.id in ids
    assert r_in_progress.id in ids


def test_list_reports_filters_by_category_id(db_session, make_category, make_report):
    cat_a = make_category(name="Roads")
    cat_b = make_category(name="Waste")
    r_roads = make_report(category_id=cat_a.id, status=ReportStatus.RESOLVED)
    make_report(category_id=cat_b.id, status=ReportStatus.RESOLVED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(category_id=cat_a.id)

    assert len(results) == 1
    assert results[0].id == r_roads.id


def test_list_reports_filters_by_status(db_session, make_category, make_report):
    cat = make_category()
    r_resolved = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(status=ReportStatus.RESOLVED)

    assert len(results) == 1
    assert results[0].id == r_resolved.id


def test_list_reports_sorted_asc_returns_oldest_first(
    db_session, make_category, make_report
):
    cat = make_category()
    r_old = make_report(category_id=cat.id)
    r_new = make_report(category_id=cat.id)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(sort="asc")

    assert results[0].id == r_old.id
    assert results[-1].id == r_new.id


def test_list_reports_sorted_desc_returns_newest_first(
    db_session, make_category, make_report
):
    cat = make_category()
    r_old = make_report(category_id=cat.id)
    r_new = make_report(category_id=cat.id)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(sort="desc")

    assert results[0].id == r_new.id
    assert results[-1].id == r_old.id



def test_list_user_reports_returns_only_reports_for_given_user(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user_a = make_user(username="user_a")
    user_b = make_user(username="user_b")
    r1 = make_report(category_id=cat.id, reporter_id=user_a.id)
    r2 = make_report(category_id=cat.id, reporter_id=user_a.id)
    make_report(category_id=cat.id, reporter_id=user_b.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_user_reports(user_a.id)

    ids = {r.id for r in results}
    assert r1.id in ids
    assert r2.id in ids
    assert len(results) == 2


def test_list_user_reports_returns_empty_when_user_has_no_reports(
    db_session, make_user
):
    user = make_user()
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_user_reports(user.id)

    assert results == []



def test_list_pending_returns_only_pending_reports(
    db_session, make_category, make_report
):
    cat = make_category()
    pending = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=cat.id, status=ReportStatus.ASSIGNED)
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_pending()

    assert len(results) == 1
    assert results[0].id == pending.id


def test_list_pending_filters_by_category_id(db_session, make_category, make_report):
    cat_a = make_category(name="Roads")
    cat_b = make_category(name="Waste")
    p_roads = make_report(category_id=cat_a.id, status=ReportStatus.PENDING_APPROVAL)
    make_report(category_id=cat_b.id, status=ReportStatus.PENDING_APPROVAL)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_pending(category_id=cat_a.id)

    assert len(results) == 1
    assert results[0].id == p_roads.id


def test_list_pending_returns_empty_when_no_pending_reports(
    db_session, make_category, make_report
):
    cat = make_category()
    make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_pending()

    assert results == []



def test_list_operator_reports_for_operator_returns_only_category_reports(
    db_session, make_category, make_report
):
    cat_a = make_category(name="Roads")
    cat_b = make_category(name="Waste")
    r_roads = make_report(category_id=cat_a.id, status=ReportStatus.ASSIGNED)
    make_report(category_id=cat_b.id, status=ReportStatus.ASSIGNED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_operator_reports(Role.OPERATOR, category_id=cat_a.id)

    assert len(results) == 1
    assert results[0].id == r_roads.id


def test_list_operator_reports_for_admin_returns_all_non_pending(
    db_session, make_category, make_report
):
    cat_a = make_category(name="Roads")
    cat_b = make_category(name="Waste")
    r1 = make_report(category_id=cat_a.id, status=ReportStatus.ASSIGNED)
    r2 = make_report(category_id=cat_b.id, status=ReportStatus.IN_PROGRESS)
    make_report(category_id=cat_a.id, status=ReportStatus.PENDING_APPROVAL)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_operator_reports(Role.ADMIN)

    ids = {r.id for r in results}
    assert r1.id in ids
    assert r2.id in ids
    assert len(results) == 2



def test_add_follower_and_get_follower_returns_follower(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    repo.add_follower(ReportFollower(report_id=report.id, user_id=user.id))
    db_session.commit()

    result = repo.get_follower(report.id, user.id)

    assert result is not None
    assert result.report_id == report.id
    assert result.user_id == user.id


def test_get_follower_returns_none_when_user_is_not_following(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    result = repo.get_follower(report.id, user.id)

    assert result is None


def test_remove_follower_deletes_follower_record(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    follower = ReportFollower(report_id=report.id, user_id=user.id)
    repo.add_follower(follower)
    db_session.commit()

    repo.remove_follower(follower)
    db_session.commit()

    assert repo.get_follower(report.id, user.id) is None


def test_list_followers_returns_all_followers_for_report(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user_a = make_user(username="follower_a")
    user_b = make_user(username="follower_b")
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    repo.add_follower(ReportFollower(report_id=report.id, user_id=user_a.id))
    repo.add_follower(ReportFollower(report_id=report.id, user_id=user_b.id))
    db_session.commit()

    results = repo.list_followers(report.id)

    user_ids = {f.user_id for f in results}
    assert user_a.id in user_ids
    assert user_b.id in user_ids



def test_add_photo_associates_photo_with_report(
    db_session, make_category, make_report
):
    cat = make_category()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    repo.add_photo(
        ReportPhoto(
            report_id=report.id,
            file_path="/media/buca.jpg",
            original_filename="buca.jpg",
            content_type="image/jpeg",
        )
    )
    db_session.commit()

    result = repo.get_by_id(report.id)
    assert len(result.photos) == 1
    assert result.photos[0].file_path == "/media/buca.jpg"


def test_add_status_entry_associates_history_with_report(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id, reporter_id=user.id)
    db_session.commit()

    repo = ReportRepository(db_session)
    repo.add_status_entry(
        ReportStatusHistory(
            report_id=report.id,
            previous_status=None,
            new_status=ReportStatus.PENDING_APPROVAL,
            note="Report submitted.",
            changed_by_id=user.id,
        )
    )
    db_session.commit()

    result = repo.get_by_id(report.id)
    assert len(result.status_history) == 1
    assert result.status_history[0].new_status == ReportStatus.PENDING_APPROVAL
    assert result.status_history[0].note == "Report submitted."


def test_add_persists_report_via_repository(db_session, make_category, make_user):
    cat = make_category()
    user = make_user()
    db_session.commit()

    repo = ReportRepository(db_session)
    report = Report(
        title="Direct add test",
        description="Added via repo.add()",
        latitude=45.0,
        longitude=9.0,
        is_anonymous=False,
        status=ReportStatus.PENDING_APPROVAL,
        reporter_id=user.id,
        category_id=cat.id,
    )
    returned = repo.add(report)
    db_session.commit()

    assert returned is report
    assert report.id is not None



def test_list_reports_filters_by_date_from(db_session, make_category, make_report):

    cat = make_category()
    r_old = make_report(category_id=cat.id)
    r_new = make_report(category_id=cat.id)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(date_from=datetime(2026, 3, 1))

    ids = {r.id for r in results}
    assert r_new.id in ids
    assert r_old.id not in ids


def test_list_reports_filters_by_date_to(db_session, make_category, make_report):

    cat = make_category()
    r_old = make_report(category_id=cat.id)
    r_new = make_report(category_id=cat.id)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_reports(date_to=datetime(2026, 3, 1))

    ids = {r.id for r in results}
    assert r_old.id in ids
    assert r_new.id not in ids


def test_list_pending_filters_by_date_from(db_session, make_category, make_report):

    cat = make_category()
    r_old = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    r_new = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_pending(date_from=datetime(2026, 3, 1))

    ids = {r.id for r in results}
    assert r_new.id in ids
    assert r_old.id not in ids


def test_list_pending_filters_by_date_to(db_session, make_category, make_report):

    cat = make_category()
    r_old = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    r_new = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    _set_created_at(db_session, r_old, datetime(2026, 1, 1, 10, 0, 0))
    _set_created_at(db_session, r_new, datetime(2026, 6, 1, 10, 0, 0))
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_pending(date_to=datetime(2026, 3, 1))

    ids = {r.id for r in results}
    assert r_old.id in ids
    assert r_new.id not in ids



def test_list_all_returns_all_reports_regardless_of_status(
    db_session, make_category, make_report
):
    cat = make_category()
    r1 = make_report(category_id=cat.id, status=ReportStatus.PENDING_APPROVAL)
    r2 = make_report(category_id=cat.id, status=ReportStatus.RESOLVED)
    r3 = make_report(category_id=cat.id, status=ReportStatus.REJECTED)
    db_session.commit()

    repo = ReportRepository(db_session)
    results = repo.list_all()

    ids = {r.id for r in results}
    assert r1.id in ids
    assert r2.id in ids
    assert r3.id in ids
    assert len(results) == 3