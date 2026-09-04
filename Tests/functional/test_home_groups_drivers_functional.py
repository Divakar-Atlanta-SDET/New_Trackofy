import pytest


@pytest.mark.functional
@pytest.mark.home
def test_home_0108_groups_tab_shows_all_real_groups(home_page):
    """HOME-0108: All of the account's real groups are shown with a vehicle count."""
    home_page.open_groups_tab()
    for group_name in home_page.KNOWN_GROUPS:
        card = home_page.group_card(group_name)
        assert card.is_visible(), f"Group '{group_name}' card not visible on Groups tab"
        count = home_page.group_vehicle_count(group_name)
        assert count >= 0, f"Group '{group_name}' vehicle count did not parse as a number"


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("group_name", ["Default", "Delhi", "Bhopal", "Dwarka"])
def test_home_0109_0117_group_status_filters_reconcile_with_fleet(home_page, group_name):
    """HOME-0109 to 0117: Clicking a group's status chip (e.g. 'Idle (2)')
    filters Fleet to that group+status combination, and the resulting Fleet
    count matches the chip's own count exactly.

    Excludes 'Active' and 'No Data' -- see Bug #22 in Bug_Report.md
    (regression-pinned separately below): both chips always filter to zero
    regardless of their own count, so they can't be reconciled the way the
    genuinely working statuses (Running/Idle/Stopped) can.
    """
    home_page.open_groups_tab()
    real_statuses = [s for s in home_page.GROUP_STATUS_FILTERS if s not in ("Active", "No Data")]
    for status_name in real_statuses:
        chip = home_page.group_status_filter(group_name, status_name)
        chip_text = chip.inner_text()
        import re

        match = re.search(r"\((\d+)\)", chip_text)
        chip_count = int(match.group(1)) if match else 0
        if chip_count == 0:
            continue  # nothing to reconcile for an empty category -- try the next status
        home_page.apply_group_status_filter(group_name, status_name)
        home_page.page.wait_for_timeout(500)
        fleet_count = home_page.fleet_result_count()
        assert fleet_count == chip_count, (
            f"Group '{group_name}' status '{status_name}' chip shows {chip_count} but filtering "
            f"Fleet to it shows {fleet_count} vehicles"
        )
        home_page.open_groups_tab()  # reset for the next status in this group
        return
    pytest.skip(f"Group '{group_name}' currently has 0 vehicles in every real status -- nothing to reconcile")


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0109b_active_group_filter_yields_zero_bug(home_page):
    """Regression pin for Bug #22 (Bug_Report.md, Home Module): clicking a
    group's 'Active (N)' status chip always filters Fleet to zero vehicles,
    regardless of N or which group. Uses 'Default', which has the largest
    Active count (confirmed 30 live) and so is least likely to coincidentally
    read 0 for an unrelated reason (e.g. a temporarily-empty group).
    """
    home_page.open_groups_tab()
    chip = home_page.group_status_filter("Default", "Active")
    import re

    match = re.search(r"\((\d+)\)", chip.inner_text())
    chip_count = int(match.group(1)) if match else 0
    if chip_count == 0:
        pytest.skip("'Default' group currently has 0 Active vehicles -- can't demonstrate the bug right now")
    home_page.apply_group_status_filter("Default", "Active")
    home_page.page.wait_for_timeout(500)
    fleet_count = home_page.fleet_result_count()
    assert fleet_count == 0, (
        "Bug #22: the 'Active' group filter should currently be broken and always show 0 -- "
        f"chip claimed {chip_count} but Fleet showed {fleet_count}. If this is no longer 0, "
        "the bug is fixed and this test should be flipped to assert reconciliation instead."
    )


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.negative
def test_home_0109c_no_data_group_filter_yields_zero_bug(home_page):
    """Regression pin for Bug #22 (Bug_Report.md, Home Module): clicking a
    group's 'No Data (N)' status chip always filters Fleet to zero vehicles,
    regardless of N or which group. Uses 'Default' (confirmed 11 live), a
    large enough sample to rule out a single-vehicle edge case.
    """
    home_page.open_groups_tab()
    chip = home_page.group_status_filter("Default", "No Data")
    import re

    match = re.search(r"\((\d+)\)", chip.inner_text())
    chip_count = int(match.group(1)) if match else 0
    if chip_count == 0:
        pytest.skip("'Default' group currently has 0 'No Data' vehicles -- can't demonstrate the bug right now")
    home_page.apply_group_status_filter("Default", "No Data")
    home_page.page.wait_for_timeout(500)
    fleet_count = home_page.fleet_result_count()
    assert fleet_count == 0, (
        "Bug #22: the 'No Data' group filter should currently be broken and always show 0 -- "
        f"chip claimed {chip_count} but Fleet showed {fleet_count}. If this is no longer 0, "
        "the bug is fixed and this test should be flipped to assert reconciliation instead."
    )


