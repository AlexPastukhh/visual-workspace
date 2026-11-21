# VT15 — нефинальная независимая проверка unit после человека, если он обязателен

Это задание для **нового чата-оценщика с Fortis Repo**, а не исполнителя.
Владелец передаёт четыре точных идентификатора **actionId, variantId, runId,
unitId** завершённой единицы, версию принятого `visual-testing.yaml` и,
если `human_review_required: true`, путь к уже готовому
`evaluations/<runId>/<unitId>/human-review.md`. Не искать «последний run»
и не подставлять отсутствующие данные.

**Проверка порядка — до начала ревью и до создания любого decision.md:**
прочитай `practical-tests/actions/<actionId>/visual-testing.yaml` для
**точно выбранного варианта** и его `human_review_required`, затем
[HUMAN-REVIEW.md](../../HUMAN-REVIEW.md). Если флаг `true`, сначала
подтверди наличие **реального предыдущего** `human-review.md` именно для этих
`actionId / variantId / runId / unitId`, его `human_verdict` и источник
реального отзыва человека. При его отсутствии, несовпадении идентификаторов,
отсутствии явного human verdict или неясном происхождении **остановись**:
верни владельцу `HUMAN_REVIEW_PENDING` или `INCONCLUSIVE` и назови
недостающие данные. **Не начинай техническую оценку, не создавай
`decision.md` и не придумывай за человека отзыв.** Даже если человек
выразил `CHANGES_REQUESTED`, обязательный остаточный технический аудит
проводится **после** реального отзыва, чтобы собрать остальные проблемы.

Когда этот gate пройден (либо флаг строго `false`), прочитай принятый
Visual Workspace README/UC-VIS-004/008, `action.yaml`, соответствующий
`visual-testing.yaml`, конкретный `work_prompt`,
`practical-tests/UNIT-SUBMISSION-CONTRACT.md`,
`practical-tests/_evaluator/unit-gates/README.md`, действующий rubric
`practical-tests/_evaluator/README.md`. Используй **только**
`runs/<runId>/reports/units/<unitId>/submission.md` и указанные в нём
действительные source/exports/QA/frames; если доказательства недостаточны,
фиксируй `INCONCLUSIVE` без фантазирования. Не объявляй решение
владельца и не меняй требования.

**Если `human_review_required: true`, прочитай человеческие `visual_findings`
и `visual_aspects_already_judged` ПЕРЕД проверкой визуального качества.**
Конкретные уже оценённые человеком визуальные недостатки **не проверяй
повторно** и не оспаривай их эстетическую тяжесть: перечисли в отдельном
разделе `Human-reported visual findings excluded from re-review`, обозначь
`HUMAN_REPORTED / NOT_RECHECKED` и сошлись на исходном human-review. Не
приписывай эти находки независимому чату. Если отзыв «плохо выглядит» без
конкретики — зафиксируй неопределённость, но не выдумывай дефекты.

**Проверь все ОСТАЛЬНЫЕ требования**, не ограничиваясь только журналами:
исходники и редактируемость, соблюдение запрета image_gen, реальный экспорт,
импорт и воспроизведение в Godot/Blender, техническое поведение анимации
и loop, последовательность кадров, неизменённые части при правке, другие
не оценённые человеком ракурсы/области, оригинальный reference SHA256,
tool provenance, тайминги и полноту evidence. Если замечание человека
пересекается с техническим дефектом (например, визуальный отрыв детали от
неверного rig), **проверь техническую причину и связанные обязательные
требования**, но не трать время на повторное художественное суждение.
Перед чтением runner self-review осмотри реальный источник/экспорт/QA
для проверяемых технических фактов; если tool trace недоступен, укажи
`TOOL_PROVENANCE_UNKNOWN` вместо уверенного утверждения. Для двухэтапных
VT08/VT09 проверь v1/v2 source diff и фактическую сохранность неизменяемых
свойств. Для VT11/VT12 **не используй VT15**: их собственные Action evaluator-промпты
сверяют ответы испытуемого с закрытым эталоном **после обеих частей**,
не выполняя второй самостоятельный поиск визуальных дефектов; см.
`practical-tests/actions/DEFECT-SCORING.md`.

Запиши **только собственное техническое заключение**
`evaluations/<runId>/<unitId>/decision.md` в
`/workspace/repo/Workfiles/visual-workspace-practical-tests/` по
`practical-tests/_evaluator/unit-gates/decision-template.md`. Если флаг
`true`, явно добавь `scope: TECHNICAL_ONLY / NOT_FINAL`, точную ссылку на
предшествующий human-review, `Human-reported visual findings excluded from
re-review`, список действительно проверенных **остальных** критериев,
неизвестные и **технический** verdict `APPROVED` /
`APPROVED_WITH_NOTES` / `CHANGES_REQUIRED` / `BLOCKED` / `INCONCLUSIVE`.
Если флаг `false`, решение независимого чата следует штатному rubric.

**Никогда не создавай `human-review.md` или `overall-review.md` и не пиши
итоговое `ACCEPTED`, PASS или «тест пройден» при флаге `true`.** Только
владелец/оркестратор сводит два реальных решения **после** заключения чата;
человеческое `CHANGES_REQUESTED` блокирует общий PASS, даже если технический
вердикт положительный. Не исправляй runner Workfiles, исходники,
референсы, fixtures, GitHub или скрытые ключи. Верни фактический путь к
`decision.md`, использованные идентификаторы и статус **нефинальности**.
