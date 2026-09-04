import pytest
from playwright.sync_api import expect


@pytest.mark.positive
def test_set_135_toggle_ais_subalert_persists(ais_alert_page):
    """SET-135/137: toggling a sub-alert on and saving persists after
    reopening the dialog; toggling it back off restores the original state."""
    ais_alert_page.open_edit_for_row(0)
    toggle = ais_alert_page.toggles().first
    was_checked = toggle.get_attribute("aria-checked") == "true"

    try:
        toggle.click()
        ais_alert_page.page.wait_for_timeout(300)
        expect(ais_alert_page.update_btn).to_be_enabled()
        ais_alert_page.update_btn.click()
        ais_alert_page.wait_for_dialog_closed()

        ais_alert_page.open_edit_for_row(0)
        reopened_toggle = ais_alert_page.toggles().first
        expect(reopened_toggle).to_have_attribute("aria-checked", str(not was_checked).lower())
    finally:
        toggle_again = ais_alert_page.toggles().first
        if (toggle_again.get_attribute("aria-checked") == "true") != was_checked:
            toggle_again.click()
            ais_alert_page.page.wait_for_timeout(300)
            ais_alert_page.update_btn.click()
            ais_alert_page.wait_for_dialog_closed()
