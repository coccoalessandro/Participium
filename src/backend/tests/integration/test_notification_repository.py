from __future__ import annotations

import pytest

from participium.models.enums import NotificationType
from participium.repositories.notification_repository import NotificationRepository

pytestmark = pytest.mark.integration


def test_add_persists_notification_and_get_by_id_retrieves_it(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = NotificationRepository(db_session)
    from participium.models.notification import Notification

    notif = Notification(
    user_id=user.id,
    report_id=report.id,
    type=NotificationType.MESSAGE,
    title="New message",       
    body="You have a message", 
    is_read=False,
)
    repo.add(notif)
    db_session.commit()

    result = repo.get_by_id(notif.id)

    assert result is not None
    assert result.user_id == user.id
    assert result.report_id == report.id
    assert result.type == NotificationType.MESSAGE
    assert result.is_read is False


def test_get_by_id_returns_none_when_notification_does_not_exist(db_session):
    repo = NotificationRepository(db_session)

    assert repo.get_by_id(9999) is None



def test_list_for_user_returns_all_notifications_for_user(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user_a = make_user(username="user_a")
    user_b = make_user(username="user_b")
    report = make_report(category_id=cat.id)
    n1 = make_notification(user_id=user_a.id, report_id=report.id)
    n2 = make_notification(user_id=user_a.id, report_id=report.id)
    make_notification(user_id=user_b.id, report_id=report.id)
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_for_user(user_a.id)

    ids = {n.id for n in results}
    assert n1.id in ids
    assert n2.id in ids
    assert len(results) == 2


def test_list_for_user_returns_empty_when_user_has_no_notifications(
    db_session, make_user
):
    user = make_user()
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_for_user(user.id)

    assert results == []



def test_list_unread_message_notifications_returns_unread_message_notifications(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    unread = make_notification(
        user_id=user.id, report_id=report.id,
        notification_type=NotificationType.MESSAGE, is_read=False,
    )
    make_notification(
        user_id=user.id, report_id=report.id,
        notification_type=NotificationType.MESSAGE, is_read=True,
    )
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_unread_message_notifications(user_id=user.id)

    assert len(results) == 1
    assert results[0].id == unread.id


def test_list_unread_message_notifications_filters_by_report_id(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report_a = make_report(category_id=cat.id)
    report_b = make_report(category_id=cat.id)
    n_a = make_notification(
        user_id=user.id, report_id=report_a.id,
        notification_type=NotificationType.MESSAGE, is_read=False,
    )
    make_notification(
        user_id=user.id, report_id=report_b.id,
        notification_type=NotificationType.MESSAGE, is_read=False,
    )
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_unread_message_notifications(user_id=user.id, report_id=report_a.id)

    assert len(results) == 1
    assert results[0].id == n_a.id


def test_list_unread_message_notifications_excludes_non_message_types(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    make_notification(
        user_id=user.id, report_id=report.id,
        notification_type=NotificationType.STATUS_CHANGE, is_read=False,
    )
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_unread_message_notifications(user_id=user.id)

    assert results == []


def test_list_unread_message_notifications_returns_empty_when_all_read(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    make_notification(
        user_id=user.id, report_id=report.id,
        notification_type=NotificationType.MESSAGE, is_read=True,
    )
    db_session.commit()

    repo = NotificationRepository(db_session)
    results = repo.list_unread_message_notifications(user_id=user.id)

    assert results == []



def test_delete_for_user_removes_all_notifications_for_user(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user = make_user()
    report = make_report(category_id=cat.id)
    make_notification(user_id=user.id, report_id=report.id)
    make_notification(user_id=user.id, report_id=report.id)
    db_session.commit()

    repo = NotificationRepository(db_session)
    repo.delete_for_user(user.id)
    db_session.commit()

    assert repo.list_for_user(user.id) == []


def test_delete_for_user_does_not_affect_other_users_notifications(
    db_session, make_category, make_user, make_report, make_notification
):
    cat = make_category()
    user_a = make_user(username="user_a")
    user_b = make_user(username="user_b")
    report = make_report(category_id=cat.id)
    make_notification(user_id=user_a.id, report_id=report.id)
    n_b = make_notification(user_id=user_b.id, report_id=report.id)
    db_session.commit()

    repo = NotificationRepository(db_session)
    repo.delete_for_user(user_a.id)
    db_session.commit()

    remaining = repo.list_for_user(user_b.id)
    assert len(remaining) == 1
    assert remaining[0].id == n_b.id