# visual-workspace — Backlog

Этот файл — единое место для **будущих** улучшений визуальной доставки.
Сценарий и критерии приёмки: [UC-VIS-001](use-cases/media-github-review.md#uc-vis-001).

## Следующие улучшения

1. **Положительный живой E2E PNG.** Создать тестовое PNG из настоящего run,
   пройти `github.publish_visual_review` → Owner ASK → GitHub Issue/attachments
   → verified URL/receipt/readback. Не смешивать unit tests с live acceptance.
2. **Typed видео-вложения (`.mp4`, `.webm`, при необходимости `.mov`).** В
   Fortis Gateway спроектировать отдельный проверенный маршрут с bounded file
   validation, TLS, owner-ASK, идемпотентным run, durable progress/receipts,
   защитой от частичных удалённых эффектов и проверкой реального playback.
   Учесть лимиты GitHub и поддерживаемые кодеки; не подключать GitHub CLI/PAT
   в Docker Repo как обход Gateway.
3. **Оригиналы 3D и viewer.** Определить поддержанные исходные форматы
   (`.stl`, `.glb`, `.blend`), приватное хранение, GitHub blob/release/attachment
   и download/viewer ссылки, правила безопасности и QA. Для STL проверить
   нативный GitHub viewer на реальном файле; для остальных viewer не
   предполагать. Добавить typed Gateway операции до обещания auto-upload.
4. **Удобный единый отчёт.** Связать PNG-превью, исходный артефакт, версию,
   hash, длительность, QA и подтверждённые ссылки в одном Issue; при
   анимации показывать poster + playable media; при 3D — ракурсы + viewer.
   Проверять приватную доступность для владельца перед статусом «готово».

Все изменения Gateway и публикации проходят его собственные UC/PR/CI/owner
процедуры; этот backlog не даёт права обходить policy.
