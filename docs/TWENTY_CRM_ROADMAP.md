# Twenty CRM — Roadmap IT GROUP

> Цель: превратить self-hosted Twenty CRM в единую операционную систему продаж IT GROUP и последовательно реализовать возможности, подтверждённые через Twenty MCP.

## Текущее состояние

Уже реализовано:
- воронка: Новый лид → Первый контакт → Есть интерес → Выявление потребности → КП отправлено → Переговоры → Успешно / Проиграно;
- поля сделки: Источник, Услуга, Статус связи, Следующий контакт, Следующее действие, Бюджет клиента, Причина отказа;
- поле компании: Отрасль;
- представления: Воронка продаж, Все сделки, Кому написать сегодня, Просроченные Follow-up, Новые лиды;
- workflow «IT GROUP — Инициализация нового лида»: новый лид получает статус связи «Не связывались» и действие «Связаться с новым лидом».

## Принципы реализации

1. Работать короткими циклами с измеримым Definition of Done.
2. Сначала штатные возможности Twenty и MCP; кастомный код — только когда штатного механизма недостаточно.
3. Не удалять production-данные и Docker volumes.
4. Автоматизации перед активацией валидировать.
5. Любые массовые изменения сначала проверять выборкой.
6. Каждая интеграция должна иметь наблюдаемость: понятную ошибку, лог или контрольное представление.

## Roadmap

### Cycle 1 — CRM Core + Follow-up
**Цель:** ни один активный лид не должен теряться после первого контакта.

- [x] Настроить стадии продаж.
- [x] Создать CRM-поля.
- [x] Создать рабочие views.
- [x] Инициализировать новый лид.
- [ ] Автоматизировать создание Follow-up-задачи.
- [ ] Контролировать сделки без следующего контакта.
- [ ] Контролировать просроченные Follow-up.
- [ ] Останавливать Follow-up для WON/LOST.
- [ ] Провести end-to-end тест тестовой сделки.

**DoD:** для каждого активного лида видно следующее действие и срок; просрочка обнаруживается; закрытые сделки не создают новые Follow-up.

### Cycle 2 — Sales Dashboard
**Цель:** руководитель видит состояние продаж на одном экране.

- [ ] KPI: активные сделки.
- [ ] KPI: сумма воронки.
- [ ] KPI: Won за период.
- [ ] KPI: новые лиды.
- [ ] График сделок по стадиям.
- [ ] График по источникам.
- [ ] График по услугам.
- [ ] Просроченные Follow-up.
- [ ] Таблица «Кому написать сегодня».

Инструменты: dashboards, dashboard tabs/widgets, aggregate/bar/line/pie charts, record-table widgets.

### Cycle 3 — CRM UX + Data Model
**Цель:** карточки и структура Twenty соответствуют процессам IT GROUP.

- [ ] Оптимизировать карточку сделки.
- [ ] Оптимизировать карточку компании.
- [ ] Оптимизировать карточку контакта.
- [ ] Добавить недостающие custom objects/fields.
- [ ] Настроить table/kanban/calendar views.
- [ ] Настроить фильтры, сортировки и колонки.
- [ ] Нормализовать обязательные поля.

Инструменты: object metadata, field metadata, views, view fields, filters, sorts.

### Cycle 4 — Lead Generation
**Цель:** стандартизировать поступление и обработку холодных и входящих лидов.

- [ ] 2ГИС / ручной импорт.
- [ ] Лиды с сайта.
- [ ] Источники Avito, Telegram, WhatsApp, рекомендации.
- [ ] Bulk create/upsert.
- [ ] Дедупликация People/Companies.
- [ ] Автоматическое создание сделки.
- [ ] Первичная квалификация.

Инструменты: People/Companies/Opportunities CRUD, bulk operations, upsert, crm-hygiene, enrich.

### Cycle 5 — Tasks, Notes, Files, Timeline
**Цель:** история взаимодействия хранится внутри CRM.

- [ ] Связывать задачи со сделками/компаниями/контактами.
- [ ] Связывать заметки с CRM-записями.
- [ ] Использовать attachments.
- [ ] Контролировать timeline activity.
- [ ] Стандартизировать шаблоны заметок и задач.

Инструменты: Tasks, Notes, Task Targets, Note Targets, Attachments, Timeline Activities.

### Cycle 6 — Communications
**Цель:** коммуникации становятся частью CRM-процесса.

- [ ] Подключить рабочий email.
- [ ] Черновики follow-up писем.
- [ ] Отправка писем из CRM-процесса.
- [ ] Messages / threads.
- [ ] Calendar events + participants.
- [ ] Call recordings при доступности.
- [ ] Campaigns / Lists.

