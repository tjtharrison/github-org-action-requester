"""Process issue from GitHub API."""

import configparser
import os
import subprocess
import yaml
import shutil

# If not on github actions, load .env file
if not os.environ.get("GITHUB_ACTIONS"):
    import dotenv

    dotenv.load_dotenv()

gh_issue_title = os.environ["GH_ISSUE_TITLE"]
gh_issue_body = os.environ["GH_ISSUE_BODY"]
gh_issue_number = os.environ["GH_ISSUE_NUMBER"]
gh_issue_author = os.environ["GH_ISSUE_AUTHOR"]
ACTION_DIR = "action_dir"


def read_issue_body():
    """
    Read issue body provided and return action request.

    Raises:
        KeyError: If issue body is missing required fields.

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
            action_request = {
                "name": config[section]["name"],
                "description": config[section]["description"],
                "version": config[section]["requested_version"],
            }
    except KeyError as error_message:
        raise KeyError(str(error_message)) from error_message

    print("Action request parsed successfully")

    return action_request


def validate_inputs(action_request):
    """
    Validate action request inputs.

    Args:
        action_request (dict): Dictionary with action request.

    Raises:
        Exception: If provided values are not valid.

    Returns:
        True if provided values are valid.

    """
    print("Creating working directory")
    try:
        os.mkdir(ACTION_DIR)
    except FileExistsError:
        print("Working directory already exists, removing")
        shutil.rmtree(ACTION_DIR)

    print("Validating action request inputs")
    action_name = action_request["name"]
    action_version = action_request["version"]

    print(f"Processing {action_name}@{action_version}")

    # Check if action is available
    print("Checking if action is available")
    try:
        subprocess.check_output(
            f"gh repo clone {action_name} {ACTION_DIR} -- -b {action_version}",
            shell=True,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as error_message:
        print(f"Error cloning action: {error_message}")
        raise Exception(f"Error cloning action: {error_message}") from error_message

    print(
        "Repository cloned successfully at requested version, working directory ready"
    )

    return True


def main():
    """
    Process issue from GitHub API.

    Returns:
        True if issue is processed successfully.
    """
    # Parse values from issue body
    print(f"Processing issue: #{gh_issue_number}")
    try:
        action_request = read_issue_body()
    except TypeError as error_message:
        print(f"Error reading issue body: {error_message}")
        return False
    except KeyError as error_message:
        print(f"Missing field on requested action: {error_message}")
        return False
    except configparser.MissingSectionHeaderError as error_message:
        print("No actions requested in issue body")
        return False

    # Validate inputs
    try:
        validate_inputs(action_request)
    except Exception as error_message:
        print(f"Error processing issue: {error_message}")
        return False

    print()
    print("Issue processed successfully")
    # Remove .git directory from working directory
    print("Removing .git directory from working directory")
    try:
        subprocess.check_output(
            f"rm -rf {ACTION_DIR}/.git", shell=True, stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as error_message:
        print(f"Error removing .git directory: {error_message}")
        return False

    print("Writing action request to file")
    # Write action request to file
    try:
        with open(f"action_request.txt", "w", encoding="UTF-8") as action_request_file:
            action_request_file.write(
                f'Action name: {action_request["name"]}\n'
                f'Action description: {action_request["description"]}\n'
                f'Action version: {action_request["version"]}\n'
            )
    except KeyError as error_message:
        print(f"Error writing action request to file: {error_message}")
        return False

    # Updating request yaml
    print("Updating request yaml")
    try:
        with open("github-actions-allow-list.yml") as github_actions_allow_list:
            action_allow_list_contents = yaml.safe_load(github_actions_allow_list)
    except FileNotFoundError:
        print("github-actions-allow-list.yml not found")
        raise FileNotFoundError
    except yaml.YAMLError as error_message:
        raise yaml.YAMLError() from error_message

    # Add action to allow list
    full_action_name = f'{action_request["name"]}/{action_request["version"]}'
    if full_action_name not in action_allow_list_contents["actions"]:
        print(f"Adding {full_action_name} to allow list")
        action_allow_list_contents["actions"].append(full_action_name)
    else:
        print(f"{full_action_name} already in allow list")

    # Write allow list to file
    try:
        with open("github-actions-allow-list.yml", "w") as github_actions_allow_list:
            yaml.dump(action_allow_list_contents, github_actions_allow_list)
    except yaml.YAMLError as error_message:
        raise yaml.YAMLError() from error_message


    print("All done, exiting")
    return True


if __name__ == "__main__":
    main()
