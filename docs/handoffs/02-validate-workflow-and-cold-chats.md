# Handoff 02 — проверить versioned review, обновить UC и испытать чистые чаты

**Для второго отдельного чистого чата.** Этот handoff запускается только
после завершения Handoff 01 и owner-managed activation нового метода.

## ОБЯЗАТЕЛЬНОЕ ПРЕДУСЛОВИЕ — проверь в самом начале

На момент получения этого задания новый метод **уже должен существовать
в работающем Gateway**, а не только в source checkout.

До любых изменений, создания Issue или тестовых публикаций:

1. Прочитай live capabilities:
   `c = default_client()`
   `caps = c.capabilities(refresh=True)`.
2. Убедись, что `append_visual_revision` присутствует в
   `caps['askGitHub']` для текущего actor и repository
   `visual-workspace`.
3. Убедись, что доступны оба typed метода:
   `c.github.prepare_visual_revision` и
   `c.github.append_visual_revision`.
4. Проверь, что policy именно ASK для revision write, а не ALLOW/DENY,
   и что live Gateway/image identity соответствует релизу из Handoff 01.

**Если хотя бы одно условие не выполнено — STOP.** Ничего не публикуй,
не создавай новый Issue, не используй новый Issue как fallback и не
объявляй задачу начатой. Верни точные capabilities/блокер владельцу.
Отсутствие метода в live нельзя компенсировать импортом source-кода.

## Цель

Доказать на практике весь workflow Visual Workspace:
создание/проверка 2D и 3D ассетов/анимаций → QA по письменному brief →
показ v1 → owner feedback → исправление исходника → v2 комментарием
в **том же Issue** → сохранение v1/v2 и provenance → owner acceptance →
один Source PR только после согласования. Затем актуализировать use cases,
backlog и тестовый комплект, после чего подготовить и провести проверки
с действительно чистыми чатами.
## Bootstrap и исходное состояние

1. Начни с `/workspace/repo/README.md`.
2. В `/workspace/repo/Repos/visual-workspace` прочитай
   `README.md`, `AGENTS.md`, `WORKFLOW.md`,
   `docs/use-cases/README.md`, `docs/use-cases/media-github-review.md`,
   `docs/BACKLOG-IMPROVEMENTS.md`, `practical-tests/README.md`,
   `practical-tests/TIMING.md`, `qa/INDEX.md`, `qa/STATUS.md`,
   `tools/README.md`.
3. В Fortis Approvals прочитай актуальные UC-GW-003/005/009 и раздел
   Append Visual Revision; перечитай live capabilities ещё раз перед write.
4. Проверь актуальные GitHub Issue/PR и локальный Git state через Gateway.
   Не доверяй snapshot из handoff, если live данные изменились.
5. Работай в отдельном task worktree от чистого актуального
   `visual-workspace/main`. Не меняй старые worktrees и legacy tree.
   Все test run outputs — только в Workfiles, не в `projects/` и не в repo.

Состояние на дату подготовки этого handoff: Issue #5 — Northlight Beacon v1 —
открыт, содержит одну PNG reference и ноль комментариев. Его run marker
`northlight-beacon-e2e-v3-20261117` — publication run ID, не версия artwork.
Используй #5 для v2 только если live Gateway доказывает durable original
reservation/baseRunId. Если не доказывает — не обходи precondition:
согласуй/создай отдельный test v1 Issue штатным publisher, затем продолжай.

## Этап A — проверить revision API без публикации

1. Проверь contract/typed signature и exact current live policy.
2. Подготовь PNG и вызови `prepare_visual_revision(...)`; проверь
   `payloadSha256`, список media, размеры и SHA-256. Это локальный
   read-only preview, не GitHub write.
3. Убедись, что повторная подготовка не создаёт stage, ASK или comment.
4. Проверь негативные входы без upstream side effects: wrong repository,
   wrong issue, wrong baseRunId, asset mismatch, revision gap/duplicate,
   invalid source SHA, repeated runId, >5 PNG, invalid/oversize PNG.
5. Подтверди, что revision write требует отдельный ASK и не наследует
   v1 publish ALLOW. Не симулируй owner WebAuthn и не подменяй его.

## Этап B — настоящий v1 → v2 E2E в одном Issue

Публикация — реальный GitHub side effect. Выполняй только в рамках
порученного владельцем теста и через Fortis typed client/Gateway.

1. Выбери один небольшой, понятный 2D-ассет или animation preview.
   Зафиксируй brief, assetId/orderId, source commit SHA, QA summary,
   v1 runId и исходные PNG. Не делай тест на случайном fixture с раскрытым
   evaluator key.
2. Если пригодного v1 Issue нет, создай его через
   `publish_visual_review` после проверки live policy и owner approval,
   если она требуется. Сохрани requestId, receipt, Issue number, baseRunId,
   run marker и attachment references. Прочитай Issue обратно.
3. Получи конкретное замечание владельца. Не придумывай owner feedback.
   Если пользователь ещё не дал замечание, покажи v1 и дождись его.
4. Измени исходник в Docker/Git, создай v2, пройди релевантный QA и
   зафиксируй точный full source SHA. Сохрани v1 как отдельный артефакт;
   не редактируй PNG из Issue.
5. Подготовь v2 через `prepare_visual_revision`, затем один раз вызови
   `append_visual_revision` с новым immutable requestId, новым runId,
   тем же Issue number/baseRunId/assetId, revision=2 и preview hash.
6. Если ответ PENDING — ждать owner decision в Owner Portal. Не повторять
   call, не менять UUID, не отправлять второй request. После approval
   дождаться EXECUTED и прочитать receipt.
