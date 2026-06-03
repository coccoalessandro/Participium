## 1 `participium.services.auth_service.AuthService.authenticate`

Suggested test file: `test_authenticate.py`

Prototype: `authenticate(identifier: str, password: str) -> User`

| TC-ID | identifier | password | Input |Expected | Fixture |
| :---- | :--------- | :------- | :---- |:------- | :------ |
|  TC-1 | empty | * | ("","psw19") | AuthenticationError("credentials are invalid") | * |
|  TC-2 | * | empty | ("Group19","") | AuthenticationError("credentials are invalid") | * |
|  TC-3 | any | * | ("Group19","psw19") | AuthenticationError("credentials are invalid")| * |
|  TC-4 | * | any | ("Group20","psw19") | AuthenticationError("credentials are invalid") | * |
|  TC-5 | correct username | correct | ("Group20","psw20") | The authenticated `User` | Active and Verified |
|  TC-6 | correct and verified email | correct | ("Group20@gmail.com","psw20") | The authenticated `User` | Active and Verified |
|  TC-7 | correct email | correct | ("Group20@gmail.com","psw20") | AuthenticationError("the matched user exists but email is not verified") | Active and not Verified email |
|  TC-8 | correct username | correct | ("Group20","psw20") | AuthenticationError("the matched user exists but email is not verified") | Active and not Verified email |
|  TC-9 | correct username | correct | ("Group20","psw20") | AuthenticationError("the matched user exists but is inactive") | Inactive |
|  TC-10 | correct email | correct | ("Group20@gmail.com","psw20") | AuthenticationError("the matched user exists but is inactive") | Inactive |

## 2 `participium.core.utils.parse_date`

Suggested test file: `test_parse_date.py`

Prototype: `parse_date(value: str | None) -> datetime | None`

| TC-ID | value | Input | Expected | Fixture |
| :---- | :---- | :---- | :------- | :------ |
| TC-1 | None | (None) | None | * |
| TC-2 | empty | ("") | None | * |
| TC-3 | valid ISO | ("2026-04-20T10:30:00") | datetime | * |
| TC-4 | invalid | ("32/13-210") | ValueError | * |

## 3 `participium.core.status_flow.ensure_transition_allowed`

Suggested test file: `test_status_flow.py`

Prototype: `ensure_transition_allowed(current_status: ReportStatus, next_status: ReportStatus) -> bool`

Allowed transitions:
`Pending Approval -> Pending Approval | Assigned | Rejected`;
`Assigned -> Assigned | In Progress | Suspended | Resolved`;
`In Progress -> In Progress | Suspended | Resolved`;
`Suspended -> Suspended | In Progress | Resolved`;
`Rejected -> Rejected`;
`Resolved -> Resolved`.

| TC-ID | current_status | next_status | Expected | Fixture |
| :---- | :------------- | :---------- |:---------- |  :------ |
| TC-1 | Pending Approval | Pending Approval / Assigned / Rejected | True | * |
| TC-2 | Pending Approval | In Progress / Suspended / Resolved | ValidationError | * |
| TC-3 | Assigned | Assigned / In Progress / Suspended / Resolved | True | * |
| TC-4 | Assigned | Pending Approval / Rejected | ValidationError | * |
| TC-5 | In Progress | In Progress / Suspended / Resolved | True | * |
| TC-6 | In Progress | Rejected / Pending Approval / Assigned | ValidationError | * |
| TC-7 | Suspended | Suspended / In Progress / Resolved | True | * |
| TC-8 | Suspended | Pending Approval / Assigned / Rejected | ValidationError | * |
| TC-9 | Rejected | Rejected | True | * |
| TC-10 | Rejected | Pending Approval / Assigned / In Progress / Suspended / Resolved | ValidationError | * |
| TC-11 | Resolved | Resolved | True | * |
| TC-12 | Resolved | Pensig Approval / Assigned / In Progess / Suspended / Rejected | ValidationError | * |


## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

