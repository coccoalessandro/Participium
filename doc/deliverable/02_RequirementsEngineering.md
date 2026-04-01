# 1) Stakeholders


| ID     | Stakeholder name | Description | Role | Main concerns |
|:-------|:-----------------|:------------|:-----|:--------------|
| STK-1 | Citizen (registered) | Registered citizens can submit reports, track their evolution, and interact with the municipality. They own a citizen account created by providing their identity information | User who can view and submit reports | Ease of use of the interfaces, privacy of personal data |
| STK-2 | Citizen (visitors) | Unregistered users who can access the public portal to browse reports, statistics, and map views without authentication | Public viewer | Accessibility of information, usability of navigation, transparency of data |
| STK-3 | Municipal office | Personnel of the municipality responsible for managing reports, including validation, assignment, operational handling, and communication with citizens | Internal system user managing reports|Efficient workflow management, ease of use, timely updates, clear communication with citizens |
| STK-4 | System administrator | Technical user responsible for configuring the system, managing users, and accessing advanced analytics and statistics | System manager | System reliability, security, access control, data integrity |
| STK-5 | OpenStreetMap API | External service providing map data and geolocation functionalities used to display and select report locations | External geolocation service | Availability, accuracy of map data, performance |
| STK-6 | Authentication system | External or integrated service that manages user authentication, registration, and identity verification | Identity provider | Security, privacy, authentication reliability |
| STK-7 | Notification platform | Component responsible for generating and delivering in-platform notifications related to report updates | Notification service | Timeliness, reliability, correct delivery of notifications |
| STK-8 | Email service | External service used to send email notifications to users who opted for them | Communication service | Deliverability, latency, spam filtering issues |
| STK-9 | Direct messaging platform | Internal system enabling communication between citizens and operators through messages | Communication channel | Message reliability, usability, data privacy |
| STK-10 | Development team | Group responsible for designing, implementing, maintaining, and evolving the Participium system | System builder and maintainer | Code quality, maintainability, scalability, requirement clarity |
| STK-11 | Municipality of Turin | Public authority for which the system is developed | Commisioner | Transparency, public trust, efficiency of urban issue resolution |
| STK-12 | Urban service providers | external companies or municipal contractors responsible for physically resolving reported issues (e.g., maintenance, repairs) | Service executor | Clear task assignment, timely communication, operational efficiency |


---


# 2) Context Diagram


Attach your context diagram as an image under `../data/img/` and link it here:


![](../../data/img/context-diagram.png)


---


# 3) Interfaces


| ID    | Interface | Actor       | Physical interface | Logical interface |
|:------|:----------|:------------|:-------------------|:------------------|
| IF-1 | | Citizen (registered) | Smartphone/PC with internet connection | Web GUI | 
| IF-2 | | Citizen (visitor) | Smartphone/PC with internet connection | Web GUI | 
| IF-3 | | Municipal officer | Smartphone/PC with internet connection | Web GUI |
| IF-4 | | System administrator | Smartphone/PC with internet connection | Web GUI | 
| IF-4 | | OpenStreetMap API | Internet connection | Map APIs | 
| IF-5 | | Authetication system | Internet connection | Authentication APIs | 
| IF-6 | | Notification platform | Internet connection | Notification APIs | 
| IF-7 | | Email service | Internet connection | Email APIs | 
| IF-8 | | Direct messaging platform | Internet connection | Messaging APIs |  


---


# 4) Personas


