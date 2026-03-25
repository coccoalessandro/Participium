# 1) Use Case Diagram

Attach your use case diagram as an image under `../data/img/` and link it here:

![](../../data/img/use-case-diagram.png)

Also, make sure to include the JSON source file downloaded from the UML Modeler used to draw the diagram in the `../data/` folder.

# 2) Use Case Narratives

Add one narrative for each use case shown in the diagram.
  
| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |  UC1 - Create account                           |
| Scope                   |  Participium                           |
| Level                   |  User goal                           |
| Intention in Context    |  The visitor user wants to register in the system                           |
| Primary actor           |   Visitor                          |
| Supporting actors       |     -                        |
| Stakeholders' interests |     System administrators: ensuring safety for user accounts                        |
| Precondition            |      -                       |
| Minimum guarantees      |      -                       |
| Success guarantees      |    The account is created for the user                         |
| Trigger                 |      -                       |
| Main success scenario   |  1. The user asks to registewr to Participium <br>                                               2. The system asks if the registration is as Citizen or Municipal officer. <br>   3. The user selects the type of account. <br>  4. The system shows the signup page and asks for username, first name, last name, email and password. <br> 5. The user inserts the required data. <br>   6. the system sends a verification email. <br> 7. The user confirms the email account. <br>  8. The system confirms data and saves the profile. <br> <br> The use case terminates with success|
| Extensions              | 5a.1 The user cancels the registration <br> 5a.2 The system doesn’t register the account. Use case fails <br> <br>  8a.1 The user inserts a username which is already registered from step 2 <br> 8a.2 The system shows an error and the use case restarts <br> <br>  4b.1 The user inserts a weak password <br>  4b.2 The system shows an error and the use case restarts from step 2 |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |  UC2 - Login                           |
| Scope                   |  Participium                           |
| Level                   | User goal                 |
| Intention in Context    | The user wants to login in the system as a citizen |
| Primary actor           | Unlogged user                            |
| Supporting actors       | Authentication system                            |
| Stakeholders' interests |  -                           |
| Precondition            |  User has an account                           |
| Minimum guarantees      |   -                          |
| Success guarantees      |    The user is logged in the system                         |
| Trigger                 |   -                          |
| Main success scenario   | 1. The user asks to login <br> 2. The system shows the form for credentials <br> 3. The user inserts email and password <br> 4. The system validates and logs the user in <br> <br> The use case terminates with success                            |
| Extensions              |  4a.1 Invalid email or password <br> 4a.2 The system shows an error - the use case goes to step 2                            |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |  UC3 - Search for reports                          |
| Scope                   |  Participium                          |
| Level                   |  User goal              |
| Intention in Context    |  The user wants to search for reports by type or locations|
| Primary actor           |  Registered/visitor user                          |
| Supporting actors       |  -                          |
| Stakeholders' interests |  -                           |
| Precondition            |  -                          |
| Minimum guarantees      |  Previous searches are shown to the user  |
| Success guarantees      |  The searched reports are shown to the user  |
| Trigger                 |   -                          |
| Main success scenario   |    1. The user enters the search query <br> 2. The system shows the results of the query <br> 3. The user selects the report he is looking for. <br> <br>  The use case terminates with success  |
| Extensions              |     2a.1 No reports are found with the search query <br> 2a.2 The system shows search error to the user and the shows the results of previous searches   |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |  UC4 - Filter reports                          |
| Scope                   |                      Participium      |
| Level                   |   User goal             |
| Intention in Context    | The user wants to apply additional filters on a general query |
| Primary actor           |   Registered/visitor user                          |
| Supporting actors       |   -                         |
| Stakeholders' interests |  -                           |
| Precondition            |   -                         |
| Minimum guarantees      |    Previous searches are shown to the user                         |
| Success guarantees      |   The searched reports are shown to the user                         |
| Trigger                 |   -                          |
| Main success scenario   |  1. The user enters the search query <br> 2. The system shows the results of the query <br> 3. The user selects filters to apply to the reports <br> 4. The system shows the available reports according to the filters <br> 5. The user selects the report he is looking for. <br> <br>  The use case terminates with success               |
| Extensions              |   2a.1 No reports are found with the search query <br> 2a.2 The system shows search error to the user and the shows the results of previous searches <br> <br> 4a.1 No reports are found with the filters <br> 4a.2 The system shows search error to the user and the shows the results of previous searches      |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |   UC5 - Search for reports with map view                         |
| Scope                   |        Participium                    |
| Level                   |      User goal          |
| Intention in Context    | The user wants to search for reports with map view |
| Primary actor           |     Registered/visitor user                           |
| Supporting actors       |   OpenStreetMap API                         |
| Stakeholders' interests |  -                           |
| Precondition            |  -                          |
| Minimum guarantees      |  The map view shows an overall view of Turin                          |
| Success guarantees      |  The searched reports are shown to the user                        |
| Trigger                 |   -                          |
| Main success scenario   |  1. The users navigates trough the map view and selects the report <br> 2. The system shows the details of the selected report <br> <br>  The use case terminates with success            |
| Extensions              |  -         |

| Use Case                |                             |
|:------------------------|:----------------------------|
| ID                      |  UC6 - Search for reports with table view                          |
| Scope                   |  Participium                           |
| Level                   |      User goal          |
| Intention in Context    |  The user wants to search for reports with table view |
| Primary actor           |    Registered/visitor user                        |
| Supporting actors       |   -                         |
| Stakeholders' interests |  -                           |
| Precondition            |  -                          |
| Minimum guarantees      |   -                          |
| Success guarantees      |   The table view shows an overall list of reports                         |
| Trigger                 |   -                          |
| Main success scenario   |   1. The users navigates trough the table view and selects the report <br> 2. The system shows the details of the selected report <br> <br>  The use case terminates with success             |
| Extensions              |    -       |

# 3) Traceability Table

| UC ID | REQ ID |
| :---- | :----- |
| UC-XX | FR-XX  |
