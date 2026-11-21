# visual-workspace

Публичный репозиторий визуальных проектов и результатов. Производство,
визуальное QA, интеграция в игру и публикация владельцу — связанные, но
отдельные этапы.

## Главные документы

- [WORKFLOW.md](WORKFLOW.md) — общий процесс создания, исправления и QA.
- [Реестр UC-VIS-001–009](docs/use-cases/README.md) — выбор сценария.
- [UC-VIS-009](docs/use-cases/media-github-review.md#uc-vis-009) — показ,
  версии, GitHub Issue и обратная связь владельца.
- [Backlog](docs/BACKLOG-IMPROVEMENTS.md) — актуальные пробелы и приоритеты.
- [Готовые handoffs](docs/handoffs/README.md) — два задания для отдельных
  чатов: активация revision API и последующая сквозная проверка.
- [Практические тесты UC-VIS-008](practical-tests/README.md) — готовые
  промпты для проверки новых чатов, включая [VR01 — versioned review](practical-tests/prompts-tool-safe/VR01-versioned-review-v1.md) и [матрицу независимых прогонов](practical-tests/CLEAN-CHAT-MATRIX-20261119.md).

## Модель версий

**Действующая модель:** один GitHub Issue на одну логическую единицу
обратной связи (ассет или согласованный заказ). В публичном репозитории
описания и PNG доступны всем: не публиковать секреты или частные материалы.
v1 создаёт Issue; v2, v3 и следующие ревизии добавляются новыми
комментариями с отдельными PNG, QA и source SHA в **тот же Issue**.
Независимые заказы получают отдельные Issue. Внутренние черновики не
публикуются. PR создаётся после принятия результата владельцем, а не
на каждый визуальный вариант.

**Проверенное live-состояние на 2026-11-19:**

- `publish_visual_review` и `append_visual_revision` объявлены в
  `allowGitHub` для `visual-workspace`, policy обоих методов — **ALLOW**.
  `appendRevisionPolicy=ALLOW`, source-gated same-Issue comments v2+.
  Другие GitHub-операции не наследуют этот scope. Capabilities проверять
  `c.capabilities(refresh=True)` **перед каждым write**.
- Публикация ограничена 1–5 PNG до 10 MiB на файл. Вторая версия
  публикуется с исходным `issueNumber`, `baseRunId`, `assetId`, следующим
  `revision`, **новыми** `runId`/`requestId`, полным source Git SHA и
  `expected_payload_sha256` локальной подготовки.
- **E2E подтверждён:** [Northlight Beacon v1 — Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5)
  сохранила body/PNG; [v2 — один комментарий](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589)
  с новой PNG, Git SHA и `EXECUTED` receipt. Владелец сообщил, что PNG
  отображается нормально. Это **ISSUE_REVIEWED**, не `SOURCE_MERGED`
  или `GAMEPLAY_ACCEPTED`.
- Потерянный ответ, `UNCERTAIN` или другой недоказанный эффект:
  **STOP, расследование того же requestId по UC-GW-009**, без второго
  UUID, повторного комментария или нового Issue как fallback.

Git/Docker остаются источником редактируемых исходников. Issue — витрина
и обсуждение; PNG-превью не является оригиналом `.blend`/`.glb` или видео.
Для игровой приёмки нужны принятый source PR, CI, owner merge, защищённый
Mirror Pull Windows `main` и реальный запуск Godot на Windows.

## Создание и проверка

Для новой задачи ИИ выбирает UC, создаёт исходники в собственном task
worktree, использует применимые инструменты и QA-модули, открывает реальные
PNG/кадры и сопоставляет результат с письменным brief. Не считать
контактный лист заменой полноразмерному просмотру или статичный preview
доказательством игрового поведения.

- [Asset Workbench](projects/asset-workbench/README.md) — минимальные 2D/3D сцены.
- [Blackjack Underworld UI mockups](projects/blackjack-underworld-mockups/README.md) — редактируемые UI-состояния, не готовая игра.
- [Animation Relay](projects/playable-animation-demo/README.md) — проверяемое управление и анимация в игре.
- [QA Registry](qa/INDEX.md) и [Tool index](tools/README.md) — доступные проверки и инструменты.

Blender/Godot и их библиотеки устанавливаются отдельно от Git, в
игнорируемой `.local-tools` на Docker primary. В task worktree использовать
`./tools/link-shared-tools.sh`; не коммитить бинарники среды. QA-кэш,
временные рендеры и Workfiles не являются автоматически сохранённой
Git-версией.

**Инструменты при практических тестах:** используются Visual Workspace, Fortis Repo, редактируемые SVG/Blender/Godot исходники и настоящие runtime PNG. **AI image generation / image_gen не заменяет исполнение задачи или QA**; ограничения продублированы в каждом актуальном сценарном сообщении и в шаблонах незапланированных исправлений. [Парные ссылки на этапы и независимую оценку](practical-tests/scenarios/README.md), [SV пары](practical-tests/review-scenarios/README.md), [contract результатов](practical-tests/UNIT-SUBMISSION-CONTRACT.md).

Новые [сценарии создания по референсу RS01–RS04](practical-tests/reference-scenarios/README.md) проверяют визуальную точность повторения, сохранение деталей при изменениях, композицию двух образцов и построение 3D по одному 2D-виду. Референсы CC0 закреплены в репозитории с SHA256; все RS тесты пока NOT RUN. [Гибкий каталог для выборочных прогонов](practical-tests/reference-scenarios/SCENARIO-CATALOG.md).

Практические тесты UC-VIS-008 имеют отдельные [сценарные последовательности SC01–SC05](practical-tests/scenarios/README.md): первоначальное задание и два последующих сообщения в одном чате, v1 Issue и v2/v3 комментарии, с оценкой по [новой матрице](practical-tests/SCENARIO-MATRIX-20261120.md).

[Оценка каждой отдельной единицы работы независимым чатом](practical-tests/_evaluator/unit-gates/README.md) позволяет остановить сценарий, добавить внеплановое исправление с отдельным ID и затем продолжить исходные этапы, сохраняя историю.

Для поиска недостатков в готовых 2D/3D-анимациях есть [сценарии SV01–SV03](practical-tests/review-scenarios/README.md): два основных связанных набора и один дополнительный; каждое последовательное сообщение одного сценария выполняется в том же новом чате, без GitHub-публикаций. [Матрица](practical-tests/REVIEW-SCENARIO-MATRIX-20261120.md).

Практические тесты UC-VIS-008 используют один готовый промпт на новый чат:
обычно 2–3 visual cases на один bootstrap, один production order на чат,
разные уровни сложности, независимая оценка и замер T0–T5. Все результаты
тестов хранятся в `/workspace/repo/Workfiles/`, не в репозитории. Тестовые
чаты не получают evaluator key и не публикуют fixture results в Issues.
