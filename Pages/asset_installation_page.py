from playwright.sync_api import Page
from components.search import SearchComponent

class AssetInstallationPage:
    def __init__(self, page: Page):
        self.page = page
        self.search = SearchComponent(page)

        # Installations page locators
        self.table_header = page.locator("thead th")
        self.add_installation_button = page.get_by_role("button", name="New Installation")
        self.delete_installation_button = page.get_by_role("button", name="Delete installation")
        # Confirmed live 2026-09-15: an unscoped, case-insensitive "delete"
        # substring match also matches the row-level "Delete Installation"
        # action buttons underneath the confirm dialog, and .last could
        # resolve to one of THOSE (hidden behind the dialog's own backdrop)
        # instead of the dialog's real "Delete" button -- scope to the
        # dialog itself and match its exact button text.
        self.confirm_delete_button = page.locator(".cdk-overlay-container").last.get_by_role("button", name="Delete", exact=True)
        
        
    def open_installation_wizard(self):
        '''Open the installation wizard.'''
        self.add_installation_button.click()
        
    def delete_installation(self):
        '''Delete an installation -- whichever one is first in the table.'''
        self.delete_installation_button.nth(0).click()
        self.confirm_delete_button.last.click()
        self._wait_for_delete_dialog_closed()

    def delete_installation_in_row(self, row):
        '''Delete a specific row (e.g. scoped to today's date) rather than
        whichever installation happens to be first in the whole table --
        matters when the table also contains older, undeletable "historical"
        records the app refuses to remove (deleting one of those shows an
        error toast, not a success one, and would wrongly fail a test
        expecting a plain success).'''
        row.get_by_role("button", name="Delete installation").click()
        self.confirm_delete_button.last.click()
        self._wait_for_delete_dialog_closed()

    def _wait_for_delete_dialog_closed(self):
        # The confirm dialog's overlay backdrop can still be fading out when
        # the next delete_installation() call fires (confirmed live
        # 2026-09-15, deleting several in a row: a later click gets
        # intercepted by ".cdk-overlay-backdrop") -- wait for it to
        # genuinely close before returning control to the caller. (Not
        # waiting on confirm_delete_button itself -- that locator's own
        # "delete" substring match also matches the row-level "Delete
        # Installation" action buttons, so it never reports fully hidden.)
        backdrop = self.page.locator(".cdk-overlay-backdrop")
        if backdrop.count() > 0:
            backdrop.last.wait_for(state="hidden", timeout=5000)
        
    def search_installation(self, search_term: str):
        '''Search for an installation.'''
        self.search.search(search_term)

    @property
    def table_rows(self):
        return self.page.locator("tbody tr")

    def clear_search(self):
        self.search.clear_search()
