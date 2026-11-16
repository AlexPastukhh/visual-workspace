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

## P0 — включить same-Issue revisions в production

1. **Fortis Gateway: активировать `append_visual_revision`.**
   В Fortis Approvals source уже присутствуют `prepare_visual_revision()`,
   `append_visual_revision()`, строгий GitHub contract, native adapter,
   route allowlist, runtime `ASK` для `visual-workspace` и offline suite
   `test_visual_revisions.py` (9/9 PASS на проверенном source checkout).
   Но live capabilities на 2026-11-17 метод не объявляют. Не дублировать
   готовый код: сначала аудитировать gaps, затем довести UC-GW-003/005,
   exact-SHA CI, owner-managed Gateway image release и live readback.
   Требуемое live доказательство: `append_visual_revision` объявлен в
   `askGitHub` только для `visual-workspace`; `publish_visual_review`
   остаётся совместимым; чужие репозитории получают DENY.
2. **Настоящий v2 E2E в том же Issue.**
   Проверить `prepare_visual_revision` → typed append → owner ASK/WebAuthn
   → `EXECUTED` receipt → GitHub comment/attachment readback. Убедиться,
   что номер Issue тот же, v1 body/PNG не изменились, появился ровно один
   v2 comment с marker, `assetId`, `baseRunId`, `runId`, revision и source SHA.
   Owner должен открыть реальную PNG в браузере. Не считать unit test или
   ссылку на attachment доказательством доступности байтов.
3. **Исходная публикация #5 — кандидат, не гарантированный target.**
   Перед использованием проверить, что Gateway может доказать исходную
   durable reservation/baseRunId для Issue #5. Если доказательства нет,
   не обходить precondition: создать новый согласованный v1 Issue после
   live release и тестировать v2 на нём. Не отправлять новый Issue для v2
   без явного согласия владельца.

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

## Текущий проверенный срез — 2026-11-17

- Live `publish_visual_review`: `ALLOW` только для `visual-workspace`;
  PNG-only, 1–5 файлов, до 10 MiB каждый.
- Live `append_visual_revision`: отсутствует в capabilities; same-Issue v2+
  ещё не доступен.
- Issue #5: открыт, одна PNG reference, ноль comments. Run marker
  `northlight-beacon-e2e-v3-20261117` — это run ID, не revision label.
- Fortis Approvals source candidate: commit
  `bdb3ec581db7157b05f5d6c5282c7d3a7b6d0a35`; focused offline tests 9/9.
  Это не deployed image и не live E2E.

## Передача работы

- [Handoff 01](handoffs/01-activate-append-visual-revision.md) — аудит,
  завершение и live activation typed revision method в Fortis Approvals.
- [Handoff 02](handoffs/02-validate-workflow-and-cold-chats.md) — только
  после live capability: сквозные проверки, актуализация UC/backlog и
  независимые чистые чаты.
