# Trackofy v6 — Miscellaneous Pages & Account Utilities

## 1. Purpose

This document explains the miscellaneous/support/account utilities visible around the Trackofy v6 application shell. These features are not part of the primary operational modules such as Home, Dashboard, Unit, Tracking, Reports, Settings, Administrator, or Video Telematics, but they are important because they control the user's account, exported files, support communication, localization, appearance, session lifecycle, help resources, and product feedback.

The analyzed UI contains the following areas:

1. **Account menu**
   - My Profile
   - Downloads
   - Support
   - Change Password
   - Appearance
   - Language
   - Sign Out
2. **My Profile**
   - Profile identity/details
   - Profile completion indicator
   - Account usage/limits
   - Personal & Preferences
   - Billing Information
   - Change Password entry point
3. **Downloads**
   - Generated report/file history
   - Report name
   - Requested date/time
   - Duration/date range
   - Status
   - Download action
   - Search and pagination
4. **Support**
   - Support ticket listing
   - Ticket number
   - Description
   - Raised On
   - Priority
   - Status
   - Attachment indicator
   - History/view action
   - Raise Ticket
5. **Raise Support Ticket**
   - Unit selection
   - Category
   - Severity
   - Comment
   - Contact information
   - Submit Ticket
6. **Change Password**
   - Current-password verification
   - New password
   - Confirm new password
   - Password-rule indicators
   - Password visibility controls
   - Update Password
7. **Appearance**
   - Switch between light and dark mode
8. **Language**
   - Language preference using Google Translate
9. **Sign Out**
   - Terminates the current authenticated session
10. **Help Center**
    - Documentation overview
    - Search
    - Quick links
    - Popular sections
    - Common issues
    - Getting Started
    - Troubleshooting
    - Support-help entry point
11. **Feedback**
    - Feedback prompt
    - New/Old/Not sure version preference
    - New-version UX rating
    - Positive improvement tags
    - Negative/missing-feature tags
    - Optional suggestions
    - Optional attachment
    - Mobile and Email fields
    - Cancel/Submit

---

# 2. Global Account Menu

The account control is located in the top navigation bar. Opening it displays an **Account** panel with the subtitle **Profile & preferences**.

The menu provides direct access to:

| Option | Purpose |
|---|---|
| My Profile | View/update account information |
| Downloads | Access generated report files |
| Support | Track and raise support requests |
| Change Password | Change the authenticated user's password |
| Appearance | Switch between light and dark UI |
| Language | Change language preference |
| Sign Out | End the current session |

### Functional expectations

- The menu should open and close reliably.
- Every menu item should route to the correct destination.
- Closing/reopening the menu should not change account state.
- Navigation should preserve authentication where appropriate.
- Restricted features must remain protected by authorization.
- The menu should remain usable across supported resolutions and themes.

---

# 3. My Profile

## 3.1 Overview

The Profile & Account page exposes the user's account identity and account-level information.

The observed page contains:

- Profile picture
- User name
- Account-holder indicator
- Email
- Mobile number
- Profile completion percentage
- Account usage
- Personal & Preferences
- Billing Information
- Change Password action

## 3.2 Profile Completion

The page displays a visual completion indicator. In the analyzed screen it shows **100% complete**.

The indicator should accurately reflect the underlying profile completeness and should update when profile information is changed.

## 3.3 Account Usage

The account usage area displays current consumption and remaining limits. The analyzed UI includes:

- Devices
- SMS
- Sub Users
- Email

Each card displays a limit/remaining value and usage progress.

### Important testing points

- Remaining values must match backend/account data.
- Usage must never exceed the configured limit without an explicitly supported overage state.
- Progress indicators must represent the actual usage.
- Changes in account resources should update the displayed values.
- The page must handle zero, full, and near-limit usage correctly.

## 3.4 Personal & Preferences

Observed fields include:

- Name
- Mobile
- Email
- WhatsApp
- Timezone
- Language
- Currency
- Address

The displayed values should match the user's account configuration.

## 3.5 Billing Information

Observed billing information includes:

- Company
- Address
- Billing Cycle
- Payment Type
- TIN/GST No

These values are account-specific and should not be exposed to unauthorized users.

---

# 4. Downloads

## 4.1 Purpose

Downloads provides access to generated report files. It is especially important for asynchronous report generation because a report request may complete later rather than immediately.

The analyzed page shows:

- Download count
- Rows-per-page selector
- Pagination
- Search downloads
- Report Name
- Requested On
- Duration
- Status
- Download action

## 4.2 Report Status

The observed records include statuses such as:

- **Done**
- **Pending**

### Done

A completed file should expose a working download action.

### Pending

A report that is still being generated should not provide a misleading download action. The UI should clearly indicate that processing is incomplete.

