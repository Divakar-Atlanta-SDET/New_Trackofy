from playwright.sync_api import Page

from Pages.base_page import BasePage


class ForgotPasswordPage(BasePage):
    """Forgot Password recovery flow (/forgot-password). Confirmed live:
    a 3-step flow (Account -> Verify -> Reset). The Account step starts
    on phone recovery (placeholder "Enter 10-digit phone number", type
    tel) with a "Use email instead" toggle that switches to an email
    field ("Use phone number instead" to switch back). Real OTP
    delivery (SMS/email) means the Verify/Reset steps can't be driven
    end-to-end without a real registered phone/email and access to the
    delivered code -- neither is available in this environment.
    """

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Forgot Password", exact=True)
        self.back_to_login_btn = page.get_by_role("button", name="Back to Login")
        self.phone_input = page.get_by_placeholder("Enter 10-digit phone number")
        self.email_input = page.get_by_placeholder("name@example.com")
        self.send_code_btn = page.get_by_role("button", name="Send Verification Code")
        self.use_email_instead_btn = page.get_by_role("button", name="Use email instead")
        self.use_phone_instead_btn = page.get_by_role("button", name="Use phone number instead")

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/forgot-password")
        self.wait_for_visible(self.heading)

    def switch_to_email(self):
        self.use_email_instead_btn.click()
        self.page.wait_for_timeout(500)

    def switch_to_phone(self):
        self.use_phone_instead_btn.click()
        self.page.wait_for_timeout(500)

    def fill_phone(self, phone: str):
        self.phone_input.fill(phone)

    def fill_email(self, email: str):
        self.email_input.fill(email)

    def back_to_login(self):
        self.back_to_login_btn.click()
