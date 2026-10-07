import json
import sqlite3
import subprocess
from pathlib import Path
from urllib.parse import quote, urlencode

root = Path(__file__).resolve().parents[1]
database = root / "data/gitskills/agent_skills_sample.db"
output = root / "data/gitskills/evolution_pilot.json"


def fetch(url):
    return subprocess.check_output(["curl", "-fsSL", "--retry", "2", url])


def get_file_stats(repository, sha, path):
    url = f"/repos/{repository}/commits/{sha}?per_page=100"
    pages = json.loads(subprocess.check_output(["gh", "api", "--paginate", "--slurp", url]))
    for page in pages:
        for file in page["files"]:
            if file["filename"] == path or file.get("previous_filename") == path:
                return file["additions"], file["deletions"]
    raise ValueError(f"File not found in commit {sha}: {repository}/{path}")


connection = sqlite3.connect(database)
skills = connection.execute("""
    SELECT repo_full_name, name, path, last_commit_at, commit_count, content
    FROM artifacts
    WHERE dedup_primary = 1 AND history_fetched = 1 AND commit_count > 1
    ORDER BY commit_count DESC
    LIMIT 10
""").fetchall()
connection.close()

revisions = []
for repository, name, path, last_date, expected_count, current_text in skills:
    options = urlencode({"path": path, "until": last_date, "per_page": 100})
    url = f"https://api.github.com/repos/{repository}/commits?{options}"
    commits = json.loads(fetch(url))

    for commit in reversed(commits):
        sha = commit["sha"]
        additions, deletions = get_file_stats(repository, sha, path)
        file_url = f"https://raw.githubusercontent.com/{repository}/{sha}/{quote(path)}"
        try:
            content = fetch(file_url).decode("utf-8")
        except (subprocess.CalledProcessError, UnicodeDecodeError):
            content = None
            print(f"Missing file at {sha[:8]}: {repository}/{path}", flush=True)
        revisions.append({
            "repo_full_name": repository,
            "path": path,
            "name": name,
            "commit_sha": sha,
            "committed_at": commit["commit"]["committer"]["date"],
            "message": commit["commit"]["message"].splitlines()[0],
            "additions": additions,
            "deletions": deletions,
            "content": content,
        })

    latest_text = revisions[-1]["content"]
    print(f"{repository}: {len(commits)}/{expected_count} commits, latest text matches: {latest_text == current_text}", flush=True)

output.write_text(json.dumps(revisions, ensure_ascii=False, indent=2) + "\n")
print(f"Saved {len(revisions)} revisions to {output}")
