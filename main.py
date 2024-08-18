import github
import json
import os
import re

ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def clean_board():
    return [0 for _ in range(9)]

def read_game_state():
    try:
        with open("game.json", "r") as f:
            return json.load(f)
    except:
        return {"board": clean_board(), "player": 1}

def save_game(game):
    with open("game.json", "w+") as f:
        json.dump(game, f)

def close_with_error(issue, msg):
    issue.create_comment(f"ERROR: {msg}")
    issue.edit(state="closed", labels=["Invalid"])

def player_emoji(player):
    if player == 1: return "❌"
    elif player == 2: return "⭕"

def board_segment(player, index):
    if player == 0:
        return f"[{index}](https://github.com/{GITHUB_REPO}/issues/new?title=Update:{index})"
    else:
        return player_emoji(player)

def render_board(board):
    rows = []
    for row_start in range(0, 9, 3):
        row = board[row_start:row_start+3]
        row_internal = "|".join(board_segment(player, row_start + index) for index, player in enumerate(row))
        rows.append(f"|{row_internal}|")
    rows.insert(1, "|---|---|---|")
    return "\n".join(rows)

def render_readme(game):
    player = player_emoji(game["player"])
    lines = [
            "# Board",
            render_board(game["board"]),
            f"## Current player: {player}"
            ]
    return "\n".join(lines)

def winning_set(row):
    row = set(row)
    return len(row) == 1 and row != {0}

def win(game):
    board = game["board"]
    for row_start in range(0, 9, 3):
        row = board[row_start:row_start+3]
        if winning_set(row): return True
    for col in range(3):
        col = [board[col], board[col + 3], board[col + 6]]
        if winning_set(col): return True
    if winning_set([board[0], board[4], board[8]]): return True
    if winning_set([board[2], board[4], board[6]]): return True

    return False

def main():
    client = github.Github(GITHUB_TOKEN)
    repo = client.get_repo(GITHUB_REPO)
    issue = repo.get_issue(number=ISSUE_NUMBER)

    title = issue.title
    try:
        number = int(re.match(r"Update:(\d+)", title).group(1))
    except:
        close_with_error(issue, "Invalid input format")
        return

    if number > 8 or number < 0:
        close_with_error(issue, "Input must be in range 1-9")
        return

    game = read_game_state()

    if game["board"][number] != 0:
        close_with_error(issue, "That square is already taken")
        return

    game["board"][number] = game["player"]
    game["player"] = 2 if game["player"] == 1 else 1
    save_game(game)

    readme = render_readme(game)
    issue.create_comment(readme)

    if win(game):
        issue.create_comment("Congrats you won!")
        game = {"board": clean_board(), "player": 1}
        readme = render_readme(game)
    if all(x != 0 for x in game["board"]):
        issue.create_comment("Wow its a draw, who would have expected this :P")
        game = {"board": clean_board(), "player": 1}
        readme = render_readme(game)

    with open("README.md", "w+") as f:
        f.write(readme)

    issue.edit(state="closed")

if __name__ == "__main__":
    main()