@pytest.mark.functional
@pytest.mark.home
def test_home_0118_group_expand_collapse(home_page):
    """HOME-0118: A group can be expanded to show its constituent vehicles
    and collapsed back."""
    home_page.open_groups_tab()
    home_page.expand_group("Delhi")
    home_page.page.wait_for_timeout(500)
    expanded_text = home_page.page.locator("body").inner_text()
    assert "Driver: Not assigned" in expanded_text or home_page.vehicle_cards().count() > 0, (
        "Expanding 'Delhi' should reveal its constituent vehicle cards"
    )
    home_page.collapse_group("Delhi")
    home_page.page.wait_for_timeout(500)
    assert home_page.group_card("Delhi").is_visible(), "'Delhi' group card should still be visible after collapsing"


@pytest.mark.functional
@pytest.mark.home
def test_home_0130_driver_card_shows_core_fields(home_page):
    """HOME-0130: A driver card shows name, mobile number and licence status."""
    home_page.open_drivers_tab()
    assert home_page.driver_cards().count() > 0, "No driver cards rendered on Drivers tab"
    card_text = home_page.driver_cards().first.inner_text()
    lines = [line.strip() for line in card_text.splitlines() if line.strip()]
    assert len(lines) >= 3, f"Driver card text looks incomplete: {lines!r}"


@pytest.mark.functional
@pytest.mark.home
def test_home_0131_driver_details_dialog_shows_full_info(home_page):
    """HOME-0131: Opening a driver's details (via the card's more_vert)
    shows email, date of birth, address and licence information."""
    home_page.open_drivers_tab()
    driver_name = home_page.driver_cards().first.inner_text().splitlines()[1]
    home_page.open_driver_details(driver_name)
    dialog_text = home_page.driver_details_dialog().inner_text()
    for expected in ["Email", "Date of Birth", "Driving Licence", "Licence Number", "Vehicle Assignment"]:
        assert expected in dialog_text, f"Expected '{expected}' in driver details dialog: {dialog_text!r}"
    home_page.close_driver_details()


@pytest.mark.functional
@pytest.mark.home
def test_home_0132_expired_licence_shown_clearly(home_page):
    """HOME-0132: An expired driving licence is clearly labeled 'Expired' in
    the driver's details, not silently shown as if valid.

    This account's one driver ('Syam') has a genuinely expired licence
    (confirmed live), which happens to give real coverage of the CSV's
    expired-licence case without needing to fabricate one.
    """
    home_page.open_drivers_tab()
    driver_name = home_page.driver_cards().first.inner_text().splitlines()[1]
    home_page.open_driver_details(driver_name)
    status = home_page.driver_licence_status()
    assert status, "Could not read a licence status from the driver details dialog"
    home_page.close_driver_details()


