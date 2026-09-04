# Trackofy v6 — Administrator Module Explanation

## 1. Module Overview

The **Administrator** module is Trackofy's sub-user management and access-control module. Its primary purpose is to let an administrator create sub-users and control exactly what those users can access and operate.

The module manages four major authorization layers:

1. **User credentials and special command access**
2. **Menu access through Menu Groups**
3. **General/application permissions**
4. **Unit/vehicle permissions**

It also provides lifecycle operations for existing users: **view permissions, edit, and delete**.

> **QA perspective:** This is not merely a CRUD module. It is an authorization-control module. A permission should be considered correctly implemented only when the resulting sub-user can perform what was granted and cannot perform what was denied.

---

## 2. User Management Page

The Administrator landing page is **User Management**. It lists configured sub-users in a tabular format.

The visible columns/actions include:

| Field | Purpose |
|---|---|
| Sr No | Sequential record number |
| User Name | Sub-user login identifier |
| Password | Password representation/control |
| Status | Current user state, e.g. Active |
| Created At | User creation date |
| Permissions | Manage/view permission configuration |
| Edit | Modify user configuration |
| Delete | Remove the selected user |

The page also provides:

- **Add User** button
- Rows-per-page selector
- Pagination controls
- Matching-record count
- User search
- Export/action controls

### Row-level actions

Each user has three important actions:

- **Permissions** — manage the user's access configuration.
- **Edit** — modify the existing user configuration.
- **Delete** — remove the sub-user.

---

# 3. Create User — Four-Step Wizard

Selecting **Add User** opens the **Create User** wizard.

The wizard contains four stages:

```text
Step 1 → Personal Info
Step 2 → Menu Access
Step 3 → General Permission
Step 4 → Unit Permission
```

The wizard includes progress indication and navigation controls such as **Next Step**, **Back**, **Cancel**, and finally **Submit**.

A user should be considered created only after the final submission succeeds.

---

# 4. Step 1 — Personal Info

The first step configures the sub-user's basic credentials, selected vehicles and Arm/Disarm capability.

The screen contains:

- Vehicles selector
- User Name*
- Password*
- Confirm Password*
- Arm/Disarm Command — **Yes / No**

## 4.1 Vehicle Selection

The administrator can select vehicles for the new sub-user.

The selected vehicles establish the user's vehicle scope for the configuration.

### Important checks

- Vehicle selector opens correctly.
- Available vehicles are displayed.
- Vehicle can be selected.
- Multiple vehicles can be selected if supported.
- Selected vehicles remain selected when moving between wizard steps.
- Removing a selected vehicle works correctly.
- Vehicle selections are not silently reset.

## 4.2 Username

Username is mandatory.

Test:

- Empty value
- Valid value
- Duplicate username
- Leading/trailing spaces
- Minimum/maximum length
- Special characters
- Case handling
- Existing username collision
- Username retention during wizard navigation

## 4.3 Password

Password is mandatory and should follow the application's configured password rules.

Test:

- Empty password
- Valid password
- Weak password
- Minimum/maximum length
- Special characters
- Numeric characters
- Upper/lowercase characters
- Masking
- Password retention while navigating the wizard

## 4.4 Confirm Password

Confirm Password must match Password.

Expected behaviour:

- Matching passwords are accepted.
- Mismatched passwords are rejected.
- Empty confirmation is rejected.
- Changing Password invalidates an old confirmation value.
- Validation feedback is clear.

## 4.5 Arm/Disarm Command

The first step contains an **Arm/Disarm Command** setting with **Yes** and **No** options.

The description indicates that this controls whether the user can view/use Arm and Disarm controls.

Because Arm/Disarm is a vehicle-control capability, it is a **critical authorization item**.

It should be tested at two levels:

### Configuration level

- Yes can be selected.
- No can be selected.
- Selected value is retained.
- Saved value is visible when the user is edited.

### Effective authorization level

Login as the created sub-user and verify:

