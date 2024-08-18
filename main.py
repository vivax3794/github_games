import github
import json
import os
import re

ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def clean_board():
    return [[0 for _ in range(3)] for _ in range(3)]

def read_game_state():
    try:
        with open("game.json", "r") as f:
            return json.load(f)
    except:
        return {"board": clean_board(), "player": 1}

def main():
    client = github.Github(GITHUB_TOKEN)
    repo = client.get_repo(GITHUB_REPO)
    issue = repo.get_issue(number=ISSUE_NUMBER)

    title = issue.title
    try:
        number = int(re.match(r"Update:(\d+)", title).group(1))
    except:
        issue.create_comment("Invalid input")
        issue.edit(state="closed", labels=["Invalid"])
        return

    issue.create_comment(f"you selected {number}")
    issue.edit(state="closed")

if __name__ == "__main__":
    main()