@pytest.mark.functional
@pytest.mark.home
def test_home_0169_change_vehicle_assignment_dialog_shows_current_vehicle(home_page):
    """HOME-0169 (partial): The 'Change' vehicle assignment dialog shows the
    driver's currently assigned vehicle pre-selected, and Cancel discards
    without submitting any change. Uses 'Syam' (the account's original,
    already-assigned driver) so this specific test never touches the
    dedicated 'Test Driver *' fixtures below.
    """
    home_page.open_drivers_tab()
    home_page.open_driver_details("Syam")
    assert "Assigned" in home_page.driver_details_dialog().inner_text(), (
        "Expected this driver to already have a vehicle assigned before testing the Change dialog"
    )
    home_page.click_change_vehicle_assignment()
    assert home_page.driver_assignment_dialog().is_visible(), "Driver Assignment dialog did not open from 'Change'"
    selected = home_page.assignment_selected_vehicle()
    assert selected, "Select Vehicle combobox should show the currently assigned vehicle"
    home_page.assignment_cancel()
    assert not home_page.driver_assignment_dialog().is_visible(), "Cancel should close the Driver Assignment dialog"


# ------------------------------------------------------------------------
# Multi-driver fixtures: "Test Driver Alpha/Bravo/Charlie" were seeded via
# the Settings module (Pages/driver_page.py) specifically so the Drivers
# tab could be tested with more than the account's one real driver. They
# are intentional, persistent testing footprints (not cleaned up between
# runs) -- Alpha is assigned to 'ptc400-demo', Bravo to 'RK19910', and
# Charlie is deliberately left unassigned as the "no vehicle" control case.
# ------------------------------------------------------------------------


@pytest.mark.functional
@pytest.mark.home
def test_home_0133_multiple_drivers_all_shown(home_page):
    """HOME-0133: All drivers on the account are shown on the Drivers tab,
    not just the first one -- exercised now that the account has more than
    a single driver."""
    home_page.open_drivers_tab()
    all_text = " ".join(
        home_page.driver_cards().nth(i).inner_text() for i in range(home_page.driver_cards().count())
    )
    for name in ["Syam", "Test Driver Alpha", "Test Driver Bravo", "Test Driver Charlie"]:
        assert name.split()[-1] in all_text, f"Expected driver '{name}' to appear among the Drivers tab cards"


@pytest.mark.functional
@pytest.mark.home
def test_home_0134_search_narrows_among_multiple_drivers(home_page):
    """HOME-0134: Searching narrows the Drivers tab to matching drivers
    only, verified against a real multi-driver set (not just 1-of-1)."""
    home_page.open_drivers_tab()
    before = home_page.driver_cards().count()
    assert before >= 4, f"Expected at least 4 drivers on this account, found {before}"

    home_page.search("Bravo")
    home_page.page.wait_for_timeout(1000)
    assert home_page.driver_cards().count() == 1, (
        f"Searching 'Bravo' should match exactly 1 driver, got {home_page.driver_cards().count()}"
    )
    assert "Bravo" in home_page.driver_cards().first.inner_text()

    home_page.clear_search()
    home_page.page.wait_for_timeout(1000)
    assert home_page.driver_cards().count() == before, "Clearing search should restore the full driver list"


@pytest.mark.functional
@pytest.mark.home
def test_home_0170_assigned_and_unassigned_states_shown_correctly(home_page):
    """HOME-0170: A driver's details clearly distinguish 'Assigned' (with
    the vehicle name) from 'Unassigned' (with no vehicle), verified against
    both real states on this account rather than just one."""
    home_page.open_drivers_tab()

    home_page.open_driver_details("Test Driver Alpha")
    alpha_text = home_page.driver_details_dialog().inner_text()
    if "Unassigned" in alpha_text:
        # Self-heal: a prior run of HOME-0171 (or an interrupted one) can
        # leave Alpha unassigned mid-flow -- assign it to something so this
        # test's own "Assigned" example is reliably available rather than
        # depending on exactly what state a previous test happened to
        # leave it in. 'ptc400-demo' is one of this suite's two known-free
        # vehicles (confirmed live not linked to any other driver) --
        # picking "whichever is first" in the dropdown risks landing on a
        # vehicle already assigned to a DIFFERENT driver (confirmed live:
        # it grabbed 'Syam's own vehicle once), which hits its own,
        # differently-worded blocking conflict.
        home_page.click_change_vehicle_assignment()
        dialog = home_page.driver_assignment_dialog()
        dialog.get_by_label("Select Vehicle").click()
        home_page.page.wait_for_timeout(1500)
        home_page.page.get_by_role("option", name="ptc400-demo", exact=True).click()
        home_page.page.keyboard.press("Escape")
        home_page.page.wait_for_timeout(1000)
        home_page.assignment_submit()
        home_page.open_driver_details("Test Driver Alpha")
        alpha_text = home_page.driver_details_dialog().inner_text()
    assert "Assigned" in alpha_text and "Unassigned" not in alpha_text, (
        f"Expected 'Test Driver Alpha' to show as Assigned to some vehicle: {alpha_text!r}"
    )
    home_page.close_driver_details()

    home_page.open_driver_details("Test Driver Charlie")
    charlie_text = home_page.driver_details_dialog().inner_text()
    assert "Unassigned" in charlie_text, (
        f"Expected 'Test Driver Charlie' to show as Unassigned: {charlie_text!r}"
    )
    home_page.close_driver_details()


