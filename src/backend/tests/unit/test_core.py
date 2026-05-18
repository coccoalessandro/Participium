from __future__ import annotations

from datetime import datetime
from unittest.mock import Mock

import pytest
from flask import Flask, g, Blueprint

from participium.core.auth import current_user, login_required, login_user, logout_user, roles_required
from participium.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    NotFoundError,
    ValidationError,
)
from participium.core.security import generate_token, hash_password, verify_password
from participium.core.serialization import (
    _media_url,
    _serialize_party,
    _serialize_reporter,
    _viewer_follows_report,
    serialize_category,
    serialize_report_detail,
    serialize_report_summary,
    serialize_user,
    serialize_message,
    serialize_notification
)
from participium.core.status_flow import ensure_transition_allowed
from participium.core.utils import build_csv, parse_date, utcnow
from participium.models.enums import ReportStatus, Role, NotificationType

pytestmark = pytest.mark.unit

_TS = datetime(2026, 5, 15, 10, 0, 0)

P = ReportStatus.PENDING_APPROVAL
A = ReportStatus.ASSIGNED
I = ReportStatus.IN_PROGRESS
S = ReportStatus.SUSPENDED
R = ReportStatus.REJECTED
V = ReportStatus.RESOLVED


def _user(*, user_id: int = 1, role: Role = Role.CITIZEN, category_id: int | None = None) -> Mock:
    u = Mock()
    u.id = user_id
    u.username = "test_user"
    u.first_name = "Test"
    u.last_name = "User"
    u.email = "test@example.com"
    u.role = role
    u.category_id = category_id
    u.is_active = True
    u.is_email_verified = True
    u.email_notifications_enabled = True
    u.profile_picture_path = None
    u.category = None
    u.created_at = _TS
    return u


def _report(
    *,
    status: ReportStatus = P,
    is_anonymous: bool = False,
    reporter=None,
    reporter_id: int | None = 1,
    category_id: int = 5,
    followers: list | None = None,
    status_history: list | None = None,
    messages: list | None = None,
) -> Mock:
    r = Mock()
    r.id = 1
    r.title = "Test"
    r.description = "Desc"
    r.status = status
    r.is_anonymous = is_anonymous
    r.reporter = reporter
    r.reporter_id = reporter_id
    r.category_id = category_id
    r.category = Mock()
    r.category.id = 1
    r.category.name = "Roads"
    r.category.is_active = True
    r.category.created_at = _TS
    r.latitude = 45.0
    r.longitude = 9.0
    r.rejection_reason = None
    r.photos = []
    r.followers = followers or []
    r.status_history = status_history or []
    r.messages = messages or []
    r.created_at = _TS
    r.updated_at = _TS
    return r


def _follower(*, user_id: int) -> Mock:
    f = Mock()
    f.user_id = user_id
    return f


@pytest.fixture
def flask_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["TESTING"] = True
    return app


@pytest.mark.parametrize("exc_class, expected_status", [
    (ValidationError,     400),
    (AuthenticationError, 401),
    (AuthorizationError,  403),
    (NotFoundError,       404),
])
def test_exception_subclass_has_correct_status_code_and_is_domain_error(exc_class, expected_status):
    err = exc_class("msg")

    assert err.status_code == expected_status
    assert isinstance(err, DomainError)
    assert str(err) == "msg"


def test_domain_error_accepts_custom_status_code():
    assert DomainError("x", status_code=422).status_code == 422



def test_hash_and_verify_password_roundtrip():
    hashed = hash_password("secret")

    assert verify_password("secret", hashed) is True
    assert verify_password("wrong",  hashed) is False


def test_hash_password_is_salted():
    assert hash_password("secret") != hash_password("secret")


def test_generate_token_produces_unique_non_empty_strings():
    tokens = {generate_token() for _ in range(10)}

    assert len(tokens) == 10
    assert all(len(t) > 0 for t in tokens)



def test_utcnow_returns_current_datetime():
    before = datetime.utcnow()
    result = utcnow()
    after  = datetime.utcnow()

    assert before <= result <= after


@pytest.mark.parametrize("value, expected", [
    (None,                  None),
    ("",                    None),
    ("2026-05-15T10:30:00", datetime(2026, 5, 15, 10, 30, 0)),
])
def test_parse_date_valid_inputs(value, expected):
    assert parse_date(value) == expected


