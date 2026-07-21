import pytest

import server


@pytest.fixture(autouse=True)
def reset_store():
    server.EXPENSES.clear()
    server._next_id = 1
    yield


def test_add_expense_stores_record():
    record = server.add_expense(12.5, "Food", "2026-07-21", "lunch")
    assert record["id"] == 1
    assert record["amount"] == 12.5
    assert record["category"] == "Food"
    assert record["date"] == "2026-07-21"
    assert record["note"] == "lunch"
    assert server.EXPENSES == [record]


def test_add_expense_defaults_note_to_empty_string():
    record = server.add_expense(5, "Misc", "2026-07-21")
    assert record["note"] == ""


def test_add_expense_ids_increment():
    first = server.add_expense(1, "Food", "2026-07-01")
    second = server.add_expense(2, "Food", "2026-07-02")
    assert (first["id"], second["id"]) == (1, 2)


@pytest.mark.parametrize("bad_amount", [0, -5, -0.01])
def test_add_expense_rejects_non_positive_amount(bad_amount):
    with pytest.raises(ValueError):
        server.add_expense(bad_amount, "Food", "2026-07-21")


def test_get_monthly_summary_groups_by_category():
    server.add_expense(12.5, "Food", "2026-07-21", "lunch")
    server.add_expense(40, "Food", "July 5, 2026", "groceries")
    server.add_expense(100, "Transport", "07/10/2026", "gas")
    server.add_expense(20, "Food", "2026-06-15", "different month")

    summary = server.get_monthly_summary("2026-07")

    assert summary == {
        "Food": {"total": 52.5, "count": 2},
        "Transport": {"total": 100.0, "count": 1},
    }


def test_get_monthly_summary_accepts_flexible_month_text():
    server.add_expense(12.5, "Food", "2026-07-21")

    assert server.get_monthly_summary("July 2026") == {
        "Food": {"total": 12.5, "count": 1}
    }


def test_get_monthly_summary_empty_when_no_matches():
    server.add_expense(12.5, "Food", "2026-06-21")
    assert server.get_monthly_summary("2026-07") == {}


def test_get_monthly_total_sums_matching_month():
    server.add_expense(12.5, "Food", "2026-07-21")
    server.add_expense(100, "Transport", "07/10/2026")
    server.add_expense(20, "Food", "2026-06-15")

    assert server.get_monthly_total("2026-07") == 112.5


def test_get_monthly_total_zero_when_no_matches():
    assert server.get_monthly_total("2026-07") == 0


def test_unparseable_date_falls_back_to_substring_match():
    server.add_expense(7, "Misc", "sometime later", "no clean parse target")
    assert server.get_monthly_total("later") == 7
