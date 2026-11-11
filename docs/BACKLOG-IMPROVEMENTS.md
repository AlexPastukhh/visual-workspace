# visual-workspace — Backlog

Единственный список будущих улучшений; актуальный цикл и ограничения:
[UC-VIS-009](use-cases/media-github-review.md#uc-vis-009).

## Приоритет: единый Issue и управляемая история ревизий

1. **Gateway: append-revision в уже существующий Issue.** Сделать отдельную
   typed owner-ASK операцию для добавления версии `vN` как нового комментария
   к Issue первого результата: точный `issueNumber`/repository, `asset_id`,
   immutable `run_id`/`requestId`, verified original Issue identity, owner
   access, SHA-256/size списка PNG, durable per-revision reservation/receipts,
   protection against duplicate or partial effects, strict upload budget,
   readback and latest-index updates. Не перезаписывать существующие
   вложения и не смешивать независимые заказы. При `UNCERTAIN`: расследование,
   а не второй publish для того же результата.
2. **Index/state и источник каждой версии.** В Issue показывать историю
   `v1 SUPERSEDED → v2 REJECTED → v3 ACCEPTED`, изменения и ссылку на
   исходный Git SHA/проверенный архив оригинала. Добавление/переключение
   latest без удаления прежних комментариев; source provenance/retention
   проверять до объявления `REPRODUCIBLE`.
3. **Положительный PNG E2E.** Один настоящий PNG → staged → ASK →
   приватный GitHub Issue → attachments → receipt/URL/readback.
   Затем проверка второй версии с новой разрешённой операцией (пункт 1).

## Другие форматы и доставка

4. **Typed видео/GIF attachment.** Разрешённый `.mp4`/`.webm` с проверкой
   codec/playback, границами размера, полным TLS/ASK/receipt/idempotency,
   хранением оригинала; PNG-постер не считать записью видео.
5. **3D source/model/viewer.** Версионированные `.stl`/`.glb`/`.blend`,
   безопасное хранение и viewer/download, проверенный STL browser preview
   только когда GitHub содержит настоящий файл. Без прямого PAT/git push.
6. **Retention и контролируемая очистка.** Явное правило для published
   snapshots, source Git commits, исходных больших бинарников, project-local
   `.fortis-state` и Workfiles. Автоматический purge не включать, пока
   не проверена возможность восстановления обязательных опубликованных
   версий; отдельные точные cleanup-scopes и retention/backup evidence.
7. **Независимая приёмка нового чата (UC-VIS-008).** Полный
   `practical-tests/` с текстовыми заданиями, ключом оценщика, PNG/видео
   frame fixtures и протоколом T0–T5 остался в исходной незавершённой
   `work/initial-visual-workspace-20261101`. Вынести его отдельным проверенным
   task/PR после проверки комплекта, конфиденциальности ключа и результатов;
   не смешивать с минимальным production workflow (UC001–007,009).
8. **Gameplay acceptance.** Явная связка rendered review → accepted PR/CI
   → owner GitHub merge → guarded Mirror Windows main → Godot тест и
   возврат замечаний; фиксировать проверенную версию источников и факт
   запуска владельцем. Не подменять Godot доказательство PNG/скриншотом.

Изменения Gateway выполняются в его собственном репозитории и релизном
цикле. Документация не даёт права обходить ASK, менять credentials
или копировать защищённые Gateway volumes ради версии картинки.