| ID     | Name | Role | Background / Context | Goals | Constraints | Devices / Usage setting | Accessibility / Additional needs |
|:-------|:-----|:-----|:---------------------|:------|:------------|:------------------------|:---------------------------------|
| PER-1 | Jack | Registered citizen | Citizen of Turin who usually goes to work by car and uses Participium every morning to report and visualize the reports | Avoid traffic disruptions and contribute to improving city service | Limited time due to work; cannot spend much time creating detailed reports | Mostly his smartphone, sometimes his PC | Clear and minimal GUI, simple to use with his smartphone |
| PER-2 | John | Visitor citizen | Non resident student of Turin who once per week uses car sharing to reach places in Turin far from his home and uses Participium not to be stuck in the traffic | Avoid traffic disruptions | Passive user | Smartphone | Clear and minimal GUI, simple to use with his smartphone |
| PER-3 | Mary | Municipal officer | She works for the municipality of Turin and her role is to check submitted reports and update their status | Maintaining reports quality and contributing to improve the city service | Time loss in deleting fake reports and in making the bad written ones useful | PC workstation | Automatization of report validation |
| PER-4 | Lian | System administrator | Technical member of the administration team who works in the security department | Guarantee user data protection and integrity | Must comply with GDPR internal privacy policies and must quickly respond to data integrity incidents | PC workstation | Secure authentication service and clear GDPR documentation |
| PER-6 | Lucy | Development team member | Software engineer in charge of implementing new features and maintaining Participium | Deliver reliabke and maintainable system updates | Must follow coding standards | PC workstation and IDE | Access to development tools and documetation |
| PER-7 | Frank | Municipality of Turin employee | Administrative staff responsible for ensuring policies are applied | Proper handling of urban issues | Limited technical skills | PC workstation | User-friendly GUI and tutorials |
---


# 5) User Stories


| ID    | Persona/Role | User story (As a… I want… so that…) |
|:------|:-------------|:------------------------------------|
| US-1 | Visitor citizen | As a visitor citizen, I want to create an account on Participium so that I can access the platform |
| US-2 | Registered citizen | As a registered citizen, I want to update my account on Participium |
| US-3 | Registered citizen | As a registered citizen, I want to be able to submit a new report on the platform with all the details I consider useful such as photos, location and category |
| US-4 | Registered citizen | As a registered citizen, I want to be able to submit my reports with anonymity option |
| US-5 | Visitor citizen | As a citizen, I want to check the reports in my city and their status so that I can be informed about issues in my area |
| US-6 | Registered citizen | As a registered citizen, I want to follow/unfollow the reports in my city and their status so that I can be informed about their status changes |
| US-7 | Visitor citizen | As a citizen, I want to find reports based on category filters and sorts the results. |
| US-8 | Visitor citizen | As a citizen, I want to find reports by using the map or the table view |
| US-9 | Visitor citizen | As a citizen, I want to export the table view in a CSV format |
| US-10 | Registered citizen | As a citizen, I want to receive notifications when report status changes. |
| US-11 | Registered citizen | As a citizen, I want to receive notifications about messages from municipality officers |
| US-12 | Registered citizen | As a citizen, I want to receive emails about report status changes of already published ones |
| US-13 | Registered  citizen | As a citizen, I want to receive emails about messages from municipality officers |
| US-14 | Visitor citizen | As a citizen, I want to check public statistics |
| US-15 | Registered citizen | As a citizen, I want to communicate with municipality officers |
| US-16 | Municipal officer | As a municipal officer, I want to access the platform with special permissions on reports |
| US-17 | Municipal officer | As a municipal officer, I want to check reports and be able to update their status. |
| US-18 | Municipal officer | As a municipal officer, I want to communicate with citizens and urban service providers |
| US-19 | System administrator | As a system administrator, I want to guarantee the security on user data |
| US-20 | System administrator | As a system administrator, I want to access the platform with special permissions on reports |
| US-21 | System administrator | As a system administrator, I want to access private statistics so that I can monitor system usage and report trends |
| US-22 | Development team | As a development team member, I want to implement new features according to requirements so that the system meets user needs |
| US-23 | Development team | As a development team member, I want to maintain and update the codebase to improve maintainability and scalability |
| US-24 | Municipality of Turin | As a municipality of Turin member, I want to track the effectiveness of the platform so that I can be sure it is useful for the citizens |
| US-25 | Visitor citizen | As a visitor citizen, I want to login to my existing account.