## 4.3 Download integrity

Testing should verify:

- The downloaded file corresponds to the correct report.
- The file is not another user's report.
- The generated file is not corrupt.
- The file format matches the requested export format.
- The downloaded report contains the expected date range and filters.
- Repeated downloads do not unexpectedly alter the source record.

## 4.4 Search and pagination

Search should work against the available download metadata and pagination should correctly reflect the filtered result set.

Edge cases include:

- No downloads
- One download
- More than one page
- Search with no match
- Search after changing page size
- Search after a new report becomes available
- Pending-to-Done status transition

---

# 5. Support

## 5.1 Support Management

The Support Management page is the user's ticket-management area.

The analyzed UI displays:

- Ticket count
- Raise Ticket button
- Rows-per-page selector
- Pagination
- Search tickets
- Ticket Number
- Description
- Raised On
- Priority
- Status
- Attachment indicator
- History/view action

## 5.2 Ticket listing

Each ticket should remain associated with the correct account and should display the correct:

- Ticket identifier
- Issue description
- Creation timestamp
- Priority
- Status
- Attachment information
- History

The user should not be able to see another account's tickets.

## 5.3 Search

The ticket search should support normal ticket discovery and should return a clean empty state when there are no matches.

## 5.4 Ticket history/view

The history/view action should expose the correct ticket's information and communication/history trail.

Testing should verify that opening one ticket never displays another ticket's details.

---

# 6. Raise Support Ticket

The **Raise Support Ticket** dialog is a structured form.

## 6.1 Unit Selection

The form starts with a Unit Selection section.

Observed behavior:

- Select one or more vehicles.
- A selected-count indicator is shown.
- Vehicle selection is optional/required according to the configured business rule.

Testing should verify:

- Vehicle dropdown opens.
- Available units are correctly scoped to the logged-in account.
- Multiple units can be selected where supported.
- Selected count is accurate.
- Removing a unit updates the count.
- Unauthorized units cannot be selected.

## 6.2 Ticket Details

The form contains:

- Select Category*
- Select Severity*
- Comment*

The comment area displays a **0/200** counter in the analyzed UI.

Testing should cover:

- Required validation.
- Maximum length.
- Minimum meaningful input.
- Whitespace-only input.
- Special characters.
- Unicode.
- HTML/script payloads.
- SQL-like payloads.
- Counter accuracy.
- Pasting content.
- New lines.

## 6.3 Contact Information

The observed form contains:

- Email*
- Mobile Number*

The mobile field displays a country-code prefix in the analyzed UI.

Validation should cover:

- Valid email.
- Invalid email.
- Empty email.
- Boundary-length email.
- Valid mobile.
- Invalid mobile.
- Empty mobile.
- Country-code behavior.
- Leading/trailing spaces.

## 6.4 Submission

A valid ticket should be submitted exactly once.

The resulting ticket should:

- Receive a ticket number.
- Appear in Support Management.
- Preserve selected units.
- Preserve category/severity/comment/contact details.
- Have the expected initial status.
- Not be duplicated by repeated clicks.

Network/API failures must not produce false success.

---

# 7. Change Password

The Change Password workflow is security-sensitive.

The analyzed UI contains two logical stages.

## 7.1 Stage 1 — Verify Identity

The user enters:

- Current Password*

and selects **Verify**.

The current password must be verified before the new password can be changed.

### Cases

- Correct current password → verification succeeds.
- Incorrect current password → verification fails.
- Empty current password → required validation.
- Repeated incorrect attempts → application should follow configured rate-limiting/security rules.
- Expired session → operation must not proceed.

## 7.2 Stage 2 — Create New Password

Fields:

- New Password*
- Confirm New Password*

The UI displays password requirements:

- 8+ characters
- Lowercase letter
- Special character
- Uppercase letter
- Number

The exact rule enforcement should be verified against the application's configured password policy.

## 7.3 Password rules

Testing must verify each rule independently and in combination.

Examples:

- Exactly 8 characters.
- 7 characters.
- Uppercase only.
- Lowercase only.
- Number present.
- Special character present.
- All required categories satisfied.
- Unicode characters.
- Spaces.
- Very long passwords.
- Same password as old password if reuse is prohibited.
- New password equals confirm password.
- New password differs from confirm password.

## 7.4 Password visibility

The eye/visibility controls should:

- Toggle visibility only for the intended field.
- Never expose another password field.
- Preserve the value while toggling.
- Work independently for current/new/confirm fields where applicable.

## 7.5 Successful password change

After successful update:

- The new password should work.
- The old password should no longer work when password replacement is expected.
- The current session should follow the application's intended session policy.
- A success message should be displayed.
- Passwords must never be shown in plaintext in logs, URLs, or UI notifications.

---

# 8. Appearance

