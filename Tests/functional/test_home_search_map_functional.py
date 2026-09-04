import pytest


@pytest.mark.functional
@pytest.mark.home
def test_home_0021_search_filters_fleet_tab(home_page):
    """HOME-0021: Searching on the Fleet tab filters vehicle cards to matches."""
    home_page.open_fleet_tab()
    before = home_page.fleet_result_count()
    vehicle_id = home_page.visible_vehicle_ids(max_count=1)[0]
    home_page.search(vehicle_id)
    home_page.page.wait_for_timeout(1000)
    after = home_page.fleet_result_count()
    assert after < before, f"Searching for '{vehicle_id}' should narrow the {before} vehicles shown, got {after}"
    assert vehicle_id in home_page.visible_vehicle_ids(), f"Searched vehicle '{vehicle_id}' should be in the results"
    home_page.clear_search()
    home_page.page.wait_for_timeout(1000)
    assert home_page.fleet_result_count() == before, "Clearing search should restore the original Fleet count"


@pytest.mark.functional
@pytest.mark.home
def test_home_0022_search_filters_groups_tab(home_page):
    """HOME-0022: Searching on the Groups tab filters group cards to matches."""
    home_page.open_groups_tab()
    before = home_page.group_cards().count()
    home_page.search("Delhi")
    home_page.page.wait_for_timeout(1000)
    after = home_page.group_cards().count()
    assert after < before, f"Searching for 'Delhi' should narrow the {before} groups shown, got {after}"
    home_page.clear_search()
    home_page.page.wait_for_timeout(1000)
    assert home_page.group_cards().count() == before, "Clearing search should restore the original Groups count"


@pytest.mark.functional
@pytest.mark.home
def test_home_0023_search_filters_drivers_tab(home_page):
    """HOME-0023: Searching on the Drivers tab filters driver cards to matches."""
    home_page.open_drivers_tab()
    before = home_page.driver_cards().count()
    driver_name = home_page.driver_cards().first.inner_text().splitlines()[1]
    home_page.search(driver_name)
    home_page.page.wait_for_timeout(1000)
    after = home_page.driver_cards().count()
    assert after >= 1, f"Searching for the existing driver '{driver_name}' should return at least 1 result"
    home_page.clear_search()
    assert home_page.driver_cards().count() == before, "Clearing search should restore the original Drivers count"


@pytest.mark.functional
@pytest.mark.home
def test_home_0024_search_no_match_shows_empty_state(home_page):
    """HOME-0024: Searching for a nonsense query on Fleet shows an empty state, not an error."""
    home_page.open_fleet_tab()
    home_page.search("zzz-nonexistent-vehicle-zzz")
    home_page.page.wait_for_timeout(1000)
    assert home_page.fleet_result_count() == 0, "A nonsense search should show 0 results"
    home_page.clear_search()


@pytest.mark.functional
@pytest.mark.home
def test_home_0209_0210_map_and_hybrid_mode_toggle(home_page):
    """HOME-0209/0210: Switching between Map and Hybrid view modes works
    without error.

    Precise per-vehicle marker verification is not attempted here -- the
    map is rendered by a third-party GIS provider (confirmed live: "Mapa
    GISrael") without individually addressable DOM elements per marker
    (a guessed [role='button'][title=...] locator matched 0 elements for a
    real, currently-visible vehicle), so that level of detail isn't
    reliably automatable without deeper reverse-engineering of that
    provider's rendering -- deferred rather than asserting against a guess.
    """
    home_page.open_fleet_tab()
    home_page.switch_to_map_mode()
    home_page.page.wait_for_timeout(1000)
    assert "/home" in home_page.page.url, "Switching to Map mode should stay on the Home page"
    home_page.switch_to_hybrid_mode()
    home_page.page.wait_for_timeout(1000)
    assert "/home" in home_page.page.url, "Switching to Hybrid mode should stay on the Home page"