---






# 6) Functional Requirements (FR)


| ID    | Requirement statement (The system shall…) | Priority | User story ID | Notes |
|:------|:------------------------------------------|:---------|:--------------|:------|
| FR-1 | The system shall provide means to create and manage user accounts | Critical | US-1 | Covers user account lifecycle (registration, profile management, and authentication). | 
| FR-1.1 | The system shall allow users to define and update basic profile information (username, first name, last name)| Important | US-2 | Supports personalization of users within the system. |
| FR-1.2 | The system shall verify user email through a verification link. | Important | US-1 | Required to ensure account validity and prevent misuse or fake accounts. |
| FR-1.3 | The system shall allow registered users to optionally add a profile picture to their account. | Important | US-2 | Optional feature enhancing user profile personalization. |
| FR-2 | The system shall allow visitors (un-registered users) to login to an existing account. | Critical | US-24 | Authentication is required to access protected functionalities (precondition for actions such as report creation and following). |
| FR-3 | The system shall allow registered users to create a new report. | Critical | US-3 | Core functionality of the system; central domain object is the Report. |
| FR-3.1 | The system shall allow registered users to select a geographic location on a map for a report. | Important | US-3 | Uses external map services (OpenStreetMap) for geolocation. |
| FR-3.2 | The system shall allow registered users to add a title and a textual description to a report | Critical | US-3 | Mandatory fields required for report understanding and processing. |
| FR-3.3 | The system shall allow registered users to upload up to 3 photos per report. | Important | US-3 | Limited number of images to control storage and performance.  |
| FR-3.4 | The system shall allow users to select a category for a report from a predefined set. | Critical | US-3 | Ensures classification and routing of reports. |
| FR-3.5 | The system shall allow registered users to submit reports anonymously. |  | US-3/US-4 | Supports user privacy while maintaining report visibility. |
| FR-4 | The system shall provide means to search for reports | Critical | US-5 |  High-level requirement grouping report discovery functionalities.|
| FR-4.1 | The system shall allow user to search for reports based on category filters. | US-7 | Critical | Enables filtering to refine report search results. |
| FR-4.2 | The system shall allow users to sort report results based on selected criteria (date, category, status, ascending/descending...). | Important | US-7 | Improves usability by allowing users to organize results. |
| FR-4.3 | The system shall allow user to search for reports by using table and/or map view | Critical | US-8 | Supports both map-based and table-based exploration of reports. |
| FR-5 | The system shall notify users | Critical | US-10/US-11 | Refers to system-generated updates related to report lifecycle and interactions.|   
| FR-5.1 | The system shall support in-platform notifications for the reporting citizen and for who follows the report. | Important | US-10 | Default notification mechanism for users interacting with reports. |
| FR-5.2 | The system shall (optionally) send email notifications to registered users. | Important | US-12/US-13 | Optional communication channel based on user preferences. |
| FR-5.3 | The system shall allow direct messaging between users and municipal operators. | Critical | US-11 | Enables two-way communication between citizens and municipal operators. |
| FR-6 | The system shall allow users to export the table view in a CSV format | Important | US-9 | Supports transparency and external analysis of public data. |
| FR-7 | The system shall provide public statistics to all users.| Important | US-14 | Provides aggregated public insights into report data. |
| FR-7.1 | The system shall provide advanced (private) statistics for administrators. | Important | US-21 |Restricted access to advanced analytics for administrative purposes. |
| FR-8 | The system shall display reports | Critical | US-5/US-6 | Core visualization capability of the system. |
| FR-8.1 | The system shall display the complete content of each report in its detailed view (title, description, category, location, attached photos...). | Represents the report detail view as described in the baseline.| US-5| |
| FR-8.2 | The system shall allow registered users to start following a report (including reports submitted by others). | Important | US-6 |Enables user engagement and tracking of report evolution. |
| FR-8.3 | The system shall allow registered users to stop following a report. | Important | US-6 |Completes the follow functionality (user control over subscriptions). |
| FR-9 | The system shall provide means to municipal officers to login with special permissions on reports | Critical | US-16 | Role-based access with elevated permissions for municipal officers. |
| FR-9.1 | The system shall allow municipal officers to check reports and be able to change their status. | Critical | US-17 | Supports report lifecycle management (status updates). |
| FR-9.2 | The system shall allow municipal officers to communicate with citizens and urban service providers via platform messages | Critical | US-18 | Extends communication capabilities to include operational actors. |
| FR-10 | The system shall allow system administrator to login with special permissions on configuration aspects and extended analytics | Critical | US-20 | Role-based access with elevated permission for municipal officers |