- Arm/Disarm controls are available when permitted.
- Controls are unavailable when permission is denied.
- Unauthorized commands cannot be executed through direct API/request manipulation.

---

# 5. Step 2 — Menu Access

The second step controls the user's **Menu Group**.

The screen has two primary areas:

### Available Groups

Existing groups are listed on the left. The supplied screen shows examples such as:

- 5 feb
- 6 Feb
- AppTesting
- example21
- Full control
- sales

The actual group list is data-dependent.

### Selected Menu Group

When a group is selected, its configuration is displayed on the right, including:

- Group name
- Number of menus
- Assigned menus
- Child menus where applicable

For example, the supplied screen shows a group containing:

```text
Home
Dashboard
    └── Tabular
```

This demonstrates that a Menu Group is a predefined collection of application menus.

---

# 6. Existing Group vs New Group

The Menu Access step provides two approaches.

## Option A — Existing Group

The administrator can select an already-created Menu Group.

The selected group provides the menu structure assigned to the sub-user.

Verify:

1. Correct group can be selected.
2. Selected group is visually identified.
3. Its menus are displayed.
4. Child menus are displayed correctly.
5. The intended group is retained during navigation.
6. No unrelated group is accidentally assigned.

## Option B — Create New Group

The **Add Group** control allows creation of a new Menu Group.

The supplied screenshots do not show the internal fields of the Add Group form, so those fields should not be assumed here. Once available, they should be documented and tested separately.

At minimum, a newly created group should be verified to:

- Save successfully.
- Appear in Available Groups.
- Contain its configured menus.
- Be selectable for a sub-user.
- Expose only its intended menus.

---

# 7. Menu Group Authorization Model

Menu access is the first major authorization layer.

Conceptually:

```text
Sub User
   |
   +-- Menu Group
          |
          +-- Home
          +-- Dashboard
          +-- Unit
          +-- Tracking
          +-- Reports
          +-- Other assigned modules
```

The actual modules depend on the selected group.

### Important security rule

A hidden menu must not automatically mean secure authorization.

If a user does not have access to Reports, for example, testing should verify all relevant layers:

```text
Reports menu hidden
        +
Direct Reports navigation blocked
        +
Reports API/action unauthorized
```

---

# 8. Step 3 — General Permission

The third step provides granular **application-level permissions**.

The supplied screen shows these permission categories:

- Driver
- Driver Management
- Route Management
- User
- Sensor Configuration
- Alert Configuration
- Vehicle Group
- Video Telematics

Each category displays the number of available permissions and can be expanded/collapsed.

Example structure:

```text
Driver
   ├── Permission 1
   ├── Permission 2
   └── Permission 3
```

The exact individual permissions are configuration-dependent.

---

# 9. General Permission Behaviour

Testing should cover:

- Expand category.
- Collapse category.
- Select individual permission.
- Unselect individual permission.
- Verify checkbox state.
- Verify permission count/state.
- Select permissions across multiple categories.
- Navigate backward and forward.
- Confirm selections persist.
- Save the configuration.
- Verify the permissions from the sub-user account.

The key validation is not whether the checkbox can be selected; it is whether the corresponding functionality is actually authorized for the sub-user.

---

# 10. General Permission Categories

## Driver

Controls configured Driver-related functionality.

Verify granted and revoked permissions independently.

## Driver Management

Controls Driver Management functionality.

Verify that a sub-user without the required permission cannot perform restricted Driver Management operations.

## Route Management

Controls route-related functionality.

Test both menu visibility and operation-level authorization.

## User

Controls user-related operations.

This category deserves additional security attention because user-management permissions can potentially expose or modify other user accounts.

## Sensor Configuration

Controls sensor configuration capabilities.

Verify unauthorized users cannot perform restricted configuration operations.

## Alert Configuration

Controls alert configuration capabilities.

Test both access visibility and actual operation authorization.

## Vehicle Group

Controls vehicle-group functionality.

Verify that the user cannot access or modify functionality beyond the granted permission.

## Video Telematics

