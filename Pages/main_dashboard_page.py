import re
from datetime import datetime, timedelta
from playwright.sync_api import Locator, Page
from Pages.base_page import BasePage


class MainDashboardPage(BasePage):
    """Page object for the main Trackofy application Dashboard tab (/dashboard/graphical)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self._last_date_filter_request: dict | None = None

        # Header and Top Controls
        self.dashboard_heading = page.get_by_role("heading", name="Dashboard", exact=True)
        self.graphical_view_button = page.get_by_role("button", name=re.compile(r"Graphical", re.I)).first
        self.tabular_view_button = page.get_by_role("button", name=re.compile(r"Tabular", re.I)).first
        self.refresh_dashboard_button = page.get_by_role("button", name=re.compile(r"Refresh dashboard", re.I)).first
        self.ai_insights_button = page.get_by_role("button", name=re.compile(r"AI Insights", re.I)).first
        self.widgets_button = page.locator("button").filter(has_text=re.compile(r"Widgets", re.I)).first
        self.trash_button = page.locator("button").filter(has_text=re.compile(r"Trash", re.I)).first

        # Top Summary KPI Cards
        self.total_fleet_metric = page.get_by_text("Total Fleet", exact=True).first
        self.active_devices_metric = page.get_by_text("Active Devices", exact=True).first
        self.running_devices_metric = page.get_by_text("Running", exact=True).first
        self.idle_devices_metric = page.get_by_text("Idle", exact=True).first
        self.stopped_devices_metric = page.get_by_text("Stopped", exact=True).first
        self.no_data_devices_metric = page.get_by_text("No Data", exact=True).first
        self.expired_devices_metric = page.get_by_text("Expired Devices", exact=True).first
        self.bms_enabled_metric = page.get_by_text("BMS Enabled", exact=True).first
        self.video_enabled_metric = page.get_by_text("Video Enabled", exact=True).first

        # Store & Drawer Overlays
        self.widget_store_heading = page.get_by_role("heading", name=re.compile(r"Widget Stores", re.I)).first
        self.close_widget_store_button = page.get_by_role("button", name=re.compile(r"Close widget stores", re.I)).first
        self.fleet_widget_store_link = page.get_by_role("link", name=re.compile(r"Fleet Widget Store", re.I)).first
        self.bms_widget_store_link = page.get_by_role("link", name=re.compile(r"BMS Widget Store", re.I)).first
        self.video_telematics_store_link = page.get_by_role("link", name=re.compile(r"Video Telematics", re.I)).first

    def open_graphical_dashboard(self):
        """Navigate directly to the graphical dashboard route."""
        self.page.goto("/dashboard/graphical")
        self.wait_for_dashboard_ready()

    def open_tabular_dashboard(self):
        """Navigate directly to the tabular / live dashboard route."""
        self.page.goto("/dashboard/live")
        self.wait_until_ready()

    def wait_for_dashboard_ready(self):
        """Wait until the main dashboard container and KPI section are fully loaded."""
        self.page.wait_for_url(re.compile(r".*/dashboard/(graphical|live|tabular)?.*$"), timeout=15000)
        self.wait_until_ready()
        self.wait_for_visible(self.dashboard_heading)

    def switch_to_tabular_view(self):
        """Click on Tabular view button."""
        self.wait_for_visible(self.tabular_view_button)
        self.tabular_view_button.click()
        self.wait_until_ready()

    def switch_to_graphical_view(self):
        """Click on Graphical view button."""
        self.wait_for_visible(self.graphical_view_button)
        self.graphical_view_button.click()
        self.wait_until_ready()

    def refresh_dashboard(self):
        """Click on Refresh dashboard button and wait for reload."""
        self.wait_for_visible(self.refresh_dashboard_button)
        self.refresh_dashboard_button.click()
        self.wait_for_loading_to_finish()

    def get_widget_titles_order(self) -> list[str]:
        """Extract order of visible widget card headings on the dashboard."""
        self.wait_until_ready()
        headings = self.page.locator("main h2, main h3, [class*='card'] h2").all()
        titles: list[str] = []
        for h in headings:
            if h.is_visible():
                txt = h.inner_text().strip()
                if txt and txt not in {"Dashboard", "Widget Stores", "Build your dashboard", "Actions"}:
                    titles.append(txt)
        return titles

    def drag_and_drop_widget(self, source_title: str, target_title: str):
        """Drag a widget card handle onto a target widget card position."""
        source_heading = self.page.get_by_role("heading", name=source_title, exact=True).first
        target_heading = self.page.get_by_role("heading", name=target_title, exact=True).first
        self.wait_for_visible(source_heading)
        self.wait_for_visible(target_heading)

        source_card = source_heading.locator("xpath=ancestor::*[contains(@class, 'card') or contains(@class, 'grid') or contains(@class, 'wrapper')][position()<=4]").last
        target_card = target_heading.locator("xpath=ancestor::*[contains(@class, 'card') or contains(@class, 'grid') or contains(@class, 'wrapper')][position()<=4]").last

        source_handle = source_card.locator(".grid-drag-handle, [aria-label*='Reorder'], mat-icon:has-text('open_with')").first
        if not source_handle.is_visible():
            source_handle = source_card

        source_handle.drag_to(target_card)
        self.wait_for_loading_to_finish()

    def open_widget_store(self):
        """Click Widgets button to open Widget Store drawer."""
        self.wait_for_visible(self.widgets_button)
        self.widgets_button.click()
        self.wait_for_visible(self.widget_store_heading)

    def close_widget_store(self):
        """Close Widget Store drawer."""
        if self.close_widget_store_button.is_visible():
            self.close_widget_store_button.click()
        else:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def open_trash_store(self):
        """Click Trash button to navigate to the Trash Store page (/trash)."""
        self.wait_for_visible(self.trash_button)
        self.trash_button.click()
        self.wait_for_visible(self.page.get_by_role("heading", name=re.compile(r"Trash Store", re.I)))
        self.wait_for_loading_to_finish()

    def _is_on_trash_store(self) -> bool:
        return self.page.get_by_role("heading", name=re.compile(r"Trash Store", re.I)).first.is_visible()

    def open_ai_insights(self):
        """Click AI Insights button in header."""
        self.wait_for_visible(self.ai_insights_button)
        self.ai_insights_button.click()
        self.wait_for_loading_to_finish()

    def get_widget_column_header(self, widget_title: str, column_name: str) -> Locator:
        """Get column header locator for a given table column."""
        header = self.page.locator("th, [role='columnheader']").filter(has_text=column_name).first
        return header

    def click_column_header_to_sort(self, widget_title: str, column_name: str):
        """Click a widget table column header to toggle sorting (Ascending / Descending)."""
        header = self.get_widget_column_header(widget_title, column_name)
        self.wait_for_visible(header)
        header.click()
        self.wait_for_loading_to_finish()

    def get_widget_table_column_values(self, widget_title: str, column_name: str) -> list[str]:
        """Extract visible cell values under a given column in a widget table."""
        rows = self.page.locator("tbody tr, table tr").all()
        values: list[str] = []
        for r in rows:
            cells = r.locator("td, [role='cell']").all()
            if cells:
                txt = cells[0].inner_text().strip()
                if txt and txt != "No data available" and txt != "No data found":
                    values.append(txt)
        return values

    def open_widget_filter(self, widget_title: str):
        """Click the Filter widget data icon button on a widget card."""
        filter_button = self.page.locator("button").filter(has=self.page.locator("mat-icon:has-text('filter_alt'), img[alt*='filter']")).first
        self.wait_for_visible(filter_button)
        filter_button.click()
        self.wait_for_loading_to_finish()

    # ─── Card Helpers ──────────────────────────────────────────────────────────────

    def get_all_card_titles(self) -> list[str]:
        """Return list of all visible widget card title texts."""
        self.wait_until_ready()
        headings = self.page.locator("main h2, main h3, [class*='card'] h2").all()
        titles = []
        for h in headings:
            if h.is_visible():
                txt = h.inner_text().strip()
                if txt and txt not in {"Dashboard", "Widget Stores", "Build your dashboard", "Actions"}:
                    titles.append(txt)
        return titles

    def get_card_locator(self, title: str):
        """Return the container locator for a widget card by its heading title.

        ponytail: get_by_role(exact=True), not a \\b...\\b regex, ^...$ regex, or plain
        has_text substring -- \\b fails on titles ending in punctuation (e.g. "SOC
        Status [BMS]"); Locator.filter's has_text regex matches raw unnormalized text
        so ^...$ can miss too; and a plain has_text substring can wrongly match a
        different card whose title contains this one (e.g. "Alerts" inside "Adas
        Alerts"). get_by_role's computed accessible name is normalized AND exact.
        """
        heading = self.page.get_by_role("heading", name=title, exact=True).first
        return heading.locator("xpath=ancestor::*[contains(@class, 'card') or contains(@class, 'grid') or contains(@class, 'wrapper')][position()<=4]").last

    def get_card_record_count(self, title: str) -> int:
        """Return the integer record count shown on a widget card. Returns -1 if not found."""
        card = self.get_card_locator(title)
        text = card.inner_text()
        match = re.search(r"(\d+)\s*(records|Total Vehicles)", text, re.I)
        if match:
            return int(match.group(1))
        badges = card.locator("span, .badge, .count").all()
        for b in badges:
            if b.is_visible():
                val = b.inner_text().strip()
                if val.isdigit():
                    return int(val)
        return -1

    def card_is_visible(self, title: str) -> bool:
        """Return True if a card with the given title is visible on the dashboard."""
        heading = self.page.get_by_role("heading", name=title, exact=True).first
        return heading.is_visible()

    def click_card_view_details(self, title: str):
        """Click View details button on the named card."""
        card = self.get_card_locator(title)
        btn = card.get_by_role("button", name=re.compile(r"View details", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def open_card_actions_menu(self, title: str):
        """Click More widget actions dropdown on the named card.

        Closes any menu already open first: 'Edit'/'Add to Trash' are matched
        unscoped (self.page) by callers, so a still-open previous menu's items
        can otherwise be matched instead of the freshly-opened one -- especially
        when trashing several cards back-to-back.
        """
        self.page.keyboard.press("Escape")
        card = self.get_card_locator(title)
        btn = card.get_by_role("button", name=re.compile(r"More widget actions", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def click_card_edit(self, title: str):
        """Open the Edit settings panel for a named card via the actions dropdown."""
        self.open_card_actions_menu(title)
        edit_btn = self.page.get_by_role("button", name=re.compile(r"Edit", re.I)).first
        self.wait_for_visible(edit_btn)
        edit_btn.click()
        self.wait_for_loading_to_finish()

    def click_add_to_trash(self, title: str):
        """Click Add to Trash for a named card via the actions dropdown and confirm.

        Clicking 'Add to Trash' opens a 'Move to Trash' confirmation dialog; the
        card is only actually trashed once 'Move' is clicked there. Waits for a
        matching card heading to disappear (not just the dialog) so the dashboard
        grid has settled before a caller acts on the next card -- counted rather
        than a single .first locator, since duplicate card titles do occur (e.g.
        two cards both named "Alerts") and .first isn't guaranteed to track the
        specific instance that was just trashed.
        """
        heading = self.page.get_by_role("heading", name=title, exact=True)
        count_before = heading.count()
        self.open_card_actions_menu(title)
        trash_btn = self.page.get_by_role("button", name=re.compile(r"Add to Trash", re.I)).first
        self.wait_for_visible(trash_btn)
        trash_btn.click()
        confirm_dialog = self.page.get_by_role("dialog", name=re.compile(r"Move to Trash", re.I))
        self.wait_for_visible(confirm_dialog)
        confirm_dialog.get_by_role("button", name=re.compile(r"^Move$", re.I)).click()
        self.wait_for_dialog_closed()
        self.wait_for_loading_to_finish()
        for _ in range(int(self.DEFAULT_TIMEOUT_MS / 500)):
            if heading.count() < count_before:
                break
            self.page.wait_for_timeout(500)

    def get_card_table_headers(self, title: str) -> list[str]:
        """Return column header texts from the table in the named widget card."""
        card = self.get_card_locator(title)
        headers = card.locator("th, [role='columnheader']").all()
        return [h.inner_text().strip() for h in headers if h.is_visible() and h.inner_text().strip()]

    def get_card_table_row_count(self, title: str) -> int:
        """Return number of data rows in the table of the named widget card."""
        card = self.get_card_locator(title)
        rows = card.locator("tbody tr, table tr").all()
        return len([r for r in rows if r.is_visible() and "No data" not in r.inner_text()])

    # ─── Card Settings (Edit Panel) ───────────────────────────────────────────────
    # The "Edit" action opens an inline "Widget Settings" panel (not a modal dialog),
    # anchored by an <h3>"Widget Settings" heading inside its own <main> container.
    # Chart Type / Sorting are mat-select comboboxes whose option lists render in a
    # portaled overlay at the page root, so those options are queried on self.page.

    def _settings_panel(self) -> Locator:
        """Return the container for the currently open Widget Settings panel."""
        heading = self.page.get_by_role("heading", name=re.compile(r"Widget Settings", re.I)).first
        return heading.locator("xpath=ancestor::main[1]")

    def set_card_name(self, name: str):
        """Fill the Widget Title input in the settings panel."""
        inp = self._settings_panel().get_by_role("textbox", name=re.compile(r"Widget Title", re.I)).first
        self.wait_for_visible(inp)
        inp.fill(name)

    def get_card_name_value(self) -> str:
        """Read current value from the Widget Title input in the settings panel."""
        inp = self._settings_panel().get_by_role("textbox", name=re.compile(r"Widget Title", re.I)).first
        self.wait_for_visible(inp)
        return inp.input_value()

    def click_save_settings(self):
        """Click 'Update Widget' in the card settings panel and wait for it to close."""
        heading = self.page.get_by_role("heading", name=re.compile(r"Widget Settings", re.I)).first
        btn = self._settings_panel().get_by_role("button", name=re.compile(r"Update Widget", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_hidden(heading)
        self.wait_for_loading_to_finish()

    def click_cancel_settings(self):
        """Click Cancel in the card settings panel and wait for it to close.

        The panel's "Widget Preview" reflects field edits live, so a caller
        checking card state right after Cancel must wait for the panel to
        actually unmount rather than just the click resolving.
        """
        heading = self.page.get_by_role("heading", name=re.compile(r"Widget Settings", re.I)).first
        btn = self._settings_panel().get_by_role("button", name=re.compile(r"^Cancel$", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_hidden(heading)
        self.wait_for_loading_to_finish()

    def select_chart_type(self, chart_type: str):
        """Select a chart type (Bar, Line, Spline, Area, Areaspline, Scatter) via the Chart Type mat-select."""
        combo = self._settings_panel().get_by_role("combobox", name=re.compile(r"Chart Type", re.I)).first
        self.wait_for_visible(combo)
        combo.click()
        option = self.page.get_by_role("option", name=chart_type, exact=True).first
        self.wait_for_visible(option)
        option.click()

    def set_sort_direction(self, direction: str):
        """Select Ascending or Descending sort order via the Sorting mat-select."""
        option_text = "Desc" if re.match(r"desc", direction, re.I) else "Asc"
        combo = self._settings_panel().get_by_role("combobox", name=re.compile(r"Sorting", re.I)).first
        self.wait_for_visible(combo)
        combo.click()
        option = self.page.get_by_role("option", name=option_text, exact=True).first
        self.wait_for_visible(option)
        option.click()

    def set_chart_color(self, hex_color: str):
        """Fill the 'Select chart color' hex input in the settings panel."""
        inp = self._settings_panel().get_by_role("textbox", name=re.compile(r"Select chart color", re.I)).first
        self.wait_for_visible(inp)
        inp.fill(hex_color)

    def get_chart_color(self) -> str:
        """Read the current value of the chart color input in the settings panel."""
        inp = self._settings_panel().get_by_role("textbox", name=re.compile(r"Select chart color", re.I)).first
        return inp.input_value()

    def toggle_column_in_settings(self, column_name: str, check: bool | None = None):
        """Toggle a table-column checkbox in the card settings panel."""
        cb = self._settings_panel().get_by_role("checkbox", name=re.compile(rf"^{re.escape(column_name)}$", re.I)).first
        self.wait_for_visible(cb)
        is_checked = cb.is_checked()
        if check is True and not is_checked:
            cb.check()
        elif check is False and is_checked:
            cb.uncheck()
        elif check is None:
            cb.click()

    # ─── Card Date Filter ──────────────────────────────────────────────────────────

    def open_card_date_filter(self, card_title: str):
        """Click Filter widget data on a named card."""
        card = self.get_card_locator(card_title)
        btn = card.get_by_role("button", name=re.compile(r"Filter widget data", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def select_card_date_option(self, option: str):
        """Click a date option and capture the resulting card-data API request.

        The date-filter buttons expose no active/selected state in the DOM (no
        aria-pressed, no distinguishing class), so the applied range can only be
        verified via the from_date/to_date the card's data request actually used.
        """
        btn = self.page.get_by_role("button", name=re.compile(rf"^{re.escape(option)}$", re.I)).first
        self.wait_for_visible(btn)
        try:
            with self.page.expect_request(
                lambda r: "dashborad.php" in r.url and r.method == "POST", timeout=self.DEFAULT_TIMEOUT_MS
            ) as req_info:
                btn.click()
            import json
            self._last_date_filter_request = json.loads(req_info.value.post_data or "{}")
        except Exception:
            btn.click()
            self._last_date_filter_request = None
        self.wait_for_loading_to_finish()

    def get_active_card_date_label(self) -> str:
        """Infer the applied date-range label from the last card-filter API request.

        ponytail: there is no accessible UI indicator of the selected range, so this
        derives the label from the from_date/to_date actually sent to the server.
        """
        if not self._last_date_filter_request:
            return ""
        try:
            from_date = datetime.strptime(self._last_date_filter_request["from_date"][:10], "%Y-%m-%d").date()
            to_date = datetime.strptime(self._last_date_filter_request["to_date"][:10], "%Y-%m-%d").date()
        except (KeyError, ValueError):
            return ""
        today = datetime.now().date()
        if from_date == today and to_date == today:
            return "Today"
        if from_date == today - timedelta(days=1) and to_date == from_date:
            return "Yesterday"
        if from_date == today - timedelta(days=6) and to_date == today:
            return "Last 7 Days"
        if from_date == today.replace(day=1) and to_date == today:
            return "This Month"
        return f"{from_date} to {to_date}"

    # ─── Global Filter ─────────────────────────────────────────────────────────────

    def open_global_filter(self):
        """Click Filter dashboard button."""
        btn = self.page.get_by_role("button", name=re.compile(r"Filter dashboard", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def select_global_filter_quick_range(self, option: str):
        """Click a Quick range date option (Today/Yesterday/Last 7 days/This Month).

        The global filter's Apply button stays disabled until a quick range is
        selected -- the unit/vehicle picker is optional (labelled "Unit (optional)").
        """
        dlg = self.page.get_by_role("dialog").filter(has_text="Filter dashboard")
        btn = dlg.get_by_role("button", name=re.compile(rf"^{re.escape(option)}$", re.I)).first
        self.wait_for_visible(btn)
        btn.click()

    def select_global_filter_vehicle(self, vehicle_name: str):
        """Select a vehicle/unit in the global filter's 'All units' combobox.

        Opening it renders a portaled listbox (role=listbox, name 'All units') with
        a 'Search unit' textbox and one option per vehicle/unit id.
        """
        combo = self.page.get_by_role("combobox", name=re.compile(r"All units", re.I)).first
        self.wait_for_visible(combo)
        combo.click()
        listbox = self.page.get_by_role("listbox", name=re.compile(r"All units", re.I))
        self.wait_for_visible(listbox)
        try:
            search = listbox.get_by_role("textbox", name=re.compile(r"Search unit", re.I))
            search.fill(vehicle_name)
            option = listbox.get_by_role("option", name=vehicle_name, exact=True).first
            self.wait_for_visible(option)
            option.click()
        finally:
            # The listbox overlay (and its backdrop) stays open after picking an
            # option -- or after a failed search/click above -- and sits on top of
            # the dialog's Apply button; Escape is the only thing that reliably
            # collapses it, and this must run even on failure so a caller's
            # try/except around an invalid vehicle_name doesn't leave the overlay
            # (and its backdrop) stuck blocking every click after it.
            self.page.keyboard.press("Escape")
            try:
                self.wait_for_hidden(listbox)
                # The cdk-overlay backdrop can still be mid-fade (present but
                # non-interactive to us, yet intercepting real clicks) for a moment
                # after the listbox itself reports hidden; give it a beat to finish.
                self.page.locator(".cdk-overlay-backdrop-showing").first.wait_for(
                    state="detached", timeout=self.SHORT_TIMEOUT_MS
                )
            except Exception:
                pass

    def apply_global_filter(self):
        """Click Apply in the global filter panel."""
        btn = self.page.get_by_role("button", name=re.compile(r"^Apply$", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def clear_global_filter(self):
        """Click Reset button in the global filter panel."""
        btn = self.page.get_by_role("button", name=re.compile(r"^Reset$", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    def close_global_filter(self):
        """Close the global filter panel via its 'Close filter' button."""
        btn = self.page.get_by_role("button", name=re.compile(r"Close filter", re.I)).first
        if btn.is_visible():
            btn.click()
        else:
            self.page.keyboard.press("Escape")
        self.wait_for_loading_to_finish()

    def is_global_filter_active(self) -> bool:
        """Return True if a global filter is currently applied.

        The 'Filter dashboard' header button switches to a highlighted
        `bg-(--mat-sys-primary-container)` base class once a filter is applied;
        there's no separate chip/badge element for this in the DOM. Must match
        that exact class token, not a substring -- the button's unapplied state
        also carries a `hover:bg-(--mat-sys-primary-container)` variant class,
        which contains the same substring but only takes effect on hover.
        """
        btn = self.page.get_by_role("button", name=re.compile(r"Filter dashboard", re.I)).first
        classes = (btn.get_attribute("class") or "").split()
        return "bg-(--mat-sys-primary-container)" in classes

    # ─── Widget Store ──────────────────────────────────────────────────────────────

    def open_fleet_store(self):
        """Open Fleet Widget Store tab in the widget store drawer."""
        self.wait_for_visible(self.fleet_widget_store_link)
        self.fleet_widget_store_link.click()
        self.wait_for_loading_to_finish()

    def open_bms_store(self):
        """Open BMS Widget Store tab."""
        self.wait_for_visible(self.bms_widget_store_link)
        self.bms_widget_store_link.click()
        self.wait_for_loading_to_finish()

    def open_video_telematics_store(self):
        """Open Video Telematics Store tab."""
        self.wait_for_visible(self.video_telematics_store_link)
        self.video_telematics_store_link.click()
        self.wait_for_loading_to_finish()

    def get_store_widget_names(self) -> list[str]:
        """Return names of all widgets listed in the currently open store page.

        A store can legitimately be empty (e.g. Video Telematics on some
        accounts), so this waits briefly for content to settle without treating
        "nothing there" as an error.
        """
        try:
            self.page.locator("main article").get_by_role("heading").first.wait_for(
                state="visible", timeout=self.SHORT_TIMEOUT_MS
            )
        except Exception:
            pass
        items = self.page.locator("main article").get_by_role("heading").all()
        return [i.inner_text().strip() for i in items if i.is_visible()]

    def add_widget_from_store(self, widget_name: str):
        """Click 'Add to Dashboard' for a named widget's layout card in the store.

        A widget already on the dashboard shows its layout(s) as Locked with no
        Add button, so this picks the first layout that still has one available.
        """
        item = self.page.locator("main article").filter(
            has=self.page.get_by_role("heading", name=re.compile(rf"^{re.escape(widget_name)}$", re.I))
        ).first
        btn = item.get_by_role("button", name=re.compile(r"Add to Dashboard", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()

    # ─── Trash ────────────────────────────────────────────────────────────────────

    def get_trash_items(self) -> list[str]:
        """Return list of widget names currently on the Trash Store page.

        Requires open_trash_store() to have been called first.
        """
        articles = self.page.locator("article").filter(has_text=re.compile(r"In Trash", re.I))
        names = []
        for i in range(articles.count()):
            heading = articles.nth(i).get_by_role("heading").first
            if heading.is_visible():
                names.append(heading.inner_text().strip())
        return names

    def restore_from_trash(self, title: str):
        """Restore a named card from Trash via its 'Add to Dashboard' button.

        Navigates to the Trash Store page if not already there, and returns to the
        graphical dashboard afterwards so callers can assert on dashboard state.
        """
        if not self._is_on_trash_store():
            self.open_trash_store()
        item = self.page.locator("article").filter(
            has=self.page.get_by_role("heading", name=re.compile(rf"^{re.escape(title)}$", re.I))
        ).first
        btn = item.get_by_role("button", name=re.compile(r"Add to Dashboard", re.I)).first
        self.wait_for_visible(btn)
        btn.click()
        self.wait_for_loading_to_finish()
        self.open_graphical_dashboard()

    def count_visible_cards(self) -> int:
        """Count how many widget card headings are currently visible on the dashboard."""
        return len(self.get_all_card_titles())
