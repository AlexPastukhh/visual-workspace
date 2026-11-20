АКТУАЛЬНОЕ ОГРАНИЧЕНИЕ ИНСТРУМЕНТОВ: создавай/меняй визуальный объект именно средствами Visual Workspace через Fortis Repo: редактируемые SVG/Blender/Godot исходники, реальный экспорт/импорт и Godot/Blender QA. НЕ используй image_gen, AI-генерацию картинок или text-to-image для создания/изменения рабочего объекта и подмены PNG/QA. Не подменяй исходное задание новой красивой картинкой. При отсутствии источника или нужного инструмента фиксируй BLOCKED. Публикация в GitHub допустима ТОЛЬКО если её отдельно разрешает сам исходный промпт (VR01); исторические C-промпты её запрещают.

# VR01 v1 — новая 2D-работа с версионным review в одном GitHub Issue

Это отдельное обычное **пользовательское задание для нового чистого чата**
с Fortis Repo. Handoff 02 и исторический Northlight Issue #5 не являются
входными ресурсами для сдачи работы. Не раскрывай оценочные ключи, результаты
прошлых прогонов или ожидаемые ошибки.

**T0:** до чтения README получи реальное UTC-время из контейнера.
Прочитай `/workspace/repo/README.md` и `/workspace/repo/AGENTS.md`,
затем действующий `/workspace/repo/Repos/visual-workspace/README.md` на
принятом чистом `main`; следуй выбранным UC-VIS, `WORKFLOW.md`,
`docs/use-cases/media-github-review.md`, `practical-tests/TIMING.md`,
QA Registry и tools. Запиши после bootstrap T1. Не стартуй из прежнего
task worktree и не используй результаты другого теста.

**Заказ:** самостоятельно создай небольшой оригинальный читаемый 2D
компасный значок для навигационного UI (НЕ копию Northlight Beacon),
с прозрачными углами и двумя хорошо отличимыми цветами. Объяви кратко
целевые параметры (форматы, пиксели, Godot, QA), подготовь письменный
brief, редактируемый SVG, Godot сцену/проект, фактическую полноразмерную
PNG из Godot и подходящий QA. Сохрани исходники в новом task worktree,
все QA captures, временные файлы и отчёты — в собственной уникальной
`/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<run-id>/`.
Не редактируй исторические промпты, fixtures или другие Workfiles.

**Это поручение включает проверку настоящей GitHub-публикации**
для публичного `visual-workspace`; не публикуй непроверенные/private
материалы. Перед каждым реальным write проверь typed Gateway:
`c.capabilities(refresh=True)`, `publish_visual_review` и
`append_visual_revision` под `allowGitHub`, обе политики `ALLOW`,
точные actor/repo и публичность, наличие typed `prepare_*` методов.
При любом несовпадении **STOP**, без прямого PAT/CLI/HTTP и второго
Issue как fallback. Handoff 01/02 — исторические материалы; live
capabilities первичны.

**v1:** сохрани полный source Git SHA и реальную PNG (SHA256/размер),
вызови read-only `prepare_visual_review`, затем ровно один scoped
`publish_visual_review` с новым сохранённым `runId`/`requestId` и
ожидаемым digest. Докажи `EXECUTED`, Issue number, durable
baseRunId, один исходный PNG, receipt/readback. Попроси владельца
посмотреть v1 по GitHub ссылке и сообщить конкретное изменение.
**Не выдумывай его отзыв**. Если отзыва нет, остановись на
`V1_OWNER_FEEDBACK_PENDING`, не фабрикуй v2 или PASS.

**v2:** только после реального owner feedback измени именно
редактируемые исходники, сохрани новый source SHA, повторно
выполни Godot QA и изучи реальные полноразмерные PNG. Вызови
`prepare_visual_revision` и проверь стабильный `payloadSha256`,
затем ровно один `append_visual_revision` с тем же
`issueNumber/baseRunId/assetId`, `revision=2`, новым
`runId/requestId`, новым source SHA и expected hash.
Gateway READ должен доказать неизменные v1 body/PNG, **один** v2
comment с marker/sourceSha/вложением и тот же Issue. Не заменяй
неизвестный исход новым UUID и не делай v3 поверх UNCERTAIN;
используй UC-GW-009 для read-only investigation.

**Acceptance:** владелец открывает v2 PNG **в браузере** и
подтверждает отображение и качество. Only then `ISSUE_REVIEWED`;
это НЕ равно source merge или Windows gameplay. Source PR
предлагать только после явного принятия владельцем, с обычным
CI и owner merge; не мёрджить за владельца.

**Timing/evidence:** фактические UTC T0–T5 (T2 после brief/плана;
T3 при первом реально просмотренном Godot кадре; T4 после
создания/QA; T5 после проверки итогового отчёта) и
T5−T0, T3−T0; не придумывать недостающие отметки.
Записать model/config если известно, workspace main SHA/dirty
state, в каком worktree создавалась работа, QA frame paths,
Git SHA v1/v2, original и revision media SHA256,
run IDs/request IDs, точные Issue/комментарий URLs,
решение владельца, все receipts, provenance и оставшиеся
проверки. Тех. QA, визуальный acceptance и gameplay
разделять. Если новая беседа не создана — статус NOT RUN.
