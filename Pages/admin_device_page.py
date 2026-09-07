from playwright.sync_api import Locator, Page

from Pages.base_page import BasePage


class AdminDevicePage(BasePage):
    """Add Device (/admin/device/add-device), Unassign Device
    (/admin/device/unassign-device, a browse/search list of NEVER-
    assigned inventory -- not where an assigned device gets unassigned),
    Manage Device (/admin/device/manage-device, whose per-owner "View
    Devices" dialog is the REAL unassign action).

    Confirmed live end-to-end (assign a real device to a real end user,
    verify, then unassign and verify restoration): selecting UserType=
    "End User" on Add Device reveals a combined device+vehicle+owner
    assignment form (IMEI autocomplete search by first-4-digits, End User
    autocomplete search by name, Vehicle Name/Type/Icon) -- Add Device is
    genuinely "assign a device to a user" in one step, matching the
    user's own description of this panel's core purpose."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Confirmed live: UserType/Protocol are PrimeNG p-select comboboxes
        # whose <label for=...> doesn't resolve via get_by_label (the
        # label's `for` id doesn't match the rendered combobox element) --
        # positional access via get_by_role("combobox") in DOM/label order
        # is the same documented exception already used for unlabeled
        # comboboxes in administrator_page.py (vehicles_select()). IMEI,
        # despite ALSO resolving to role="combobox", is a genuinely
        # different component (p-autocomplete, a real text input with
        # placeholder "Enter first 4 digits of IMEI") -- see
        # search_and_select_imei() for its real selection mechanism.
        self.user_type_combobox = page.get_by_role("combobox").nth(0)
        self.imei_input = page.get_by_role("combobox").nth(1)
        self.protocol_combobox = page.get_by_role("combobox").nth(2)
        self.serial_no_input = page.get_by_label("Serial No", exact=False)
        self.device_model_input = page.get_by_label("Device Model", exact=False)
        # Confirmed live: get_by_label("Mobile") ambiguously matches both
        # this field ("Mobile *") and "Mobile 2" -- matching the literal
        # "Mobile *" (with the asterisk) as a substring disambiguates
        # without needing exact=True (which would require the whole label
        # to be just "Mobile", which it isn't either). Also confirmed:
        # this field enforces minlength="13", i.e. a country-code-
        # prefixed number, not a bare 10-digit one.
        self.mobile_input = page.get_by_label("Mobile *", exact=False)
        self.port_no_input = page.get_by_label("Port No", exact=False)
        self.assign_device_button = page.get_by_role("button", name="Assign Device")
        self.search_input = page.get_by_placeholder("Search")

    # ------------------------------------------------------------- Add Device
    def open_add_device(self, base_url: str):
        self.page.goto(f"{base_url}/admin/device/add-device")
        self.expect_path("/admin/device/add-device")

    def select_user_type(self, value: str = "End User"):
        self.user_type_combobox.click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=value, exact=True).click()
        self.page.wait_for_timeout(1000)

    def search_and_select_imei(self, imei_prefix: str):
        """Confirmed live: this field only searches on the first 4 digits
        (its own placeholder says so) and its real suggestion-list items
        are <li class="p-autocomplete-option"> WITHOUT role="option" --
        get_by_role("option") can't reach them, get_by_text on the known
        IMEI substring is the reliable match. Selecting a suggestion
        auto-fills Serial No and Device Model for real."""
        self.imei_input.click()
        self.imei_input.press_sequentially(imei_prefix[:4], delay=80)
        suggestion = self.page.get_by_text(imei_prefix, exact=False).first
        self.wait_for_visible(suggestion, timeout=8000)
        suggestion.click()
        self.page.wait_for_timeout(500)

    def select_combobox_option(self, combobox: Locator, option_name: str, exact: bool = False):
        combobox.click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=option_name, exact=exact).first.click()
        self.page.wait_for_timeout(300)

    def fill_port_no_if_editable(self, value: str):
        # Confirmed live: selecting a Protocol auto-derives and locks a
        # default Port No (rendered disabled, already p-filled) for at
        # least some protocols -- only fill it if it's still editable.
        if self.port_no_input.is_enabled():
            self.port_no_input.fill(value)

    # ------------------------------------------------------------- End-user assignment section
    # Confirmed live: selecting UserType="End User" reveals an additional
    # "User Information" section (End User*/Vehicle Name*/Vehicle Type*/
    # Vehicle Icon*/Creation Date*/Expiry Date*) -- Add Device is really
    # "add a device to inventory AND assign it to a vehicle under a
    # specific end user" in one combined form, not a two-step process.
    def end_user_combobox(self) -> Locator:
        return self.page.get_by_role("combobox").nth(3)

    def search_and_select_end_user(self, name_prefix: str, expect_text: str):
        """Same p-autocomplete mechanism as IMEI (see
        search_and_select_imei) -- searches End User by name-prefix.
        Confirmed live: newly-created dummy users (this session's own
        AutoQA test records) did NOT surface in this search even with
        their exact first-name prefix -- root cause not isolated
        (possible indexing delay). Reliable against pre-existing real
        end users. `expect_text` is the substring to match in the
        suggestion (e.g. the real user's full name)."""
        self.end_user_combobox().click()
        self.end_user_combobox().press_sequentially(name_prefix[:4], delay=80)
        suggestion = self.page.get_by_text(expect_text, exact=False).first
        self.wait_for_visible(suggestion, timeout=8000)
        suggestion.click()
        self.page.wait_for_timeout(500)

    def vehicle_type_combobox(self) -> Locator:
        return self.page.get_by_role("combobox").nth(4)

    def vehicle_icon_combobox(self) -> Locator:
        return self.page.get_by_role("combobox").nth(5)

    def vehicle_name_input(self) -> Locator:
        # Confirmed live: no `for` attribute on this label either --
        # get_by_placeholder is the reliable reach.
        return self.page.get_by_placeholder("Enter vehicle name")

    def is_assign_button_enabled(self) -> bool:
        return self.assign_device_button.is_enabled()

    def submit_add_device(self):
        # Confirmed live: the "Device assigned successfully" toast fires
        # before the assignment is reliably queryable via Manage Device's
        # own data -- navigating there and reading the owner's device
        # list immediately after can race a real backend-processing
        # delay (confirmed reproducing intermittently even with a 1.5s
        # wait here). A longer settle wait is deliberate, not a guess.
        self.assign_device_button.click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(3500)

    # ------------------------------------------------------------- Unassign Device (browse inventory)
    # Confirmed live: despite the name, this page is a browse/search list
    # of devices that have NEVER been assigned (raw inventory) -- it is
    # NOT where an already-assigned device gets unassigned from its
    # owner. The real unassign action lives inside Manage Device's
    # per-owner "View Devices" dialog (see device_list_dialog() below).
    def open_unassign_device(self, base_url: str):
        self.page.goto(f"{base_url}/admin/device/unassign-device")
        self.expect_path("/admin/device/unassign-device")

    def search(self, query: str):
        # Confirmed live: same broken-search pattern as Manage User (Bug
        # #56) -- this box does not actually filter the list either.
        self.search_input.fill(query)
        self.search_input.press("Enter")
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)

    def rows(self) -> Locator:
        return self.page.locator("table tbody tr")

    def row_by_imei(self, imei: str) -> Locator:
        return self.rows().filter(has_text=imei).first

    # ------------------------------------------------------------- Manage Device
    def open_manage_device(self, base_url: str):
        self.page.goto(f"{base_url}/admin/device/manage-device")
        self.expect_path("/admin/device/manage-device")

    def end_user_tab(self) -> Locator:
        return self.page.get_by_role("tab", name="End User")

    def dealer_tab(self) -> Locator:
        return self.page.get_by_role("tab", name="Dealer")

    def switch_to_dealer_tab(self):
        self.dealer_tab().click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(800)

    def switch_to_end_user_tab(self):
        self.end_user_tab().click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(800)

    def row_by_owner_name(self, name: str) -> Locator:
        return self.rows().filter(has_text=name).first

    def open_device_list_dialog(self, owner_row: Locator):
        # Confirmed live: the "Device" p-tag (count + label) opens a
        # dialog listing every device under this owner -- the REAL place
        # to unassign an already-assigned device (each row has its own
        # pi-trash icon, confirmed working, see unassign_device_in_dialog).
        # Confirmed live (a real, reproducible bug in this test suite,
        # not the app): reading device_row_in_dialog() right after this
        # returns can race the dialog's own data load and report 0 rows
        # even though the real row is there a moment later -- always wait
        # for the "N records" header text before trusting row reads.
        owner_row.locator("p-tag").first.click(force=True)
        self.wait_for_visible(self.device_list_dialog().first)
        self.wait_for_body_pattern(r"\d+\s*records?")

    def device_list_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container, .p-dialog")

    def device_row_in_dialog(self, imei: str) -> Locator:
        return self.device_list_dialog().locator("table tbody tr").filter(has_text=imei)

    def wait_for_device_in_dialog(self, base_url: str, owner_name: str, imei: str, max_attempts: int = 6) -> Locator:
        """Confirmed live: a just-submitted device assignment is
        genuinely eventually-consistent server-side -- reading the
        owner's device list immediately (even several seconds) after a
        "Device assigned successfully" toast can still show the OLD
        list. Takes the owner's NAME (not a Locator) and re-navigates to
        Manage Device + re-fetches the row fresh every attempt -- an
        earlier version reused one Locator across retries and appeared
        to hang re-clicking a stale/detached row after the table
        re-rendered, silently never opening a fresh dialog."""
        row = None
        for attempt in range(max_attempts):
            self.open_manage_device(base_url)
            self.page.wait_for_timeout(1200)
            owner_row = self.row_by_owner_name(owner_name)
            self.open_device_list_dialog(owner_row)
            row = self.device_row_in_dialog(imei)
            if row.count() > 0:
                return row
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)
            if attempt < max_attempts - 1:
                self.page.wait_for_timeout(2000)
        return row

    def unassign_device_in_dialog(self, imei: str):
        """Confirmed live: clicking this row's trash icon opens a
        PrimeNG p-confirmpopup ("Do you want to delete this device ?")
        that some very-short-lived state discards if you wait too long
        before clicking Yes (an earlier attempt with a ~1-2s delay before
        clicking Yes silently lost the popup with no error) -- click Yes
        immediately after the trash-icon click with no intervening wait."""
        row = self.device_row_in_dialog(imei)
        row.locator("i.pi-trash").click(force=True)
        popup = self.page.locator(".p-confirmpopup")
        popup.get_by_role("button", name="Yes", exact=True).click(timeout=5000)
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)
