"""Process issue from GitHub API."""

import os
import subprocess
import configparser

# If not on github actions, load .env file
if not os.environ.get("GITHUB_ACTIONS"):
    import dotenv
    dotenv.load_dotenv()

gh_issue_title = os.environ["GH_ISSUE_TITLE"]
gh_issue_body = os.environ["GH_ISSUE_BODY"]
gh_issue_number = os.environ["GH_ISSUE_NUMBER"]
gh_issue_author = os.environ["GH_ISSUE_AUTHOR"]


def read_issue_body():
    """
    Read issue body provided and return action request.

    Returns:
        Dictionary with action request.
    """
    print("Reading issue body")

    # Read request body
    config = configparser.ConfigParser()
    config.read_string(gh_issue_body)

    # Set default values
    action_request = {}

    # Get sections
    sections = config.sections()

    try:
        for section in sections:
            print()
            print(f"Processing request: {section}")
            action_request[section] = {
                "name": config[section]["name"],
                "description": config[section]["description"],
                "version": config[section]["requested_version"]
            }
    except KeyError as error_message:
        raise KeyError(str(error_message)) from error_message

    print("Action request parsed successfully")

    return action_request


def validate_inputs(action_requests):
    """
    Validate action request inputs.

    Returns:
        True if provided values are valid.

    """
    print("Validating action request inputs")
    for action_request in action_requests:
        action_name = action_requests[action_request]["name"]
        repo_name = action_name.split("/")[1]
        action_description = action_requests[action_request]["description"]
        action_version = action_requests[action_request]["version"]

        print(f'Processing {action_name}@{action_version}')

        # Check if action is available
        print(f"Checking if action is available")
        try:
            subprocess.check_output(
                f"gh repo clone {action_name} -- -b {action_version}",
                shell=True,
                stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as error_message:
            print(f"Error cloning action: {error_message}")
            raise Exception(f"Error cloning action: {error_message}") from error_message

    # Delete directory
    try:
        subprocess.check_output(
            f"rm -rf {repo_name}",
            shell=True,
            stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as error_message:
        print(f"Error deleting directory: {error_message}")
        raise Exception(f"Error deleting directory: {error_message}") from error_message

    print("Repository cloned successfully at requested version")

    return True


def main():
    """
    Process issue from GitHub API.

    Returns:
        True if issue is processed successfully.
    """
    print(f"Processing issue: #{gh_issue_number}")
    try:
        action_requests = read_issue_body()
    except TypeError as error_message:
        print(f"Error reading issue body: {error_message}")
        return False
    except KeyError as error_message:
        print(f"Missing field on requested action: {error_message}")
        return False
    except configparser.MissingSectionHeaderError as error_message:
        print(f"No actions requested in issue body")
        return False

    try:
        validate_inputs(action_requests)
    except Exception as e:
        print(f"Error processing issue: {e}")
        return False

    return True


if __name__ == "__main__":
    main()