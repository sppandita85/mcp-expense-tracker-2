from dateutil import parser as date_parser

from fastmcp import FastMCP

mcp = FastMCP("Expense Tracker")

EXPENSES: list[dict] = []
_next_id = 1


def _month_key(value: str) -> str | None:
    try:
        parsed = date_parser.parse(value, fuzzy=True)
    except (ValueError, OverflowError):
        return None
    return f"{parsed.year:04d}-{parsed.month:02d}"


def _matches_month(expense_date: str, month: str) -> bool:
    expense_key = _month_key(expense_date)
    month_key = _month_key(month)
    if expense_key is not None and month_key is not None:
        return expense_key == month_key
    return month.strip().lower() in expense_date.strip().lower()


@mcp.tool
def add_expense(amount: float, category: str, date: str, note: str = "") -> dict:
    """Record a single expense and return the stored record."""
    if amount <= 0:
        raise ValueError("amount must be a positive number")

    global _next_id
    expense = {
        "id": _next_id,
        "amount": amount,
        "category": category,
        "date": date,
        "note": note,
    }
    EXPENSES.append(expense)
    _next_id += 1
    return expense


@mcp.tool
def get_monthly_summary(month: str) -> dict:
    """Return expenses for the given month, grouped by category."""
    summary: dict[str, dict[str, float | int]] = {}
    for expense in EXPENSES:
        if not _matches_month(expense["date"], month):
            continue
        bucket = summary.setdefault(expense["category"], {"total": 0.0, "count": 0})
        bucket["total"] += expense["amount"]
        bucket["count"] += 1
    return summary


@mcp.tool
def get_monthly_total(month: str) -> float:
    """Return the total amount spent in the given month."""
    return sum(
        expense["amount"] for expense in EXPENSES if _matches_month(expense["date"], month)
    )


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
