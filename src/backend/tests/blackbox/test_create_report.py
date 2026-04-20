from __future__ import annotations

from participium.services.report_service import ReportService

# Function: 
# Inputs: reporter: User, category_id: int | str | None, title: str | None, description: str | None, latitude: float | str | None, longitude: float | str | None, photos: list[FileStorage], is_anonymous: bool = False
# Expected Output:
# - The created `Report`, reloaded after persistence if successful.
# - ValidationError: if `category_id` is missing, malformed, unknown, or refers to an inactive category.
# - ValidationError: if `title` or `description` is missing.
# - ValidationError: if `latitude` or `longitude` is missing.
# - ValidationError: if coordinates cannot be converted to valid numeric values.
# - ValidationError: if there are no valid uploaded photos.
# - ValidationError: if more than 3 valid photos are provided.
# def create_report(
#   self,
#   reporter: User,
#   category_id: int | str | None,
#   title: str | None,
#   description: str | None,
#   latitude: float | str | None,
#   longitude: float | str | None,
#   photos: list[FileStorage],
#   is_anonymous: bool = False,
#   ) -> Report
#| TC-ID | reporter | category_id | title |description | latitude | longitude |photos | is_anonymous | Input |Expected | Fixture |
#| :---- | :------- | :---------- | :---- |:---------- | :------- | :-------- | :---- | :------------: | :---- | :------ | :------- |