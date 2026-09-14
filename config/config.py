import os
from dotenv import load_dotenv

load_dotenv()

TEST_VEHICLE_NAME = os.getenv("TRACKOFY_TEST_VEHICLE", "GCBL10536MHG26DG08215")
REPORT_TEST_VEHICLE_NAME = os.getenv("TRACKOFY_REPORT_TEST_VEHICLE", "GCBL10536MHG14AG04459")
REPORT_TEST_DRIVER_NAME = os.getenv("TRACKOFY_REPORT_TEST_DRIVER", "syam")
# Standard Reports test window: 1-31 August 2026. Chosen per direct user
# instruction (2026-09-12) to keep every report's data validated against
# one consistent, known-good month -- avoids both the missing-telemetry-
# partition 500 for old/unavailable months (Bug_Report.md #17) and cross-
# report noise from each test picking its own ad hoc range.
#
# Written in MM/DD order, not the field's own DD/MM/YYYY label: confirmed
# live (Bug_Report.md #6) that the app's date parser actually reads input
# as MM/DD regardless of the label, silently transposing day/month when
# both are <=12. Writing "08/01/2026" (intending 1 Aug) resolves correctly
# to 1 Aug and redisplays as "01/08/2026"; the literal DD/MM string
# "01/08/2026" would instead be silently misread as 8 Jan. The end date's
# day (31) cannot be misread as a month, so it isn't ambiguous either way,
# but is kept in the same MM/DD-first form for consistency.
REPORT_START_DATE = os.getenv("TRACKOFY_REPORT_START_DATE", "08/01/2026")
REPORT_END_DATE = os.getenv("TRACKOFY_REPORT_END_DATE", "08/31/2026")

# Real inbox used to verify actual scheduled-report email delivery (AS-219)
# via IMAP -- a Gmail App Password (not the account's normal login
# password) is required in my_test_email_password for this to work.
TEST_RECIPIENT_EMAIL = os.getenv("My_test_email")
TEST_RECIPIENT_EMAIL_PASSWORD = os.getenv("my_test_email_password")