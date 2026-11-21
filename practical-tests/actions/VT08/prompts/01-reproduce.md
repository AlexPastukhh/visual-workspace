# VT08.crate.01 — воспроизвести деревянный ящик по PNG (L2)

НОВЫЙ независимый чат с Fortis Repo. Настоящий Visual Workspace SVG/Godot, без image_gen, text-to-image и других AI-генераторов картинок для результата или QA. **Нельзя вставлять референс в сцену как новый результат, автоматически трассировать PNG или использовать исходный SVG автора.** Исходный репозиторий только читать, GitHub/Issue/PR не использовать.

Сначала измерь UTC T0 до README, выполни bootstrap Visual Workspace, `WORKFLOW.md`, UC-VIS-001/004/008 и `practical-tests/TIMING.md`; затем измеряй T1–T5. Создай один уникальный `runId` и Workfiles папку `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/`, где храни собственные редактируемые исходники, экспорт, Godot и QA.

**Закреплённый референс из accepted `main`:** `practical-tests/reference-scenarios/references/cartoon_wooden_crate-reference.png`, SHA256 `034315917477a48cfd74b6858768dc0040c1a66320b76b4f4c90854d114618b7`. Сверь `references/PROVENANCE.md`. При отсутствии PNG в accepted `main` или неправильном хеше — BLOCKED_INPUT_NOT_ACCEPTED, без подмены из другого источника.

**Заказ только для первого этапа:** заново создай редактируемый SVG деревянного ящика, вид строго сверху, по PNG 256×256: квадратная наружная рамка, Х-образные диагональные балки поверх горизонтальных досок, коричнево-золотые тона, тонкие линии, прозрачный фон. Не превращай вид сверху в 3D-куб. Экспортируй PNG 256×256 и открой реальное Godot 4.7 превью; сравни с референсом side-by-side. Сохрани первый исходник, первую версию PNG, SHA256 исходного SVG и QA как **неизменяемую базовую версию** для сравнения со следующим этапом.

Сохрани `reports/units/VT08.crate.01/submission.md` по контракту unit handoff с `scenarioId=VT08:top-down-crate-l2`, `actionId=VT08`, `variantId=top-down-crate-l2`, `unitId=VT08.crate.01`, runId, prompt/main SHA, reference SHA, source/export/QA/timing и замечаниями. Не открывай другие этапы теста и `_evaluator/`. После первой сдачи остановись: новое изменение может прийти только отдельным пользовательским сообщением в **этом же чате**, после независимой оценки первой версии.
