# github-org-action-requester

# THIS IS A WIP

Repository for managing request for GitHub Actions in a GitHub Organization. 

It works with [github-actions-allow-list-as-code-action](https://github.com/ActionsDesk/github-actions-allow-list-as-code-action) to update the allow list for GitHub Actions across a GitHub Org after running a set of security tooling and actions against requested action.

## Sequence diagram

```mermaid
sequenceDiagram
    Issue->>Assess workflow: Request for new GitHub Action
    Assess workflow-->>Assess workflow: Verifies input
    Assess workflow-->>Sec scan branch PR: Creates branch & PR
    Sec scan branch PR-->>Sec scan workflow: Triggers workflow
    Sec scan workflow-->>Sec scan workflow: Clone action repo
    Sec scan workflow-->>Sec scan workflow: Runs security scan (CodeQL)
    Sec scan workflow-->>Sec scan branch PR: Return status
    Sec scan branch PR-->>Req action workflow: Triggers workflow
    Req action workflow-->>Req action workflow: Collects action detail
    Req action workflow-->>Sec scan branch PR: Return detail
    Sec scan branch PR-->>CODEOWNER: Notification of PR
    CODEOWNER-->>Sec scan branch PR: Approve PR
    Sec scan branch PR-->>Sec scan branch PR: Merge PR
    Sec scan branch PR-->>Sec scan branch PR: Delete branch
    Sec scan branch PR-->>Issue: Issue updated and closed
    
```

# Requirements

* This repo requires a PAT with Organisation admin rights to be added as a secret to the repo. The PAT is used to create a branch and PR to update the allow list for GitHub Actions across a GitHub Org.
* Access to CodeQL scanning on GitHub (Eg public repository or GHAS license)
* 