The Account menu contains an Appearance option described as switching the interface to dark mode.

The feature is a UI preference rather than an operational data change.

## 8.1 Light → Dark

Verify:

- Theme changes without broken layout.
- Text remains readable.
- Inputs, dialogs, menus, tables and cards adapt.
- Icons remain visible.
- Status badges retain sufficient contrast.
- Modals and overlays use the correct theme.

## 8.2 Dark → Light

The reverse transition must restore the light theme correctly.

## 8.3 Persistence

Verify theme behavior after:

- Page refresh.
- Navigation between modules.
- Browser restart where persistence is supported.
- Sign out/sign in where preference is account-level.
- Opening dialogs after theme change.

---

# 9. Language

The application exposes a Language option in Account preferences. Based on the provided context, language translation is implemented using **Google Translate**.

Testing should therefore treat this as an integration/localization feature.

## 9.1 Language selection

Verify:

- Language control opens correctly.
- Available languages are displayed.
- Selecting a supported language changes translatable UI text.
- The selected language is retained according to the application's persistence model.

## 9.2 Translation coverage

Check:

- Navigation labels.
- Buttons.
- Headings.
- Forms.
- Validation messages.
- Table headers.
- Dialogs.
- Tooltips.
- Empty states.
- Notifications.
- Support content where translation is expected.

## 9.3 Translation quality/integrity

The test objective should not assume every translated phrase is linguistically perfect. Instead verify:

- Text is not clipped.
- Layout does not break due to longer translations.
- No raw translation placeholders appear.
- No untranslated technical tokens unexpectedly replace UI text.
- Dynamic values remain intact.
- Numbers, dates and identifiers are not corrupted.

## 9.4 Language switching regression

Switching languages must not:

- Log the user out.
- Clear filters unexpectedly.
- Lose form data.
- Change account data.
- Break navigation.

---

# 10. Sign Out

Sign Out ends the current authenticated session.

## Expected behavior

After sign out:

- The authenticated session is invalidated according to the application's session design.
- The user is redirected to the login/authentication entry point.
- Protected pages cannot be accessed simply with browser Back.
- Refreshing a previously protected page does not restore authenticated access.
- Session tokens/cookies are not accepted after logout where invalidation is expected.
- Another user can safely sign in from the same browser.

Security testing should also verify logout behavior across multiple tabs and direct URL access.

---

# 11. Help Center

The Help Center is available through the application launcher represented by the **9-dot/grid icon** in the navigation area.

The analyzed Help Center contains:

- Trackofy Help Center heading
- Search articles/guides
- Home
- Contents sidebar
- Overview
- Device
- Sensor
- Quick Links
- Popular Sections
- Common Issues
- Getting Started
- Troubleshooting
- Support Help

## 11.1 Overview

The landing page provides quick access to common operational topics.

Quick links observed include:

- Device Setup
- Sensor Configuration
- Reports
- Alerts
- Video Telematics
- Live Tracking

Popular sections include:

- Live Tracking & Map
- Device & Protocol Help
- Sensors & Parameters
- Reports & Analytics

## 11.2 Search

Search should:

- Accept valid search terms.
- Return relevant articles.
- Handle partial terms.
- Handle no-result queries.
- Handle empty queries.
- Handle special characters.
- Remain usable on long result sets.

## 11.3 Common issues

The Help Center exposes troubleshooting shortcuts such as:

- Vehicle not showing live location
- Report data is missing
- Alert is not triggering
- Sensor value looks incorrect

Each should open the correct help content.

## 11.4 Navigation

The sidebar contains content categories such as Device and Sensor. Navigation should not break browser history or lose the current article unexpectedly.

---

# 12. Feedback Prompt

A small feedback prompt can appear in the application, asking the user to share feedback about the new Trackofy version.

The observed prompt contains:

- "Using New Trackofy?"
- "Share feedback (30 sec) to help us improve."
- Dismiss
- Give Feedback

## Expected behavior

### Dismiss

Dismiss should close the prompt without opening the feedback form.

### Give Feedback

Give Feedback should open the Feedback form.

The prompt must not block core application functionality.

---

# 13. Feedback Form

The feedback model is a separate form/wizard-style dialog.

## 13.1 Version preference

The user can select:

- New
- Old
- Not sure

Exactly one selection should be active if the design intends a single-choice response.

## 13.2 New-version UX rating

The form displays a five-star rating.

Testing should cover:

- 1 star
- 2 stars
- 3 stars
- 4 stars
- 5 stars
- Changing the selected rating
- Reset/initial state

## 13.3 Positive feedback tags

Observed options include:

- Faster loading
- Better UI/UX
- Dashboard improved
- Reports improved
- Tracking improved
- Settings easier

The implementation should define whether multiple selections are permitted. If multi-select is intended, combinations must be tested.

