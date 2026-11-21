# RS02.01 — 2D-ящик: локальное изменение с сохранением формы

Работай через Fortis Repo в НОВОМ независимом чате с Visual Workspace. Перед чтением README зафиксируй реальное UTC T0, затем прочитай /workspace/repo/README.md, /workspace/repo/AGENTS.md, accepted visual-workspace/README.md, WORKFLOW.md, применимые UC-VIS-001–005/008/009, QA и practical-tests/TIMING.md. Создай отдельный зарегистрированный task worktree для новых редактируемых исходников и Git source SHA; все screenshots/QA/timing/reports одного сценария складывай в одну новую уникальную Workfiles папку /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/.

**Это тест СОЗДАНИЯ ПО РЕФЕРЕНСУ.** Смотри только зафиксированные PNG в practical-tests/reference-scenarios/references/; исходный SVG/AI/3D объект автора не скачивай, не импортируй и не трассируй автоматически как свой результат. Не считай вставку reference PNG в Godot самостоятельным созданием. Используй реальные собственные SVG/Blender/Godot source/edit/export и проверь реальные полноразмерные Godot/Blender кадры. Запрещены image_gen и любые AI image-generation инструменты вместо собственной работы или QA. Если это недоступно — BLOCKED, а не синтетическая подмена. Сверяй референс и экспорт side-by-side при одинаковом размере; качество нельзя доказывать только сводной метрикой.

**Даю явное разрешение опубликовать только собственные QA-проверенные PNG в НОВОМ GitHub Issue visual-workspace** через typed Gateway UC-VIS-009 после live capabilities/ALLOW и подготовки неизменного payload digest. Запиши actual requestId, Issue, baseRunId, assetId, полные source SHA, PNG SHA, receipt/readback. Не публикуй оригинальные CC0-референсы под видом созданных ассетов; не пользуйся прямым PAT/HTTP, не повторяй UNCERTAIN и не создавай fallback issue. Публикация — ещё не принятие.

**Заданные PNG-референсы:**
- practical-tests/reference-scenarios/references/cartoon_wooden_crate-reference.png

**Заказ:** Воссоздай как самостоятельный редактируемый SVG плоский квадратный деревянный ящик, вид строго сверху, по референсу PNG 256×256: широкая квадратная наружная рамка, Х-образные диагональные перекладины поверх горизонтальных досок, коричнево-золотые тона и тонкие линии. Не превращай его в 3D-куб. Экспортируй прозрачный PNG 256×256, сделай сцену Godot 4.7 и полноразмерный side-by-side QA с визуальной проверкой при игровом размере.

**Воспроизводимость:** вычисли и запиши SHA256 каждого реально показанного pinned reference PNG из accepted main и сверь с references/PROVENANCE.md; укажи accepted main HEAD. Сохрани независимый собственный исходник, а не содержимое исходной картинки.

**После исполнения:** сохрани фактический указатель доказательств по контракту practical-tests/UNIT-SUBMISSION-CONTRACT.md: /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/RS02.01/submission.md. Укажи actual runId, source full Git SHA, источник и результат, paths PNG/QA, Issue/revision/comment (или N/A), timings/receipts и ограничения. Не читай _evaluator/ или соседний evaluate-файл, не изменяй исторические SC/SV/C/V.
