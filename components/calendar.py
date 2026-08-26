from playwright.sync_api import Page, Locator


class Calendar:

    def __init__(self, page: Page, calendar_button: Locator):
        self.page = page

        # Calendar toggle for the specific date field
        self.calendar_button = calendar_button

        # Calendar popup
        self.calendar = page.locator("mat-calendar")

        # Calendar navigation
        self.previous_month_button = self.calendar.get_by_role(
            "button",
            name="Previous month"
        )

        self.next_month_button = self.calendar.get_by_role(
            "button",
            name="Next month"
        )

        # Year/month selection
        self.choose_year_month_button = self.calendar.get_by_role(
            "button",
            name="Choose month and year"
        )

        # Year navigation
        self.previous_24_years_button = self.calendar.get_by_role(
            "button",
            name="Previous 24 years"
        )

        # Year navigation
        self.next_24_years_button = self.calendar.get_by_role(
            "button",
            name="Next 24 years"
        )
    
    def open_calendar(self):
        """Open the calendar."""
        self.calendar_button.click()

        self.calendar.wait_for(state="visible")

    def open_year_month_selection(self):
        """Open the year/month selection view."""
        self.choose_year_month_button.click()

    def previous_month(self):
        """Navigate to the previous month."""
        self.previous_month_button.click()

    def next_month(self):
        """Navigate to the next month."""
        self.next_month_button.click()

    def previous_24_years(self):
        """Navigate to the previous set of 24 years."""
        self.previous_24_years_button.click()

    def next_24_years(self):
        """Navigate to the next set of 24 years."""
        self.next_24_years_button.click()

    def select_year(self, year: str):
        """Select the specified year."""
        self.calendar.get_by_text(
            str(year),
            exact=True
        ).click()

    def select_month(self, month: str):
        """Select the specified month."""
        self.calendar.get_by_text(
            month,
            exact=True
        ).click()

    def select_date(self, date: str):
        """Select the specified date."""
        self.calendar.get_by_text(
            str(date),
            exact=True
        ).click()

    def select_date_by_month_year(
        self,
        year: str,
        month: str,
        date: str
    ):
        """Select a complete date using year, month, and day."""

        self.open_calendar()

        self.open_year_month_selection()

        self.select_year(year)

        self.select_month(month)

        self.select_date(date)