## 13.4 Negative/missing tags

Observed options include:

- Missing features
- Confusing flow
- Slow / lag
- Bugs / errors
- Map issues
- Report mismatch

The same selection-state rules should be verified.

## 13.5 Suggestions

The Suggestions field is optional and shows a **0/250** counter.

Test:

- Empty value.
- One character.
- Exactly 250 characters.
- More than 250 characters.
- Paste >250 characters.
- Unicode.
- Special characters.
- New lines.
- HTML/script payloads.
- SQL-like payloads.

## 13.6 Attachment

The attachment field is optional.

The analyzed UI states:

- PNG
- JPG
- PDF
- Maximum 5 MB

Test:

- Valid PNG.
- Valid JPG.
- Valid PDF.
- File exactly at supported size.
- File over 5 MB.
- Unsupported extension.
- Renamed unsupported file.
- Corrupt file.
- Empty file.
- Multiple files if only one is intended.
- Cancel file selection.
- Remove/replace selected file if supported.

## 13.7 Contact information

Observed fields:

- Mobile
- Email

Verify validation and whether the fields are pre-populated from the account profile.

## 13.8 Submit/Cancel

Cancel should close the form without submitting feedback.

Submit should:

- Validate required information.
- Submit exactly once.
- Display success/failure feedback.
- Prevent duplicate submissions.
- Preserve attachment and selected options.
- Handle server/network failure safely.

---

# 14. Cross-Feature Security Testing

Because these pages expose account information and perform state-changing operations, security testing is mandatory.

## High-value security areas

### Authentication
- Unauthenticated access to Profile.
- Unauthenticated access to Downloads.
- Unauthenticated access to Support.
- Unauthenticated access to Help Center where applicable.
- Session expiry.
- Logout invalidation.

### Authorization
- Cross-account profile access.
- Cross-account downloads.
- Cross-account support tickets.
- Unauthorized ticket manipulation.
- Unauthorized password-change requests.

### Input security
- XSS in support comments.
- XSS in feedback suggestions.
- XSS in ticket search.
- XSS in download search.
- SQL injection attempts in searchable fields.
- Malicious attachment handling.

### File security
- MIME-type spoofing.
- Extension spoofing.
- Oversized upload.
- Malicious/corrupt file.
- Unauthorized file download.
- Predictable download URLs.

### Session security
- Back-button access after logout.
- Multiple-tab logout.
- Token reuse after logout.
- Session expiration during form submission.
- Concurrent sessions according to security policy.

---

# 15. Cross-Module Regression

These utilities are tightly connected to the main Trackofy application.

Regression should include:

1. Account menu opens from every major module.
2. Switching theme does not break Dashboard.
3. Switching theme does not break Home/map.
4. Switching theme does not break Reports.
5. Language switching does not break navigation.
6. Downloads correctly exposes generated Reports output.
7. Support can reference Units available to the user.
8. Help Center opens without corrupting the main application session.
9. Feedback submission does not alter operational data.
10. Sign Out reliably terminates access to all protected modules.

---

# 16. Recommended Test Data

Maintain dedicated data for:

- Account with complete profile.
- Account with incomplete profile.
- Account with zero resource usage.
- Account near resource limits.
- Account at resource limits.
- User with multiple generated reports.
- Pending report.
- Completed report.
- Account with multiple support tickets.
- Ticket with attachment.
- Ticket with each priority/status.
- Multiple vehicles for support unit selection.
- Valid/invalid password combinations.
- Supported/unsupported feedback attachments.
- Multiple language selections.
- Light/dark theme states.

---

# 17. Priority Model

| Priority | Meaning |
|---|---|
| Critical | Authentication, authorization, password, logout, cross-account data exposure, duplicate state-changing operation |
| High | Core CRUD/navigation, downloads, support submission, theme/language persistence |
| Medium | Search, pagination, UI validation, profile presentation |
| Low | Minor visual consistency and non-blocking presentation defects |

---

# 18. Definition of Done

The miscellaneous pages should not be considered fully tested until:

- All account-menu routes work.
- Profile data and usage are accurate.
- Downloads correctly handle Pending and Done states.
- Downloads are isolated to the correct account.
- Support tickets can be created and retrieved correctly.
- Ticket history opens the correct ticket.
- Password change enforces identity verification and password policy.
- Theme switching works across the application.
- Language switching works without layout or state corruption.
- Logout invalidates authenticated access.
- Help Center navigation/search works.
- Feedback prompt and form work end-to-end.
- Feedback validation and attachment restrictions work.
- Security tests show no cross-account access or privilege escalation.
- State-changing actions are protected against duplicate submission and common failure conditions.
- Responsive/accessibility checks are completed on supported browsers and screen sizes.
