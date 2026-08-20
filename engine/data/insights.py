"""Evidence-backed insights.

An insight may only repeat what a metric already proved. It never invents a
number and never approves data that failed a rule.
"""

from __future__ import annotations

import json

SEVERITIES = ("info", "watch", "action")
_OPERATORS = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


def _format(template: str, context: dict) -> str:
    try:
        return template.format(**context)
    except (KeyError, IndexError, ValueError):
        return template


def evaluate(config, payloads: list[dict], run_summary: dict) -> list[dict]:
    """Apply the project's insight rules plus the built-in data-health rules."""

    values = {p["id"]: p.get("value") for p in payloads if p.get("kind") == "kpi"}
    results: list[dict] = []

    for rule in config.insights:
        condition = rule.get("when", {})
        metric_id = condition.get("metric")
        operator = condition.get("operator", ">")
        threshold = condition.get("value")
        actual = values.get(metric_id)
        if actual is None or metric_id not in values:
            continue
        compare = _OPERATORS.get(operator)
        if compare is None:
            continue
        try:
            triggered = compare(float(actual), float(threshold))
        except (TypeError, ValueError):
            triggered = compare(str(actual), str(threshold))
        if not triggered:
            continue
        context = {"value": actual, "threshold": threshold, **values}
        results.append({
            "id": rule.get("id", metric_id),
            "severity": rule.get("severity", "watch"),
            "title": _format(rule.get("title", metric_id), context),
            "body": _format(rule.get("body", ""), context),
            "evidence": {"metric": metric_id, "value": actual, "operator": operator,
                         "threshold": threshold},
        })

    rejected = run_summary.get("rows_rejected", 0)
    if rejected:
        results.append({
            "id": "rows_need_attention",
            "severity": "action",
            "title": f"{rejected} row(s) were not used",
            "body": ("These rows did not pass the agreed rules. They are listed under "
                     "'Rows needing attention' with the file name and row number."),
            "evidence": {"rows_rejected": rejected},
        })
    blocked = [c for c in run_summary.get("reconciliation", []) if c.get("status") == "BLOCK"]
    if blocked:
        results.append({
            "id": "totals_do_not_match",
            "severity": "action",
            "title": "Totals did not match",
            "body": "The result was not published because a control total did not reconcile.",
            "evidence": {"checks": blocked},
        })
    return results


def save(connection, run_id: str, results: list[dict]) -> None:
    connection.executemany(
        "INSERT OR REPLACE INTO insights(run_id, insight_id, severity, title, body, evidence_json)"
        " VALUES (?,?,?,?,?,?)",
        [(run_id, r["id"], r.get("severity", "info"), r.get("title", ""), r.get("body", ""),
          json.dumps(r.get("evidence", {}), ensure_ascii=False, default=str)) for r in results])
