# RS01.01 — Точное визуальное повторение 2D-иконки

Работай через Fortis Repo в НОВОМ независимом чате с Visual Workspace. Перед чтением README зафиксируй реальное UTC T0, затем прочитай /workspace/repo/README.md, /workspace/repo/AGENTS.md, accepted visual-workspace/README.md, WORKFLOW.md, применимые UC-VIS-001–005/008/009, QA и practical-tests/TIMING.md. Создай отдельный зарегистрированный task worktree для новых редактируемых исходников и Git source SHA; все screenshots/QA/timing/reports одного сценария складывай в одну новую уникальную Workfiles папку /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/.

**Это тест СОЗДАНИЯ ПО РЕФЕРЕНСУ.** Смотри только зафиксированные PNG в practical-tests/reference-scenarios/references/; исходный SVG/AI/3D объект автора не скачивай, не импортируй и не трассируй автоматически как свой результат. Не считай вставку reference PNG в Godot самостоятельным созданием. Используй реальные собственные SVG/Blender/Godot source/edit/export и проверь реальные полноразмерные Godot/Blender кадры. Запрещены image_gen и любые AI image-generation инструменты вместо собственной работы или QA. Если это недоступно — BLOCKED, а не синтетическая подмена. Сверяй референс и экспорт side-by-side при одинаковом размере; качество нельзя доказывать только сводной метрикой.

**Даю явное разрешение опубликовать только собственные QA-проверенные PNG в НОВОМ GitHub Issue visual-workspace** через typed Gateway UC-VIS-009 после live capabilities/ALLOW и подготовки неизменного payload digest. Запиши actual requestId, Issue, baseRunId, assetId, полные source SHA, PNG SHA, receipt/readback. Не публикуй оригинальные CC0-референсы под видом созданных ассетов; не пользуйся прямым PAT/HTTP, не повторяй UNCERTAIN и не создавай fallback issue. Публикация — ещё не принятие.

**Заданные PNG-референсы:**
- practical-tests/reference-scenarios/references/bomb-circle-reference.png

**Заказ:** Создай своими силами векторную иконку бомбы по указанному PNG 256×256 с максимально близким видом: крупный почти чёрный округлый корпус, тёмная горловина, короткий наклонённый коричневый фитиль с витками и два белых блика справа, как на референсе. Повтори пропорции, светотень, расположение и прозрачность. Сохрани новый редактируемый SVG, экспорт PNG 256×256 и Godot 4.7 сцену, проверь в игре при 64px и при оригинальном 256px. Не вставляй исходный PNG в сцену вместо созданной собственной графики.

**Воспроизводимость:** вычисли и запиши SHA256 каждого реально показанного pinned reference PNG из accepted main и сверь с references/PROVENANCE.md; укажи accepted main HEAD. Сохрани независимый собственный исходник, а не содержимое исходной картинки.

**После исполнения:** сохрани фактический указатель доказательств по контракту practical-tests/UNIT-SUBMISSION-CONTRACT.md: /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/RS01.01/submission.md. Укажи actual runId, source full Git SHA, источник и результат, paths PNG/QA, Issue/revision/comment (или N/A), timings/receipts и ограничения. Не читай _evaluator/ или соседний evaluate-файл, не изменяй исторические SC/SV/C/V.
