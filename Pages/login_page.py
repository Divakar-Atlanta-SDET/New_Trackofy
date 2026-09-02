from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page:Page,config):
        self.page = page
        self.config = config
        # locators
        self.username_input = page.get_by_placeholder("Enter username or email")
        self.password_input = page.get_by_placeholder("Enter password")
        self.login_btn = page.get_by_role("button", name="Sign in", exact=True)
        
    def open(self):
        self.page.goto(self.config["base_url"])
        
    def enter_username(self,username: str):
        self.username_input.fill(username)
        
    def enter_password(self,password: str):
        self.password_input.fill(password)
        
    def click_login(self):
        self.login_btn.click()
    
    
    def login(self, username: str, password: str):
        if "/home" in self.page.url:
            return
        try:
            self.username_input.wait_for(state="visible", timeout=10000)
            self.username_input.fill(username)
            self.password_input.fill(password)
            self.login_btn.click()
        except Exception:
            if "/home" in self.page.url:
                return
            raise

