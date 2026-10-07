# Cycle 7 — IT GROUP integrations runbook

Status: **completed**, verified 2026-10-07 (Asia/Yekaterinburg).

## Topology and contract

1. MODX `ITG_LeadHandler`, published resource `lead-submit.html` (id 28), accepts JSON POST fields `name`, `contact` (email or phone), `message`, optional `website`, `source`, `page`, `referrer`, and `utm_*`, plus a blank `company` honeypot. It creates Person, Opportunity and follow-up Task directly through Twenty REST API and looks up an existing Person by email/phone before creating one. Four real Opportunities with `source=WEBSITE` were already confirmed. The separate Twenty workflow `IT GROUP — Website Lead → CRM` (core workflow `61622025-b41c-42e9-ae54-d4b85caf846b`, version `67ef6ccc-b16d-40e1-be31-5ddf9d0aa354`) is ACTIVE but is **not** the current MODX submission path; do not send the same lead to both paths.
2. Twenty outgoing webhook `6e9234fa-866c-4f68-bd2b-d611c36a6cf6` subscribes only to `opportunity.created` and `opportunity.updated`. Its target is the existing public HTTPS proxy `n8n.karpiev.ru` with a private webhook path. Keep the path out of Git and chat. The receiver is workflow `itgC7901e7a356f6`, `IT GROUP — Twenty opportunity events`.
3. The n8n receiver checks the event timestamp (five-minute window), recomputes Twenty's HMAC-SHA256 with an encrypted credential, and compares it before normalizing event metadata. Only `opportunity.created` with `source=WEBSITE` reaches the enabled Telegram node; updates do not send a second alert. The node uses the encrypted `Telegram IT GROUP` credential for `@itgsystem_bot` and the recipient found from the intended chat after the old bot webhook was removed. It retries up to three times with five seconds between attempts. Bot token and Chat ID remain inside n8n.
4. n8n → Twenty is checked by manual workflow `itgC7TwentyApiChk`, `IT GROUP — Twenty API connectivity check`: an authenticated HTTP GET of Twenty REST metadata completed successfully. The workflow is inactive, so it has no scheduled side effect. Its `httpHeaderAuth` credential `itgC7TwentyHeader` is encrypted by n8n and currently uses the existing MODX Twenty API key. The plaintext transfer files were removed. The import template is [`integrations/n8n/twenty-api-check.template.json`](../integrations/n8n/twenty-api-check.template.json). Before enabling any write flow, issue a dedicated least-privilege key and add a stable external lead id/deduplication so a retry cannot create another Person/Opportunity. A write from n8n has not been tested.

## ZimaOS deployment facts

- Host: `ainur@192.168.1.160`, SSH key `~/.ssh/codex_zimaos`.
- n8n is an existing CasaOS Compose app at `/var/lib/casaos/apps/n8n/docker-compose.yml`, image reported as `n8nio/n8n:2.29.1` by Docker (the app log reports runtime `2.22.3`; resolve this discrepancy before upgrades). Container `n8n` listens on port 5678 and mounts `/DATA/AppData/n8n` to `/home/node/.n8n`.
- Encrypted workflow and credential backups were made before changes, after setup, and before Telegram binding under `/DATA/AppData/n8n/backups/`, restricted to the container user. Keep them with the n8n encryption key and data directory. No existing Compose file or other service data was changed.
- The import template is [`integrations/n8n/twenty-events.template.json`](../integrations/n8n/twenty-events.template.json). Bind its placeholders privately, import, publish, then restart only n8n to register its webhook. Do not import the template over an existing workflow id without a fresh backup.

## Verification on 2026-10-07

- `n8n` health endpoint: HTTP 200; direct test POST to its private webhook: HTTP 200, execution 20 `success`.
- Twenty server and worker can both GET the n8n health endpoint: HTTP 200.
- Twenty webhook registration lists `opportunity.created` and `opportunity.updated`.
- The first two test Opportunities did not arrive while the webhook targeted `192.168.1.160`. The installed Twenty worker's `CallWebhookJob` classifies private/internal IP targets as blocked; queue jobs completed without n8n executions. Both records were soft deleted.
- After switching to the existing HTTPS proxy, test Opportunity `af34bdb1-ebca-4176-bcb2-957fd68cae93` produced successful n8n executions **21** (created) and **22** (updated). That record was soft deleted.
- Manual n8n → Twenty API workflow `itgC7TwentyApiChk` executed successfully using its encrypted header credential and returned Twenty REST metadata. The large temporary CLI output was removed without printing its body.
- A synthetic POST to `https://itgsystem.ru/lead-submit.html` returned HTTP 200 and created Person `e100b918-b48e-4bfa-8e35-f90e50b5e7ac`, Opportunity `dbd09b27-abbe-4c1e-80f3-c7a7c63d7d4d`, and a follow-up Task. The create/update events yielded successful n8n executions **23** and **24**. The Task Target, Task, Opportunity and Person were all soft deleted afterward. Earlier failed test requests produced HTTP 502 before any lead was created.
- The website failure was caused by `ITG_LeadHandler` calling a global PHP function whose `$api` and `$key` variables were local to the MODX snippet scope. The snippet was updated with a MODX snapshot and hash verification to share these values through uniquely named globals; the website POST then passed. The API key value was never printed or committed.
- The final marked website lead returned HTTP 200 and yielded successful n8n executions **32** (`opportunity.created`) and **33** (`opportunity.updated`). Execution 32 produced exactly one Telegram API message response; execution 33 produced none. All related test Person, Opportunity, Task and Task Target records were soft deleted.
- A legitimate signed event reached normalization; a forged POST was dropped before normalization. The final Telegram test used the IT GROUP bot, not the older unrelated bot.

## Failure handling and next diagnosis

1. Check n8n workflow executions for `itgC7901e7a356f6` and Twenty worker logs around a new test Opportunity. The verified baseline is executions 21–24. A successful HTTP response from a manual POST proves the receiver only; a real CRM create/update must also appear.
2. Keep the webhook on the existing HTTPS hostname: this Twenty build rejects private/internal IP targets. If delivery stops, inspect Twenty's `webhook-queue`, worker logs, HTTPS proxy and n8n executions. Do not broaden to all record events.
3. The receiver verifies Twenty's HMAC signature and timestamp before side effects. If verification fails, inspect the encrypted HMAC credential, Twenty secret, server clocks and n8n execution log. Do not bypass verification.
4. Telegram has bounded retry (three attempts, five seconds apart). For an exhausted failure, check whether Telegram already accepted the message before replaying an execution. Manual replays can duplicate alerts: this route has no durable cross-retry idempotency store.
5. Review failed executions daily and set execution-data retention according to customer-data policy. n8n currently saves both successful and failed executions. Preserve backups with the same encryption key; verify workflow activation and HMAC after recovery.

## Safety

No production data or volumes were deleted. The Telegram node is active for new WEBSITE opportunities. Do not use `docker compose down -v`; preserve the n8n data directory and its encryption key during recovery.
