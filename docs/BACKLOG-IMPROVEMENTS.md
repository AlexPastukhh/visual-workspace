# visual-workspace — Backlog

Единственный список незакрытых улучшений Visual Workspace. Текущие
правила owner-review и версий принадлежат
[UC-VIS-009](use-cases/media-github-review.md#uc-vis-009).
Общие provider/Gateway изменения реализуются в Fortis Approvals, не здесь.

## Уже выполнено — не планировать повторно

- **UC-VIS-008 / practical-tests:** полный комплект визуальных и creation
  briefs, готовые prompts V01–V09 и C01–C06, evaluator rubric/key, Workfiles
  run isolation и T0–T5 timing protocol уже принят в `main`.
- **Первая публикация PNG:** положительный live E2E подтверждён в
  [Issue #5 — Northlight Beacon v1](https://github.com/AlexPastukhh/visual-workspace/issues/5).
  Live readback: Issue открыт, одна PNG attachment reference, комментариев нет.
- **Issue reads:** live Gateway предоставляет `list_issues`, `get_issue`,
  `list_issue_comments` для визуального репозитория.
- **Производство/QA:** общий WORKFLOW, asset QA runner, Blender/Godot
  launchers, workbench и playable animation demo уже приняты. Улучшать их
  только при обнаружении конкретного воспроизводимого пробела.

## P0 — завершено: Gateway и same-Issue v2 E2E (2026-11-19)

1. **Live Gate / image release:** `append_visual_revision` и
   `publish_visual_review` доступны для публичного `visual-workspace`;
   обе операции в `allowGitHub`, `appendRevisionPolicy=ALLOW`.
   Новый Gateway (включая исправление public-repo preflight) установлен
   через owner-managed UC-GW-005, Backup/Promote выполнены.
   Проверенный Windows Primary: image
   `sha256:60febecf08f1aafabd7369914141b779250b786a74a1d21500c54cbdc0642fb3`,
   `running/healthy/unless-stopped`.
2. **Настоящий v1 → v2:** [Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5)
   сохранил v1 body/PNG; одна [v2 revision comment](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589)
   с новой PNG, revision marker и полным source SHA. Exact `EXECUTED`
   requestId `3a2f326d-b839-46cc-928c-b697cef338c2`, commentId
   `7010209589`; оригинальная reservation доказана через readback.
   Owner ответил **«все нормально»** после предложения открыть PNG в
   браузере. Релевантный Godot QA: 6/6 статичных кадров 1280×720,
   19.515s на import/capture/sheet (не время полного чата).
3. **Scope:** проверен **один** static 2D E2E. Это не означает, что
   автоматические latest pointer/status, видео/GLB публикация,
   длительное архивирование, игровой запуск или независимые clean chats
   уже испытаны. Source PR/CI/owner merge v2 остаётся отдельным шагом.

## P1 — сделать версионную историю удобнее

4. **Явные статусы и latest pointer.** Минимальный append API сохраняет
   append-only comments и revision markers, но не создаёт центральный
   latest index. После успешного v2 E2E оценить, нужен ли компактный
   актуальный статус (`LATEST_FOR_REVIEW`, `SUPERSEDED`, `REJECTED`,
   `ACCEPTED`) в Issue body/comment. Не добавлять edit Issue body или
   сложный registry без реальной потребности; старые версии не удалять.
5. **Source provenance и воспроизводимость.** Каждая показанная ревизия
   должна указывать полный source Git SHA или проверенный durable archive,
   QA evidence и отличия от предыдущей версии. Не писать `REPRODUCIBLE`,
   если исходник остался только в незакоммиченном worktree/Workfiles.

## P2 — другие медиаформаты

6. **Видео/GIF.** Typed attachment для MP4/WebM/GIF с проверкой codec,
   playback, размеров, TLS, policy, receipt, idempotency и readback.
   PNG storyboard/poster не считать видео.
7. **3D source/model/viewer.** Безопасная публикация/просмотр `.glb`,
   `.blend`, `.stl` или отдельный проверенный viewer/download. PNG views
   не являются передачей редактируемой 3D-модели. Не использовать прямой
   PAT, git push или произвольный upload URL.

## P3 — retention и игровые доказательства

8. **Retention/cleanup.** Явные сроки и восстановление опубликованных
   snapshots, Git source commits, больших бинарников, `.fortis-state`
   и Workfiles. Автоматический purge не включать до доказанного backup/
   restore; cleanup только точными scope.
9. **Gameplay acceptance.** Сквозная связка Issue review → owner acceptance
   → source PR/CI → owner GitHub merge → guarded Mirror Pull Windows main
   → реальная проверка Godot на Windows. PNG preview не заменяет runtime.

## Текущий проверенный срез — 2026-11-19

- Live policy: `publishPolicy=ALLOW` и `appendRevisionPolicy=ALLOW`,
  1–5 PNG до 10 MiB, `visual-workspace` публичный. Capabilities не
  хардкодить; проверять заново перед каждой публикацией.
- Owner-reviewed GitHub E2E: v1 Issue #5 + один v2 comment;
  оригинальная PNG reference и body не изменились. Byte-for-byte remote
  attachment verification через GitHub API не утверждается.
- В редакторе: v2 source Git SHA
  `06b0c9fe3ae9ae1ce7effe83e128045c711701b3`; не путать с
  последующим merge SHA. Принятие картинки владельцем ещё не source merge.
- Clean-chat V08/C03/C04/C05/VR01 и optional C06: **NOT RUN**;
  готовый план — [матрица](../practical-tests/CLEAN-CHAT-MATRIX-20261119.md).

## Передача работы

- [Handoff 01](handoffs/01-activate-append-visual-revision.md) — аудит,
  завершение и live activation typed revision method в Fortis Approvals.
- [Handoff 02](handoffs/02-validate-workflow-and-cold-chats.md) — только
  после live capability: сквозные проверки, актуализация UC/backlog и
  независимые чистые чаты.
