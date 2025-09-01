# azq/usage.py
import datetime, openai

def get_usage_cost(days=14):
    """Return today's spend and total spend over the last N days."""
    today = datetime.date.today()
    start_date = today - datetime.timedelta(days=days)
    # OpenAI usage API expects isoformat
    resp = openai.Usage.list(
        start_date=start_date.isoformat(),
        end_date=today.isoformat(),
    )

    today_total, period_total = 0.0, 0.0
    for row in resp["data"]:
        amt = float(row.get("cost", 0))
        date = datetime.date.fromisoformat(row["aggregation_timestamp"].split("T")[0])
        if date == today:
            today_total += amt
        period_total += amt

    return today_total, period_total

