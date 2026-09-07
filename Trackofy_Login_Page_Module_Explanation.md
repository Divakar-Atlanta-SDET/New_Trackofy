# Trackofy v6 — Login & Authentication Page

## 1. Overview

The Trackofy Login Page is the primary authentication entry point for the application.

The page allows users to:
- Sign in using a username/email and password.
- Accept the Terms & Privacy condition.
- Recover access through **Forgot password?**
- Sign in using Google.
- Open the **Help Center**.
- Contact **Support**.
- Open **Terms & Privacy**.
- Access Trackofy mobile applications through Google Play and Apple App Store.
- Open **Release Notes**.

The provided login screen uses a split-screen layout:
- **Left:** Trackofy branding, fleet/map visualization and product feature highlights.
- **Right:** Authentication form and supporting links.

---

## 2. Login Page Layout

### Left Section

Visible elements include:
- Trackofy logo.
- **Fleet Intelligence Platform** text.
- **Live Fleet** status indicator.
- Product messaging:
  - "Control every mile."
  - "Optimize every move."
- Supporting text about real-time visibility, intelligent alerts and smarter operations.
- Fleet/map visualization.
- Vehicle information card.
- Feature cards:
  1. Live Tracking
  2. Smart Alerts
  3. Video Telematics
  4. Asset Health
  5. Reports & Insights

These elements are primarily promotional content and must not interfere with authentication.

### Right Section

The authentication section contains:
- **Welcome back!**
- Username or Email.
- Password.
- Terms & Privacy checkbox.
- Forgot password?
- Sign in.
- Sign in with Google.
- Help Center.
- Contact Support.
- Mobile app links.
- Privacy / Terms / Release Notes links.

---

## 3. Username or Email

Label: **Username or Email**

Placeholder: **Enter username or email**

### Test coverage
Verify:
- Valid username.
- Valid email.
- Invalid username.
- Invalid email format.
- Empty value.
- Leading/trailing spaces.
- Unsupported special characters.
- Unicode input.
- Very long input.
- Copy/paste.
- Browser autofill.

The application should not expose sensitive account information through validation messages.

---

## 4. Password

Label: **Password**

Placeholder: **Enter password**

The password is masked by default and includes a visibility control.

### Test coverage
Verify:
- Valid password.
- Invalid password.
- Empty password.
- Minimum/maximum boundaries.
- Special characters.
- Spaces.
- Unicode characters.
- Copy/paste.
- Password visibility toggle.

### Password visibility
1. Password is masked initially.
2. Clicking the eye icon reveals it.
3. Clicking again masks it.
4. Toggling does not change the password value.
5. Toggling does not submit the form.
6. Control is keyboard accessible.

---

## 5. Terms & Privacy

The page contains:

**I accept Terms & Privacy**

### Test coverage
Verify:
- Checkbox is displayed.
- Checkbox can be selected/deselected.
- State is visually clear.
- Sign-in behavior when unchecked.
- Sign-in behavior when checked.
- Terms link opens the correct content.
- Privacy link opens the correct content.
- Legal links do not submit the login form.

If acceptance is mandatory, sign-in without acceptance should be prevented with appropriate validation.

---

## 6. Sign In

Primary button: **Sign in**

### Successful login
With valid credentials and required conditions:
1. User clicks Sign in.
2. Authentication request is submitted.
3. Credentials are validated.
4. User is authenticated.
5. User is redirected to the appropriate authenticated page.

### Invalid credentials
Verify:
- Authentication fails.
- User remains on login page.
- Appropriate error is displayed.
- Error does not unnecessarily reveal whether the account exists.

### Empty fields
Test:
- Empty username/email.
- Empty password.
- Both empty.

No invalid authentication request should be submitted unnecessarily.

---

## 7. Authentication Error Handling

Test:
- Incorrect username/email.
- Incorrect password.
- Invalid credential combination.
- Locked/disabled account if supported.
- Expired account/password if supported.
- Server error.
- Authentication timeout.
- Network interruption.
- Token/session generation failure.
- Unexpected backend response.

The UI must not show false success when authentication fails.

---

## 8. Forgot Password

The login page provides **Forgot password?**

The provided recovery screen shows three steps:

1. **Account**
2. **Verify**
3. **Reset**

The first step is **Recover your account** and asks for a phone number to receive a **6-digit verification code**.

A **Use email instead** option is also available.

### Account / Phone
Field:
- **Phone Number***

Button:
- **Send Verification Code**

Test:
- Valid phone.
- Invalid phone.
- Empty phone.
- Short/long number.
- Unsupported characters.
- Country-code behavior.
- Registered number.
- Unregistered number.
- Copy/paste.

### Email recovery
Verify:
- Use email instead switches the recovery method.
- Valid/invalid/empty email handling.
- Verification code delivery.
- Return/switch behavior if supported.

