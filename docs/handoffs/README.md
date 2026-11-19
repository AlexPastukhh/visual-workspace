# Handoffs — versioned GitHub visual review

Два независимых задания для передачи в **два отдельных чистых чата**.
Выполнять строго по порядку: Handoff 02 зависит от live результата Handoff 01.

## Порядок

1. [Handoff 01 — активировать append visual revision](01-activate-append-visual-revision.md)
   - Репозиторий: fortis-approvals.
   - Задача: аудитировать существующий source candidate, закрыть недостающую
     интеграцию, провести CI/PR и owner-managed Gateway release.
   - Результат: live capabilities объявляют append_visual_revision
     в allowGitHub для visual-workspace, policy ALLOW.
2. [Handoff 02 — E2E, обновление UC и clean-chat tests](02-validate-workflow-and-cold-chats.md)
   - Репозиторий: visual-workspace (и read-only audit Fortis Approvals).
   - Precondition исполнен: метод доступен в live Gateway, policy **ALLOW**
     (поправка владельца к историческому тексту Handoff 02).
   - E2E исполнен: v1→настоящий owner feedback→v2 в [Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589),
     владелец подтвердил отображение. Source PR/документы оформляются
     отдельно; независимые clean chats **NOT RUN**.

## Правила передачи

- Каждый handoff отправлять целиком из соответствующего Markdown-файла
  как обычный пользовательский prompt.
- Не склеивать оба handoff в один чат: второй должен быть независимым
  и стартовать только после реального live activation первого.
- Source code / merged PR / green CI не равны live activation. Проверять
  capabilities работающего Gateway.
- Не выполнять GitHub writes из браузерного UI, PAT, GitHub CLI или прямого REST.
  Все действия — через Fortis typed client/Gateway и owner policy.
- Не повторять неизвестный write outcome новым UUID. Для UNCERTAIN
  использовать UC-GW-009.
- Визуальные test runs и отчёты хранить в Workfiles; не засорять repo.
- Не заявлять clean-chat PASS, пока новый чат реально не выполнен и
  его артефакты независимо не оценены.

## Историческая исходная точка при подготовке — 2026-11-17

- Visual Workspace main: b2163de421fc351a132b3f3970ca935dedaf2f64.
- Fortis Approvals main source snapshot: bdb3ec581db7157b05f5d6c5282c7d3a7b6d0a35.
- Existing candidate methods and offline revision tests exist in source.
- Live Gateway does not advertise append_visual_revision.
- Existing v1 Issue: [#5 — Northlight Beacon](https://github.com/AlexPastukhh/visual-workspace/issues/5).

Эти значения — ориентир для bootstrap, не замена повторному чтению live
состояния в начале каждого handoff.


## Проверенный результат — 2026-11-19

- Handoff 01: owner-managed Gateway image update прошёл; scoped
  `appendRevisionPolicy=ALLOW`, не ASK. Публичный GitHub repository допускается.
- Handoff 02, E2E: [один v2-комментарий в исходном Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589),
  исходная v1 сохранена, PNG проверена владельцем, source v2
  `06b0c9fe3ae9ae1ce7effe83e128045c711701b3`.
- Новые документы/промпты/PR — следующий source этап, не часть
  Gateway image release. Для independent cold acceptance см.
  [VR01 v1](../../practical-tests/prompts/VR01-versioned-review-v1.md)
  и [матрицу](../../practical-tests/CLEAN-CHAT-MATRIX-20261119.md).
  Все fresh-chat запуски остаются NOT RUN.
