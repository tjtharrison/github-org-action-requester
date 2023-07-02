"""Collect detail from the requested action."""

import os
import subprocess

import requests


def get_action_name():
    """
    Get action name from the requested action.

    Raises:
        subprocess.CalledProcessError: If git command fails.

    Returns:
        Action name.
    """
    # Get modified action
    try:
        modified_action_name = (
            str(
                subprocess.check_output(
                    f'git diff main HEAD github-actions-allow-list.yml | grep "^+" | grep -v "yml"',
                    shell=True,
                    stderr=subprocess.STDOUT,
                )
            )
            .replace("+- ", "")
            .strip()
            .replace("\\n'", "")
        )
    except subprocess.CalledProcessError as error_message:
        print(f"Error getting modified action name: {error_message}")
        raise subprocess.CalledProcessError from error_message

    print(modified_action_name)

    return modified_action_name


def get_security_policy(action_name):
    """
    Get security policy from the requested action.

    Args:
        action_name: Action name.

    Returns:
        Security policy or None.
    """
    # Get security policy
    security_policy = (
        str(
            subprocess.check_output(
                f"gh api repos/{action_name}/community/profile",
                shell=True,
                stderr=subprocess.STDOUT,
            )
        )
        .replace('b\'{"security_advisories_url": "', "")
        .strip()
        .replace("\\n'", "")
    )

    return security_policy


def main():
    """Run main function."""
    action_name = get_action_name().split("@")[0].strip()
    action_version = get_action_name().split("@")[1].strip()

    try:
        security_policy = get_security_policy(f"{action_name}@{action_version}")
    except subprocess.CalledProcessError:
        security_policy = None

    # Check if dependabot is enabled via graphql
    dependabot_enabled = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
        json={
            "query": f'query {{ repository(owner: "{action_name.split("/")[0]}", name: "{action_name.split("/")[1]}") {{ hasIssuesEnabled }} }}'
        },
        timeout=5,
    ).json()["data"]["repository"]["hasIssuesEnabled"]

    # Check dependabot findings via graphql
    dependabot_findings = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
        json={
            "query": f'query {{ repository(owner: "{action_name.split("/")[0]}", name: "{action_name.split("/")[1]}") {{ vulnerabilityAlerts(first: 100) {{ nodes {{ securityVulnerability {{ package {{ name }} severity }} }} }} }} }}'
        },
        timeout=5,
    ).json()["data"]["repository"]["vulnerabilityAlerts"]["nodes"]

    # Check if codeql is enabled via graphql
    codeql_enabled = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
        json={
            "query": f'query {{ repository(owner: "{action_name.split("/")[0]}", name: "{action_name.split("/")[1]}") {{ hasIssuesEnabled }} }}'
        },
        timeout=5,
    ).json()["data"]["repository"]["hasIssuesEnabled"]

    # Get count of recent commits via graphql
    recent_commits = requests.post(
        "https://api.github.com/graphql",
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
        json={
            "query": f'query {{ repository(owner: "{action_name.split("/")[0]}", name: "{action_name.split("/")[1]}") {{ defaultBranchRef {{ target {{ ... on Commit {{ history(first: 100) {{ totalCount }} }} }} }} }} }}'
        },
        timeout=5,
    ).json()["data"]["repository"]["defaultBranchRef"]["target"]["history"][
        "totalCount"
    ]

    # Get url for README
    readme = f"https://github.com/{action_name}/blob/main/README.md"

    print(
        "\n".join(
            [
                f"Action name: {action_name}",
                "",
                "Security 🔒",
                f"Security policy: {security_policy} 📄"
                "\n"
                f"Dependabot enabled: {dependabot_enabled} 🕵"
                "\n"
                f"Open vulnerabilities: {len(dependabot_findings)} 🐛",
                "\n" "Code quality 📈",
                f"CodeQL enabled: {codeql_enabled} 🤖",
                f"Recent commits: {recent_commits} 📅",
                "\n" "Documentation 📖",
                f"README: [link]({readme}) 📄",
            ]
        )
    )


if __name__ == "__main__":
    main()
