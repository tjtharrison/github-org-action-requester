"""Process issue from GitHub API."""

import os

gh_issue_title = os.environ["GH_ISSUE_TITLE"]
gh_issue_body = os.environ["GH_ISSUE_BODY"]
gh_issue_number = os.environ["GH_ISSUE_NUMBER"]
gh_issue_author = os.environ["GH_ISSUE_AUTHOR"]


def main():
    """
    Process issue from GitHub API.

    Returns:
        True if issue is processed successfully.
    """
    print(f"Processing issue: {gh_issue_title}")
    print(f"Body: {gh_issue_body}")
    print(f"Number: {gh_issue_number}")
    print(f"Author: {gh_issue_author}")

    return True

if __name__ == "__main__":
    main()