Controls Video Telematics functionality.

Verify that the required menu and permission configuration both produce the intended access.

---

# 11. Step 4 — Unit Permission

The fourth step controls **unit/vehicle-level permissions**.

The supplied screen contains:

### Select Units

A vehicle/unit selector used to choose one or more units.

### Available Permissions

Permissions applicable to the selected units are displayed.

The supplied screen shows a **Unit** category containing:

- Change Advanced Settings
- Change Icon
- Manage Services

The exact available permissions may depend on the application configuration.

---

# 12. Unit Permission Model

Unit permissions can be understood as:

```text
Sub User
   |
   +-- Unit Scope
          |
          +-- Vehicle A
          |     ├── Change Advanced Settings
          |     ├── Change Icon
          |     └── Manage Services
          |
          +-- Vehicle B
                ├── Change Advanced Settings
                ├── Change Icon
                └── Manage Services
```

The important distinction is that **unit scope** and **unit permission** are separate concepts.

A user may have a permission but still not be allowed to perform it on a vehicle that is outside their assigned unit scope.

---

# 13. Unit Selection

Test:

- Open unit selector.
- Verify available units.
- Select one unit.
- Select multiple units if supported.
- Change selected units.
- Remove a unit.
- Verify permissions update for the selected units.
- Verify selections survive navigation.
- Verify selections are retained before Submit.

### Critical security scenario

If a sub-user is assigned Vehicle A but not Vehicle B, the user must not gain access to Vehicle B merely because Vehicle B exists in the administrator's account.

---

# 14. Unit-Level Permissions

For example:

```text
Vehicle A
[✓] Change Advanced Settings
[ ] Change Icon
[✓] Manage Services
```

The expected effective access would be:

- Change Advanced Settings → allowed for Vehicle A.
- Change Icon → denied for Vehicle A.
- Manage Services → allowed for Vehicle A.

The same permission must not automatically become available for unassigned vehicles.

---

# 15. Final Submit

The final wizard step contains **Submit**.

A successful submission should result in a consistent user configuration containing:

1. Credentials.
2. Selected vehicles.
3. Arm/Disarm setting.
4. Menu Group.
5. General permissions.
6. Unit assignments.
7. Unit permissions.

The newly created user should then appear in User Management.

---

# 16. Existing User — Edit

The **Edit** action modifies an existing sub-user.

Editing should preserve existing configuration unless the administrator explicitly changes it.

Test changes to:

- Password.
- Vehicle assignment.
- Arm/Disarm permission.
- Menu Group.
- General permissions.
- Unit permissions.

### High-value edit test

Create a user with:

```text
Reports       = Allowed
Tracking      = Allowed
Vehicle A     = Allowed
Vehicle B     = Not Allowed
Arm/Disarm    = No
```

Edit it to:

```text
Reports       = Removed
Tracking      = Allowed
Vehicle A     = Allowed
Vehicle B     = Allowed
Arm/Disarm    = Yes
```

After saving, verify that the sub-user receives the new configuration and that removed permissions are genuinely revoked.

---

# 17. Existing User — Permissions Action

The **Permissions** action on a user row provides access to that user's authorization configuration.

Verify:

- Correct user is loaded.
- Existing menu group is correct.
- Existing general permissions are correct.
- Existing unit assignments are correct.
- Existing unit permissions are correct.
- Changes can be saved.
- Cancel does not modify configuration.
- Changes affect only the selected user.

---

# 18. Delete User

The **Delete** action is destructive and should be tested carefully.

Verify:

- Correct user is targeted.
- Confirmation is shown where implemented.
- Cancel prevents deletion.
- Confirm deletes only the selected user.
- Deleted user disappears from the list.
- Deleted credentials cannot authenticate.
- Previous permissions cannot still be used.
- Other users remain unaffected.
- Backend authorization also enforces deletion rules.

---

# 19. User Search

The User Management page provides a user search field.

Test:

