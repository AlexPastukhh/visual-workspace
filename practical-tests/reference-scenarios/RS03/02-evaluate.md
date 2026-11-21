# RS03.02 — независимая оценка

Ты независимый оценщик ОДНОЙ завершённой единицы RS в НОВОМ чате Fortis Repo. Ты не исполнитель. Получи от владельца точный runId; у каждого этапа имеется маршрут /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/RS03.02/submission.md и итоговый путь /workspace/repo/Workfiles/visual-workspace-practical-tests/evaluations/<runId>/RS03.02/decision.md. Если подтверждённого runId нет, неоднозначность => INCONCLUSIVE, не подставляй последний результат.

Прочитай Visual Workspace README, исходное требование и unit-gates/README.md. Сначала просмотри настоящие reference PNG, исходники, реально экспортированные PNG и full-res Godot/Blender QA, Git source SHA, publication receipt; запиши наблюдения до чтения self-review исполнителя. Проверь подмену: импортированный оригинальный reference PNG/SVG/mesh или image_gen/AI-generated финальный арт не соответствует независимому созданию и требует CHANGES_REQUIRED. При недоступном tool-call trace отмечай TOOL_PROVENANCE_UNKNOWN. Нельзя создавать изображение, изменять исходник, Workfiles runner или GitHub.

Сохрани самостоятельный decision.md с конкретными визуальными признаками, ограничениями проверки, source/editability, pipeline import, real QA, issue/revision proof, timing and severity, verdict APPROVED/APPROVED_WITH_NOTES/CHANGES_REQUIRED/BLOCKED/INCONCLUSIVE. Не подменяй решение владельца. Оцени только текущую единицу, не объявляй полный сценарий PASS до всех его частей.

**Сверь конкретное требование:** practical-tests/reference-scenarios/RS03/02-work.md

**Зафиксированные эталонные PNG:**
- practical-tests/reference-scenarios/references/crate-reference.png
- practical-tests/reference-scenarios/references/barrel-reference.png

**Идентичность входа:** независимо пересчитай SHA256 показанных эталонных PNG и сравни с references/PROVENANCE.md; если не совпало, INCONCLUSIVE для сопоставимого benchmark. Проверь точный accepted Git HEAD промпта и фактического выполнения, отличай техническое качество от художественного сходства.

**Критерии для этой единицы:** Локальная смена фурнитуры без потери составного силуэта, искажений перспективы и исходных деталей дерева; реальное изменение source и append-only история.
