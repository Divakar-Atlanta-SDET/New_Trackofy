import pytest
from playwright.sync_api import expect


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
    assert home_page.map_mode_is_selected("Map")
    assert "/home" in home_page.page.url, "Switching to Map mode should stay on the Home page"
    home_page.switch_to_hybrid_mode()
    home_page.page.wait_for_timeout(1000)
    assert home_page.map_mode_is_selected("Hybrid")
    assert "/home" in home_page.page.url, "Switching to Hybrid mode should stay on the Home page"


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("entity", ["Fleet", "Groups", "Drivers"])
@pytest.mark.parametrize("variant", ["partial", "case", "nonexistent", "special"])
def test_home_search_variants(home_page, entity, variant):
    """HOME-0022..0035: search excludes unrelated cards in each entity tab."""
    getattr(home_page, f"open_{entity.lower()}_tab")()
    names = home_page.rendered_entity_names(entity)
    assert names, f"No {entity} data available for search"
    original = names[0]
    query = original[:max(1, len(original)//2)] if variant == "partial" else original.swapcase()
    if variant in ("nonexistent", "special"):
        query = "astra-no-match-987654" if variant == "nonexistent" else "<>&'\"astra987654"
    home_page.search(query)
    home_page.page.wait_for_timeout(700)
    actual = home_page.rendered_entity_names(entity)
    if variant in ("nonexistent", "special"):
        assert not actual, f"Nonmatching query returned {len(actual)} cards"
        expect(home_page.search_empty_state()).to_be_visible()
    else:
        if not actual:
            home_page.page.screenshot(path=f"Tests/home_search_{entity}_{variant}_astra.png", full_page=True)
        assert actual, f"{entity} search for {query!r} returned no cards, although {original!r} exists"
        assert all(query.casefold() in name.casefold() for name in actual), "Search included unrelated cards"
    home_page.clear_search()
    home_page.page.wait_for_timeout(700)
    assert original in home_page.rendered_entity_names(entity), "Clear did not restore original entity"


@pytest.mark.functional
@pytest.mark.home
@pytest.mark.parametrize("status", ["Active", "Running", "Idle", "Stopped", "No Data"])
def test_home_0036_0040_search_and_status_intersection(home_page, status):
    """Search must not restore records excluded by the selected status."""
    home_page.apply_fleet_status_filter(status)
    names = home_page.visible_vehicle_ids()
    if not names:
        pytest.skip(f"No {status} vehicles available for a matching-search test")
    target = names[0]
    home_page.search(target)
    home_page.page.wait_for_timeout(700)
    actual = home_page.visible_vehicle_ids()
    assert target in actual
    assert all(target.casefold() in name.casefold() for name in actual)
    if status != "Active":
        assert all(value == status for value in home_page.rendered_vehicle_statuses()), "Search restored a vehicle outside the selected status"
    home_page.search("astra-no-match-987654")
    expect(home_page.vehicle_cards()).to_have_count(0)
    home_page.clear_search()
    home_page.page.wait_for_timeout(700)
    assert home_page.fleet_result_count() == home_page.fleet_status_count(status)


@pytest.mark.functional
@pytest.mark.home
def test_home_0298_latest_search_wins(home_page):
    """Rapid input changes must settle on the final query."""
    target = home_page.visible_vehicle_ids()[0]
    for query in (target, "astra-no-match-987654", target):
        home_page.search_input.fill(query)
    home_page.page.wait_for_timeout(1000)
    names = home_page.visible_vehicle_ids()
    assert target in names
    assert all(target.casefold() in name.casefold() for name in names)
