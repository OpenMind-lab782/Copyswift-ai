# CopySwiftAI Documents Studio — Browser E2E Execution Contract

**Project:** Documents Studio
**Workstream:** PDF EDITOR BROWSER
**Purpose:** Define the controlled execution environment and evidence requirements for real browser end-to-end verification.

## 1. Objective

The browser E2E environment SHALL provide repeatable evidence that the implemented Document Studio browser layer operates correctly through the real browser UI and the server-authoritative backend.

The browser E2E workflow SHALL verify:

`browser UI → HTTP API → Document Studio workspace → persistence → export → reopen`

The workflow SHALL NOT use production services or production databases.

## 2. Execution Environment

Browser E2E SHALL execute in an isolated GitHub-hosted `ubuntu-latest` runner.

The runner SHALL:

- use Python 3.13;
- install the repository's existing `requirements.txt`;
- install required MuPDF system dependencies;
- use a dedicated browser automation framework;
- use a controlled Chromium browser instance;
- use an isolated test database;
- start a local instance of the application;
- terminate the application after testing.

The Termux development environment SHALL NOT be required to contain a browser executable.

## 3. Dependency Boundary

Browser automation dependencies SHALL be scoped to the browser-E2E workflow/test environment.

The implementation SHALL NOT modify production runtime dependencies unless a genuine application dependency is demonstrated.

The browser binary SHALL exist only within the isolated CI execution environment.

No production deployment SHALL be triggered by browser-E2E execution.

## 4. Database Isolation

Browser E2E SHALL use an isolated database created specifically for the test run.

The test SHALL NOT connect to:

- the production PostgreSQL database;
- the production Render service;
- the repository's development `copyswift.db`;
- any user's persistent database.

Database state SHALL be disposable.

## 5. Application Isolation

The browser SHALL communicate with a locally running application instance.

The application SHALL bind only to the CI runner's local test environment.

The test SHALL wait for an explicit application readiness condition before launching browser assertions.

A browser test SHALL FAIL rather than silently continue when the application cannot become ready.

## 6. Test Fixture

The browser E2E workflow SHALL use a deterministic PDF fixture whose source identity can be independently verified.

The fixture SHALL have:

- deterministic bytes;
- known SHA-256;
- known page count;
- known page geometry;
- known original content;
- at least one editable document element;
- at least one unrelated element that must survive editing.

The test SHALL record the fixture's source SHA-256 before import.

The fixture SHALL never be overwritten by the application.

## 7. Authentication

The browser test SHALL establish an authenticated Document Studio session using a dedicated test identity.

The identity SHALL be isolated from real users.

The browser SHALL not supply a client-controlled email address as proof of workspace ownership.

Server-side session authentication SHALL remain authoritative.

## 8. Required Browser Workflow

The minimum real-browser workflow SHALL be:

1. Open Document Studio.
2. Authenticate.
3. Import the deterministic PDF.
4. Confirm successful import.
5. Confirm the imported page geometry.
6. Confirm the document token exists.
7. Select an editable element.
8. Perform a supported edit.
9. Confirm the browser enters dirty state.
10. Save.
11. Confirm server-confirmed save success.
12. Confirm the server revision changes as expected.
13. Export the saved document.
14. Confirm export success.
15. Reopen the saved document.
16. Confirm the same document token remains associated.
17. Confirm the saved revision is returned.
18. Confirm the requested edit persists.
19. Confirm unrelated document content remains present.
20. Verify source identity/integrity evidence.

## 9. Browser Interaction Coverage

The acceptance suite SHALL cover the implemented supported interactions, including:

- selection;
- movement;
- resizing;
- text editing;
- supported text styling;
- image editing;
- adding supported text;
- adding supported images;
- deletion;
- duplication;
- dirty-state handling;
- save;
- revision conflict handling;
- export;
- reopen.

An interaction SHALL only be included where the current implementation exposes that capability.

The test SHALL NOT invent unsupported browser functionality.

## 10. Persistence Verification

A successful browser interaction SHALL NOT itself be treated as persistence.

Persistence SHALL be established only after server confirmation.

After save, the test SHALL verify:

- document token;
- server revision;
- returned authoritative document;
- requested edit;
- preservation of unrelated elements.

After reopen, the test SHALL independently verify that the persisted state can be recovered from the server.

## 11. Revision Verification

The browser SHALL never invent or locally increment revisions.

The test SHALL verify that:

- save uses the server-confirmed revision;
- successful save returns the authoritative revision;
- stale revision produces the documented conflict;
- local unsaved work survives a conflict;
- reopen returns the server's revision;
- export does not operate against a stale revision.

## 12. Export Verification

Export success SHALL NOT be considered sufficient browser acceptance.

The test SHALL establish that the exported result corresponds to the saved authoritative document.

Where practical, the exported PDF SHALL be independently inspected for:

- valid PDF structure;
- expected page count;
- expected page geometry;
- requested edit;
- preservation of unrelated content.

## 13. Source Preservation

The test SHALL establish that browser editing does not replace the imported source identity.

At minimum, evidence SHALL cover:

- original source SHA-256;
- document token;
- baseline/source identity;
- page count;
- page geometry;
- preservation of unrelated elements.

The original source bytes SHALL NOT be replaced by the exported or edited PDF.

## 14. Failure Semantics

The test SHALL fail closed.

The browser test SHALL FAIL if:

- authentication unexpectedly fails;
- import fails;
- page geometry changes unexpectedly;
- document token changes unexpectedly;
- save is reported successful without server confirmation;
- revision becomes inconsistent;
- stale save succeeds;
- local work is silently discarded;
- export succeeds against stale state;
- reopen returns an unexpected workspace;
- source identity is not preserved;
- an expected browser control is absent;
- the application cannot become ready.

The test SHALL NOT convert an error into an apparent PASS.

## 15. Evidence

A successful browser-E2E run SHALL produce machine-readable test results.

On failure, the workflow SHOULD preserve:

- browser screenshot;
- browser console output;
- application logs;
- browser trace where supported;
- relevant HTTP failure information.

Evidence SHALL identify the commit tested.

No secret, production credential, production database URL, or real user data SHALL be included in artifacts.

## 16. CI Boundary

Browser E2E SHALL be implemented as a dedicated workflow rather than silently modifying the existing Payment Engine CI semantics.

The browser workflow SHALL be independently identifiable.

It SHALL run against the repository commit supplied by GitHub Actions.

Production deployment SHALL remain a separate operation.

## 17. Human-Control Boundary

The browser-E2E workflow SHALL validate the implementation but SHALL NOT authorize:

- production deployment;
- production database mutation;
- automatic remediation;
- automatic source modification;
- automatic commit;
- automatic merge.

A failing browser test SHALL stop the verification chain.

## 18. Acceptance Rule

The browser editing layer SHALL NOT be declared browser-E2E verified merely because:

- Python tests pass;
- HTTP tests pass;
- static JavaScript syntax passes;
- export succeeds;
- the application starts successfully.

Browser-E2E acceptance requires actual execution through a real browser against the isolated application runtime.

## 19. Final Verification Chain

The intended evidence chain is:

`Static validation`
→ `Python tests`
→ `isolated HTTP runtime`
→ `isolated real-browser E2E`
→ `source-integrity verification`
→ `human review`
→ `approval for any subsequent commit/deployment`

This contract does not authorize production deployment or production mutation.
