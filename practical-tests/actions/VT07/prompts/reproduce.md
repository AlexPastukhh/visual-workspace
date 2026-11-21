# VT07.bomb.01 — воспроизвести 2D-иконку по PNG (L1)

НОВЫЙ независимый чат с Fortis Repo. Используй только реальные Visual Workspace SVG/экспорт/Godot. **Нельзя использовать image_gen, text-to-image, AI-генерацию изображений, вставлять исходный PNG как свой результат, трассировать его автоматически либо импортировать готовый upstream SVG.** Создай собственный редактируемый SVG и настоящий Godot-просмотр. Репозиторий и исходный референс только для чтения; GitHub Issue/PR не создавать.

До чтения README получи фактическое UTC T0. Выполни bootstrap, UC-VIS-001/004/008, `WORKFLOW.md`, `practical-tests/TIMING.md`; измеряй T1–T5. Заведи новый `runId` и уникальную папку `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/` для source, экспорта, QA и отчётов.

**Обязательный закреплённый вход в accepted `main`:** `practical-tests/reference-scenarios/references/bomb-circle-reference.png`, SHA256 `25323922ceb32c03fb171dee01d1d5d3bd55a2f9d78dac2a40194923a699e745`. Проверь совпадение с `references/PROVENANCE.md`. Если PNG отсутствует в принятом `main` или хеш не совпадает, **BLOCKED_INPUT_NOT_ACCEPTED**: не подменяй его картинкой из веба, другого PR или другого файла.

**Заказ:** нарисуй заново векторную иконку бомбы в формате 256×256 с максимально близким видом: почти чёрный округлый корпус, тёмная горловина, короткий наклонный коричневый фитиль с витками и два белых блика справа. Сохрани силуэт, пропорции, цвет, светотень и альфа-канал. Сделай собственный SVG, экспорт прозрачного PNG 256×256 и Godot 4.7 сцену с просмотром при 64px и 256px. Сравни референс и результат side-by-side по реальным полноразмерным изображениям; запиши существенные отличия.

Сохрани `reports/units/VT07.bomb.01/submission.md` по `practical-tests/UNIT-SUBMISSION-CONTRACT.md` с `scenarioId=VT07:bomb-circle-l1`, `actionId=VT07`, `variantId=bomb-circle-l1`, `unitId=VT07.bomb.01`, accepted main HEAD, входным SHA256, source/PNG/Godot/QA путями, timing и ограничениями. GitHub Issue/source Git SHA — N/A. Верни точный `runId` для независимого оценщика; не читай `_evaluator/`.
