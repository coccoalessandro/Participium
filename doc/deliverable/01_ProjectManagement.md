# Product Breakdown Structure (PBS)

| ID | Deliverable | Type  | Notes |
|:---|:------------|:--------------------------------------------------|:------|
| S1 | Account management service | Software | |
| S2 | Report management service | Software | |
| S3 | Interaction with the municipality service | Software | |
| S4 | Administration role management | Software | |
| S5 | Mapping service | Software | |
| S6 | Notification and communication service | Software | |
| S7 | Statistics service | Software | |
| S8 | public consultation service | Software | | 
| S9 | Web client | Software | |
| I1 | City map data | Infrastructure | |
| I2 | Storage (reports) | Infrastructure | |
| I3 | Relational DB (Account, notification, Reports, Messaging) | Infrastructure | |
| I4 | Backup and disaster recovery | Infrastructure | | 
| D1 | Requirements document | Documentation | |
| D2 | Architecture and design document | Documentation | |
| D3 | Test documentation (Test plan, test report)| Documentation | |
| D4 | User manual and documentation | Documentation | |
| D5 | API documentation | Documentation | |
| D6 | Open source license | Documentation | |

---

# Work Breakdown Structure (WBS)

### WBS with traceability to PBS
| ID  | Work package | Subtask |  Traced PBS outputs (IDs) |
|:----|:-------------|:--------------------------|:----------|
| T1.1 | Requirements | Definition of functional requirements | D1 |
| T1.2 | Requirements | Definition of non functional requirements | D1 |
| T2.1 | Design and architecture | Architecture definition |  D2  |
| T2.2 | Design and architecture | Definition of storage architecture | D1 |
| T3.1 | Development | Development of APIs and backend skeleton | I1, I2, I3, I4, S1, S2, S3, S4, S5, S6, S7, S8 |
| T3.2 | Development | Development of backend | I1, I2, I3, I4, S1, S2, S3, S4, S5, S6, S7, S8 |
| T3.3 | Development | Development of web app frontend | S9 |
| T4.1 | Verification and validation | Definition of test plan | D3 |
| T4.2 | Verification and validation | Acceptance testing with the user | D3 |
| T5.1 | Deployment and go-live | Deployment of the system | D4, D5, D6 |
| T5.2 | Deployment and go-live | Monitoring and bug fixing | D4, D5, D6 |








---

# Gantt, dependencies, and critical path

## Activity table
| ID | Activity | Duration | Dependencies | Start | End | Critical | Milestone |
|:---|:---------|:---------|:-------------|:------|:----|:------|:---------|
| R# |          |          |              |       |     |       |          |


## Critical path
`X → X → X → ...`



---

# Risk Management

**Scales and thresholds**
- **Probability (P)**: 1 (rare) … 5 (almost certain)
- **Impact (I)**: 1 (minor) … 5 (critical)
- **Exposure**: `P × I` (range 1–25)

Risk level thresholds (by exposure):
- **Low**: 1–5
- **Medium**: 6–10
- **High**: 11–16
- **Very High**: >16



## Risks table
| ID | Risk | Category | P | I | P×I | Level | Mitigation / Response strategy |
|:---|:-----|:---------|--:|--:|----:|:------|:-------------------------------|
|  |      |          |   |   |     |       |                                |


