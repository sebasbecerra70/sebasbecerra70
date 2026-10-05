#!/usr/bin/env python3
"""Refresh the "Latest" section of the profile README from the project indexes."""
import re
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parents[2] / "README.md"
SOURCES = {
    "ai-lab": "https://raw.githubusercontent.com/sebasbecerra70/ai-lab/main/README.md",
    "code-a-day": "https://raw.githubusercontent.com/sebasbecerra70/code-a-day/main/README.md",
}
ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|(.+)\|\s*$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def index_rows(repo: str, url: str) -> list[tuple[str, str]]:
    text = urllib.request.urlopen(url, timeout=30).read().decode()
    block = text.split("<!-- INDEX:START -->")[1].split("<!-- INDEX:END -->")[0]
    rows = []
    for line in block.splitlines():
        m = ROW.match(line)
        if not m:
            continue
        date, rest = m.groups()
        cells = [c.strip() for c in rest.split("|")]
        if repo == "ai-lab":
            title, path = LINK.search(cells[0]).groups()
            label = f"**{title}** · {cells[2]} · {cells[1]}"
        else:
            title, path, label = cells[0], LINK.search(cells[2]).group(2), f"**{cells[0]}** · {cells[1]}"
        rows.append((date, f"- `{date}` [{repo}](https://github.com/sebasbecerra70/{repo}/tree/main/{path}): {label}"))
    return rows


def main() -> None:
    entries, totals = [], {}
    for repo, url in SOURCES.items():
        rows = index_rows(repo, url)
        totals[repo] = len(rows)
        entries.extend(rows)
    # Stable sort keeps index order within a day; newest first.
    entries.sort(key=lambda r: r[0], reverse=True)
    lines = [line for _, line in entries[:6]]
    lines.append(f"\n<sub>{totals['ai-lab']} applied-AI projects · {totals['code-a-day']} algorithm entries · updated automatically every day</sub>")
    text = README.read_text()
    start, end = "<!-- LATEST:START -->", "<!-- LATEST:END -->"
    head, rest = text.split(start)
    _, tail = rest.split(end)
    README.write_text(f"{head}{start}\n" + "\n".join(lines) + f"\n{end}{tail}")


if __name__ == "__main__":
    main()