Инструменты: send_email, draft_email, Messages, Message Threads, Calendar Events, Participants, Call Recordings, Campaigns, Lists, Blocklists.

### Cycle 7 — Integrations + Webhooks
**Цель:** связать Twenty с инфраструктурой IT GROUP.

- [ ] Website → Twenty.
- [ ] n8n ↔ Twenty.
- [ ] Telegram ↔ Twenty.
- [ ] Webhooks для record events.
- [ ] Webhooks для metadata events.
- [ ] HTTP-интеграции через workflow.
- [ ] Обработка ошибок интеграций.

Инструменты: Webhooks, workflow HTTP/CODE steps, TypeScript logic functions.

### Cycle 8 — Workflow Automation
**Цель:** автоматизировать повторяющиеся операции продаж.

- [ ] DATABASE_EVENT workflows.
- [ ] CRON workflows.
- [ ] MANUAL workflows.
- [ ] WEBHOOK workflows.
- [ ] Branching / conditions.
- [ ] Iterators.
- [ ] Workflow run monitoring.
- [ ] Error diagnostics.
- [ ] Version validation/activation.

Инструменты: workflow create/version/steps/edges/validation/activation/runs, logic function source.

### Cycle 9 — AI CRM
**Цель:** AI помогает продавать, а не заменяет контроль процесса.

- [ ] AI-квалификация лида.
- [ ] Резюме истории клиента.
- [ ] Следующее лучшее действие.
- [ ] Черновик follow-up.
- [ ] Черновик КП.
- [ ] Анализ причин отказа.
- [ ] Приоритизация сделок.
- [ ] AI Agent steps с контролируемым JSON output.

Инструменты: AI_AGENT workflow steps, update_agent, code-interpreter, deal-review, meeting-prep.

### Cycle 10 — Security + Roles
**Цель:** подготовить CRM к работе команды.

- [ ] Роли: Admin / Sales / Manager / Read-only.
- [ ] Object permissions.
- [ ] Row-level permissions при доступности лицензии.
- [ ] Минимально необходимые права.
- [ ] Проверка API/MCP access.

Инструменты: roles, object permissions, row-level permission rules, workspace members.

### Cycle 11 — Data Quality + Operations
**Цель:** CRM остаётся чистой по мере роста.

- [ ] Поиск дублей.
- [ ] Нормализация телефонов/email.
- [ ] Контроль пустых критичных полей.
- [ ] Bulk correction.
- [ ] Upsert/import routines.
- [ ] Регулярный CRM hygiene review.

Инструменты: crm-hygiene, data-manipulation, bulk CRUD/upsert, XLSX.

### Cycle 12 — Reporting + Documents
**Цель:** получать управленческие и клиентские документы из CRM.

- [ ] XLSX-экспорт/импорт.
- [ ] PDF-отчёты.
- [ ] DOCX документы.
- [ ] PPTX презентации.
- [ ] Периодические отчёты по продажам.
- [ ] Deal review.

Инструменты/skills: xlsx, pdf, docx, pptx, deal-review.

### Cycle 13 — White-label + Production Hardening
**Цель:** Twenty выглядит и эксплуатируется как CRM IT GROUP.

- [ ] Фирменное название/логотип/favicon.
- [ ] Фирменные цвета.
- [ ] Безопасный способ обновления кастомизаций.
- [ ] Backup/restore runbook.
- [ ] Health checks.
- [ ] Upgrade runbook.
- [ ] Проверка reverse proxy/HTTPS.
- [ ] Финальный production checklist.

## Подтверждённые группы MCP-возможностей

- People, Companies, Opportunities, Tasks, Notes;
- bulk create/update/delete и upsert;
- Task Targets, Note Targets, Attachments;
- Calendar Events/Participants;
- Messages/Threads, Campaigns, Lists, Blocklists;
- Call Recordings, Timeline Activities, Workspace Members;
- Object/Field Metadata;
- Views, View Fields, Filters, Sorts;
- Dashboards, Tabs, Widgets;
- Workflows, Steps, Edges, Runs, validation/activation;
- Logic Functions / TypeScript source;
- Webhooks;
- Roles, object permissions, row-level rules;
- Email send/draft;
- AI Agent configuration;
- navigation.

## Skills

- code-interpreter
- crm-hygiene
- dashboard-building
- data-manipulation
- deal-review
- enrich
- xlsx
- meeting-prep
- metadata-building
- pdf
- pptx
- roles
- view-building
- docx
- workflow-building
- workspace-demo-seeding

## Очередность

**Сейчас:** Cycle 1 → затем Cycle 2 → Cycle 3 → Cycle 4.  
Остальные циклы выполняются по мере готовности основного процесса продаж и реальной потребности бизнеса.
