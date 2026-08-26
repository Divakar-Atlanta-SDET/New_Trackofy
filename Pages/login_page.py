from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page:Page,config):
        self.page = page
        self.config = config
        # locators
        self.username_input = page.get_by_label("User Name")
        self.password_input = page.get_by_label("Password")
        self.login_btn = page.get_by_role("button", name="Log in")
        
    def open(self):
        self.page.goto(self.config["base_url"])
        
    def enter_username(self,username: str):
        self.username_input.fill(username)
        
    def enter_password(self,password: str):
        self.password_input.fill(password)
        
    def click_login(self):
        self.login_btn.click()
    
    
    def login(self, username: str, password: str):
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_btn.click()