### Verification
Test:
- Correct 6-digit OTP.
- Incorrect OTP.
- Expired OTP.
- Empty OTP.
- Fewer/more than 6 digits.
- Non-numeric characters.
- Reused OTP.
- Multiple OTP requests.
- Resend behavior.
- Rate limiting.
- Older OTP after a newer OTP request.
- Refresh during verification.

The verification step must not be bypassable.

### Reset
Verify:
- New password follows configured policy.
- Invalid password is rejected.
- Confirmation mismatch is rejected if confirmation exists.
- Successful reset.
- Old password behavior follows security policy.
- New password can be used to log in.
- Reset token/code cannot be reused.
- Expired reset tokens are rejected.

---

## 9. Google Sign-In

The page provides **Sign in with Google**.

Test:
- Successful Google authentication.
- User cancellation.
- Google authentication failure.
- Unregistered Google account.
- Existing linked account.
- Multiple Google accounts.
- Popup blocked.
- OAuth network failure.
- OAuth callback failure.
- Invalid/expired OAuth state.
- Repeated authentication attempts.

Successful and failed OAuth flows must leave the application in a consistent state.

---

## 10. Help Center

The login page provides **Help Center**.

The provided Help Center screenshot shows:
- Trackofy documentation branding.
- Search articles/guides.
- Home.
- Contents/navigation.
- Overview.
- Device.
- Sensor.
- Quick links.
- Popular sections.
- Common issues.
- Support/help entry points.

Quick links include:
- Device Setup.
- Sensor Configuration.
- Reports.
- Alerts.
- Video Telematics.
- Live Tracking.

Common issues include:
- Vehicle not showing live location.
- Report data is missing.
- Alert is not triggering.
- Sensor value looks incorrect.

### Testing
Verify:
- Help Center opens successfully.
- Correct page opens.
- It does not submit the login form.
- It is accessible while logged out if intended.
- Browser Back returns correctly.

---

## 11. Contact Support

The page provides **Contact Support**.

Verify:
- Correct support destination.
- Works without authentication if intended.
- Does not submit the login form.
- Does not unnecessarily expose user information.
- Popup/new-tab behavior is correct.

The screenshots do not establish the exact support workflow, so the actual destination should be validated against the implementation.

---

## 12. Release Notes

The login page provides **Release Notes**.

The provided Release Notes screenshot shows:
- Version **6.2**.
- Version **6.1**.
- Release date shown as **30 July 2026**.
- Release type.
- Release scope.
- Release modules.

Version 6.2 modules shown:
1. Sensor Configuration.
2. CAN Module.
3. WhatsApp Alert Notifications.
4. UI Enhancement & Analytics Upgrade.

### Testing
Verify:
- Release Notes opens correctly.
- Version selection works.
- Correct release information is displayed.
- Module navigation works.
- Back to Login works.
- Page is accessible without authentication if intended.

---

## 13. Mobile App Links

The page contains **Get the mobile app** with:
- Google Play.
- Apple App Store.

Verify:
- Google Play opens the correct Trackofy listing.
- Apple App Store opens the correct Trackofy listing.
- Links work in supported browsers.
- Neither link points to an unrelated application.
- Opening a store link does not submit the login form.

The actual destination URLs should be verified against the application's configured URLs.

---

## 14. Terms and Privacy Links

Verify:
- Terms opens correct content.
- Privacy opens correct content.
- Correct destination.
- Secure HTTPS destination where applicable.
- Works while logged out.
- Does not submit the login form.
- Browser Back returns correctly.

---

## 15. Keyboard & Accessibility

Verify keyboard navigation through:
1. Username/email.
2. Password.
3. Password visibility control.
4. Terms & Privacy.
5. Forgot password.
6. Sign in.
7. Google sign-in.
8. Help Center.
9. Contact Support.
10. Mobile app links.
11. Release Notes.

Also verify:
- Tab / Shift+Tab.
- Enter to activate appropriate controls.
- Space for checkbox.
- Visible focus indicators.
- Labels correctly associated with inputs.
- Accessible name for password visibility control.
- Accessible error messages.
- Accessible names for links/buttons.
- Color is not the only indication of state.
- Sufficient contrast.

---

## 16. Browser Navigation & Refresh

Test:
- Refreshing login page.
- Browser Back/Forward.
- Opening login in a new tab.
- Opening Forgot Password and returning.
- Opening Help Center and returning.
- Opening Release Notes and returning.

Sensitive password data should not be unnecessarily exposed after navigation/refresh.

---

## 17. Session & Authentication Security

Verify:
- Successful login creates a valid session.
- Logout invalidates the session.
- Session expiry works.
- Expired sessions redirect appropriately.
- Protected pages cannot be accessed after logout.
- Browser Back does not expose protected content after logout.
- Multiple tabs follow the intended session behavior.

