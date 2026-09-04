import re

from playwright.sync_api import Locator, Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from Pages.base_page import BasePage


class HomePage(BasePage):
    """Page object for the Trackofy Home module (real-time fleet monitoring
    dashboard). Rewritten from scratch against the live app (the previous
    version was stale -- see Bug_Report.md / plan notes for details)."""

    # "Total Fleet" and "Active Devices" are always shown in the KPI header
    # and are NOT configurable via KPI Settings (confirmed live). The other
    # 10 are toggled via the KPI Settings dialog.
    ALWAYS_ON_KPIS = ["Total Fleet", "Active Devices"]
    CONFIGURABLE_KPIS = [
        "Running",
        "Idle",
        "Stopped",
        "No Data",
        "BMS Enabled",
        "Video Enabled",
        "Expired Devices",
        "Critical Alerts",
        "Active Trips",
    ]
    # The KPI Settings dialog's checkbox for "Total Fleet" is labeled "Total
    # Vehicles" instead -- confirmed live naming mismatch between the header
    # card and its settings checkbox for the same underlying KPI.
    KPI_SETTINGS_LABEL_FOR = {"Total Fleet": "Total Vehicles"}

    FLEET_STATUS_FILTERS = ["Active", "Running", "Idle", "Stopped", "No Data", "BMS", "Video"]
    GROUP_STATUS_FILTERS = ["Active", "Running", "Idle", "Stopped", "No Data"]
    # Confirmed live -- these are this account's real groups (matches the
    # design doc's example exactly).
    KNOWN_GROUPS = ["Default", "Delhi", "Bhopal", "Dwarka"]

    def __init__(self, page: Page):
        super().__init__(page)

        # --- Side-panel tabs ---
        # Confirmed live: the DOM has a second, hidden copy of these tab
        # labels (a mobile/responsive menu) earlier in document order, so a
        # plain .first grabs the wrong (invisible) element for Groups/Drivers.
        # `:visible` keeps this lazy (re-evaluated on each use, not baked in
        # at construction time) and always picks a currently-visible match.
        self.fleet_tab = page.locator(":text-is('Fleet'):visible").first
        self.groups_tab = page.locator(":text-is('Groups'):visible").first
        self.drivers_tab = page.locator(":text-is('Drivers'):visible").first

        # --- Search (confirmed live: a plain input, NOT role=searchbox --
        # components/search.py's get_by_role("searchbox") does not match) ---
        self.search_input = page.locator("input[placeholder='Search...']")

        # --- KPI header controls ---
        self.kpi_settings_button = page.get_by_role("button", name="KPI Settings")
        self.home_settings_button = page.get_by_role("button", name="Home Settings")
        self.geolink_button = page.get_by_role("button", name="GeoLink", exact=True)

        # --- Map ---
        self.map_mode_button = page.get_by_text("Map", exact=True).first
        self.hybrid_mode_button = page.get_by_text("Hybrid", exact=True).first

        # --- Fleet pagination footer ---
        self.rows_per_page_all_button = page.get_by_text("All", exact=True)
        self.pagination_summary = page.get_by_text(re.compile(r"Showing \d+ - \d+ of \d+ vehicles"))

        # --- Alerts & Notifications ---
        # No ^/$ anchors: Playwright's has_text/get_by_text regex has no
        # multiline flag, so an anchored pattern only matches the very
        # start/end of an element's whole flattened text -- these labels
        # are not always the first/only line of their containing element
        # (confirmed live the same way as the group status chips).
        self.alerts_tab_link = page.get_by_text(re.compile(r"Alerts\s*\(\d+\)"))
        self.acknowledged_tab_link = page.get_by_text(re.compile(r"Acknowledged\s*\(\d+\)"))
        self.view_all_alerts_link = page.get_by_text("View all alerts", exact=True)
        self.live_alerts_button = page.get_by_text("Live", exact=True).last

    def open(self, base_url: str):
        self.page.goto(f"{base_url}/home")
        self.wait_until_ready()
        self.wait_for_visible(self.fleet_tab)
        self.wait_for_fleet_loaded()

    def wait_for_fleet_loaded(self):
        """wait_for_loading_to_finish()'s spinner check doesn't reliably
        catch this list's load delay (confirmed live: it can return before
        any vehicle card has actually rendered) -- wait for real content."""
        self.wait_for_visible(self.vehicle_cards().first)

    # ------------------------------------------------------------- tabs

    def open_fleet_tab(self):
        self.fleet_tab.click()
        self.wait_for_loading_to_finish()
        self.wait_for_fleet_loaded()

    def open_groups_tab(self):
        self.groups_tab.click()
        self.wait_for_loading_to_finish()
        # wait_for_loading_to_finish()'s spinner check doesn't reliably
        # catch this tab's load delay (confirmed live: it returns before
        # group data has actually rendered) -- wait for real content instead.
        self.wait_for_visible(self.group_cards().first)

    def open_drivers_tab(self):
        self.drivers_tab.click()
        self.wait_for_loading_to_finish()
        self.wait_for_visible(self.driver_cards().first)

    # ------------------------------------------------------------- KPI header

    def kpi_card(self, kpi_name: str) -> Locator:
        # Confirmed live: each KPI card's label is a <p class="tx-kpi..."> and
        # its card container is the nearest ancestor <div> with a fixed
        # width class -- w-[150px] for most labels, but w-[160px] for the
        # longer "Expired Devices" label (confirmed live), so match on the
        # stable shrink-0/items-center classes shared by every card's
        # container instead of a specific pixel width. The KPI Settings
        # dialog also has a checkbox labeled with the same KPI name -- when
        # that dialog exists in the DOM (even closed/hidden), a plain
        # .first can grab its hidden label instead of the real header card
        # (same class of bug as the Fleet/Groups/Drivers tab locators
        # earlier) -- restrict to a visible match.
        label = self.page.locator(f":text-is('{kpi_name}'):visible").first
        return label.locator(
            "xpath=ancestor::div[contains(@class,'shrink-0') and contains(@class,'items-center')][1]"
        )

    def kpi_visible(self, kpi_name: str) -> bool:
        """Whether this KPI's card is currently rendered. Confirmed live:
        the app hides a status KPI's card entirely (not "0") when its live
        count is zero, so a configurable status KPI can legitimately vanish
        between reads as real fleet state changes -- callers that aren't
        specifically testing that behavior should skip rather than fail
        when this is False."""
        card = self.kpi_card(kpi_name)
        return card.count() > 0 and card.is_visible()

    def get_kpi_value(self, kpi_name: str) -> str:
        card = self.kpi_card(kpi_name)
        self.wait_for_visible(card)
        text = card.inner_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line in lines:
            if line != kpi_name and re.fullmatch(r"[\d,.]+", line):
                return line
        return ""

    def click_kpi(self, kpi_name: str):
        self.kpi_card(kpi_name).click()
        self.wait_for_loading_to_finish()

    def open_kpi_settings(self):
        # Idempotent: a prior test that failed mid-dialog can leave this
        # already open -- re-clicking the trigger button in that state does
        # nothing useful and just wastes the click, so skip it.
        # Check for the checkbox content, not just the dialog container --
        # the container can briefly still read as visible mid-close-
        # animation right after a Save/Cancel, which would otherwise make
        # this wrongly skip re-opening a dialog that's actually about to
        # disappear (confirmed live: caused a 30s timeout downstream).
        running_checkbox = self.kpi_settings_checkbox("Running")
        if running_checkbox.count() > 0 and running_checkbox.is_visible():
            return
        # A stale login/info toast or the KPI strip's own horizontal-scroll
        # button can intercept this click right after page load (confirmed
        # live) -- force it, matching the interception-dismissal pattern
        # already established for other modules this session.
        self.kpi_settings_button.click(force=True)
        try:
            self.wait_for_visible(self.kpi_settings_dialog())
            # The checkbox list renders ~2s after the dialog container
            # itself (confirmed live) -- wait for real content, not just
            # the dialog shell, before anything tries to interact with a
            # checkbox.
            self.wait_for_visible(self.kpi_settings_checkbox("Running"))
        except PlaywrightTimeoutError:
            # Rare stalled open (server-load dependent) -- one bounded
            # self-heal retry rather than failing the whole test on a
            # flaky click.
            self.kpi_settings_button.click(force=True)
            self.wait_for_visible(self.kpi_settings_dialog())
            self.wait_for_visible(self.kpi_settings_checkbox("Running"))

    def kpi_settings_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text="KPI Settings")

    def kpi_settings_select_all(self):
        # Each checkbox toggles via its own Angular change-detection cycle,
        # so the "Currently selected" count (and individual checkbox states)
        # can lag a few hundred ms behind the click (confirmed live) --
        # poll until it settles at the max instead of trusting the click to
        # be synchronous.
        self.kpi_settings_dialog().get_by_text("Select All", exact=True).click()
        total_options = len(self.CONFIGURABLE_KPIS) + 1
        for _ in range(20):
            if self.kpi_settings_selected_count() == total_options:
                break
            self.page.wait_for_timeout(200)
        # The "Currently selected" count text can settle before every
        # individual checkbox's own checked state has flushed (confirmed
        # live: count reads 10 while a specific checkbox still reads
        # unchecked moments later) -- a short extra buffer avoids acting on
        # a checkbox before its own binding has caught up.
        self.page.wait_for_timeout(500)

    def kpi_settings_check_all(self):
        # Deterministic alternative to kpi_settings_select_all() for setup/
        # cleanup use -- the dialog's own "Select All" shortcut button
        # proved unreliable live for that purpose (confirmed: the account's
        # selected count drifted to 9, then 6, across repeated calls with
        # no consistent cause), so this checks each checkbox individually
        # instead. Use kpi_settings_select_all() when the test is actually
        # verifying that button's own behavior (e.g. HOME-0058).
        for kpi in self.CONFIGURABLE_KPIS + ["Total Fleet"]:
            checkbox = self.kpi_settings_checkbox(kpi)
            if not checkbox.is_checked():
                checkbox.check()
        total_options = len(self.CONFIGURABLE_KPIS) + 1
        for _ in range(20):
            if self.kpi_settings_selected_count() == total_options:
                break
            self.page.wait_for_timeout(200)

    def kpi_settings_wait_for_count(self, expected: int, timeout_ms: int = 4000):
        """Poll the 'Currently selected' count until it reaches `expected`
        -- it lags the actual checkbox state by about one Angular render
        cycle (confirmed live), so a check/uncheck immediately followed by
        a read of this count is unreliable without settling first."""
        elapsed = 0
        step = 200
        while elapsed < timeout_ms:
            if self.kpi_settings_selected_count() == expected:
                return
            self.page.wait_for_timeout(step)
            elapsed += step

    def kpi_settings_checkbox(self, kpi_name: str) -> Locator:
        label = self.KPI_SETTINGS_LABEL_FOR.get(kpi_name, kpi_name)
        return self.kpi_settings_dialog().get_by_role("checkbox", name=label)

    def kpi_settings_selected_count(self) -> int:
        text = self.kpi_settings_dialog().inner_text()
        match = re.search(r"Currently selected:\s*(\d+)", text)
        return int(match.group(1)) if match else 0

    def kpi_settings_validation_visible(self) -> bool:
        return "Select at least 6 KPIs" in self.kpi_settings_dialog().inner_text()

    def kpi_settings_save(self):
        self.kpi_settings_dialog().get_by_role("button", name="Save").click()

    def kpi_settings_cancel(self):
        self.kpi_settings_dialog().get_by_role("button", name="Cancel").click()

    def close_kpi_settings(self):
        self.kpi_settings_dialog().locator("button").filter(has_text="close").first.click()

    # ------------------------------------------------------------- Home Settings
    # (Note: the design doc describes "View Presets" as 3 layout sizes --
    # expanded/medium/compact. That is NOT what the live "Home Settings"
    # dialog does; confirmed live it configures: Default view (List/Group),
    # Map Marker style (Label/Status/Glow), and More Options toggles for
    # which action icons show (GPS/GSM/Ignition/Playback/POI/Alert/
    # Distance/Focus). Keeping the method names generic ("home settings",
    # not "view preset") to reflect what's actually there.)

    def open_home_settings(self):
        self.home_settings_button.click(force=True)
        self.wait_for_visible(self.home_settings_dialog())

    def home_settings_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text="Home Settings")

    def home_settings_save(self):
        self.home_settings_dialog().get_by_role("button", name="Save").click()

    def home_settings_cancel(self):
        self.home_settings_dialog().get_by_role("button", name="Cancel").click()

    def home_settings_reset(self):
        self.home_settings_dialog().get_by_role("button", name="Reset").click()

    # ------------------------------------------------------------- Search

    def search(self, query: str):
        self.search_input.fill(query)
        self.wait_for_loading_to_finish()

    def clear_search(self):
        self.search_input.fill("")
        self.wait_for_loading_to_finish()

    # ------------------------------------------------------------- Fleet filters

    def fleet_status_filter(self, name: str) -> Locator:
        return self.page.get_by_text(re.compile(rf"^{re.escape(name)}(\s*\(\d+\))?$")).first

    def apply_fleet_status_filter(self, name: str):
        self.fleet_status_filter(name).click()
        self.wait_for_loading_to_finish()
        # The virtualized card list re-renders after a filter change (same
        # class of timing gap as wait_for_fleet_loaded) -- give it a moment
        # to settle before anything reads card content, to avoid a stale
        # locator error mid-iteration.
        self.page.wait_for_timeout(500)

    # ------------------------------------------------------------- Vehicle cards

    def vehicle_cards(self) -> Locator:
        # Confirmed live: each vehicle card is <app-home-vehicle-card>
        # wrapping an <article>, inside a CDK virtual-scroll list (so only
        # ~13 of 36 are ever in the DOM at once -- results are limited to
        # what's currently rendered/scrolled into view). A bare "article"
        # selector is too broad -- Alert cards are also <article> elements.
        return self.page.locator("app-home-vehicle-card")

    def vehicle_card(self, vehicle_id: str) -> Locator:
        return self.vehicle_cards().filter(has_text=vehicle_id).first

    def vehicle_card_more_vert_buttons(self) -> Locator:
        return self.page.locator("button:has(mat-icon:text('more_vert'))")

    # Confirmed live: a vehicle card's three-dot menu button starts DISABLED
    # (class includes opacity-45/cursor-not-allowed/grayscale) until the
    # vehicle is "selected" by clicking its name/ID text -- clicking a
    # disabled more_vert just shows a toast ("Please select the vehicle
    # first."), not a menu. Once selected, the menu renders INLINE next to
    # the button (not in a .cdk-overlay-container like other dropdowns).
    VEHICLE_MENU_ITEMS = [
        "Focus on Map",  # not in the design doc -- confirmed live, extra item
        "Playback",
        "POI",
        "Alert",
        "Unit Maintenance",
        "Unit Insight",  # doc says "Unit Insights" (plural) -- live label is singular
    ]
    # BMS-enabled vehicles get one more item, confirmed live.
    BMS_VEHICLE_MENU_EXTRA_ITEM = "Battery Insight"

    def select_vehicle_card(self, vehicle_id: str):
        card = self.vehicle_card(vehicle_id)
        # Some devices have an identical title and subtitle (e.g. an IMEI
        # used as both name and subtitle), which makes an exact-text-match
        # ambiguous (confirmed live -- strict-mode violation) -- target the
        # title element specifically.
        card.locator(".tx-card-title").first.click()
        self.wait_for_loading_to_finish()

    def open_vehicle_menu_for(self, vehicle_id: str):
        self.select_vehicle_card(vehicle_id)
        card = self.vehicle_card(vehicle_id)
        card.locator("button:has(mat-icon:text('more_vert'))").click()
        self.wait_for_visible(self.vehicle_menu_for(vehicle_id))

    def vehicle_menu_for(self, vehicle_id: str) -> Locator:
        return self.vehicle_card(vehicle_id).locator("mat-icon", has_text="history").locator(
            "xpath=ancestor::*[self::div or self::ul][1]"
        )

    def click_vehicle_menu_item(self, vehicle_id: str, item_name: str):
        self.vehicle_card(vehicle_id).get_by_text(item_name, exact=True).click()
        self.wait_for_loading_to_finish()

    def actively_tracking_text(self) -> str:
        match = re.search(r"Actively tracking \d+ vehicle", self.visible_text())
        return match.group(0) if match else ""

    def clear_active_tracking(self):
        self.page.get_by_role("button", name="Clear", exact=True).click()

    def visible_vehicle_ids(self, max_count: int = 50) -> list[str]:
        """Vehicle identifiers currently rendered in the Fleet list. The list
        is virtualized (confirmed live: only ~13 rows exist in the DOM at
        once out of 36 total), so this only returns what's rendered."""
        cards = self.vehicle_cards()
        count = min(cards.count(), max_count)
        ids = []
        for index in range(count):
            card_text = cards.nth(index).inner_text()
            first_line = card_text.splitlines()[0].strip() if card_text else ""
            if first_line:
                ids.append(first_line)
        return ids

    def get_pagination_total(self) -> int:
        text = self.pagination_summary.inner_text()
        match = re.search(r"of\s+(\d+)\s+vehicles", text)
        return int(match.group(1)) if match else 0

    def fleet_result_count(self) -> int:
        """Total matching vehicles for the current filter/search. Falls back
        to the rendered card count when the pagination summary text doesn't
        appear at all (confirmed live: it's absent for a single-result set,
        not just hidden)."""
        if self.pagination_summary.count() > 0:
            try:
                return self.get_pagination_total()
            except Exception:
                pass
        return self.vehicle_cards().count()

    # ------------------------------------------------------------- Groups

    def group_cards(self) -> Locator:
        # Confirmed live: each group card is an <article> starting with a
        # "commute" icon, the group name, its vehicle count, and an expand
        # chevron -- there's no dedicated custom element tag for groups
        # (unlike vehicle/driver cards). Alert cards are also <article>s, so
        # this must be filtered; a plain substring match on "commute" is
        # used rather than an anchored regex -- Playwright's has_text regex
        # has no multiline flag, so `^commute` only anchors to the very
        # start of the whole innerText (confirmed live: silently matches
        # nothing even though "commute" is really the card's first line).
        return self.page.locator("article").filter(has_text="commute")

    def group_card(self, group_name: str) -> Locator:
        return self.group_cards().filter(has_text=group_name).first

    def expand_group(self, group_name: str):
        self.group_card(group_name).locator("mat-icon", has_text="keyboard_arrow_down").click()
        self.wait_for_loading_to_finish()

    def collapse_group(self, group_name: str):
        self.group_card(group_name).locator("mat-icon", has_text="keyboard_arrow_up").click()
        self.wait_for_loading_to_finish()

    def group_vehicle_count(self, group_name: str) -> int:
        text = self.group_card(group_name).inner_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        # line 0 = icon text "commute", line 1 = group name, line 2 = count
        for line in lines[2:]:
            if line.isdigit():
                return int(line)
        return 0

    def group_status_filter(self, group_name: str, status_name: str) -> Locator:
        # No ^/$ anchors: Playwright's has_text/get_by_text regex has no
        # multiline flag, so an anchored pattern only matches the very
        # start/end of the whole card's flattened text -- these status
        # chips are never the first line (confirmed live: "Idle (2)" is
        # present verbatim in the card's own inner_text() dump, yet an
        # anchored regex times out finding it).
        return self.group_card(group_name).get_by_text(
            re.compile(rf"{re.escape(status_name)}\s*\(\d+\)")
        )

    def apply_group_status_filter(self, group_name: str, status_name: str):
        self.group_status_filter(group_name, status_name).click()
        self.wait_for_loading_to_finish()

    # ------------------------------------------------------------- Drivers

    def driver_cards(self) -> Locator:
        return self.page.locator("app-home-driver-card")

    def driver_card(self, driver_name: str) -> Locator:
        return self.driver_cards().filter(has_text=driver_name).first

    def open_driver_details(self, driver_name: str):
        # Confirmed live: unlike a vehicle card's more_vert (a dropdown
        # menu), a driver card's more_vert opens a full "Driver Information"
        # details dialog directly -- there's no intermediate menu.
        self.driver_card(driver_name).locator("button:has(mat-icon:text('more_vert'))").click(force=True)
        self.wait_for_visible(self.driver_details_dialog())

    def driver_details_dialog(self) -> Locator:
        return self.page.locator(".cdk-overlay-container").filter(has_text="Driver Information")

    def close_driver_details(self):
        self.driver_details_dialog().locator("button").filter(has_text="close").first.click()

    def driver_licence_status(self) -> str:
        # "Expired" / "Licence Valid" etc, shown next to "Driving Licence"
        # -- the whole line, since the status can be multiple words
        # (confirmed live: "Licence Valid" vs. a single-word "Expired").
        text = self.driver_details_dialog().inner_text()
        match = re.search(r"Driving Licence\n(.+)", text)
        return match.group(1).strip() if match else ""

    def click_change_vehicle_assignment(self):
        # Confirmed live: the button reads "Assign" for a driver with no
        # current vehicle, and "Change" once one is already assigned --
        # same dialog either way.
        dialog = self.driver_details_dialog()
        change_btn = dialog.get_by_role("button", name="Change")
        assign_btn = dialog.get_by_role("button", name="Assign", exact=True)
        (change_btn if change_btn.count() else assign_btn).click()
        self.wait_for_loading_to_finish()

    def driver_assignment_dialog(self) -> Locator:
        # Confirmed live: same "Driver Assignment" dialog pattern as the
        # Settings module's driver_page.py -- a "Select Vehicle" combobox,
        # an unlink/unassign icon, and a submit button labeled "Assign
        # Vehicle" on a driver's first-ever assignment or "Update
        # Assignment" once one already exists.
        return self.page.locator(".cdk-overlay-container").filter(has_text="Driver Assignment")

    def assignment_selected_vehicle(self) -> str:
        return self.driver_assignment_dialog().get_by_role("combobox", name="Select Vehicle").inner_text()

    def assignment_cancel(self):
        self.driver_assignment_dialog().get_by_role("button", name="Cancel").click()
        self.page.wait_for_timeout(500)  # dialog close animation

    def unassign_current_vehicle(self):
        # Confirmed live: reassigning an already-assigned driver to a
        # DIFFERENT vehicle is a two-step flow, not a single reselect --
        # this red icon button (aria-label "Unassign current vehicle",
        # matching the same pattern already used in the Settings module's
        # driver_page.py) must be clicked first. Only after that does the
        # dialog switch to its empty "Unassigned" state, where a new
        # vehicle can be picked and the submit button relabels to "Assign
        # Vehicle". Trying to just reselect a new vehicle while the old one
        # still shows and clicking "Update Assignment" does not work -- it
        # just re-shows the "already assigned to X" warning indefinitely.
        self.driver_assignment_dialog().get_by_role("button", name="Unassign current vehicle").click()
        self.page.wait_for_timeout(1000)

    def reassign_vehicle(self, vehicle_id: str):
        """Full reassignment flow for an already-assigned driver: unassign
        the current vehicle, then assign the new one."""
        self.unassign_current_vehicle()
        dialog = self.driver_assignment_dialog()
        dialog.get_by_label("Select Vehicle").click()
        self.page.wait_for_timeout(500)
        self.page.get_by_role("option", name=vehicle_id, exact=True).click()
        self.page.keyboard.press("Escape")
        self.page.wait_for_timeout(500)
        self.assignment_submit()

    def assignment_submit(self):
        dialog = self.driver_assignment_dialog()
        update_btn = dialog.get_by_role("button", name="Update Assignment")
        if update_btn.count() > 0:
            update_btn.click()
        else:
            dialog.get_by_role("button", name="Assign Vehicle").click()
        self.wait_for_loading_to_finish()
        self.page.wait_for_timeout(1000)
        self.wait_for_loading_to_finish()

    def click_driver_call(self, driver_name: str):
        self.driver_card(driver_name).locator("mat-icon", has_text="call").click()

    # ------------------------------------------------------------- Map

    def switch_to_map_mode(self):
        self.map_mode_button.click()
        self.wait_for_loading_to_finish()

    def switch_to_hybrid_mode(self):
        self.hybrid_mode_button.click()
        self.wait_for_loading_to_finish()

    def map_vehicle_marker(self, vehicle_id: str) -> Locator:
        return self.page.locator(
            f"[role='button'][title='{vehicle_id}'], [role='button'][aria-label='{vehicle_id}']"
        ).first

    # ------------------------------------------------------------- Alerts & Notifications

    def open_alerts_tab(self):
        self.alerts_tab_link.click()
        self.wait_for_loading_to_finish()

    def open_acknowledged_tab(self):
        self.acknowledged_tab_link.click()
        self.wait_for_loading_to_finish()

    def alert_cards(self) -> Locator:
        # Confirmed live: each alert is an <article class="tx-card-hover ...">
        # in the right-hand Alerts & Notifications panel (only the currently
        # rendered page of a possibly-larger list -- alerts_count() reflects
        # the true total, not necessarily this locator's .count()).
        return self.page.locator("article.tx-card-hover")

    def alerts_count(self) -> int:
        match = re.search(r"Alerts\s*\((\d+)\)", self.visible_text())
        return int(match.group(1)) if match else 0

    def acknowledged_count(self) -> int:
        match = re.search(r"Acknowledged\s*\((\d+)\)", self.visible_text())
        return int(match.group(1)) if match else 0

    def acknowledge_alert(self, index: int = 0):
        # Confirmed live: each alert card has a "done" (acknowledge) icon
        # and a "visibility" (view) icon. Acknowledging is a real, one-way
        # mutation on live data (no unacknowledge action was found) -- use
        # sparingly and only where the CSV genuinely requires it.
        self.alert_cards().nth(index).locator("mat-icon", has_text="done").click()
        self.wait_for_loading_to_finish()

    def view_alert(self, index: int = 0):
        self.alert_cards().nth(index).locator("mat-icon", has_text="visibility").click()
        self.wait_for_loading_to_finish()

    def click_view_all_alerts(self):
        self.view_all_alerts_link.click()
        self.wait_for_loading_to_finish()

    def click_live_alerts(self):
        self.live_alerts_button.click()
        self.wait_for_loading_to_finish()

    # ------------------------------------------------------------- GeoLinks

    def open_geolinks(self):
        if self.geolinks_dialog().is_visible():
            return
        self.geolink_button.click(force=True)
        self.wait_for_loading_to_finish()
        try:
            self.wait_for_visible(self.geolinks_dialog())
        except PlaywrightTimeoutError:
            # One bounded self-heal retry, matching the pattern already
            # established for the KPI Settings dialog's occasional stalled
            # open under this much back-to-back live interaction.
            self.geolink_button.click(force=True)
            self.wait_for_visible(self.geolinks_dialog())

    def geolinks_dialog(self) -> Locator:
        # Confirmed live: the panel's own heading text switches between
        # "Geo Links" (list view) and "Create GeoLink" (create-form view),
        # so a fixed-text filter that only matches one breaks on the other.
        return self.page.locator(".cdk-overlay-container").filter(
            has_text=re.compile(r"Geo\s*Links|GeoLink")
        )

    def geolinks_count(self) -> int:
        match = re.search(r"(\d+)\s*links?", self.geolinks_dialog().inner_text())
        return int(match.group(1)) if match else 0

    def geolink_row(self, title: str) -> Locator:
        return self.geolinks_dialog().locator("tr, [role='row']").filter(has_text=title)

    def close_geolinks(self):
        self.geolinks_dialog().locator("button").filter(has_text="close").first.click()

    def click_create_geolink(self):
        # Confirmed live: "Create GeoLink" is only the empty-state's own
        # call-to-action button, present exclusively when the list has 0
        # links. "New GeoLink" is the persistent trigger at the top of the
        # panel that exists regardless of list state -- use it, since it
        # works in both cases (the empty-state's own "Create GeoLink" button
        # simply doesn't exist once >=1 link exists, which caused every
        # create attempt to time out for an account with any existing
        # links).
        create_btn = self.geolinks_dialog().get_by_role("button", name="New GeoLink")
        try:
            create_btn.click(timeout=10000)
        except PlaywrightTimeoutError:
            # A loading spinner can transiently intercept this click under
            # heavy back-to-back load -- one bounded self-heal retry.
            create_btn.click()
        self.wait_for_visible(self.geolinks_dialog().get_by_label("Share name"))

    def fill_geolink_share_name(self, name: str):
        self.geolinks_dialog().get_by_label("Share name").fill(name)

    def select_geolink_vehicle(self, vehicle_id: str):
        dialog = self.geolinks_dialog()
        dialog.get_by_label("Select Vehicles").click()
        self.page.get_by_role("option", name=vehicle_id).click()
        # The mat-select dropdown's own transparent backdrop stays open and
        # intercepts clicks elsewhere in the form until dismissed -- Escape
        # is the standard way to close a Material multi-select overlay.
        self.page.keyboard.press("Escape")

    def fill_geolink_start(self, date_value: str, time_value: str):
        self.geolinks_dialog().get_by_label("Start date").fill(date_value)
        self.geolinks_dialog().get_by_label("Start time").fill(time_value)

    def fill_geolink_expiry(self, days: int = 0, hours: int = 1):
        self.geolinks_dialog().get_by_label("Expiry days").fill(str(days))
        self.geolinks_dialog().get_by_label("Expiry hours").fill(str(hours))

    def select_geolink_access(self, level: str):
        # level: "Map only" or "Map and details"
        self.geolinks_dialog().get_by_text(level, exact=True).click()

    def submit_geolink_form(self):
        self.geolinks_dialog().get_by_role("button", name="Create", exact=True).click()
        self.wait_for_loading_to_finish()

    def cancel_geolink_form(self):
        self.geolinks_dialog().get_by_role("button", name="Cancel", exact=True).click()

    def geolink_create_button_enabled(self) -> bool:
        return self.geolinks_dialog().get_by_role("button", name="Create", exact=True).is_enabled()

    def get_geolink_share_url(self) -> str:
        # After Create, a "Share GeoLink" panel appears showing the public
        # tracking URL -- confirmed live at .../geolink/redirect?token=...
        text = self.geolinks_dialog().inner_text()
        match = re.search(r"https://\S+/geolink/redirect\?token=\S+", text)
        return match.group(0) if match else ""

    def cancel_geolink_share_panel(self):
        self.geolinks_dialog().get_by_role("button", name="Cancel").click()
        self.page.wait_for_timeout(500)

    def delete_geolink(self, title: str):
        # Two-step confirmation (confirmed live): the row's delete icon
        # opens a "Delete Geolink" confirmation dialog; the mutation only
        # happens once "Delete" inside that dialog is clicked too. The row
        # removal itself lags the confirm click a little (confirmed live)
        # -- poll for it instead of a fixed sleep.
        self.geolink_row(title).first.locator("mat-icon", has_text="delete_outline").click()
        self.wait_for_loading_to_finish()
        confirm_dialog = self.page.locator(".cdk-overlay-container").last
        confirm_dialog.get_by_role("button", name="Delete", exact=True).click()
        self.wait_for_loading_to_finish()
        for _ in range(15):
            if self.geolink_row(title).count() == 0:
                return
            self.page.wait_for_timeout(500)
