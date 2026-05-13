from __future__ import annotations

from datetime import datetime
from unittest.mock import MagicMock, Mock

import pytest

from participium.core.exceptions import AuthorizationError, NotFoundError, ValidationError
from participium.models.enums import ReportStatus, Role
from participium.models.report import Report, ReportPhoto, ReportStatusHistory
from participium.models.user import User
from participium.services.report_service import ReportService

pytestmark = pytest.mark.whitebox



def _user(*, user_id: int, username: str = "test_citizen") -> User:
    return User(id=user_id, username=username)


def _photo(*, filename: str | None = "test.jpg", content_type: str = "image/jpeg") -> Mock:
    photo = Mock()
    photo.filename = filename
    photo.content_type = content_type
    return photo


def _mock_user(
    *,
    user_id: int = 1,
    role: Role = Role.CITIZEN,
    category_id: int | None = None,
) -> Mock:
    user = Mock(spec=User)
    user.id = user_id
    user.role = role
    user.category_id = category_id
    return user


def _mock_report(
    *,
    report_id: int = 1,
    reporter_id: int = 10,
    category_id: int = 5,
    status: ReportStatus = ReportStatus.PENDING_APPROVAL,
) -> MagicMock:
    report = MagicMock(spec=Report)
    report.id = report_id
    report.reporter_id = reporter_id
    report.category_id = category_id
    report.status = status
    report.rejection_reason = None
    return report



@pytest.fixture
def report_service_bundle() -> dict[str, object]:
    session = Mock()
    report_repository = Mock()
    category_repository = Mock()
    storage_service = Mock()
    notification_service = Mock()

    service = ReportService(
        session=session,
        report_repository=report_repository,
        category_repository=category_repository,
        storage_service=storage_service,
        notification_service=notification_service,
    )

    return {
        "service": service,
        "session": session,
        "report_repository": report_repository,
        "category_repository": category_repository,
        "storage_service": storage_service,
        "notification_service": notification_service,
    }