For token-based authentication:
- Invalid tokens are rejected.
- Expired tokens are rejected.
- Tampered tokens are rejected.
- Tokens cannot be used for another account.
- Sensitive tokens are not unnecessarily exposed in URLs or logs.

---

## 18. Brute Force & Rate Limiting

Test:
- Repeated incorrect passwords.
- High-frequency login requests.
- Multiple attempts against one account.
- Attempts against multiple accounts.
- Automated repeated requests.

Verify the application's configured protection such as:
- Rate limiting.
- Temporary lockout.
- Progressive delay.
- CAPTCHA/challenge if implemented.
- Security logging/alerting.

---

## 19. Input Security

Test username/email and authentication-related inputs for:
- XSS.
- SQL injection.
- HTML injection.
- Special characters.
- Unicode.
- Oversized input.

Example inputs:
- `<script>alert(1)</script>`
- `' OR 1=1 --`
- `" OR "1"="1`

Expected:
- No script execution.
- No SQL manipulation.
- No sensitive server error.
- Safe validation/error handling.

Apply the same principle to Forgot Password inputs.

---

## 20. Transport Security

Verify:
- Login uses HTTPS.
- Credentials are transmitted securely.
- Password is not sent through insecure requests.
- No mixed-content authentication resources.
- Authentication cookies/tokens have appropriate security attributes.
- Sensitive authentication data is not exposed through URL parameters.

---

## 21. Error Message Security

Authentication errors should not unnecessarily reveal:
- Whether a username exists.
- Whether an email belongs to an account.
- Database errors.
- Stack traces.
- Internal API details.
- Authentication service internals.

Errors should remain useful without exposing unnecessary security information.

---

## 22. Performance

Measure:
- Initial login-page load.
- Static asset loading.
- Login API response.
- Google OAuth initiation.
- Forgot Password request.
- OTP verification.
- Password reset.
- Help Center navigation.
- Release Notes loading.

Test under:
- Normal network.
- Slow network.
- High latency.
- Network interruption.
- Multiple simultaneous authentication attempts.

---

## 23. Responsive Testing

Test:
- Desktop.
- Laptop.
- Tablet.
- Mobile.

Verify:
- Login form remains usable.
- Inputs remain accessible.
- Sign-in button remains visible.
- Links do not overlap.
- Promotional section behaves correctly.
- Mobile app links remain accessible.
- No unintended horizontal scrolling.
- Text remains readable.
- Mobile keyboard does not obscure critical controls.

---

## 24. Cross-Browser Testing

Validate supported versions of:
- Chrome.
- Edge.
- Firefox.
- Safari where applicable.

Focus on:
- Login rendering.
- Password visibility.
- Checkbox behavior.
- OAuth.
- Navigation links.
- Responsive layout.
- Browser autofill.
- Form submission.

---

## 25. Recommended Test Data

### Valid accounts
- Valid username + password.
- Valid email + password.
- Google-linked account if supported.

### Invalid accounts
- Invalid username.
- Invalid email.
- Incorrect password.
- Non-existing account.
- Disabled/locked account if supported.

### Recovery
- Registered phone.
- Unregistered phone.
- Registered email.
- Unregistered email.
- Valid OTP.
- Expired OTP.
- Incorrect OTP.

### Security
- XSS payloads.
- SQL injection payloads.
- Oversized input.
- Special characters.
- Unicode input.

---

## 26. Priority Classification

| Priority | Scope |
|---|---|
| Critical | Authentication, authorization, session security, password handling, brute-force protection |
| High | Login success/failure, Forgot Password, OTP verification, Google Sign-In, Terms acceptance |
| Medium | Help Center, Release Notes, support links, mobile app links, responsive behavior |
| Low | Minor visual inconsistencies and non-blocking presentation issues |

---

## 27. Definition of Done

The Login & Authentication area should be considered adequately tested when:

- Valid username/email login works.
- Valid password authentication works.
- Invalid credentials are rejected.
- Required Terms & Privacy acceptance is enforced if configured as mandatory.
- Password visibility toggle works.
- Forgot Password phone flow works.
- Forgot Password email flow works.
- OTP validation works securely.
- Password reset works securely.
- Google Sign-In works and handles failure/cancellation correctly.
- Help Center link works.
- Contact Support link works.
- Terms link works.
- Privacy link works.
- Release Notes link works.
- Google Play link is correct.
- Apple App Store link is correct.
- Login session is created correctly.
- Logout/session expiration is enforced.
- Protected resources cannot be accessed without authentication.
- Brute-force/rate-limit protections work.
- XSS/SQL injection tests are passed.
- Authentication errors do not leak sensitive information.
- HTTPS and secure authentication transport are verified.
- Responsive behavior is validated.
- Accessibility basics are validated.
- Supported browsers are validated.
- Network/API failure scenarios are handled correctly.
