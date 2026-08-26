from Pages.login_page import LoginPage
from playwright.sync_api import expect
from components.toast_notifcations import ToastNotifications

def test_login(page, config,credentials):
    login_page = LoginPage(page, config)
    toast = ToastNotifications(page)
    login_page.open()
    login_page.login( credentials["username"], credentials["password"] )
    expect(toast.success_toast).to_be_visible()
    expect(page).to_have_url(f"{config["base_url"]}/home")
