# Design authority and change control

Version: 0.1 | Date: 8 October 2026 | Status: Draft

Human direction -> requirements -> architecture/contracts -> human design approval -> scoped implementation -> tests/checks -> PR -> human approval -> merge.

Documents: Draft -> In Review -> Approved. ADRs: Proposed -> Accepted, then Deprecated or Superseded. Record owner, version/date, approver, decision evidence and history. No agent self-approval; no approval inferred from generated text. Conflicting sources require explicit resolution.

Routine local implementation choices fit an approved task. Service boundaries, stores, public/event compatibility, identity/tenancy, model/provider, infrastructure exposure and required user behaviour changes need a design-change proposal before implementation.

Work on a task branch; consult relevant approved sources; implement scope; verify; update contracts/docs/traceability; PR; automated/specialist review; human approval. Deployment, spend, destructive migration, shared-platform changes and merge require applicable authorisation. The current task authorises writing this draft pack, not those actions.

ChatGPT prepares design/specifications; Copilot implements approved slices. Architecture/security/reviewer agents advise, never replace human authority. Audit concise decisions and evidence, not private model reasoning.
