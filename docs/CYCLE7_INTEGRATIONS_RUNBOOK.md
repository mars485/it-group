# Cycle 7 — IT GROUP integrations runbook

Status: **in progress**, checked 2026-10-07 (Asia/Yekaterinburg). Do not close issue #8 yet.

## Topology and contract

1. MODX `ITG_LeadHandler`, published resource `lead-submit.html` (id 28), accepts JSON POST fields `name`, `contact` (email or phone), `message`, optional `website`, `source`, `page`, `referrer`, and `utm_*`, plus a blank `company` honeypot. It creates Person, Opportunity and follow-up Task directly through Twenty REST API and looks up an existing Person by email/phone before creating one. Four real Opportunities with `source=WEBSITE` were already confirmed. The separate Twenty workflow `IT GROUP — Website Lead → CRM` (core workflow `61622025-b41c-42e9-ae54-d4b85caf846b`, version `67ef6ccc-b16d-40e1-be31-5ddf9d0aa354`) is ACTIVE but is **not** the current MODX submission path; do not send the same lead to both paths.
2. Twenty outgoing webhook `6e9234fa-866c-4f68-bd2b-d611c36a6cf6` subscribes only to `opportunity.created` and `opportunity.updated`. Its target is the existing public HTTPS proxy `n8n.karpiev.ru` with a private webhook path. Keep the path out of Git and chat. The receiver is workflow `itgC7901e7a356f6`, `IT GROUP — Twenty opportunity events`.
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
- The first two test Opportunities did not arrive while the webhook targeted `192.168.1.160`. The installed Twenty worker's `CallWebhookJob` classifies private/internal IP targets as blocked; queue jobs completed without n8n executions. Both records were soft deleted.
- After switching to the existing HTTPS proxy, test Opportunity `af34bdb1-ebca-4176-bcb2-957fd68cae93` produced successful n8n executions **21** (created) and **22** (updated). That record was soft deleted.
- A synthetic POST to `https://itgsystem.ru/lead-submit.html` returned HTTP 200 and created Person `e100b918-b48e-4bfa-8e35-f90e50b5e7ac`, Opportunity `dbd09b27-abbe-4c1e-80f3-c7a7c63d7d4d`, and a follow-up Task. The create/update events yielded successful n8n executions **23** and **24**. The Task Target, Task, Opportunity and Person were all soft deleted afterward. Earlier failed test requests produced HTTP 502 before any lead was created.
- The website failure was caused by `ITG_LeadHandler` calling a global PHP function whose `$api` and `$key` variables were local to the MODX snippet scope. The snippet was updated with a MODX snapshot and hash verification to share these values through uniquely named globals; the website POST then passed. The API key value was never printed or committed.
- Website → Twenty → n8n is verified. The full Website → Twenty → n8n → Telegram chain is **not** verified because the recipient Chat ID is not configured.

## Failure handling and next diagnosis

1. Check n8n workflow executions for `itgC7901e7a356f6` and Twenty worker logs around a new test Opportunity. The verified baseline is executions 21–24. A successful HTTP response from a manual POST proves the receiver only; a real CRM create/update must also appear.
2. Keep the webhook on the existing HTTPS hostname: this Twenty build rejects private/internal IP targets. If delivery stops, inspect Twenty's `webhook-queue`, worker logs, HTTPS proxy and n8n executions. Do not broaden to all record events.
3. Do not enable Telegram until the destination Chat ID is confirmed through a server-side setting or a deliberate message from the intended recipient. Keep the bot token inside n8n credentials; never paste it into Git or chat. Restrict the receiver to the Twenty source and verify the webhook signature before enabling side effects.
4. For production delivery, retry transient HTTP failures with bounded backoff and a stable idempotency key based on event/record id. Store only minimal diagnostic metadata (event type, record id, timestamp, result); set an explicit execution retention period and review failures daily. n8n currently saves success/error executions, so review retention before passing real customer payloads.
5. After binding an approved Telegram Chat ID and adding signature validation, re-test one marked lead through the actual website form, confirm Person and Opportunity, n8n execution, and exactly one Telegram message. Soft delete only those test CRM records. Confirm `opportunity.updated` separately. Close issue #8 only after this and the reverse n8n → Twenty leg pass.

## Safety

No production data or volumes were deleted. The n8n workflow currently performs no external action: its Telegram node is disabled. Do not use `docker compose down -v`; preserve the n8n data directory and its encryption key during recovery.
