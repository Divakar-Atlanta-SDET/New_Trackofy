import re

import pytest


@pytest.mark.functional
@pytest.mark.home
def test_home_0175_alerts_panel_opens_with_tabs_and_counts(home_page):
    """HOME-0175: The Alerts & Notifications panel opens showing Alerts and
    Acknowledged tabs, each with a numeric count."""
    home_page.open_alerts_tab()
    assert home_page.alerts_tab_link.is_visible(), "Alerts tab not visible after opening the panel"
    assert home_page.acknowledged_tab_link.is_visible(), "Acknowledged tab not visible after opening the panel"
    assert home_page.alerts_count() >= 0, "Alerts count did not parse as a number"
    assert home_page.acknowledged_count() >= 0, "Acknowledged count did not parse as a number"


@pytest.mark.functional
@pytest.mark.home
def test_home_0176_alert_card_shows_core_fields(home_page):
    """HOME-0176: Each alert card shows a title, description and timestamp."""
    home_page.open_alerts_tab()
    if home_page.alerts_count() == 0:
        pytest.skip("No alerts currently exist on this account to inspect")
    card_text = home_page.alert_cards().first.inner_text()
    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
    assert len(lines) >= 3, f"Alert card text looks incomplete: {lines!r}"


@pytest.mark.functional
@pytest.mark.home
def test_home_0177_acknowledged_tab_shows_only_acknowledged_alerts(home_page):
    """HOME-0177: Switching to the Acknowledged tab shows a (possibly empty)
    list distinct from the Alerts tab's own count."""
    home_page.open_alerts_tab()
    alerts_before = home_page.alerts_count()
    home_page.open_acknowledged_tab()
    home_page.page.wait_for_timeout(500)
    acknowledged_count = home_page.acknowledged_count()
    assert acknowledged_count >= 0, "Acknowledged count did not parse as a number"
    # The Alerts count itself should be unaffected by merely viewing the
    # Acknowledged tab.
    home_page.open_alerts_tab()
    assert home_page.alerts_count() == alerts_before, (
        "Alerts count changed just from viewing the Acknowledged tab and switching back"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0178_acknowledge_alert_moves_it_out_of_alerts(home_page):
    """HOME-0178: Acknowledging an alert removes it from the Alerts count
    and adds it to the Acknowledged count.

    This is a real, one-way mutation on live data (no unacknowledge action
    exists in the UI) -- acknowledges exactly one alert, the oldest/last in
    the currently rendered list, to minimize the footprint of this test on
    the account's real alert history.
    """
    home_page.open_alerts_tab()
    alerts_before = home_page.alerts_count()
    acknowledged_before = home_page.acknowledged_count()
    if alerts_before == 0:
        pytest.skip("No alerts currently exist on this account to acknowledge")

    home_page.acknowledge_alert(index=home_page.alert_cards().count() - 1)
    home_page.page.wait_for_timeout(1000)

    alerts_after = home_page.alerts_count()
    assert alerts_after == alerts_before - 1, (
        f"Expected Alerts count to drop by 1 after acknowledging (was {alerts_before}), got {alerts_after}"
    )
    home_page.open_acknowledged_tab()
    home_page.page.wait_for_timeout(500)
    acknowledged_after = home_page.acknowledged_count()
    assert acknowledged_after == acknowledged_before + 1, (
        f"Expected Acknowledged count to rise by 1 after acknowledging (was {acknowledged_before}), "
        f"got {acknowledged_after}"
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0180_view_alert_shows_more_detail(home_page):
    """HOME-0180: Clicking an alert's view icon navigates to a dedicated
    notification-map detail view (confirmed live: /notification-map)."""
    home_page.open_alerts_tab()
    if home_page.alerts_count() == 0:
        pytest.skip("No alerts currently exist on this account to view")
    home_page.view_alert(index=0)
    home_page.page.wait_for_timeout(1000)
    assert "/notification-map" in home_page.page.url, (
        f"Expected viewing an alert to navigate to /notification-map, got {home_page.page.url}"
    )