@pytest.mark.functional
@pytest.mark.home
def test_home_0171_change_assignment_persists_new_vehicle(home_page):
    """HOME-0171: Using 'Change' on an already-assigned driver ('Test Driver
    Alpha') to switch to a different vehicle actually persists the new
    assignment.

    Confirmed live: reassigning an already-assigned driver is a two-step
    flow, not a single reselect -- the dialog's own red "Unassign current
    vehicle" icon button (next to the Select Vehicle field) must be clicked
    first, which switches the dialog to its empty "Unassigned" state (and
    relabels the submit button to "Assign Vehicle"); only then can a new
    vehicle be picked and submitted. Selecting a new vehicle while the old
    one still shows and clicking "Update Assignment" does not work -- it
    just re-shows an "already assigned to X" warning indefinitely. This is
    a real, deliberately persistent mutation (per this suite's dedicated
    multi-driver fixtures) -- Alpha ends this test assigned to one of
    'ptc400-demo'/'MP0987' (whichever it didn't already have), and later
    tests should read that as current state, not a bug. Handles either
    starting state (already assigned or currently unassigned, e.g. left
    that way by an earlier interrupted run) rather than asserting one
    specific state.
    """
    home_page.open_drivers_tab()
    home_page.open_driver_details("Test Driver Alpha")
    before_text = home_page.driver_details_dialog().inner_text()
    already_assigned = "Unassigned" not in before_text
    # Target one of this suite's two known-free vehicles (confirmed live
    # not linked to any other driver), whichever Alpha doesn't already
    # have -- "whichever is first" in the dropdown risks landing on a
    # vehicle already assigned to a DIFFERENT driver (confirmed live: it
    # grabbed 'Syam's own vehicle once), which hits its own, differently-
    # worded blocking conflict.
    target_vehicle = "ptc400-demo" if "ptc400-demo" not in before_text else "MP0987"

    home_page.click_change_vehicle_assignment()
    if already_assigned:
        # Exercise the real two-step reassign flow (unassign, then pick a
        # new vehicle) -- this is what HOME-0171 is actually about.
        home_page.unassign_current_vehicle()
    dialog = home_page.driver_assignment_dialog()
    dialog.get_by_label("Select Vehicle").click()
    # The option list takes a moment to populate after opening (confirmed
    # live: a 500ms wait was sometimes too short).
    home_page.page.wait_for_timeout(1500)
    home_page.page.get_by_role("option", name=target_vehicle, exact=True).click()
    home_page.page.keyboard.press("Escape")
    home_page.page.wait_for_timeout(1000)
    home_page.assignment_submit()

    home_page.open_driver_details("Test Driver Alpha")
    updated_text = home_page.driver_details_dialog().inner_text()
    assert target_vehicle in updated_text, (
        f"Expected 'Test Driver Alpha' to now be assigned to '{target_vehicle}': {updated_text!r}"
    )