| TC-ID | reporter | category_id | title |description | latitude | longitude |photos | is_anonymous |Expected | Fixture |
| :---- | :------- | :---------- | :---- |:---------- | :------- | :-------- | :---- | :------------: | :---- |:------ |
| TC-1 | correct | correct | correct | correct | correct | correct | correct | correct | Report | active and verified user, active category |
| TC-2 | * | empty | * | * | * | * | * | * | ValidationError | active and verified user |
| TC-3 | * | malformed | *| * | * | * | * | * | ValidationError | active and verified user |
| TC-4 | * | unkown | *| * | * | * | * | * | ValidationError | active and verified user |
| TC-5 | * | inactive category | *| * | * | * | * | * | ValidationError | active and verified user, inactive category |
| TC-6 | * | * | empty | * | * | * | * | * | ValidationError | active and verified user, active category |
| TC-7 | * | * | * | empty | * | * | * | * | ValidationError | active and verified user, active category |
| TC-8 | * | * | *| * | empty | * | * | * | ValidationError | active and verified user, active category |
| TC-9 | * | * | *| * | * | empty | * | * | ValidationError | active and verified user, active category |
| TC-10 | * | * | * | * | non convertible | * | * | * | ValidationError | active and verified user, active category |
| TC-11 | * | * | *| * | * | non convertible | * | * | ValidationError | active and verified user, active category |
| TC-12 | * | * | *| * | * | * | non valid photos | * | ValidationError | active and verified user, active category |
| TC-13 | * | * | *| * | * | * | too many photos | * | ValidationError | active and verified user, active category |

## 5 `participium.services.report_service.ReportService.update_status`

Suggested test file: `test_update_status.py`

Prototype: `update_status(report_id: int, operator: User, next_status_value: str, note: str | None = None) -> Report`

| TC-ID | report_id | operator | next_status_value | note | Input | Expected | Fixture |
| :---- | :-------- | :------- | :---------------- | :--- | :---- | :------- | :-------|
| TC-1 | existing | authorized | valid allowed | * | (1, operator, "assigned", None) | Updated Report | existing report and authorized operator |
| TC-2 | existing | unauthorized | valid | * | (1, user, "assigned", None) | AuthorizationError | existing report and unauthorized operator |
| TC-3 | existing | operator outside category | valid | * | (1, operator_other_category, "assigned", None) | AuthorizationError | existing report and operator assigned to another category |
| TC-4 | non-existing | authorized | valid | * | (999, operator, "assigned", None) | NotFoundError | authorized operator |
| TC-5 | existing | authorized | invalid | * | (1, operator, "invalid_status", None) | ValidationError | existing report and authorized operator |
| TC-6 | existing | authorized | rejected | empty | (1, operator, "rejected", None) | ValidationError | existing report and authorized operator |
| TC-7 | existing | authorized | rejected | not-empty | (1, operator, "rejected", "Not enough information.") | Updated Report | existing report and authorized operator |
| TC-8 | existing | authorized | valid not allowed | None | (1, operator, "pending_approval", None) | ValidationError | existing report with status resolved and authorized operator |

## 6 `participium.services.report_service.ReportService.list_public_reports`

Suggested test file: `test_public_reports.py`

Prototype: `list_public_reports(category_id: int | None = None, status: ReportStatus | None = None, date_from: datetime | None = None, date_to: datetime | None = None, sort: str = "desc") -> list[Report]`

| TC-ID | category_id | status | date_from | date_to | sort | Input | Expected | Fixture |
| :---- | :---------- | :----- | :-------- | :------ | :--- | :---- | :------- | :--------- |
| TC-1 | * | * | * | * | desc | (1, ReportStatus.RESOLVED, 10/02/26, 15/03/26, "desc") | list[Report] marching all filters ordered by newest first | existing public reports |
| TC-2 | * | * | * | * | asc | (1, ReportStatus.RESOLVED, 10/02/26, 15/03/26, "asc") | list[Report] matching all filters ordered by oldest first | existing public reports |
| TC-3 | None | None | None | None | valid | (None, None, None, None, "desc") | list[Report] | existing public reports |


