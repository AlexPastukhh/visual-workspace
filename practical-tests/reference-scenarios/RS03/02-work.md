# RS03.02 — изменение после RS03.01

Это новое требование владельца В ТОМ ЖЕ исходном чате и в продолжение того же Visual Workspace task. Продолжай редактировать свой реальный исходный SVG/Blender/Godot, не начинай новый заказ и не создавай новый Issue. Обязательно только Fortis Repo и реальные source/edit/QA. Запрещены image_gen и другие генераторы AI-картинок. Сохраняй все прошлые несменённые требования, тот же scenario runId, исходные Git/source assets и issueNumber. После QA опубликуй следующую реальную revision через typed append_visual_revision в том же Issue со своим новым source SHA и requestId; при UNCERTAIN остановись и расследуй. Замерь S2.0–S2.5 и owner wait отдельно. Референсы неизменяемые PNG, не импортируй их как свой новый исходник.

**Новое требование:** Поменяй цвет только металлических накладок и заклёпок нового контейнера на медно-бронзовый металл с тёмными креплениями. Не меняй деревянные доски, общую геометрию, перспективу, размер 256×256 и прозрачный фон. Повтори QA и опубликуй следующую версию в том же Issue.

**Оригинальные референсы (только для сверки):**
- practical-tests/reference-scenarios/references/crate-reference.png
- practical-tests/reference-scenarios/references/barrel-reference.png

**Воспроизводимость:** вычисли и запиши SHA256 каждого реально показанного pinned reference PNG из accepted main и сверь с references/PROVENANCE.md; укажи accepted main HEAD. Сохрани независимый собственный исходник, а не содержимое исходной картинки.

**После исполнения:** сохрани фактический указатель доказательств по контракту practical-tests/UNIT-SUBMISSION-CONTRACT.md: /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/RS03.02/submission.md. Укажи actual runId, source full Git SHA, источник и результат, paths PNG/QA, Issue/revision/comment (или N/A), timings/receipts и ограничения. Не читай _evaluator/ или соседний evaluate-файл, не изменяй исторические SC/SV/C/V.
