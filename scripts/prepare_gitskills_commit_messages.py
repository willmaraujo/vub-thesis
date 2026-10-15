import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
history_file = root / "data/gitskills/evolution_pilot.json"
output_file = root / "data/gitskills/commit_messages.json"

history = json.loads(history_file.read_text())
messages = []

for row in history:
    message = row["message"]
    subject = next((line.strip() for line in message.splitlines()
                    if line.strip() and line.strip() != "@"), "")

    messages.append({
        "skill": row["name"] or Path(row["path"]).parent.name,
        "repo_full_name": row["repo_full_name"],
        "path": row["path"],
        "commit_sha": row["commit_sha"],
        "committed_at": row["committed_at"],
        "subject": subject,
        "message": message,
        "additions": row["additions"],
        "deletions": row["deletions"],
        "commit_url": f"https://github.com/{row['repo_full_name']}/commit/{row['commit_sha']}",
    })

output_file.write_text(json.dumps(messages, ensure_ascii=False, indent=2) + "\n")
print(f"Saved {len(messages)} commit messages to {output_file}")