- Exact username.
- Partial username.
- Case variations.
- Non-existent username.
- Special characters.
- Leading/trailing spaces.
- Rapidly changing search values.
- Clearing search.

Search must not alter user data or expose users outside the administrator's authorized scope.

---

# 20. Pagination and Rows Per Page

The User Management table supports rows-per-page selection and pagination.

Test:

- Default row count.
- Change rows per page.
- First page.
- Next page.
- Previous page.
- Last page.
- Single-page dataset.
- Multi-page dataset.
- Pagination after searching.
- Pagination after creating a user.
- Pagination after deleting a user.

Verify records are neither duplicated nor skipped.

---

# 21. Wizard Navigation and State Preservation

The wizard must preserve configuration while navigating:

```text
Step 1 → Step 2 → Step 3 → Step 4
```

and:

```text
Step 4 → Step 3 → Step 2 → Step 1
```

Verify that:

- Username remains intact.
- Password state behaves correctly.
- Selected vehicles remain intact.
- Arm/Disarm selection remains intact.
- Selected Menu Group remains intact.
- General permissions remain selected.
- Unit selections remain selected.
- Unit permissions remain selected.
- Back does not unexpectedly reset state.
- Cancel does not create a partial user.
- Closing the wizard does not create a partial user.

---

# 22. Authorization Model

Administrator authorization should be tested as multiple independent layers.

| Layer | Example | Purpose |
|---|---|---|
| Menu Access | Reports | Controls module/menu visibility |
| General Permission | Operation permission | Controls application-level capability |
| Unit Scope | Vehicle A | Controls which vehicles are in scope |
| Unit Permission | Manage Services | Controls what can be done to a unit |
| Special Command | Arm/Disarm | Controls vehicle-control command capability |

These layers should be tested individually and in combination.

---

# 23. Critical Permission Combinations

## Menu allowed, operation denied

```text
Menu = Allowed
Permission = Denied
```

Expected: The user must not perform the restricted operation.

## Permission allowed, menu denied

```text
Menu = Denied
Permission = Allowed
```

Expected: Direct navigation must not bypass the missing menu access.

## Unit permission allowed, unit not assigned

```text
Manage Services = Allowed
Vehicle B = Not Assigned
```

Expected: Vehicle B must remain inaccessible for that operation.

## Unit assigned, permission denied

```text
Vehicle A = Assigned
Manage Services = Denied
```

Expected: Assignment alone must not grant Manage Services.

## Arm/Disarm denied

```text
Arm/Disarm = No
```

Expected: The sub-user cannot execute Arm/Disarm.

## Fully authorized scenario

```text
Menu Access        = Allowed
General Permission = Allowed
Unit Assigned      = Yes
Unit Permission    = Allowed
Arm/Disarm         = Yes
```

Expected: The user can perform the configured functionality for the configured units.

---

# 24. Security Testing Priorities

Because this module controls access to other Trackofy modules and vehicle operations, security testing should include:

### Horizontal privilege escalation

User A must not access or modify User B's:

- Permissions
- Units
- Credentials
- Configuration

### Vertical privilege escalation

A sub-user must not obtain administrator-level access by manipulating:

- URLs
- Client-side state
- Browser storage
- Request payloads
- API parameters
- Hidden UI controls

### Direct URL access

If Reports is not assigned, verify that a sub-user cannot simply enter the Reports URL manually.

### API authorization

The backend should independently validate:

- Identity
- Menu access
- General permission
- Unit scope
- Unit permission
- Arm/Disarm authorization

Client-side checkbox state must never be the sole authorization mechanism.

---

# 25. Reliability and Failure Testing

Important scenarios include:

- Create User API failure.
- Menu Group API failure.
- Permission API failure.
- Unit assignment API failure.
- Network interruption.
- Session expiry during wizard.
- Browser refresh during wizard.
- Double-click Next Step.
- Double-click Submit.
- Stale API responses.
- Concurrent administrator edits.
- User deleted by another administrator while being edited.
- Permission changes by another administrator while a stale edit screen is open.

