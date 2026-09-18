"""Open or update one GitHub issue per finding; never close a case automatically."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com"


def request(method: str, path: str, payload: dict | None = None) -> object:
    token = os.environ["GITHUB_TOKEN"]
    body = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        API + path, data=body, method=method,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def ensure_labels(repo: str) -> None:
    wanted = {
        "sod-exception": ("Segregation of duties monitoring exception", "5319E7"),
        "severity:critical": ("Critical control exception", "B60205"),
        "severity:high": ("High control exception", "D93F0B"),
        "human-action-required": ("A human decision is required", "FBCA04"),
        "human-closure-review": ("Finding disappeared; verify evidence before closure", "0E8A16"),
    }
    current = {row["name"] for row in request("GET", f"/repos/{repo}/labels?per_page=100")}  # type: ignore[union-attr]
    for name, (description, color) in wanted.items():
        if name not in current:
            request("POST", f"/repos/{repo}/labels", {"name": name, "description": description, "color": color})


def main() -> int:
    repo = os.environ["GITHUB_REPOSITORY"]
    ensure_labels(repo)
    evidence = json.loads((ROOT / "output/control_evidence.json").read_text(encoding="utf-8"))
    findings = {row["finding_id"]: row for row in evidence["findings"]}
    issues = request("GET", f"/repos/{repo}/issues?state=open&labels=sod-exception&per_page=100")
    existing = {}
    for issue in issues:  # type: ignore[union-attr]
        marker = next((token for token in issue["body"].split() if token.startswith("finding-id:")), "")
        if marker:
            existing[marker.removeprefix("finding-id:")] = issue
    for finding_id, finding in findings.items():
        case = (ROOT / "output/cases" / f"{finding_id}.md").read_text(encoding="utf-8")
        body = f"finding-id:{finding_id}\n\n{case}"
        labels = ["sod-exception", f"severity:{finding['severity']}", "human-action-required"]
        payload = {"title": f"[{finding['severity'].upper()}] {finding['rule']} {finding['object_id']}", "body": body, "labels": labels}
        if finding_id in existing:
            request("PATCH", f"/repos/{repo}/issues/{existing[finding_id]['number']}", payload)
        else:
            request("POST", f"/repos/{repo}/issues", payload)
    for finding_id, issue in existing.items():
        if finding_id not in findings:
            labels = sorted(set(issue["labels"][i]["name"] if isinstance(issue["labels"][i], dict) else issue["labels"][i] for i in range(len(issue["labels"]))) | {"human-closure-review"})
            request("PATCH", f"/repos/{repo}/issues/{issue['number']}", {"labels": labels})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, FileNotFoundError, urllib.error.HTTPError) as exc:
        print(f"Issue sync failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
