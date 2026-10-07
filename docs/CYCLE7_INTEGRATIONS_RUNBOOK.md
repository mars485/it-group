# Cycle 7 — IT GROUP integrations runbook

Status: **in progress**, checked 2026-10-07 (Asia/Yekaterinburg). Do not close issue #8 yet.

## Topology and contract

1. MODX `ITG_LeadHandler`, published resource `lead-submit` (id 28), sends a lead to the active Twenty workflow `IT GROUP — Website Lead → CRM` (core workflow `61622025-b41c-42e9-ae54-d4b85caf846b`, version `67ef6ccc-b16d-40e1-be31-5ddf9d0aa354`). Its POST body uses `name`, `email`, `phone`, `message`, `page`, and optional `utm_source`. The workflow creates Person and Opportunity with `source=WEBSITE`.
2. Twenty outgoing webhook `6e9234fa-866c-4f68-bd2b-d611c36a6cf6` subscribes only to `opportunity.created` and `opportunity.updated`. Its target is the private n8n webhook URL. Keep the private path out of Git and chat. The receiver is workflow `itgC7901e7a356f6`, `IT GROUP — Twenty opportunity events`.
3. The n8n receiver normalizes event name, record id, and receive time. Its Telegram send node is **disabled** until a recipient Chat ID is approved and bound. A Telegram bot credential exists in n8n; the existing bot workflow derives Chat ID from an inbound message and does not provide a fixed notification recipient.
4. n8n → Twenty should call the existing active Twenty inbound workflow through an HTTP Request node. Bind its exact URL privately from the deployed MODX handler or Twenty workflow UI; do not copy the URL into the repository. Before enabling, add a stable external lead id and deduplication so a retry cannot create another Person/Opportunity. This reverse leg has not been deployed or tested.

## ZimaOS deployment facts

- Host: `ainur@192.168.1.160`, SSH key `~/.ssh/codex_zimaos`.
- n8n is an existing CasaOS Compose app at `/var/lib/casaos/apps/n8n/docker-compose.yml`, image reported as `n8nio/n8n:2.29.1` by Docker (the app log reports runtime `2.22.3`; resolve this discrepancy before upgrades). Container `n8n` listens on port 5678 and mounts `/DATA/AppData/n8n` to `/home/node/.n8n`.
- A pre-change encrypted backup of all n8n workflows and credentials is in `/DATA/AppData/n8n/backups/cycle7-20261007/`, restricted to the container user. Keep it with the n8n encryption key and data directory. No existing Compose file or other service data was changed.
- The import template is [`integrations/n8n/twenty-events.template.json`](../integrations/n8n/twenty-events.template.json). Replace both `REPLACE_WITH_*` values privately, import with the n8n CLI, publish, then restart only n8n to register its webhook. Do not import the template over an existing workflow id without a fresh backup.

## Verification on 2026-10-07

- `n8n` health endpoint: HTTP 200; direct test POST to its private webhook: HTTP 200, execution 20 `success`.
- Twenty server and worker can both GET the n8n health endpoint: HTTP 200.
- Twenty webhook registration lists `opportunity.created` and `opportunity.updated`.
- Test Opportunities `469f8eca-9e49-4883-b717-0f08d0ed256d` and `ed89f4b2-1246-4044-90f0-3a60769081d1` were created; the first was updated. No new n8n execution appeared after either create/update, including after restarting the Twenty worker. Both test records were soft deleted.
- Website → Twenty was already evidenced by four real `source=WEBSITE` deals. The full Website → Twenty → n8n → Telegram chain is **not** verified.

## Failure handling and next diagnosis

1. Check n8n workflow executions for `itgC7901e7a356f6` and Twenty worker logs around a new test Opportunity. A successful HTTP response from a manual POST proves the receiver only; it does not prove Twenty emits events.
2. Inspect Twenty's outgoing webhook dispatcher and queue, including whether its private-network target is filtered, whether event names match this version's runtime, and whether server/worker webhook caches refresh. Use a receiver under approved HTTPS if private HTTP is disallowed. Do not broaden to all record events.
3. Do not enable Telegram until the destination Chat ID is confirmed through a server-side setting or a deliberate message from the intended recipient. Keep the bot token inside n8n credentials; never paste it into Git or chat. Restrict the receiver to the Twenty source and verify the webhook signature before enabling side effects.
4. For production delivery, retry transient HTTP failures with bounded backoff and a stable idempotency key based on event/record id. Store only minimal diagnostic metadata (event type, record id, timestamp, result); set an explicit execution retention period and review failures daily. n8n currently saves success/error executions, so review retention before passing real customer payloads.
5. Re-test one marked test lead through the actual website form, confirm Person and Opportunity, n8n execution, and exactly one Telegram message. Soft delete only those test CRM records. Confirm `opportunity.updated` separately. Close issue #8 only after this and the reverse n8n → Twenty leg pass.

## Safety

No production data or volumes were deleted. The n8n workflow currently performs no external action: its Telegram node is disabled. Do not use `docker compose down -v`; preserve the n8n data directory and its encryption key during recovery.
