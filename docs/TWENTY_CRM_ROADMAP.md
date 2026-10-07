# Twenty CRM — Roadmap IT GROUP

> Цель: превратить self-hosted Twenty CRM в единую операционную систему продаж IT GROUP и последовательно реализовать возможности, подтверждённые через Twenty MCP.

## Текущее состояние

Реализовано:
- воронка продаж IT GROUP;
- Follow-up-контур и рабочие представления;
- Sales Dashboard;
- адаптация Company / Person / Opportunity под процесс IT GROUP;
- Lead Generation: единая модель Company → Person → Opportunity и расширенный справочник источников;
- источники: 2ГИС, сайт, Avito, Юла, Яндекс Директ, Яндекс Карты, Telegram, WhatsApp, рекомендации, холодный контакт, другое.

## Принципы реализации

1. Работать короткими циклами с измеримым Definition of Done.
2. Сначала штатные возможности Twenty и MCP; кастомный код — только когда штатного механизма недостаточно.
3. Не удалять production-данные и Docker volumes.
4. Автоматизации перед активацией валидировать и проверять реальным E2E-тестом.
5. Любые массовые изменения сначала проверять выборкой.
6. Каждая интеграция должна иметь наблюдаемость: понятную ошибку, лог или контрольное представление.

## Roadmap

### Cycle 1 — CRM Core + Follow-up ✅ COMPLETED 2026-10-07
**Цель:** ни один активный лид не должен теряться после первого контакта.

### Cycle 2 — Sales Dashboard ✅ COMPLETED 2026-10-07
**Цель:** руководитель видит состояние продаж на одном экране.

### Cycle 3 — CRM UX + Data Model ✅ COMPLETED 2026-10-07
**Цель:** карточки и структура Twenty соответствуют процессам IT GROUP.

### Cycle 4 — Lead Generation ✅ COMPLETED 2026-10-07
**Цель:** стандартизировать поступление и обработку холодных и входящих лидов.

- [x] 2ГИС / ручной импорт.
- [x] Сайт.
- [x] Avito.
- [x] Юла.
- [x] Яндекс Директ.
- [x] Яндекс Карты.
- [x] Telegram.
- [x] WhatsApp.
- [x] Рекомендации.
- [x] Холодный контакт.
- [x] Bulk create/upsert — утверждён паттерн для массовых загрузок.
- [x] Дедупликация: Company по домену/названию; Person по email, далее телефон/ручная проверка.
- [x] Единая модель Company → Person → Opportunity.
- [x] Новый Opportunity создаётся сразу с stage=NEW, contactStatus=NOT_CONTACTED и nextAction=«Связаться с новым лидом».
- [x] Представления для Юлы, Яндекс Директа и Яндекс Карт.
- [x] E2E-тест Company → Person → Opportunity.
- [x] Тестовые записи удалены.

**Техническое решение:** встроенный UPDATE_RECORD в DATABASE_EVENT workflow текущей сборки Twenty валидируется, но runtime возвращает `Object record ID and name are required`. Дефект воспроизведён на двух версиях workflow. Оба workflow деактивированы. Инициализация обязательных полей перенесена в точку создания Opportunity (MCP/API/import adapter), что прошло E2E-проверку.

### Cycle 5 — Tasks, Notes, Files, Timeline ✅ COMPLETED 2026-10-07
**Цель:** история взаимодействия хранится внутри CRM.

- [x] Tasks связаны с Opportunity / Company / Person через Task Targets.
- [x] Notes связаны с Opportunity / Company / Person через Note Targets.
- [x] Принят шаблон задачи: «Цель → Результат».
- [x] Принят шаблон заметки: «Контекст → Потребность → Договорённости → Следующий контакт».
- [x] Attachment-модель проверена: файл может быть связан с Opportunity, Company, Person, Task или Note.
- [x] Проверен Timeline: создание CRM-записей, задач, заметок и target-связей автоматически отражается в Timeline.
- [x] Проведён E2E-тест и тестовые записи удалены.

**Примечание по файлам:** реальный Attachment подтверждён после загрузки пользователем: файл связан с Opportunity и отражается в Timeline.

### Cycle 6 — Communications ✅ COMPLETED 2026-10-07
**Цель:** коммуникации становятся частью CRM-процесса.

- [x] Рабочий email `info@itgsystem.ru` подключён через IMAP/SMTP/CalDAV.
- [x] Messages / Threads синхронизируются: подтверждены реальные сообщения и треды.
- [x] Participants синхронизируются; адрес `info@itgsystem.ru` подтверждён как отправитель.
- [x] Безопасный тест черновика выполнен через подключённый аккаунт; внешняя отправка не выполнялась.
- [x] Calendar синхронизируется: в CRM присутствуют реальные календарные события.
- [x] Calendar participants проверены; на момент проверки записей участников нет.
- [x] Call Recordings проверены; на момент проверки записей нет.
- [x] Campaigns / Lists проверены; на момент проверки записей нет.