The application must not display a false success state when the server operation failed.

---

# 26. Data Consistency

After creating a user, verify the complete configuration end-to-end.

Example:

```text
Username:
    subuser01

Arm/Disarm:
    Yes

Menu Group:
    Operations

General Permissions:
    Tracking
    Reports
    Driver

Units:
    Vehicle A
    Vehicle B

Unit Permissions:
    Vehicle A → Change Icon
    Vehicle A → Manage Services
    Vehicle B → Change Advanced Settings
```

The administrator view should show the saved configuration correctly.

Then login as the sub-user and verify **effective access**.

---

# 27. Recommended End-to-End QA Flow

## Phase 1 — Create

Create a sub-user with:

- Selected vehicles.
- Username/password.
- Arm/Disarm = No.
- Existing Menu Group.
- Selected General Permissions.
- Selected Unit Permissions.

## Phase 2 — Administrator Verification

Verify the user appears in User Management.

Open:

- Permissions
- Edit

Confirm the saved configuration.

## Phase 3 — Sub-user Verification

Login using the new sub-user.

Verify:

- Correct menus are visible.
- Unauthorized menus are unavailable.
- Correct vehicles are visible.
- Unauthorized vehicles are unavailable.
- General permissions work.
- Unit permissions work.
- Arm/Disarm is unavailable when denied.

## Phase 4 — Modify

Edit the user and change selected permissions, units and/or Arm/Disarm configuration.

## Phase 5 — Re-verify

Login again and confirm:

- Newly granted access works.
- Removed access no longer works.
- Unit restrictions remain correct.
- Old permissions are not retained accidentally.

## Phase 6 — Delete

Delete the sub-user and verify:

- User disappears.
- Login fails.
- Previous access is no longer available.

---

# 28. Risk Classification

| Area | Risk |
|---|---|
| User creation | High |
| Password handling | Critical |
| Arm/Disarm | Critical |
| Menu Access | Critical |
| General Permissions | Critical |
| Unit Assignment | Critical |
| Unit Permissions | Critical |
| Permission Editing | Critical |
| Delete User | High |
| Search | Medium |
| Pagination | Low/Medium |
| UI/Layout | Medium |
| API failure handling | High |
| Direct URL authorization | Critical |
| API authorization | Critical |
| Privilege escalation | Critical |

---

# 29. Automation Candidates

The highest-value automated scenarios are:

1. Create sub-user.
2. Validate mandatory fields.
3. Validate duplicate username.
4. Validate password confirmation.
5. Select existing Menu Group.
6. Configure General Permissions.
7. Configure Unit Permissions.
8. Configure Arm/Disarm.
9. Submit user.
10. Verify user in User Management.
11. Edit user permissions.
12. Verify permission changes.
13. Delete user.
14. Login as created sub-user.
15. Verify menu visibility.
16. Verify vehicle/unit visibility.
17. Verify restricted module access.
18. Verify unit-level authorization.
19. Verify Arm/Disarm authorization.
20. Verify direct URL/API authorization.

These provide considerably more coverage than merely automating checkbox clicks.

---

# 30. Final Summary

The **Administrator module is Trackofy's central sub-user access-control layer**.

Its four-step wizard separates configuration into:

```text
Step 1 — Personal Info
        Credentials + Vehicles + Arm/Disarm
                    ↓
Step 2 — Menu Access
        Application Menu Group
                    ↓
Step 3 — General Permission
        Application-Level Operations
                    ↓
Step 4 — Unit Permission
        Vehicle Scope + Unit-Level Operations
```

The resulting configuration determines both **what a sub-user can access** and **what actions the user can perform on specific units**.

The most important QA principle is:

> **Do not consider an authorization feature tested merely because its checkbox saves successfully. The real test is whether the resulting sub-user can perform exactly what was granted — and nothing that was not granted.**

This makes Administrator one of the highest-risk modules in Trackofy and a major candidate for functional, authorization, security, API and end-to-end testing.
