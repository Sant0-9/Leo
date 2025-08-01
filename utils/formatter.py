def format_plan(plan: dict) -> str:
    out = []
    for week in plan.get("weeks", []):
        out.append(f"**Week {week['week']}**")
        for task in week.get("tasks", []):
            res = task.get("resources", [])
            res_str = "\n    ".join([f"[{r['title']}]({r['url']})" for r in res]) if res else ""
            out.append(f"- {task['day']}: {task['task']}\n    {res_str}")
    return "\n".join(out)