**E2E:** подключённый аккаунт `info@itgsystem.ru` обнаружен Twenty как `imap_smtp_caldav`; подтверждены реальные Message → Thread → Participants и Calendar Events. Создан тестовый черновик `[TEST] Twenty CRM — Cycle 6 Communications` самому себе без отправки. Отдельная автоматизация `IT GROUP — Напоминание о Follow-up` оставлена в DRAFT: её SEND_EMAIL-шаг не активирован, чтобы исключить автоматическую внешнюю отправку без явного утверждения получателей и текста.

### Cycle 7 — Integrations + Webhooks ⏳ IN PROGRESS 2026-10-07
**Цель:** связать Twenty с инфраструктурой IT GROUP.

- [x] Website → Twenty: MODX `ITG_LeadHandler` создаёт записи через Twenty REST API. Исправлена область видимости API-настроек в snippet; контрольная заявка через `lead-submit.html` вернула HTTP 200, создала Person + Opportunity + Task и дала два события в n8n. Тестовые записи мягко удалены. Отдельный `IT GROUP — Website Lead → CRM` также ACTIVE, но сайт его сейчас не вызывает.
- [x] n8n на ZimaOS: существующий CasaOS Compose, контейнер работает; отдельный persistent mount `/DATA/AppData/n8n`.
- [x] Twenty → n8n: подписка `opportunity.created/updated` доставляет события через существующий HTTPS-прокси `n8n.karpiev.ru`; создание и обновление тестовой сделки дали успешные n8n executions 21 и 22.
- [x] n8n → Twenty: ручной workflow `IT GROUP — Twenty API connectivity check` выполнил успешный authenticated GET к Twenty REST metadata API через зашифрованный n8n credential. Автоматическую запись в CRM не включали, чтобы не создавать дубли при retry.
- [ ] Telegram: credential бота есть в n8n, подтверждённого Chat ID для уведомлений нет; узел отправки выключен.
- [x] HTTP health check: активный `IT GROUP — Integration Health Check` проверяет `https://itgsystem.ru/`.
- [ ] Сквозной E2E Website → Twenty → n8n → Telegram и обработка ошибок/retry.

Контракт, текущее состояние, тесты и порядок восстановления: [CYCLE7_INTEGRATIONS_RUNBOOK.md](CYCLE7_INTEGRATIONS_RUNBOOK.md). Issue #8 остаётся открытым до полного DoD.

### Cycle 8 — Workflow Automation
**Цель:** автоматизировать повторяющиеся операции продаж.

- [ ] DATABASE_EVENT / CRON / MANUAL / WEBHOOK workflows.
- [ ] Branching / conditions / iterators.
- [ ] Workflow run monitoring.
- [ ] Error diagnostics.
- [ ] Version validation/activation.

### Cycle 9 — AI CRM
**Цель:** AI помогает продавать, а не заменяет контроль процесса.

- [ ] AI-квалификация лида.
- [ ] Резюме истории клиента.
- [ ] Следующее лучшее действие.
- [ ] Черновик follow-up и КП.
- [ ] Анализ причин отказа.
- [ ] Приоритизация сделок.

### Cycle 10 — Security + Roles
**Цель:** подготовить CRM к работе команды.

- [ ] Admin / Sales / Manager / Read-only.
- [ ] Object permissions.
- [ ] Row-level permissions при доступности.
- [ ] Проверка API/MCP access.

### Cycle 11 — Data Quality + Operations
**Цель:** CRM остаётся чистой по мере роста.

- [ ] Поиск дублей.
- [ ] Нормализация телефонов/email.
- [ ] Контроль пустых критичных полей.
- [ ] Bulk correction/import.
- [ ] Регулярный CRM hygiene review.

### Cycle 12 — Reporting + Documents
**Цель:** получать управленческие и клиентские документы из CRM.

- [ ] XLSX.
- [ ] PDF.
- [ ] DOCX.
- [ ] PPTX.
- [ ] Периодические отчёты / Deal review.

### Cycle 13 — White-label + Production Hardening
**Цель:** Twenty выглядит и эксплуатируется как CRM IT GROUP.

- [ ] Фирменный стиль.
- [ ] Backup/restore runbook.
- [ ] Health checks.
- [ ] Upgrade runbook.
- [ ] Reverse proxy/HTTPS.
- [ ] Финальный production checklist.

## Подтверждённые группы MCP-возможностей

People, Companies, Opportunities, Tasks, Notes; bulk CRUD/upsert; Task/Note Targets; Attachments; Calendar; Messages; Campaigns; Lists; Blocklists; Call Recordings; Timeline; metadata; Views; Dashboards; Workflows; Logic Functions; Webhooks; Roles/permissions; Email; AI Agent; navigation.

## Следующий цикл

**Cycle 7 — Integrations + Webhooks.**