## 7 `participium.services.messaging_service.MessagingService.send_message`

Suggested test file: `test_send_message.py`

Prototype: `send_message(report: Report, sender: User, body: str) -> Message`

| TC-ID | report | sender | body | Input | Expected | Fixture |
| :---- | :----- | :----- | :--- | :---- | :------- | :------ |
| TC-1 | correct | authorized | not empty | (report, AUTHORIZED_USER, "Hello, I need more information.") | Message | existing report with accessible thread |
| TC-2 | correct | unauthorized | not empty | (report, UNAUTHORIZED_USER, "Hello, I need more information.") | AuthorizationError | existing report and user without thread access |
| TC-3 | correct | authorized | empty | (report, AUTHORIZED_USER, "") | ValidationError | existing report with accessible thread |
| TC-4 | correct | authorized | blank | (report, AUTHORIZED_USER, "   ") | ValidationError | existing report with accessible thread |
| TC-5 | correct | authorized | correct | (report, AUTHORIZED_USER, "Hello, I need more information.") | ValidationError | existing report with no resolvable recipient |

## 8 `participium.core.security.verify_password`

Suggested test file: `test_verify_password.py`

Prototype: `verify_password(password: str, password_hash: str) -> bool`

| TC-ID | password | password_hash | Input | Expected | Fixture |
| :---- | :------- | :------------ | :---- | :------- | :-------|
| TC-1 | correct | valid hash | ("psw20", hash of "psw20") | True | * | 
| TC-2 | incorrect | * | ("psw19", hash of "psw20") | False | * | 
| TC-3 | empty | * | ("", hash of "psw19") | False | * | 
| TC-4 | * | empty | ("psw19", "") | False | * | 
| TC-5 | * | invalid hash | ("psw19", not a valid hash) | False | * | 


## 9 `participium.services.notification_service.NotificationService.create_notification`

Suggested test file: `test_create_notification.py`

Prototype: `create_notification(user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None`

| TC-ID | user | notification_type | title | body | report | Input | Expected | Fixture |
| :---- | :--- | :---------------- | :---- | :--- | :----- | :---- | :------- | :------ |
| TC-1 | correct | correct | correct | correct | None | (CORRECT_USER, NotificationType.STATUS_CHANGED, "Status updated", "The report status has changed.", None) | Notification | non-null user |
| TC-2 | correct | correct | correct | correct | correct | (CORRECT_USER, NotificationType.STATUS_CHANGED, "Status updated", "The report status has changed.", REPORT_WASTE) | Notification linked to report | non-null user and existing report |
| TC-3 | None | * | * | * | * | (None, NotificationType.STATUS_CHANGED, "Status updated", "The report status has changed.", None) | None | * |
| TC-4 | correct | invalid | * | * | * | (CORRECT_USER, "123", "Status updated", "The report status has changed.", REPORT_WASTE) | ValueError | * |


## 10 `participium.services.user_service.UserService.update_profile`

Suggested test file: `test_update_profile.py`

Prototype: `update_profile(user: User, username: str | None = None, first_name: str | None = None, last_name: str | None = None, email_notifications_enabled: bool | None = None, profile_picture: FileStorage | None = None) -> User`

| TC-ID | user | username | first_name | last_name | email_notifications_enabled | profile_picture | Input | Expected | Fixture |
| :---- | :--- | :------- | :--------- | :-------- | :-------------------------- | :-------------- | :---- | :------- | :------ |
| TC-1 | correct | correct unused | * | * | * | * | (CORRECT_USER, "bianchi.luca", "Mario", "Rossi", True, None) | Updated User | existing user |
| TC-2 | correct | None | None | None | None | None | (CORRECT_USER, None, None, None, None, None) | Unchanged User | existing user |
| TC-3 | correct | already used | * | * | * | * | (CORRECT_USER, "existing_username", "Mario", "Rossi", None, None) | ValidationError | existing user and existing another user with new username |