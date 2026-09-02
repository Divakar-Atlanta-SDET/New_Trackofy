def test_probe_add_driver_form(authenticated_page):
    page = authenticated_page
    page.goto("/settings/driver")
    page.wait_for_timeout(1500)
    page.get_by_role("button", name="Add Driver").click()
    page.wait_for_timeout(1000)
    print("=== ADD DRIVER FORM ===")
    print(page.locator("[role='dialog']").last.aria_snapshot()[:3000])


def test_probe_vehicle_management_tree(authenticated_page):
    page = authenticated_page
    page.goto("/settings/driver")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Vehicle Management").click()
    page.wait_for_timeout(500)
    print("=== TREE AFTER EXPANDING VEHICLE MANAGEMENT ===")
    print(page.get_by_role("tree").aria_snapshot()[:2000])
    page.get_by_role("button", name="Alert Configuration").click()
    page.wait_for_timeout(500)
    print("=== TREE AFTER EXPANDING ALERT CONFIGURATION ===")
    print(page.get_by_role("tree").aria_snapshot()[:3000])


def test_probe_vehicle_group_page(authenticated_page):
    page = authenticated_page
    page.goto("/settings/driver")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Vehicle Management").click()
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Vehicle Group").click()
    page.wait_for_timeout(1500)
    print("=== VEHICLE GROUP PAGE ===")
    print(page.locator("main").last.aria_snapshot()[:2500])


def test_probe_alert_page(authenticated_page):
    page = authenticated_page
    page.goto("/settings/driver")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Alert Configuration").click()
    page.wait_for_timeout(500)
    page.get_by_role("button", name="Speed Alert").click()
    page.wait_for_timeout(1500)
    print("=== SPEED ALERT PAGE ===")
    print(page.locator("main").last.aria_snapshot()[:2500])


def test_probe_route_page(authenticated_page):
    page = authenticated_page
    page.goto("/settings/driver")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Route Management").click()
    page.wait_for_timeout(1500)
    print("=== ROUTE MANAGEMENT PAGE ===")
    print(page.locator("main").last.aria_snapshot()[:2500])