def test_parse_date_raises_for_invalid_format():
    with pytest.raises(ValueError):
        parse_date("not-a-date")


def test_build_csv_contains_header_and_rows():
    rows = [{"id": 1, "name": "Alpha"}, {"id": 2, "name": "Beta"}]
    result = build_csv(rows, fieldnames=["id", "name"])
    lines = result.splitlines()

    assert "id" in lines[0] and "name" in lines[0]
    assert len(lines) == 3


def test_self_transition_is_always_allowed():
    for status in ReportStatus:
        assert ensure_transition_allowed(status, status) is True


@pytest.mark.parametrize("current, nxt", [
    (P, A), (P, R),
    (A, I), (A, S), (A, V),
    (I, S), (I, V),
    (S, I), (S, V),
])
def test_valid_transition_returns_true(current, nxt):
    assert ensure_transition_allowed(current, nxt) is True


@pytest.mark.parametrize("current, nxt", [
    (P, I), (P, V),         
    (R, A),           
    (V, I),                
    (I, P),                  
])
def test_invalid_transition_raises_validation_error(current, nxt):
    with pytest.raises(ValidationError):
        ensure_transition_allowed(current, nxt)



def test_media_url_none_input_returns_none():
    assert _media_url(None) is None


def test_media_url_builds_correct_path():
    assert _media_url("uuid.jpg") == "/static/uploads/uuid.jpg"


def test_serialize_category_returns_correct_fields():
    cat = Mock()
    cat.id, cat.name, cat.is_active, cat.created_at = 1, "Roads", True, _TS
    result = serialize_category(cat)

    assert result == {"id": 1, "name": "Roads", "is_active": True, "created_at": _TS.isoformat()}


def test_serialize_user_includes_key_fields():
    user = _user(user_id=5, role=Role.OPERATOR)
    result = serialize_user(user)

    assert result["id"] == 5
    assert result["role"] == "operator"
    assert result["profile_picture_url"] is None


def test_serialize_party_returns_deleted_user_for_none():
    assert _serialize_party(None) == {"id": None, "display_name": "Deleted User", "role": None}


def test_serialize_party_returns_full_name_and_role():
    result = _serialize_party(_user(user_id=3, role=Role.ADMIN))

    assert result["id"] == 3
    assert result["display_name"] == "Test User"
    assert result["role"] == "admin"


@pytest.mark.parametrize("reporter,is_anon,viewer_role,viewer_cat,viewer_id,expected_id", [
 
    (None,  False, None,           None, None, None),
  
    ("self", False, None,          None, None, "reporter"),
   
    ("self", True,  None,          None, None, None),

    ("self", True,  Role.ADMIN,    None, 99,   "reporter"),
   
    ("self", True,  Role.OPERATOR, 5,    99,   "reporter"),
 
    ("self", True,  Role.CITIZEN,  None, 1,    "reporter"),

    ("self", True,  Role.CITIZEN,  None, 99,   None),
])
def test_serialize_reporter_branches(
    reporter, is_anon, viewer_role, viewer_cat, viewer_id, expected_id
):
    reporter_mock = _user(user_id=1) if reporter == "self" else None
    report = _report(
        reporter=reporter_mock,
        reporter_id=1 if reporter_mock else None,
        is_anonymous=is_anon,
        category_id=5,
    )
    viewer = _user(user_id=viewer_id, role=viewer_role, category_id=viewer_cat) if viewer_role else None

    result = _serialize_reporter(report, viewer)

    if expected_id == "reporter":
        assert result.get("id") == 1
    else:
        assert result.get("id") is None


def test_viewer_follows_report_true_and_false():
    viewer = _user(user_id=7)

    report_with = _report(followers=[_follower(user_id=7)])
    report_without = _report(followers=[_follower(user_id=99)])

    assert _viewer_follows_report(report_with, viewer) is True
    assert _viewer_follows_report(report_without, viewer) is False
    assert _viewer_follows_report(report_without, None) is False


def test_serialize_report_summary_key_fields():
    reporter = _user(user_id=1)
    report = _report(status=V, reporter=reporter, followers=[_follower(user_id=5)])
    result = serialize_report_summary(report)

    assert result["status"] == "Resolved"
    assert result["is_public"] is True
    assert result["followers_count"] == 1


