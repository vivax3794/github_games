import github
import os

ISSUE_NUMBER = int(os.getenv("ISSUE_NUMBER"))
GITHUB_REPO = os.getenv("GITHUB_REPOSITORY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def main():
    github = github.Github(GITHUB_TOKEN)
    repo = github.get_repo(GITHUB_REPO)
    issue = repo.get_issue(number=ISSUE_NUMBER)

    issue.create_comment("Hello World!")

if __name__ == "__main__":
    main()