def test_list_public_reports_returns_list_sorted_desc(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    fake_reports = [Mock(spec=Report), Mock(spec=Report)]
    report_repository.list_reports.return_value = fake_reports

    result = service.list_public_reports(
        category_id=1,
        status=ReportStatus.RESOLVED,
        date_from=datetime(2026, 2, 10),
        date_to=datetime(2026, 2, 15),
        sort="desc",
    )

    assert result == fake_reports
    report_repository.list_reports.assert_called_once_with(
        public_only=True,
        category_id=1,
        status=ReportStatus.RESOLVED,
        date_from=datetime(2026, 2, 10),
        date_to=datetime(2026, 2, 15),
        sort="desc",
    )


def test_list_public_reports_returns_list_sorted_asc(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    fake_reports = [Mock(spec=Report)]
    report_repository.list_reports.return_value = fake_reports

    result = service.list_public_reports(sort="asc")

    assert result == fake_reports



def test_list_user_reports_delegates_to_repository(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    user = _mock_user(user_id=10)
    expected = [Mock(spec=Report), Mock(spec=Report)]
    report_repository.list_user_reports.return_value = expected

    result = service.list_user_reports(user)

    assert result == expected
    report_repository.list_user_reports.assert_called_once_with(user.id)



def test_get_report_returns_report_when_found(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    mock_report = Mock(spec=Report)
    mock_report.id = 1
    report_repository.get_by_id.return_value = mock_report

    result = service.get_report(1)

    assert result is mock_report
    report_repository.get_by_id.assert_called_once_with(1)


def test_get_report_raises_not_found_error_when_missing(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    report_repository.get_by_id.return_value = None

    with pytest.raises(NotFoundError):
        service.get_report(999)


@pytest.fixture
def accessible_report_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    """Pre-wires get_report and is_public so tests control them directly."""
    service: ReportService = report_service_bundle["service"]
    mock_report = _mock_report()
    service.get_report = Mock(return_value=mock_report)
    report_service_bundle["mock_report"] = mock_report
    return report_service_bundle


def test_get_accessible_report_returns_report_when_public(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    mock_report = accessible_report_bundle["mock_report"]
    service.is_public = Mock(return_value=True)

    result = service.get_accessible_report(1, user=None)

    assert result is mock_report


def test_get_accessible_report_raises_authorization_error_when_not_public_and_no_user(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    service.is_public = Mock(return_value=False)

    with pytest.raises(AuthorizationError):
        service.get_accessible_report(1, user=None)


def test_get_accessible_report_allows_reporter(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    mock_report = accessible_report_bundle["mock_report"]
    service.is_public = Mock(return_value=False)

    user = _mock_user(user_id=mock_report.reporter_id, role=Role.CITIZEN)

    result = service.get_accessible_report(1, user=user)

    assert result is mock_report


def test_get_accessible_report_allows_admin(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    mock_report = accessible_report_bundle["mock_report"]
    service.is_public = Mock(return_value=False)

    user = _mock_user(user_id=99, role=Role.ADMIN)

    result = service.get_accessible_report(1, user=user)

    assert result is mock_report


def test_get_accessible_report_allows_operator_with_matching_category(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    mock_report = accessible_report_bundle["mock_report"]
    service.is_public = Mock(return_value=False)

    user = _mock_user(user_id=99, role=Role.OPERATOR, category_id=mock_report.category_id)

    result = service.get_accessible_report(1, user=user)

    assert result is mock_report


def test_get_accessible_report_raises_for_operator_with_wrong_category(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    mock_report = accessible_report_bundle["mock_report"]
    service.is_public = Mock(return_value=False)

    user = _mock_user(user_id=99, role=Role.OPERATOR, category_id=mock_report.category_id + 1)

    with pytest.raises(AuthorizationError):
        service.get_accessible_report(1, user=user)


def test_get_accessible_report_raises_for_unrelated_citizen(
    accessible_report_bundle: dict[str, object],
) -> None:
    service: ReportService = accessible_report_bundle["service"]
    service.is_public = Mock(return_value=False)

    user = _mock_user(user_id=99, role=Role.CITIZEN)

    with pytest.raises(AuthorizationError):
        service.get_accessible_report(1, user=user)



@pytest.fixture
def create_report_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    active_category = Mock()
    active_category.id = 1
    active_category.is_active = True
    report_service_bundle["category_repository"].get_by_id.return_value = active_category
    report_service_bundle["active_category"] = active_category

    service: ReportService = report_service_bundle["service"]
    service.get_report = Mock()
    return report_service_bundle


def test_create_report_raises_when_category_id_is_invalid_format(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=_user(user_id=10), category_id="not_a_number",
            title="T", description="D", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_category_id_is_none(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=None,
            title="T", description="D", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_category_is_not_found(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]
    create_report_bundle["category_repository"].get_by_id.return_value = None

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=99,
            title="T", description="D", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_category_is_inactive(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]
    inactive = Mock()
    inactive.is_active = False
    create_report_bundle["category_repository"].get_by_id.return_value = inactive

    with pytest.raises(ValidationError, match="A valid active category is required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=3,
            title="T", description="D", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_title_is_missing(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="Title and description are required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="", description="D", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_description_is_missing(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="Title and description are required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="T", description="", latitude=45.0, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_latitude_is_none(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="Latitude and longitude are required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="T", description="D", latitude=None, longitude=7.0, photos=[],
        )


def test_create_report_raises_when_coordinates_are_not_numeric(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="Latitude and longitude must be valid numbers."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="T", description="D", latitude="invalid_float", longitude=7.0, photos=[],
        )


def test_create_report_raises_when_no_valid_photos_provided(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="At least one photo is required."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="T", description="D", latitude=45.0, longitude=7.0,
            photos=[_photo(filename=None)],
        )


def test_create_report_raises_when_more_than_three_photos_provided(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]

    with pytest.raises(ValidationError, match="A report can contain at most 3 photos."):
        service.create_report(
            reporter=_user(user_id=10), category_id=1,
            title="T", description="D", latitude=45.0, longitude=7.0,
            photos=[_photo(filename=f"img{i}.jpg") for i in range(4)],
        )


def test_create_report_persists_and_returns_reloaded_report(
    create_report_bundle: dict[str, object],
) -> None:
    service: ReportService = create_report_bundle["service"]
    session = create_report_bundle["session"]
    report_repository = create_report_bundle["report_repository"]
    storage_service = create_report_bundle["storage_service"]

    create_report_bundle["category_repository"].get_by_id.return_value = Mock(id=1, is_active=True)
    storage_service.save.side_effect = ["/storage/a.jpg", "/storage/b.jpg"]

    final_report = Mock(spec=Report)
    service.get_report.return_value = final_report

    result = service.create_report(
        reporter=_user(user_id=10),
        category_id="1",
        title="  Tubo Rotto  ",
        description=" Acqua che perde ",
        latitude="45.1",
        longitude="7.2",
        photos=[_photo(filename="a.jpg"), _photo(filename="b.jpg")],
        is_anonymous=True,
    )

    assert result is final_report

    saved_report = report_repository.add.call_args[0][0]
    assert saved_report.title == "Tubo Rotto"
    assert saved_report.description == "Acqua che perde"
    assert saved_report.latitude == 45.1
    assert saved_report.is_anonymous is True

    assert storage_service.save.call_count == 2
    assert report_repository.add_photo.call_count == 2

    report_repository.add_status_entry.assert_called_once()
    session.flush.assert_called_once()
    session.commit.assert_called_once()


@pytest.fixture
def follow_report_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    service: ReportService = report_service_bundle["service"]
    mock_report = _mock_report(report_id=1)
    service.get_report = Mock(return_value=mock_report)
    report_service_bundle["mock_report"] = mock_report
    return report_service_bundle


def test_follow_report_raises_validation_error_when_report_is_not_public(
    follow_report_bundle: dict[str, object],
) -> None:
    service: ReportService = follow_report_bundle["service"]
    service.is_public = Mock(return_value=False)
    user = _mock_user(user_id=10)

    with pytest.raises(ValidationError):
        service.follow_report(1, user)


def test_follow_report_returns_report_without_adding_follower_when_already_following(
    follow_report_bundle: dict[str, object],
) -> None:
    service: ReportService = follow_report_bundle["service"]
    report_repository = follow_report_bundle["report_repository"]
    mock_report = follow_report_bundle["mock_report"]
    service.is_public = Mock(return_value=True)
    report_repository.get_follower.return_value = Mock()
    user = _mock_user(user_id=10)

    result = service.follow_report(1, user)

    assert result is mock_report
    report_repository.add_follower.assert_not_called()


def test_follow_report_adds_follower_and_commits_when_not_yet_following(
    follow_report_bundle: dict[str, object],
) -> None:
    service: ReportService = follow_report_bundle["service"]
    report_repository = follow_report_bundle["report_repository"]
    session = follow_report_bundle["session"]
    service.is_public = Mock(return_value=True)
    report_repository.get_follower.return_value = None
    user = _mock_user(user_id=10)

    service.follow_report(1, user)

    report_repository.add_follower.assert_called_once()
    session.commit.assert_called_once()


@pytest.fixture
def unfollow_report_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    service: ReportService = report_service_bundle["service"]
    mock_report = _mock_report(report_id=1)
    service.get_report = Mock(return_value=mock_report)
    report_service_bundle["mock_report"] = mock_report
    return report_service_bundle


def test_unfollow_report_removes_follower_and_commits_when_following(
    unfollow_report_bundle: dict[str, object],
) -> None:
    service: ReportService = unfollow_report_bundle["service"]
    report_repository = unfollow_report_bundle["report_repository"]
    session = unfollow_report_bundle["session"]
    mock_follower = Mock()
    report_repository.get_follower.return_value = mock_follower
    user = _mock_user(user_id=10)

    service.unfollow_report(1, user)

    report_repository.remove_follower.assert_called_once_with(mock_follower)
    session.commit.assert_called_once()


def test_unfollow_report_does_nothing_when_not_following(
    unfollow_report_bundle: dict[str, object],
) -> None:
    service: ReportService = unfollow_report_bundle["service"]
    report_repository = unfollow_report_bundle["report_repository"]
    report_repository.get_follower.return_value = None
    user = _mock_user(user_id=10)

    service.unfollow_report(1, user)

    report_repository.remove_follower.assert_not_called()


def test_list_pending_reports_passes_filters_to_repository(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    date_f, date_t = datetime(2026, 1, 1), datetime(2026, 1, 31)
    filters = {"category_id": 5, "date_from": date_f, "date_to": date_t}
    expected = [Mock(spec=Report), Mock(spec=Report)]
    report_repository.list_pending.return_value = expected

    result = service.list_pending_reports(filters=filters)

    assert result == expected
    report_repository.list_pending.assert_called_once_with(
        category_id=5, date_from=date_f, date_to=date_t
    )


def test_list_operator_reports_delegates_to_repository(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    report_repository = report_service_bundle["report_repository"]

    user = _mock_user(user_id=5, role=Role.OPERATOR, category_id=3)
    expected = [Mock(spec=Report)]
    report_repository.list_operator_reports.return_value = expected

    result = service.list_operator_reports(user)

    assert result == expected
    report_repository.list_operator_reports.assert_called_once_with(user.role, user.category_id)


@pytest.fixture
def assign_report_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    service: ReportService = report_service_bundle["service"]
    service.get_report = Mock()
    service._ensure_operator_category_access = Mock()
    service._recipients = Mock(return_value=[])
    return report_service_bundle


def test_assign_report_raises_authorization_error_for_non_operator(
    assign_report_bundle: dict[str, object],
) -> None:
    service: ReportService = assign_report_bundle["service"]
    citizen = _mock_user(role=Role.CITIZEN)

    with pytest.raises(AuthorizationError):
        service.assign_report(1, citizen)


def test_assign_report_raises_validation_error_when_report_is_not_pending(
    assign_report_bundle: dict[str, object],
) -> None:
    service: ReportService = assign_report_bundle["service"]
    operator = _mock_user(role=Role.OPERATOR)
    report = _mock_report(status=ReportStatus.RESOLVED)
    service.get_report.return_value = report

    with pytest.raises(ValidationError):
        service.assign_report(1, operator)


def test_assign_report_sets_status_notifies_and_commits(
    assign_report_bundle: dict[str, object],
) -> None:
    service: ReportService = assign_report_bundle["service"]
    session = assign_report_bundle["session"]
    report_repository = assign_report_bundle["report_repository"]
    notification_service = assign_report_bundle["notification_service"]

    operator = _mock_user(user_id=99, role=Role.OPERATOR)
    report = _mock_report(status=ReportStatus.PENDING_APPROVAL)
    report.category = Mock()
    report.category.name = "Waste"
    service.get_report.return_value = report
    service._recipients.return_value = ["user1"]

    service.assign_report(1, operator)

    assert report.status == ReportStatus.ASSIGNED

    saved_history = report_repository.add_status_entry.call_args[0][0]
    assert isinstance(saved_history, ReportStatusHistory)
    assert saved_history.new_status == ReportStatus.ASSIGNED
    assert saved_history.changed_by_id == operator.id

    notification_service.notify_status_change.assert_called_once()
    session.commit.assert_called_once()


@pytest.fixture
def update_status_bundle(report_service_bundle: dict[str, object]) -> dict[str, object]:
    service: ReportService = report_service_bundle["service"]
    service.get_report = Mock()
    service._ensure_operator_category_access = Mock()
    service._recipients = Mock(return_value=["user@example.com"])
    return report_service_bundle


def test_update_status_raises_authorization_error_for_citizen(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    citizen = _mock_user(role=Role.CITIZEN)

    with pytest.raises(AuthorizationError):
        service.update_status(report_id=1, operator=citizen, next_status_value="Assigned")


def test_update_status_raises_not_found_error_when_report_missing(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    service.get_report.side_effect = NotFoundError("Report not found.")
    operator = _mock_user(role=Role.OPERATOR)

    with pytest.raises(NotFoundError):
        service.update_status(report_id=999, operator=operator, next_status_value="Assigned")


def test_update_status_raises_authorization_error_for_wrong_category(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    service.get_report.return_value = _mock_report()
    service._ensure_operator_category_access.side_effect = AuthorizationError("Access denied.")
    operator = _mock_user(role=Role.OPERATOR)

    with pytest.raises(AuthorizationError):
        service.update_status(report_id=1, operator=operator, next_status_value="Assigned")


def test_update_status_raises_validation_error_for_invalid_status_string(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    service.get_report.return_value = _mock_report()
    operator = _mock_user(role=Role.OPERATOR)

    with pytest.raises(ValidationError):
        service.update_status(report_id=1, operator=operator, next_status_value="status_inventato")


def test_update_status_raises_validation_error_for_rejection_without_note(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    service.get_report.return_value = _mock_report(status=ReportStatus.PENDING_APPROVAL)
    operator = _mock_user(role=Role.OPERATOR)

    with pytest.raises(ValidationError):
        service.update_status(report_id=1, operator=operator, next_status_value="Rejected", note="")


def test_update_status_raises_validation_error_for_disallowed_transition(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    service.get_report.return_value = _mock_report(status=ReportStatus.PENDING_APPROVAL)
    operator = _mock_user(role=Role.OPERATOR)

    with pytest.raises(ValidationError):
        service.update_status(report_id=1, operator=operator, next_status_value="Resolved")


def test_update_status_transitions_to_assigned_and_notifies(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    session = update_status_bundle["session"]
    notification_service = update_status_bundle["notification_service"]

    report = _mock_report(status=ReportStatus.PENDING_APPROVAL)
    service.get_report.return_value = report
    operator = _mock_user(role=Role.OPERATOR)

    result = service.update_status(report_id=1, operator=operator, next_status_value="Assigned")

    assert result.status == ReportStatus.ASSIGNED
    assert result.rejection_reason is None
    notification_service.notify_status_change.assert_called_once()
    session.commit.assert_called_once()


def test_update_status_transitions_to_rejected_with_note(
    update_status_bundle: dict[str, object],
) -> None:
    service: ReportService = update_status_bundle["service"]
    session = update_status_bundle["session"]

    report = _mock_report(status=ReportStatus.PENDING_APPROVAL)
    service.get_report.return_value = report
    operator = _mock_user(role=Role.OPERATOR)

    result = service.update_status(
        report_id=1, operator=operator, next_status_value="Rejected", note="Not enough info."
    )

    assert result.status == ReportStatus.REJECTED
    assert result.rejection_reason == "Not enough info."
    session.commit.assert_called_once()


def test_export_rows_returns_correct_dict_for_each_report(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]

    mock_report = Mock(spec=Report)
    mock_report.id = 1
    mock_report.title = "Buca in strada"
    mock_report.category.name = "Manutenzione"
    mock_report.status.value = "resolved"
    mock_report.created_at.isoformat.return_value = "2026-05-11T10:00:00"
    mock_report.latitude = 45.0
    mock_report.longitude = 9.0

    service.list_public_reports = Mock(return_value=[mock_report])

    result = service.export_rows()

    assert len(result) == 1
    assert result[0] == {
        "id": 1,
        "title": "Buca in strada",
        "category": "Manutenzione",
        "status": "resolved",
        "created_at": "2026-05-11T10:00:00",
        "latitude": 45.0,
        "longitude": 9.0,
    }


def test_export_rows_returns_empty_list_when_no_reports(
    report_service_bundle: dict[str, object],
) -> None:
    service: ReportService = report_service_bundle["service"]
    service.list_public_reports = Mock(return_value=[])

    assert service.export_rows() == []


@pytest.mark.parametrize("status", [
    ReportStatus.ASSIGNED,
    ReportStatus.IN_PROGRESS,
    ReportStatus.RESOLVED,
    ReportStatus.SUSPENDED,
])
def test_is_public_returns_true_for_public_statuses(status: ReportStatus) -> None:
    report = Mock(spec=Report)
    report.status = status

    assert ReportService.is_public(report) is True


@pytest.mark.parametrize("status", [
    ReportStatus.PENDING_APPROVAL,
    ReportStatus.REJECTED,
])
def test_is_public_returns_false_for_non_public_statuses(status: ReportStatus) -> None:
    report = Mock(spec=Report)
    report.status = status

    assert ReportService.is_public(report) is False


def test_recipients_includes_reporter_and_non_none_followers() -> None:
    reporter = Mock(spec=User)

    follower_with_user = Mock()
    follower_with_user.user = Mock(spec=User)

    follower_without_user = Mock()
    follower_without_user.user = None

    report = Mock(spec=Report)
    report.reporter = reporter
    report.followers = [follower_with_user, follower_without_user]

    result = ReportService._recipients(report)

    assert reporter in result
    assert follower_with_user.user in result
    assert None not in result
    assert len(result) == 2


def test_recipients_excludes_none_reporter() -> None:
    report = Mock(spec=Report)
    report.reporter = None
    report.followers = []

    result = ReportService._recipients(report)

    assert result == []


def test_ensure_operator_category_access_allows_admin() -> None:
    operator = _mock_user(role=Role.ADMIN)

    ReportService._ensure_operator_category_access(operator, Mock(spec=Report))


def test_ensure_operator_category_access_raises_for_citizen() -> None:
    operator = _mock_user(role=Role.CITIZEN)

    with pytest.raises(AuthorizationError):
        ReportService._ensure_operator_category_access(operator, Mock(spec=Report))


def test_ensure_operator_category_access_raises_for_operator_with_wrong_category() -> None:
    operator = _mock_user(role=Role.OPERATOR, category_id=10)
    report = _mock_report(category_id=99)

    with pytest.raises(AuthorizationError):
        ReportService._ensure_operator_category_access(operator, report)


def test_ensure_operator_category_access_allows_operator_with_matching_category() -> None:
    operator = _mock_user(role=Role.OPERATOR, category_id=5)
    report = _mock_report(category_id=5)

    ReportService._ensure_operator_category_access(operator, report)