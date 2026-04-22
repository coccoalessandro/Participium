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
| TC-1 | any | ("32/13-210") | ValueError |  |
| TC-2 | empty | ("") | None | |
| TC-3 | correct | ("2026-04-20") | datetime | |
| TC-4 | None | None | None | |

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
| :---- | :------------- | :---------- | :------- | :------ |
| TC-1 | Pending Approval | Pending Approval / Assigned / Rejected | True |  |
| TC-2 | Pending Approval | In Progress / Suspended / Resolved | ValidationError |  |
| TC-3 | Assigned | Assigned / In Progress / Suspended / Resolved | True |  |
| TC-4 | Assigned | Pending Approval / Rejected | ValidationError |  |
| TC-5 | In Progress | In Progress / Suspended / Resolved | True |  |
| TC-6 | In Progress | Rejected / Pending Approval / Assigned | ValidationError |  |
| TC-7 | Suspended | Suspended / In Progress / Resolved | True |  |
| TC-8 | Suspended | Pending Approval / Assigned / Rejected | ValidationError |  |
| TC-9 | Rejected | Rejected | True |  |
| TC-10 | Rejected | Pending Approval / Assigned / In Progress / Suspended / Resolved | ValidationError |  |
| TC-11 | Resolved | Resolved | True |  |
| TC-12 | Resolved | Pensig Approval / Assigned / In Progess / Suspended / Rejected | ValidationError |  |


## 4 `participium.services.report_service.ReportService.create_report`

Suggested test file: `test_create_report.py`

Prototype: `create_report(reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False) -> Report`

| TC-ID | reporter | category_id | title |description | latitude | longitude |photos | is_anonymous |Expected | Fixture |
| :---- | :------- | :---------- | :---- |:---------- | :------- | :-------- | :---- | :------------: | :---- |:------ |
| TC-1 | correct | correct | correct | correct | correct | correct | correct | correct | Report |  |
| TC-2 | * | empty | * | * | * | * | * | * | ValidationError |  |
| TC-3 | * | malformed | *| * | * | * | * | * | ValidationError |  |
| TC-4 | * | unkown | *| * | * | * | * | * | ValidationError |  |
| TC-5 | * | inactive category | *| * | * | * | * | * | ValidationError |  |
| TC-6 | * | * | empty | * | * | * | * | * | ValidationError |  |
| TC-7 | * | * | * | empty | * | * | * | * | ValidationError |  |
| TC-8 | * | * | *| * | empty | * | * | * | ValidationError |  |
| TC-9 | * | * | *| * | * | empty | * | * | ValidationError |  |
| TC-10 | * | * | * | * | non convertible | * | * | * | ValidationError |  |
| TC-11 | * | * | *| * | * | non convertible | * | * | ValidationError |  |
| TC-12 | * | * | *| * | * | * | non valid photos | * | ValidationError |  |
| TC-13 | * | * | *| * | * | * | too many photos | * | ValidationError |  |

## 5 `participium.services.report_service.ReportService.update_status`

Suggested test file: `test_update_status.py`

Prototype: `update_status(report_id: int, operator: User, next_status_value: str, note: str | None = None) -> Report`

| TC-ID | report_id | operator | next_status_value | note | Expected | Fixture |
| :---- | :-------- | :------- | :---------------- | :--- | :------- | :------ |
|  |  |  |  |  |  |  |

## 6 `participium.services.report_service.ReportService.list_public_reports`

Suggested test file: `test_public_reports.py`

Prototype: `list_public_reports(category_id: int | None = None, status: ReportStatus | None = None, date_from: datetime | None = None, date_to: datetime | None = None, sort: str = "desc") -> list[Report]`

| TC-ID | category_id | status | date_from | date_to | sort | Expected | Fixture |
| :---- | :---------- | :----- | :-------- | :------ | :--- | :------- | :------ |
|  |  |  |  |  |  |  |  |


## 7 `participium.services.messaging_service.MessagingService.send_message`

Suggested test file: `test_send_message.py`

Prototype: `send_message(report: Report, sender: User, body: str) -> Message`

| TC-ID | report | sender | body | Expected | Fixture |
| :---- | :----- | :----- | :--- | :------- | :------ |
|  |  |  |  |  |  |

## 8 `participium.core.security.verify_password`

Suggested test file: `test_verify_password.py`

Prototype: `verify_password(password: str, password_hash: str) -> bool`

| TC-ID | password | password_hash | Expected | Fixture |
| :---- | :------- | :------------ | :------- | :------ |
|  |  |  |  |  |

## 9 `participium.services.notification_service.NotificationService.create_notification`

Suggested test file: `test_create_notification.py`

Prototype: `create_notification(user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None`

| TC-ID | user | notification_type | title | body | report | Expected | Fixture |
| :---- | :--- | :---------------- | :---- | :--- | :----- | :------- | :------ |
|  |  |  |  |  |  |  |  |

## 10 `participium.services.user_service.UserService.update_profile`

Suggested test file: `test_update_profile.py`

Prototype: `update_profile(user: User, username: str | None = None, first_name: str | None = None, last_name: str | None = None, email_notifications_enabled: bool | None = None, profile_picture: FileStorage | None = None) -> User`

| TC-ID | user | username | first_name | last_name | email_notifications_enabled | profile_picture | Expected | Fixture |
| :---- | :--- | :------- | :--------- | :-------- | :-------------------------- | :-------------- | :------- | :------ |
|  |  |  |  |  |  |  |  |  |