7. Через Gateway READ проверь:
   - номер Issue у v2 тот же, что у v1;
   - Issue body и v1 PNG reference не изменились;
   - появился ровно один новый v2 comment с ожидаемым revision marker;
   - comment содержит правильные assetId/baseRunId/runId/revision/sourceSha;
   - attachment reference соответствует ожидаемому PNG;
   - не был создан второй Issue для v2;
   - receipt связан с тем же requestId/commentId.
8. Владелец должен открыть опубликованное PNG в браузере. Markdown URL
   в readback сам по себе не доказывает, что байты доступны/верны.
9. Только после полностью подтверждённой v2 можно рассмотреть v3, чтобы
   проверить последовательную привязку к предыдущему comment. v3 не
   обязательна, если v2 уже выявила дефект в методе.
10. Потерянный POST response / UNCERTAIN: только UC-GW-009 investigation
    того же UUID и durable evidence. Никакого blind replay или v3 поверх
    unresolved v2.

## Этап C — обновить Visual Workspace документы

После фактической проверки обнови документы по доказанному состоянию:

- `README.md`: current live capabilities и краткая модель версий.
- `WORKFLOW.md`: когда и как показывать владельцу, что делать до/после v1.
- `docs/use-cases/media-github-review.md` (UC-VIS-009): точный typed flow,
  ASK/ALLOW scope, receipt/readback, revision comments, source provenance,
  retention и реальные ограничения.
- `docs/use-cases/README.md`: корректные ссылки и границы UC-VIS-001–009.
- `docs/BACKLOG-IMPROVEMENTS.md`: закрыть только реально принятые задачи;
  не удалять оставшиеся video/3D/retention/gameplay gaps.
- `practical-tests/README.md` и prompts: добавить новый immutable
  ready-to-copy prompt для versioned GitHub review, если такой проверки ещё
  нет. Не переписывать исторические V01–V09/C01–C06.
- `docs/handoffs/README.md`: обновить статусы обоих handoffs и ссылки.

Не заявляй central latest-pointer/status automation, video/GLB uploads,
source archive или gameplay acceptance, если они не реализованы и не
проверены. Один Issue на логический заказ; независимые заказы — отдельные
Issues. Не создавать PR на каждую визуальную ревизию: Source PR только
после явного owner acceptance.

## Этап D — clean-chat testing

Сначала зафиксируй матрицу тестов и неизменяемые prompt IDs/версии.
Новый чат должен начинать с принятого Visual Workspace README и bootstrap
из него, а не с текущей беседы или task worktree.

Минимальная матрица:

1. **V08 — visual review mixed pair:** один чистый чат, один 2D + один 3D
   кейс, независимые вердикты, полноразмерные PNG и временная локализация.
2. **C03 — 2D animation:** отдельный чистый чат, один production order,
   editable source, Godot preview, frame/timing QA.
3. **C04 — 3D animation:** отдельный чистый чат, один production order,
   editable 3D source, export/import, views and animation QA.
4. **C05 — playable composite:** отдельный чистый чат, один сложный заказ:
   ассет → анимация → простая игровая интеграция → последовательный input test.
5. **Versioned review prompt (новый):** отдельный чистый чат, один небольшой
   заказ и настоящий v1→owner feedback→v2 same-Issue цикл. Это главный тест
   нового метода и UC-VIS-009.
6. **C06 / UC-VIS-007:** опционально проверить несколько независимых заказов
   и worktree/output isolation; не делать обычным default production test.

Не запускай несколько production orders в одном prompt, кроме специального
C06. Визуальный batch из нескольких cases допустим, но случаи одного чата
статистически коррелированы. Для оценки независимости используй отдельные
новые чаты. Не раскрывай evaluator key и ожидаемые дефекты тестируемому чату.

### Правила замера и оценки

Для каждого чистого чата зафиксируй prompt ID/version, model/config если
известны, workspace HEAD и dirty state, input case/order IDs, реальные
просмотренные PNG/frame IDs, QA/runtime результаты, ссылки на Issue/PR,
итог и Workfiles path. Сохрани `timing.md` с UTC T0–T5 по
`practical-tests/TIMING.md`: bootstrap, brief/plan, first real preview,
review/implementation, final verification/report. Отдельно измерь время
по каждому visual case; для authoring — time-to-first-preview и full completion.
Tool timings не выдавай за user UI latency.

Для каждого прогона используй отдельную папку
`/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<run-id>/`.
Не помещай test outputs в repo. Оценщик проверяет результат после сдачи:
визуальные пропуски/false positives, точность локализации, brief acceptance,
editable source, Godot import, actual gameplay, version identity and Issue history.

Чистые чаты нельзя создать автоматически из текущего диалога. Подготовь
готовые промпты для копирования владельцем в новые чаты; если реальные
независимые прогоны ещё не выполнены, явно обозначь их как NOT RUN, а не PASS.

## Критерии завершения

- Live append capability и ASK policy доказаны до начала.
- Настоящий v2 comment создан в том же Issue, receipt и readback совпадают,
  v1 осталась нетронутой, владелец проверил PNG в браузере.
- Документы и backlog отражают только проверенные факты.
- Подготовлен immutable prompt для versioned-review и список clean-chat runs.
- Все результаты/тайминги/ограничения сохранены в Workfiles.
- PR на документацию/промпты проходит проверки и owner merge через Gateway.

В финальном отчёте отдельно перечисли: что проверено live, что только
offline/source, какие clean chats реально завершены, их времена и вердикты,
какие ещё не запускались, и следующий конкретный шаг.
