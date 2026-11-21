# Visual Workspace — test Actions, V1

Это **локальный каталог из 7 тестовых Actions**. Он использует словарь Action System, но не изменяет Action Core, не регистрирует Actions в Core автоматически и не запускает управляемые AI workflows. Нормативные принципы тестов и сложности — [UC-VIS-008](../../docs/use-cases/README.md#uc-vis-008); здесь только исполняемые варианты, навигация и проверка целостности. Текущее состояние конкретных прогонов и оценки — **в Workfiles**, не в этом каталоге.

| Action | Проверяемая способность | Вариант V1 | Вход | Условная сложность | Этапы |
| --- | --- | --- | --- | --- | --- |
| [VT01](VT01/visual-testing.yaml) | Создать 2D по описанию | `crystal-text-l1` | [A01](../authoring/A01-2d-static.md), кристалл | `L1 / visual_detail` | [Создать](VT01/prompts/create.md) |
| [VT02](VT02/visual-testing.yaml) | Создать 3D по описанию | `sci-fi-crate-text-l2` | [A02](../authoring/A02-3d-static.md), контейнер | `L2 / visual_detail` | [Создать](VT02/prompts/create.md) |
| [VT07](VT07/visual-testing.yaml) | Воссоздать 2D по одному PNG | `bomb-circle-l1` | CC0 бомба из [PR #16](https://github.com/AlexPastukhh/visual-workspace/pull/16) | `L1 / visual_detail` | [Воспроизвести](VT07/prompts/reproduce.md) |
| [VT08](VT08/visual-testing.yaml) | Воссоздать и локально изменить | `top-down-crate-l2` | CC0 ящик сверху из [PR #16](https://github.com/AlexPastukhh/visual-workspace/pull/16) | `L2 / visual_detail` | [Воспроизвести](VT08/prompts/01-reproduce.md) → [Изменить](VT08/prompts/02-edit.md) |
| [VT11](VT11/visual-testing.yaml) | Слепой анализ готовых 2D клипов | `existing-turnaround-pair` | `clip-k7`, `clip-m4` | `unrated / defect_detectability` | [SV01](../review-scenarios/README.md) |
| [VT12](VT12/visual-testing.yaml) | Слепой анализ готовых 3D клипов | `existing-jumps-and-walk` | `clip-r2`, `clip-t9`, `clip-w8` | `unrated / defect_detectability` | [SV02](../review-scenarios/README.md) |
| [VT15](VT15/visual-testing.yaml) | Независимо оценить один unit | `single-unit` | Задание, реальный run и QA | `not_applicable` | [Оценить](VT15/prompts/evaluate-unit.md) |

**Сложность относится к варианту, не к Action в целом.** Для создания L1–L3 отражают визуальную детализацию; для поиска дефектов — трудность обнаружения. Существующие пять клипов **пока не калиброваны**; не определять уровень по секретному ответу, названию кейса или количеству кадров. Нет нужды добавлять новые искусственно дефектные материалы. Другие сложные Actions (создание анимации/мини-игры, совмещение референсов, 2D→3D, проверка нескольких заказов) остаются в историческом наборе, не в V1.

## Состав и связь с Action Core

- Каждый `VTxx/action.yaml` использует только допустимые в действующем Action Core ключи `name`, `category`, `instruction`. Категория `visual_testing`. **Нет** `workflow` и `schedule`: ручные сообщения ChatGPT нельзя выдавать за programmatic workflow.
- В соседнем `visual-testing.yaml` лежат версия схемы, стабильный `action_id`, `capability`, `kind`, `difficulty_basis`, конкретные `variants`, rationale, исходные briefs и закреплённые PNG с SHA256, этапы `unit_id` / `work_prompt` / `evaluation_prompt`, указатели на старые определения. Эти поля пока **не** подаются в Core валидатор как верхнеуровневые поля.
- При будущем подключении `ActionVersion` соответствует версии определения в Git, а не заменяет версии выходных PNG. Один `ActionRun` логически соответствует одной попытке в новом чате и одному `runId`; два этапа VT08, SV01 или SV02 в том же чате — связанные units внутри этого run, не два независимых холодных прогона. Реальной регистрации ActionVersion или ActionRun в Core здесь **ещё нет**.
- Исторические C/SC/SV/RS и их файлы не мигрируются задним числом. Для VT11/VT12 переиспользуются **неизменённые** SV01/SV02 work/evaluate prompts и существующий закрытый ключ. ID `SVxx.yy` оставлены у исторических units; новые unit IDs `VTxx.*` относятся только к новым промптам.

## Выбрать и выполнить

1. Выбери один variant прямо в `visual-testing.yaml` либо по [коллекциям](collections/) (`smoke-v1`, `reference-quality-v1`, `visual-review-existing-v1`). Collection — только **выборка**, не отдельный Action и не автоматический пакетный запуск.
2. Перед запуском проверь, что **каждый вход уже в принятом `visual-workspace/main`**. Для VT07/VT08 нужны два соответствующих PNG из четырёх, подготовленных в [PR #16](https://github.com/AlexPastukhh/visual-workspace/pull/16); эти варианты **BLOCKED до принятия/проверки точных файлов**. Если по состоянию Git ветка ещё не слита, запускать по открытой PR-ветке или веб-копии вместо main нельзя. Содержимое PNG не копируется в каталог Actions.
3. Открой новый независимый чат с Fortis Repo и передай **полный текст только нужного `work_prompt`**. Следующий `step` отправляется **отдельным сообщением в тот же исходный чат**, только после завершения и независимой оценки предыдущего. Не посылай оба этапа заранее.
4. Исполнитель создаёт **одну новую** `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/` на весь run, измеряет настоящие T0–T5 (и этапные S-метки), сохраняет свои source/export/PNG/QA и `reports/units/<unitId>/submission.md` по [контракту](../UNIT-SUBMISSION-CONTRACT.md). Новые V1 authoring/reference тесты **не публикуют в GitHub** и не изменяют принятый repo. Для устаревших C-промптов нет ретроактивного handoff.
5. Передай **точные** `actionId`, `variantId`, `runId`, `unitId` в **новый** чат-оценщик. Для VT01/VT02/VT07/VT08 используй общий [VT15 evaluator](VT15/prompts/evaluate-unit.md). Для VT11/VT12 используй **собственный** соседний SV evaluate-промпт каждого этапа, чтобы не раскрыть скрытый ключ до окончания всей последовательности. Оценщик сохраняет `evaluations/<runId>/<unitId>/decision.md` и не изменяет runner outputs.
6. Сохраняй первый результат, оценку и каждое отдельное исправление, даже если дальнейшая попытка лучше. При `BLOCKED`/`INCONCLUSIVE` не подменяй отсутствующие evidence выдуманными. Сравнивай повторные запуски только с учётом exact accepted Git HEAD, variant/fixture SHA, prompt revision, доступных инструментов и реально измеренного времени.

**Разделение обязанностей:** этот каталог — определения; [TIMING](../TIMING.md) — замеры; [UNIT-SUBMISSION-CONTRACT](../UNIT-SUBMISSION-CONTRACT.md) и [unit-gates](../_evaluator/unit-gates/README.md) — handoff и независимая проверка; [UC-VIS-009](../../docs/use-cases/media-github-review.md#uc-vis-009) — отдельный добровольно разрешаемый owner-review с GitHub Issue. Здесь его нет.

## Проверка каталога

Схема V1 проверяется локально без исполнения Actions. Используй Python 3 с `PyYAML>=6.0.2,<7` (совпадает с зависимостью действующего Core):

```bash
python3 practical-tests/actions/verify_catalog.py
python3 practical-tests/verify_fixtures.py
```

Пока PR #16 не в `main`, первая команда **преднамеренно остановится** из-за отсутствующих PNG. Для структурного review до слияния можно проверить точные файлы из зарегистрированного worktree PR #16, но это **не** означает готовность к запуску:

```bash
python3 practical-tests/actions/verify_catalog.py --candidate-reference-root \
  /workspace/repo/Worktrees/visual-workspace/reference-scenarios-pilot-20261121
```

В этом режиме вывод содержит `CANDIDATE_REFERENCE_ONLY` и `candidate=True`. После merge PR #16 следует повторить проверку **без** `--candidate-reference-root` и подтвердить `REFERENCE_INPUTS_ACCEPTED_IN_CURRENT_TREE`. Отдельно сопоставь семантику `action.yaml` с текущим `validate_action_document` в Action Core; local checker консервативно ограничивает Core-совместимые поля, но не делает сетевых вызовов и не заменяет реальный Core.

**Состояние V1:** YAML, промпты и контрольная структура подготовлены; фактические ActionRun/оценки **не выполнялись**. Ready ≠ run PASS.
