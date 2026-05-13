from __future__ import annotations

import pytest

from participium.repositories.message_repository import MessageRepository
from participium.models.message import Message
from sqlalchemy import text

pytestmark = pytest.mark.integration



def test_add_persists_message_via_repository(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    sender = make_user(username="sender")
    recipient = make_user(username="recipient")
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = MessageRepository(db_session)
    msg = Message(
        report_id=report.id,
        sender_id=sender.id,
        recipient_id=recipient.id,
        body="Hello from integration test",
    )
    repo.add(msg)
    db_session.commit()

    assert msg.id is not None


def test_add_persists_message_with_null_sender(
    db_session, make_category, make_user, make_report
):
    cat = make_category()
    recipient = make_user()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = MessageRepository(db_session)
    msg = Message(
        report_id=report.id,
        sender_id=None,
        recipient_id=recipient.id,
        body="System message",
    )
    repo.add(msg)
    db_session.commit()

    assert msg.id is not None
    assert msg.sender_id is None



def test_list_for_report_returns_messages_for_given_report(
    db_session, make_category, make_user, make_report, make_message
):
    cat = make_category()
    sender = make_user(username="sender")
    recipient = make_user(username="recipient")
    report = make_report(category_id=cat.id)
    m1 = make_message(report_id=report.id, sender_id=sender.id, recipient_id=recipient.id, body="First")
    m2 = make_message(report_id=report.id, sender_id=recipient.id, recipient_id=sender.id, body="Second")
    db_session.commit()

    repo = MessageRepository(db_session)
    results = repo.list_for_report(report.id)

    ids = {m.id for m in results}
    assert m1.id in ids
    assert m2.id in ids
    assert len(results) == 2


def test_list_for_report_excludes_messages_from_other_reports(
    db_session, make_category, make_user, make_report, make_message
):
    cat = make_category()
    user = make_user()
    report_a = make_report(category_id=cat.id)
    report_b = make_report(category_id=cat.id)
    m_a = make_message(report_id=report_a.id, sender_id=user.id, body="For A")
    make_message(report_id=report_b.id, sender_id=user.id, body="For B")
    db_session.commit()

    repo = MessageRepository(db_session)
    results = repo.list_for_report(report_a.id)

    assert len(results) == 1
    assert results[0].id == m_a.id


def test_list_for_report_returns_messages_in_ascending_order(
    db_session, make_category, make_user, make_report, make_message
):

    cat = make_category()
    sender = make_user(username="sender")
    recipient = make_user(username="recipient")
    report = make_report(category_id=cat.id)
    m_first = make_message(report_id=report.id, sender_id=sender.id, body="First")
    m_second = make_message(report_id=report.id, sender_id=recipient.id, body="Second")

    db_session.execute(
        text("UPDATE messages SET created_at = :ts WHERE id = :id"),
        {"ts": "2026-01-01 08:00:00", "id": m_first.id},
    )
    db_session.execute(
        text("UPDATE messages SET created_at = :ts WHERE id = :id"),
        {"ts": "2026-06-01 08:00:00", "id": m_second.id},
    )
    db_session.commit()

    repo = MessageRepository(db_session)
    results = repo.list_for_report(report.id)

    assert results[0].id == m_first.id
    assert results[-1].id == m_second.id


def test_list_for_report_returns_empty_when_no_messages(
    db_session, make_category, make_report
):
    cat = make_category()
    report = make_report(category_id=cat.id)
    db_session.commit()

    repo = MessageRepository(db_session)
    results = repo.list_for_report(report.id)

    assert results == []