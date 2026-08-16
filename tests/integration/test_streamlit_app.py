from pathlib import Path

from streamlit.testing.v1 import AppTest

REPO_ROOT = Path(__file__).resolve().parents[2]

APP_PATH = REPO_ROOT / "streamlit_app.py"

FIXTURE_PATH = (
    REPO_ROOT
    / "tests"
    / "fixtures"
    / "integration_001"
    / "RAW_INVENTORY_FIXTURE.xlsx"
)
XLSX_MIME = (
    "application/vnd.openxmlformats-officedocument."
    "spreadsheetml.sheet"
)


def _run_app() -> AppTest:
    return AppTest.from_file(
        APP_PATH,
        default_timeout=30,
    ).run()


def _upload_fixture(
    app: AppTest,
) -> None:
    app.file_uploader[0].upload(
        FIXTURE_PATH.name,
        FIXTURE_PATH.read_bytes(),
        XLSX_MIME,
    )
    app.run()


def test_streamlit_app_renders_without_exception() -> None:
    app = _run_app()

    assert len(app.exception) == 0
    assert app.button[0].label == "Analyze inventory"
    assert (
        app.file_uploader[0].label
        == "Inventory workbook"
    )
    assert (
        app.selectbox[0].value
        == "MAXIMIZE_RECOVERY_VALUE"
    )


def test_streamlit_app_rejects_missing_upload() -> None:
    app = _run_app()

    app.button[0].click()
    app.run()

    assert len(app.exception) == 0
    assert any(
        error.value
        == "Pilih satu file inventory .xlsx terlebih dahulu."
        for error in app.error
    )


def test_streamlit_app_rejects_balanced_without_ratio() -> None:
    app = _run_app()
    _upload_fixture(app)

    app.selectbox[0].select("BALANCED")
    app.run()

    assert app.number_input[1].value is None

    app.button[0].click()
    app.run()

    assert len(app.exception) == 0
    assert any(
        error.value == "Decision context tidak valid."
        for error in app.error
    )
    assert any(
        "minimum_expected_rescue_ratio"
        in str(markdown.value)
        for markdown in app.markdown
    )


def test_streamlit_app_rejects_corrupt_workbook() -> None:
    app = _run_app()

    app.file_uploader[0].upload(
        "corrupt.xlsx",
        b"this-is-not-an-xlsx",
        XLSX_MIME,
    )
    app.run()

    app.button[0].click()
    app.run()

    assert len(app.exception) == 0
    assert any(
        "File is not a zip file"
        in str(error.value)
        for error in app.error
    )


def test_streamlit_app_runs_fixture_and_exposes_download() -> None:
    app = _run_app()
    _upload_fixture(app)

    app.number_input[0].set_value(50000.0)
    app.run()

    app.button[0].click()
    app.run(timeout=60)

    assert len(app.exception) == 0
    assert any(
        success.value == "Analysis complete."
        for success in app.success
    )

    assert len(app.download_button) == 1
    assert (
        app.download_button[0].label
        == "Download Rescue Decision Report"
    )
