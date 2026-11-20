# SC01.01 — 2D светящийся энергетический кристалл (первоначальный заказ, v1)

Работай через Fortis Repo в **новом независимом чате**. До чтения документации получи точное UTC T0. Прочитай `/workspace/repo/README.md`, `/workspace/repo/AGENTS.md`, `/workspace/repo/Repos/visual-workspace/README.md`, применимые UC-VIS, `WORKFLOW.md`, `docs/use-cases/media-github-review.md`, инструменты/QA и `practical-tests/TIMING.md`. Запиши T1–T5.

**Заказ:** Создай оригинальный шестиугольный игровой кристалл-предмет 64×64 с cyan-сердцевиной и тонкой янтарной окантовкой на прозрачном фоне, сохрани редактируемый SVG, экспорт и Godot 4.7 сцену с игровым размером ~64 px в 1280×720.

Полный обязательный brief: `practical-tests/authoring/A01-2d-static.md`. Не изменяй исторический brief, benchmark prompts, fixtures или чужие Workfiles. Отличие данного сценария от исторического C-теста: редактируемые исходники сохраняй и фиксируй собственными Git-коммитами в **новом зарегистрированном task worktree**, чтобы была проверенная история source SHA; QA, PNG, временные файлы и отчёты размещай в собственной уникальной `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<run-id>/`. Исключение касается только расположения исходников; художественные и функциональные требования original brief остаются обязательными.

Объяви параметры форматов, размеров, анимации/контроллера и QA по WORKFLOW. Реально получи и открой полноразмерные кадры Godot. Для движения проверь хронологию и границы клипов, для игры — последовательный ввод и коллизии; PNG не являются доказательством playback/gameplay.

**Прошу опубликовать первую проверенную версию в новом GitHub Issue публичного `visual-workspace`.** Это явное разрешение на тестовую публикацию только безопасных собственных PNG. Перед write проверь live `default_client().capabilities(refresh=True)`: exact repo/actor, `publish_visual_review` и `append_visual_revision` в `allowGitHub`, обе политики ALLOW. 1–5 PNG до 10 MiB; никакого прямого PAT/CLI/HTTP, видео, .blend или .glb upload.

Используй read-only `prepare_visual_review`, затем один `publish_visual_review` с сохранёнными runId/requestId и expected digest. Подтверди EXECUTED receipt и readback исходного Issue; сохрани issueNumber, original baseRunId, assetId, полный Git source SHA, локальные PNG SHA256, QA evidence и ссылки. При UNCERTAIN расследуй тот же requestId без слепого повтора.

Покажи мне ссылку на v1 и попроси отзыв. Это ещё не принятие и не source merge. Не выдумывай изменения за меня: дальнейшие требования придут отдельными сообщениями **в этот же чат**. При отсутствии отзыва статус `V1_OWNER_FEEDBACK_PENDING`, не создавай v2. Отчитайся о T0–T5, T3−T0, T5−T0, фактах и ограничениях. Не открывай `_evaluator/`.
