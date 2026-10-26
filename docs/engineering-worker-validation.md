# Engineering worker validation boundaries

The review-only engineering worker is a bounded verification prototype, not an autonomous task executor.

## Required pull-request checks

- `test` validates the configured Python dependency setup, application compilation, and unit-test suite.
- `Real Chromium Document Studio E2E` validates the configured browser-based Document Studio scenarios in its test environment.
- A workflow run that ends in `startup_failure` before creating any jobs is an infrastructure or workflow-startup failure; it is not evidence that the test assertions passed or failed.

## Safe acceptance rule

Keep the pull request unmerged until both required checks have fresh successful results for the current pull-request head and the repository's required review approval is present. Do not bypass branch protection to resolve a failed or missing check.

A green result proves only the checks and scenarios actually executed. It does not establish production readiness, canonical project registration, task authorization, or isolation of arbitrary task code.

## Worker scope

The current worker fetches the exact source commit and runs fixed dependency-installation, compilation, and unit-test commands. It has read-only repository permissions and does not apply patches, commit, deploy, or receive production credentials. Dependency installation is not fully reproducible until the dependency set is completely hash-locked.
