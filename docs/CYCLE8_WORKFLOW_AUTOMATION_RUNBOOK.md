# Cycle 8 — Workflow Automation runbook

Status: completed 2026-10-07 (Asia/Yekaterinburg).

## Active workflows

| Workflow | Trigger | Action |
| --- | --- | --- |
| Twenty `IT GROUP — Задача по следующему контакту` (`32e5933f-009e-4199-a60f-a130cfb68e4f`) | `opportunity.updated` when `nextContactAt` is set and stage is open | Creates a linked TODO only if `followUpTaskId` is empty; otherwise updates the existing task. |
| Twenty `IT GROUP — Завершение Follow-up` (`f278b09b-d35c-4bb1-8506-636bb3746c47`) | Linked task changes to `DONE` | Clears `nextContactAt` and `followUpTaskId`; sets `nextAction` to `Назначить следующий контакт`. |
| n8n `IT GROUP — Daily Follow-up digest` (`itgC8Digest20261007`) | Daily 09:00 in `Asia/Yekaterinburg` | Reads up to 100 Twenty tasks with encrypted API credential, counts open `Follow-up:` tasks due today or overdue, and sends one count-only Telegram message to the approved IT GROUP chat. Sends nothing if both counts are zero. |

The MODX lead handler creates an initial intake task. It does not set `nextContactAt`, so the scheduled Follow-up workflow does not create a duplicate at submission. When a manager sets a next contact date, the Follow-up workflow creates its separate dated task and thereafter updates that same task.

The Twenty `IT GROUP — Напоминание о Follow-up` draft remains inactive: its SEND_EMAIL step has no approved recipient or content. The active n8n digest does not send customer email. Twenty `Quick Lead` supplies an existing manual workflow; the website and Twenty webhook workflows cover webhook triggers.

## n8n contract

- Template: [`follow-up-digest.template.json`](../integrations/n8n/follow-up-digest.template.json). It has placeholders and a disabled Telegram node. Bind the existing encrypted Twenty API and `Telegram IT GROUP` credentials plus recipient privately in n8n. Never commit the runtime workflow or Chat ID.
- The schedule uses `0 9 * * *` with workflow timezone `Asia/Yekaterinburg`. It is published and active. At most one summary is sent per scheduled run. A manual replay can send a duplicate; inspect Telegram delivery before retrying.
- HTTP read and Telegram send each retry up to three times with five seconds between attempts. The Code step rejects an unexpected response or a `hasNextPage` result rather than sending an incomplete summary. If the active task count reaches 100, add pagination before resuming the digest.
- n8n saves successful and failed executions so run statuses are reliable in this installed version. These executions may contain task data from the Twenty API response even though Telegram receives only counts. Restrict n8n access and configure retention according to customer-data policy. Review failures daily.
- The inactive `IT GROUP — Cycle 8 task API probe` (`itgC8TaskAuditProbe`) was used to verify authenticated read access and has no trigger or side effect.

## Verification

1. Read-only inventory found nine Twenty workflows. The two Follow-up database-event workflows were active; their recent runs were completed. The email reminder was draft, so it was not activated.
2. Test Opportunity `7d103176-5165-493e-bc8e-207fee822682` was created with source `OTHER`, outside the website Telegram notification filter. Setting `nextContactAt` created Task `6a2bcb52-a8d8-4b87-834e-3409994793ad` and one Task Target. Moving the contact date updated the same task id and due date. Marking it `DONE` cleared the Opportunity date/task link and set the next action. Task Target, Task, and Opportunity were soft deleted. Twenty run history shows completed Follow-up creation/update and completion runs.
3. The n8n manual probe read Twenty tasks and computed `dueToday=0`, `overdue=1` without sending. An enabled manual test yielded exactly one Telegram API `message_id` response. The workflow was restored to its daily Schedule Trigger and published.
4. A temporary every-minute schedule with Telegram disabled yielded n8n trigger execution **74**, status `success`, at 20:05 local time. The production cron, timezone and Telegram-enabled state were re-exported and verified after restoration. The temporary CLI and interrupted schedule test runs 35, 51, 72, 73 remain as historical `running` rows in n8n; execution 74 and later scheduled runs are the reliable baseline. Do not replay those old test rows.

## Monitoring and recovery

1. In Twenty, review runs of the two active Follow-up workflows for `FAILED`. Use `get_workflow_run` for failed step diagnostics. Check a deal's `followUpTaskId` before manually creating or replaying a task.
2. In n8n, review the digest's Executions. Confirm the next 09:00 run completes; a zero-count day has no Telegram send. On HTTP failure, verify Twenty availability and credential validity. On Telegram failure, verify the bot credential and recipient in n8n, then check whether Telegram accepted a message before replaying.
3. n8n encrypted workflow and credential backups are under `/DATA/AppData/n8n/backups/cycle8-before-20261007/` and `/DATA/AppData/n8n/backups/cycle8-final-20261007/`. Keep them with the n8n encryption key and persistent data directory. Restore without deleting volumes or using `docker compose down -v`.
