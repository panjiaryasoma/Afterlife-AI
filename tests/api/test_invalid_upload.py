from backend.main import app
from fastapi.testclient import TestClient

client = TestClient(
    app,
    raise_server_exceptions=False,
)


def test_analyze_rejects_wrong_file_extension() -> None:
    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.txt",
                b"not an xlsx",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "inventory_file harus berupa file .xlsx."
    )


def test_analyze_rejects_corrupt_xlsx_with_clear_error() -> None:
    response = client.post(
        "/api/analyze",
        files={
            "inventory_file": (
                "inventory.xlsx",
                b"this is not a real xlsx workbook",
                (
                    "application/vnd.openxmlformats-officedocument."
                    "spreadsheetml.sheet"
                ),
            )
        },
    )

    assert response.status_code == 422

    payload = response.json()

    assert "detail" in payload
    assert "XLSX" in payload["detail"]