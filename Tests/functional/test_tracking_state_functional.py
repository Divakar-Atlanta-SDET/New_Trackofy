import pytest
from playwright.sync_api import expect


@pytest.mark.functional
def test_trk_state_001_live_to_playback_split_screen_isolated(tracking):
    """TRK-STATE-001: Functional - Live -> Playback: Playback uses its own Split Screen state."""
    tracking.select_split_screen("Yes")
    expect(tracking.split_screen_select).to_contain_text("Yes")

    tracking.switch_to_playback_tracking()
    # Playback has its own independent Split Screen control -- confirmed live
    # it defaults to "No" regardless of what Live was just set to.
    expect(tracking.split_screen_select).to_contain_text("No")


@pytest.mark.functional
def test_trk_state_002_playback_to_live_vehicle_selection_isolated(tracking):
    """TRK-STATE-002: Functional - Playback -> Live: Live's own vehicle selection isn't leaked from Playback."""
    tracking.switch_to_playback_tracking()
    if tracking.available_vehicle_count() == 0:
        pytest.skip("No vehicles available on this account")
    tracking.select_vehicle_by_index(0)
    expect(tracking.load_playback_btn).to_be_enabled()

    tracking.switch_to_live_tracking()
    # Live's own Start Tracking must not be falsely enabled by Playback's pick.
    expect(tracking.start_tracking_btn).to_be_disabled()
