"""
Download helper utility for Playwright-based report download verification.
Intercepts browser download events using page.on("download", ...), saves files
to project-root downloads/ folder, and verifies file integrity and parsed rows.
"""

import csv
import time
from pathlib import Path
from playwright.sync_api import Page, Download


DOWNLOADS_DIR = Path(__file__).parent.parent / "downloads"


def ensure_downloads_dir() -> Path:
    """Create the project-root downloads/ directory if it does not exist."""
    DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
    return DOWNLOADS_DIR


def attach_download_handler(page: Page, target_dir: Path | str = None) -> list[Path]:
    """
    Attaches a Playwright download event listener to the page using page.on("download", ...).
    Automatically saves every downloaded file to the root downloads/ directory.
    Returns a live list that collects all saved file paths.
    """
    dest_dir = Path(target_dir) if target_dir else ensure_downloads_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)
    downloaded_files: list[Path] = []

    def _on_download(download: Download):
        filename = download.suggested_filename or f"download_{int(time.time())}"
        target_path = dest_dir / filename
        # Ensure unique name if file already exists
        counter = 1
        stem = target_path.stem
        suffix = target_path.suffix
        while target_path.exists():
            target_path = dest_dir / f"{stem}_{counter}{suffix}"
            counter += 1

        download.save_as(str(target_path))
        downloaded_files.append(target_path)

    page.on("download", _on_download)
    return downloaded_files


def handle_and_verify_download(
    page: Page,
    trigger_action,
    expected_extension: str = ".xlsx",
    timeout: int = 30000,
) -> Path:
    """
    Explicitly capture a file download triggered by trigger_action, save it to downloads/,
    and verify that it exists with a non-zero size.

    Args:
        page: Playwright page instance.
        trigger_action: A callable that triggers the download (e.g. lambda: button.click()).
        expected_extension: Expected file extension for validation (.xlsx, .csv, .pdf).
        timeout: Max wait time in milliseconds for the download event.

    Returns:
        Path to the saved file.

    Raises:
        AssertionError: If the file does not exist or has zero bytes.
    """
    download_dir = ensure_downloads_dir()

    with page.expect_download(timeout=timeout) as download_info:
        trigger_action()

    download: Download = download_info.value
    suggested_name = download.suggested_filename or f"report{expected_extension}"
    file_path = download_dir / suggested_name

    # Save the downloaded file to root downloads/
    download.save_as(str(file_path))

    # Verify download integrity
    assert file_path.exists(), f"Downloaded file not found at: {file_path}"
    assert file_path.stat().st_size > 0, f"Downloaded file is empty (0 bytes): {file_path}"

    if expected_extension:
        actual_ext = file_path.suffix.lower()
        assert actual_ext == expected_extension.lower(), (
            f"Expected extension '{expected_extension}' but got '{actual_ext}'"
        )

    return file_path


def list_downloads() -> list[Path]:
    """List all downloaded files in the downloads/ folder."""
    if not DOWNLOADS_DIR.exists():
        return []
    return sorted(DOWNLOADS_DIR.iterdir())


def read_csv_rows(file_path: Path | str) -> list[list[str]]:
    """Read and return all non-empty rows from a CSV file."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    rows = []
    for encoding in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, mode="r", encoding=encoding, newline="") as f:
                reader = csv.reader(f)
                for row in reader:
                    if any(field.strip() for field in row):
                        rows.append([field.strip() for field in row])
            break
        except UnicodeDecodeError:
            continue
    return rows


def count_csv_data_rows(file_path: Path | str, has_header: bool = True) -> int:
    """
    Count the number of data rows in a CSV file.
    Accurately handles Trackofy export format where Row 1 may be a Report Title
    and Row 2 is the column headers.
    """
    rows = read_csv_rows(file_path)
    if not rows:
        return 0

    if not has_header:
        return len(rows)

    # Check if first row is a title header (e.g. only 1 column while subsequent rows have many)
    if len(rows) >= 2 and len(rows[0]) == 1 and len(rows[1]) > 1:
        # Row 0 is Title, Row 1 is Column Header, data rows start from index 2
        return len(rows) - 2
    elif len(rows) > 0:
        return len(rows) - 1

    return len(rows)