def test_serialize_report_detail_with_and_without_messages():
    history = Mock()
    history.id = 1
    history.previous_status = None
    history.new_status = P
    history.note = "Submitted"
    history.changed_by = None
    history.created_at = _TS

    report = _report(status_history=[history])
    without = serialize_report_detail(report, include_messages=False)
    with_ = serialize_report_detail(report, include_messages=True)

    assert without["can_access_messages"] is False
    assert "messages" not in without
    assert with_["can_access_messages"] is True
    assert "messages" in with_



def test_login_logout_user_manages_session(flask_app):
    with flask_app.test_request_context("/"):
        user = Mock()
        user.id = 42
        login_user(user)

        from flask import session
        assert session["user_id"] == 42

        logout_user()
        assert "user_id" not in session


def test_current_user_returns_none_when_not_set(flask_app):
    with flask_app.test_request_context("/"):
        assert current_user() is None


def test_login_required_raises_on_api_path_when_no_user(flask_app):
    with flask_app.test_request_context("/api/reports"):
        g.current_user = None

        @login_required
        def view():
            return "ok"

        with pytest.raises(AuthenticationError):
            view()


def test_login_required_calls_view_when_user_present(flask_app):
    with flask_app.test_request_context("/api/reports"):
        g.current_user = Mock()

        @login_required
        def view():
            return "ok"

        assert view() == "ok"


@pytest.mark.parametrize("role, allowed_roles, should_pass", [
    (Role.ADMIN,    [Role.ADMIN],             True),
    (Role.OPERATOR, [Role.ADMIN, Role.OPERATOR], True),
    (Role.CITIZEN,  [Role.ADMIN],             False),
])
def test_roles_required(flask_app, role, allowed_roles, should_pass):
    with flask_app.test_request_context("/api/test"):
        user = Mock()
        user.role = role
        g.current_user = user

        @roles_required(*allowed_roles)
        def view():
            return "ok"

        if should_pass:
            assert view() == "ok"
        else:
            with pytest.raises(AuthorizationError):
                view()


def test_roles_required_raises_authentication_error_when_no_user(flask_app):
    with flask_app.test_request_context("/api/test"):
        g.current_user = None

        @roles_required(Role.ADMIN)
        def view():
            return "ok"

        with pytest.raises(AuthenticationError):
            view()


def test_serialize_notification_returns_correct_fields():
    notif = Mock()
    notif.id = 1
    notif.type = NotificationType.MESSAGE
    notif.title = "Nuovo messaggio"
    notif.body = "Hai un messaggio"
    notif.report_id = 3
    notif.is_read = False
    notif.created_at = _TS

    result = serialize_notification(notif)

    assert result["id"] == 1
    assert result["type"] == "message"
    assert result["is_read"] is False
    assert result["created_at"] == _TS.isoformat()


def test_serialize_message_returns_correct_fields():
    sender = _user(user_id=1)
    recipient = _user(user_id=2)
    msg = Mock()
    msg.id = 5
    msg.report_id = 3
    msg.body = "Ciao"
    msg.sender = sender
    msg.recipient = recipient
    msg.created_at = _TS

    result = serialize_message(msg)

    assert result["id"] == 5
    assert result["body"] == "Ciao"
    assert result["sender"]["id"] == 1
    assert result["recipient"]["id"] == 2

def test_login_required_redirects_on_non_api_path(flask_app):
    web = Blueprint("web", __name__)

    @web.route("/login")
    def login():
        return "login page"

    flask_app.register_blueprint(web)

    @flask_app.route("/dashboard")
    @login_required
    def dashboard():
        return "ok"

    with flask_app.test_client() as client:
        response = client.get("/dashboard")
        assert response.status_code == 302

def test_serialize_photo_returns_correct_fields():
    photo = Mock()
    photo.id = 1
    photo.file_path = "uuid.jpg"
    photo.original_filename = "buca.jpg"
    photo.content_type = "image/jpeg"

    from participium.core.serialization import serialize_photo
    result = serialize_photo(photo)

    assert result["id"] == 1
    assert result["url"] == "/static/uploads/uuid.jpg"