---


# 7) Non-Functional Requirements (NFR)


| ID     | Category | Requirement statement | Metric / Target | Verification                           | Priority | Notes |
|:-------|:---------|:----------------------|:----------------|:---------------------------------------|:---------|:------|
| NFR-1 | Efficiency | The system shall load the map view efficiently | ≤ 2 seconds (95% of requests) | Performance testing | High | Depends on network latency |
| NFR-2 | Efficiency | The system shall display report details promptly. | ≤ 1 second | Performance testing | High | After user selection  |
| NFR-3 | Efficiency | The system shall load the table view efficiently | ≤ 2 seconds for up to 1000 reports | Load testing | High | Includes filtering and sorting |
| NFR-4 | Efficiency | The system shall return search results quickly. | Performance testing | ≤ 2 seconds | High | applies to all filters |
| NFR-5 | Efficiency | The system shall process and confirm report submission efficiently | ≤ 5 seconds | Performance testing | Medium  | Excluding image uploading |
| NFR-6 | Efficiency | The system shall generate and download CSV files | ≤ 1 second | Performance testing | Medium |  |
| NFR-7 | Efficiency | The system shall deliver notifications/emails in real-time | ≤ 1 second (in-app) and ≤ 30 seconds (emails) | Monitoring | High | Email delay depends on provider |
| NFR-8 | Efficiency | The system shall process report submissions efficiently | ≤ 2 seconds | Performance testing | High | |
| NFR-9 | Maintainability | The system shall allow new evolutive features to be integrated quickly | Within 1 month of development | Code developing | High |  |
| NFR-10 | Maintainability | The system shall allow bug fixing operations | Within 1 month of developing | Code developing | High |  |
| NFR-11 | Maintainability | The system shall be easily testable | Automated testing cover at least 75% of the code | Code testing | Medium |  |
| NFR-12 | Maintainability | The system shall be modular | Code organised in independent components/modules | Code developing | High |  |
| NFR-13 | Usability | A new user must be able to learn how to submit and search a report without consulting external manuals | 90% of the users complete the submission/research within 5 minutes | User acceptance testing | High |  |
| NFR-14 | Usability | The system should provide an interface accessible to users with visual or motor impairments | Following standard guidelines | User acceptance testing | High |  |
| NFR-15 | Usability | The system must prevent the submission of incomplete reports through clear feedbacks | Implement pop-up | Functional testing | Medium |  |
| NFR-16 | Portability | The system must be compatible with the major web browsers (Chrome, Firefox, Safari) | Last 3 stable versions | Portability testing | High |  |
| NFR-17 | Reliability | The system shall support a reasonable number of registered users | at least 500,000 | Capability testing | High |  |
| NFR-18 | Reliability | The system shall support a reasonable number of concurrent users | at least 2,000 | Stress testing | High |  |
| NFR-19 | Reliability | The system must provide a stable up-time period over the year |  ≥ 99% of the time | Stress testing | High |  |
| NFR-20 | Security | The system must use encryption for user data | The encryption should not be too computationally expensive. | Security test | High |  |
| NFR-21 | Security | The system should inform users about an eventual data breach in a reasonable time | Send a notification within 5 minutes | Security test | High | |


