from __future__ import annotations

from participium.services.user_service import UserService

# Function: 
# Inputs: user(User), username(str | None), first_name(str | None), last_name(str | None), email_notifications_enabled(bool | None), profile_picture(FileStorage | None))
# Expected Output:
# - The updated `User` if the update is successful.
# - ValidationError if the `username` is already used by another account.
#def update_profile(
#        self,
#        user: User,
#        username: str | None = None,
#        first_name: str | None = None,
#        last_name: str | None = None,
#        email_notifications_enabled: bool | None = None,
#        profile_picture: FileStorage | None = None,
#    ) -> User
#| TC-ID | user | username | first_name | last_name | email_notifications_enabled| profile_picture | Input |Expected | Fixture |
#| :---- | :--- | :------- | :--------- |:--------- | :------------------------- | :-------------- | :---- |:------- | :------ |
