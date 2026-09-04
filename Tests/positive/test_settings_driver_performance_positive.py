import pytest
from playwright.sync_api import expect

# Real, confirmed field shape per parameter -- range parameters take
# Minimum/Maximum, count-only parameters take Count, Overspeed Limit
# uniquely takes Limit + Count.
_RANGE_PARAMETERS = ["Distance Range", "Idle Time Range", "Halt Time Range", "Running Time Range"]
_COUNT_ONLY_PARAMETERS = ["Harsh Acceleration", "Harsh Braking", "Rash Turning"]


def _fill_valid_value(driver_performance_page, parameter: str):
    if parameter == "Overspeed Limit":
        driver_performance_page.configure_parameter(parameter, Limit="60", Count="2")
    elif parameter in _RANGE_PARAMETERS:
        driver_performance_page.configure_parameter(parameter, Minimum="10", Maximum="50")
    elif parameter in _COUNT_ONLY_PARAMETERS:
        driver_performance_page.configure_parameter(parameter, Count="5")


@pytest.mark.positive
def test_set_057_create_valid_performance_configuration(driver_performance_page):
    """SET-057: Create a valid performance configuration; it appears in the list."""
    driver_performance_page.open_configure_form()
    categories = driver_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    driver_performance_page.select_category(category)
    driver_performance_page.select_parameter("Overspeed Limit")
    _fill_valid_value(driver_performance_page, "Overspeed Limit")
    expect(driver_performance_page.save_btn).to_be_enabled()
    driver_performance_page.save_btn.click()
    driver_performance_page.wait_for_dialog_closed()
    driver_performance_page.wait_for_visible(driver_performance_page.row_containing(category))

    try:
        expect(driver_performance_page.row_containing(category)).to_be_visible()
    finally:
        driver_performance_page.delete_configuration(category)


@pytest.mark.positive
def test_set_059_select_multiple_parameters(driver_performance_page):
    """SET-059: Selecting multiple parameters shows all of them as selected with their own configuration."""
    driver_performance_page.open_configure_form()
    for parameter in ["Overspeed Limit", "Distance Range", "Harsh Braking"]:
        driver_performance_page.select_parameter(parameter)
        expect(driver_performance_page.parameter_checkboxes[parameter]).to_be_checked()
        expect(driver_performance_page.parameter_article(parameter)).to_be_visible()


@pytest.mark.positive
def test_set_062_edit_performance_configuration(driver_performance_page):
    """SET-062: Edit an existing performance configuration; update persists after refresh."""
    driver_performance_page.open_configure_form()
    categories = driver_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    driver_performance_page.select_category(category)
    driver_performance_page.select_parameter("Overspeed Limit")
    _fill_valid_value(driver_performance_page, "Overspeed Limit")
    driver_performance_page.save_btn.click()
    driver_performance_page.wait_for_dialog_closed()
    driver_performance_page.wait_for_visible(driver_performance_page.row_containing(category))

    try:
        driver_performance_page.edit_button(category).click()
        driver_performance_page.wait_for_visible(driver_performance_page.dialog)
        driver_performance_page.configure_parameter("Overspeed Limit", Limit="80")
        driver_performance_page.save_btn.click()
        driver_performance_page.wait_for_dialog_closed()

        driver_performance_page.page.reload()
        driver_performance_page.wait_for_loading_to_finish()
        driver_performance_page.wait_for_visible(driver_performance_page.row_containing(category))
        expect(driver_performance_page.row_containing(category)).to_contain_text("80")
    finally:
        driver_performance_page.delete_configuration(category)


@pytest.mark.positive
def test_set_063_delete_performance_configuration(driver_performance_page):
    """SET-063: Delete a performance configuration; it is removed from the list."""
    driver_performance_page.open_configure_form()
    categories = driver_performance_page.available_categories()
    if not categories:
        pytest.skip("Every performance category is already configured on this account")
    category = categories[0]
    driver_performance_page.select_category(category)
    driver_performance_page.select_parameter("Overspeed Limit")
    _fill_valid_value(driver_performance_page, "Overspeed Limit")
    driver_performance_page.save_btn.click()
    driver_performance_page.wait_for_dialog_closed()
    driver_performance_page.wait_for_visible(driver_performance_page.row_containing(category))
    expect(driver_performance_page.row_containing(category)).to_be_visible()

    driver_performance_page.delete_configuration(category)
    expect(driver_performance_page.row_containing(category)).to_have_count(0)
