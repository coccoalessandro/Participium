from __future__ import annotations

from participium.services.notification_service import NotificationService

# Function: 
# Inputs: user (User | None), notification_type (NotificationType), title (str), body (str), report (Report | None)
# Expected Output:
# - A persisted `Notification` for a non-null user, otherwise `None`.
# - Exception: No documented domain exception from the method contract itself.
# - Exception: Email delivery failures, if any, are internally swallowed after logging.
#def create_notification(self, user: User | None, notification_type: NotificationType, title: str, body: str, report: Report | None = None) -> Notification | None
#| TC-ID | user | notification_type | title | body | report | Input |Expected | Fixture |
#| :---- | :--- | :---------------- | :---- |:---- | :----- | :---- | :------- | :------ |