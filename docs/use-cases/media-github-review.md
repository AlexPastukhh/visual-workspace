<a id="uc-vis-009"></a>

# UC-VIS-009 — Итерации медиа → обратная связь → GitHub → сохранение версий

## Когда

ИИ создаёт или исправляет 2D-иллюстрацию/спрайт, 3D-модель/сцену,
2D/3D-анимацию или игровой визуальный результат и должен **показать
владельцу** картинку/кадры, получить комментарии, выпустить следующую
ревизию и не потерять ранние. Для **игрового запуска** владелец проверяет
Godot-проект у себя на Windows после синхронизации принятого GitHub `main`.
Это дополнение к производственному процессу, **не** альтернативный редактор,
система QA или замена Git-доставке кода.

## Цель и границы ответственности

- **Docker + Git:** рабочие и выбранные опубликованные **исходники** (сцены,
  `.blend`, скрипты, спрайты, настройки импорта), технические тесты, возможность
  исправить следующую версию на основе исходника, а не GitHub-превью.
- **GitHub Issue:** публичная **витрина обратной связи** для владельца:
  PNG/кадры, описание различий, статус ревизии, проверенные ссылки; ранние
  опубликованные варианты остаются видимыми как история, не подменяют файлы
  проекта. Issue и Git-исходники имеют **разную идентичность и назначение**.
- **Gateway:** авторизация, policy per operation (`ALLOW`/`ASK`/`DENY`),
  одноразовые writes, durable receipts и обработка неопределённого исхода.
  На 2026-11-19 обе visual write-операции имеют строго scoped `ALLOW` для
  `visual-workspace`; repository visibility может быть public или private.
  Перед каждым write перечитать live capabilities. Прямой GitHub PAT/CLI/HTTP
  upload со стороны ИИ запрещён как fallback.
- **Owner:** оценивает изображение/анимацию по ссылке и задаёт изменения;
  для игры принимает Source PR/merge, выполняет защищённый Mirror Pull Windows
  `main` и самостоятельно проверяет проект в Godot.

### Как работает Issue в live Gateway (2026-11-19)

| Событие | Подтверждённый путь |
| --- | --- |
| Черновик и технический QA | Issue автоматически не создаётся. Подготовить реальную PNG, source commit и brief. |
| Публикация v1 | `prepare_visual_review` (без эффекта), затем scoped-`ALLOW` `publish_visual_review`: **новый Issue** с 1–5 PNG, новым `runId` и `requestId`, receipt и проверка через Gateway READ. |
| Исправление v2+ | Исходный `assetId`, `issueNumber` и `baseRunId`; после реального owner feedback — новая source-версия, новый `runId`, `prepare_visual_revision` и один `append_visual_revision` с expected hash. Новая PNG публикуется **комментарием в тот же Issue**; v1 не переписывается. |
| Owner acceptance | Владелец проверяет ссылку/изображение в браузере; `ISSUE_REVIEWED` не означает source merge или gameplay acceptance. |
| Неизвестный исход | `DISPATCHED`/`UNCERTAIN`/lost ACK: STOP, осмотр **того же** requestId по UC-GW-009. Ни повторный POST, ни новый Issue как fallback недопустимы. |

Центральный latest pointer, автоматические статусы `SUPERSEDED`/`ACCEPTED`
и проверка байтов удалённого GitHub PNG средствами текущего READ API
**не реализованы**. Версии доступны в исходном Issue и его комментариях.

**Принцип:** один Issue на одну логическую единицу обратной связи
(например, «персонаж X», «анимация бега X» или один согласованный составной
заказ). Несколько **независимых** заказов получают отдельные Issue; не
смешивать их историю в один бесконечный тред. **Номер Issue — ID обсуждения,
а `run_id` — ID конкретного рендера/ревизии**: не путать их.

## Полный повторяемый цикл

1. **Выбрать работу и исходник.** 2D/3D-ассет, анимация, составной заказ и
   игровая интеграция идут через соответствующие сценарии производства.
   Для существующего объекта продолжать его task/исходники и brief;
   использовать новый linked worktree по Git-контракту, когда задача
   действительно независима. Указать `asset_id`/`order_id`, платформу,
   редактор, editable/source формат, Godot runtime/export формат и критерии
   приёмки. Не создавать новый проект вместо исправления существующего.
2. **Сохранить рабочую версию.** Редактировать источники и выполнять подходящие
   тесты. Для **каждой версии, предъявленной владельцу**, запомнить хотя бы:
   `asset_id`, `vN`, уникальный `run_id`, исходный Git SHA (когда есть
   коммит), путь и SHA-256 оригинала, preview/QA, время, замечания и статус.
   В рабочем проекте `brief.md` отвечает за требования, `asset.qa.json` —
   за настройки захвата; не создавать второй конкурирующий реестр задач.
   До обещания воспроизводимой старой версии сохранить редактируемые исходники
   **отдельным проверенным Git-коммитом / принятым долговременным архивом**.
   Не утверждать, что незакоммиченные исходники входят в Git-историю.
3. **Сделать ранний и итоговый визуальный QA.** В Docker получить PNG-кадры
   и последовательности, открыть реальные изображения, а при анимации
   проверить нужные моменты, переходы и цикл; для 3D — ракурсы, масштаб и
   соответствие модели. Временные `.fortis-state` capture/cache и каталоги
   `/workspace/repo/Workfiles/.../<run_id>/` **не** считаются Git-коммитами
   или вечным архивом. Для продолжения работы использовать исходные файлы,
   `.blend`/Godot-scene/генераторы, а не картинку из GitHub.
4. **Подготовить показ.** Записать, что изменилось относительно `vN-1`,
   что проверено, что ещё не готово, оригиналы и ссылки на предыдущие версии.
   Для PNG подготовить 1–5 обычных файлов до 10 MiB каждый внутри
   `/workspace/repo/Workfiles/<project>/<run_id>/.../*.png`. Новый `run_id`
   для каждой действительно новой версии, **не** новый случайный UUID для
   повторения неоднозначной публикации.
5. **Показать v1 штатным Gateway.** Перед write:
   `c = default_client(); caps = c.capabilities(refresh=True)`.
   Для `visual-workspace` проверить `publish_visual_review` в
   `allowGitHub` и `visualReview.publishPolicy=ALLOW`. Публиковать выбранную
   QA-проверенную версию, а не каждый промежуточный кадр. Сохранить один
   immutable `runId`/`requestId`, локально подготовить payload hash,
   затем выполнить typed publisher **один раз**. `PENDING` ещё не Issue.
6. **Прочитать v1 обратно.** Для `EXECUTED` проверить receipt, точный
   номер Issue и `runIdMarker`, исходное тело и ссылку на PNG через
   `get_issue` / `find_visual_review_run`. Убедиться, что владелец
   действительно открывает PNG. Публичный Issue/PNG не содержат секретов.
7. **Отработать owner feedback и опубликовать v2+ в том же Issue.**
   Сохранить фактическое замечание (не выдумывать), отредактировать
   **исходники** в той же задаче и сделать новый source commit; выполнить
   применимые Godot/QA и открыть реальные PNG. Подтвердить исходный
   `baseRunId`, `assetId` и durable reservation, новый последовательный
   `revision`, новый `runId` и `requestId`. Повторно проверить
   `append_visual_revision` в `allowGitHub` и
   `visualReview.appendRevisionPolicy=ALLOW`. Сначала чистая локальная
   `prepare_visual_revision(...)`, сохранить `payloadSha256` и PNG SHA,
   затем один `append_visual_revision(...,expected_payload_sha256=...)`.
   Доказать `EXECUTED` receipt, тот же Issue, неизменные body/v1 PNG,
   ровно один v2 comment, marker/assetId/revision/runId/sourceSha,
   отдельную новую PNG-ссылку и просмотр владельцем в браузере.
   Текущий append API не редактирует Issue body, не удаляет старые версии
   и не даёт права комментировать произвольные Issues. При любом
   `UNCERTAIN` расследовать исходный UUID по UC-GW-009; не пытаться
   заменить v2 новым Issue или перейти к v3 поверх неопределённого v2.
8. **Закрепить результат.** После принятия владельцем отметить выбранную
   версию и её source SHA; ссылки на отклонённые версии оставить для
   сравнения с пометкой «отклонена/заменена». `ISSUE_REVIEWED` ≠
   `SOURCE_MERGED` ≠ `GAMEPLAY_ACCEPTED`. Подготовить исходники/сцены для
   обычной Git PR/CI/owner-merge доставки, а не считать GitHub Issue
   исходником игры.
9. **Для игры — Windows/Godot acceptance.** Проверить GitHub PR/CI и
   owner-merge, затем использовать защищённый **Mirror → Pull Windows main**
   для точного принятого merge SHA. Пользователь открывает проект в Godot
   на Windows, запускает сцены/игру, проверяет ввод, анимацию, переходы,
   коллизии и поведение. Превью в GitHub не доказывает игровой запуск.
   Если владелец сообщает дефект из Godot, исправить **исходники** в новой
   task-итерации и повторить нужную QA/PR/merge/Mirror-цепочку; не обходить
   GitHub через прямой push.

### Сохранение всех вариантов и политика очистки

| Слой | Что действительно остаётся | Можно ли очистить |
| --- | --- | --- |
| GitHub Issue + PNG-вложения | v1 остаётся в исходном Issue; v2+ — отдельные append-only комментарии и PNG references в **том же Issue** (для Northlight проверено #5, v2 comment 7010209589) | Не удалять/переписывать версии; доступность GitHub links зависит от GitHub и статуса репозитория. Gateway readback возвращает ссылки, но не хеш оригинальных байтов на GitHub. |
| Git-исходники | Только явно закоммиченные/доставленные исходные файлы; старые состояния можно найти по их SHA при сохранённой истории | Не переписывать историю, не `force`/reset ради очистки. Git не архивирует игнорируемые файлы и кэши |
| Docker task worktree | Текущая изменяемая работа и ещё не принятые исходники | Только через штатный Fortis `cleanup_task`, после merge/проверки и сохранения нужного source. Удаление worktree **не** равно удалению Git-коммитов |
| Project-local `.fortis-state`, Godot `.godot`, Workfiles | Промежуточные рендеры, пофазный QA, временные кадры, игнорируемые файлы; уникальные run-папки сейчас не перезаписываются штатным QA-runner | **Не гарантированы навсегда.** Очистка — только выбранных точных путей после проверки нужности, source/QA/backup, без массового `clean`/`prune` |
| Gateway state volume | Staged PNG по UUID, metadata и GitHub receipts в защищённых томах/SQLite; не источник редактируемой 3D-сцены | Не чистить самостоятельно. Защищённое Backup/Promote/retention принадлежит владельцу Gateway |

**Ответ на «все ли версии остаются?»:** нормативная цель — **все показанные
владельцу версии** имеют доступную ссылку, состав превью и сохранённый
воспроизводимый источник. Текущая реализация **не гарантирует** это
автоматически: не все промежуточные Docker-рендеры и не все незакоммиченные
`.blend`/Godot-файлы попадают в Git. До реализации архива agent должен
явно сообщать, какие версии реально сохранились и где; если необходимо
сохранить *каждую* промежуточную попытку, включать отдельную фиксацию её
оригиналов **до** допустимой очистки. Не удалять неудачный вариант только
потому, что владелец попросил следующий.

### Форматы 2D / 3D / анимаций и ограничения публикации

| Результат | Превью сейчас | Оригинал / запуск |
| --- | --- | --- |
| 2D иллюстрация, спрайт | PNG в GitHub Issue | Editable PSD/Krita/Godot-ресурс только если отдельно сохранён и опубликован подтверждённым способом |
| 3D модель, сцена | 1–5 PNG ракурсов/turntable-кадров | `.blend`/`.glb`/`.stl` не загружаются текущим Gateway методом; STL может иметь GitHub viewer **только после отдельной реальной публикации файла** |
| 2D/3D анимация | Постер + ключевые PNG кадры; для движения нужны временные границы и последовательность | MP4/WebM/GIF не публикуются текущим Gateway методом; PNG-превью **не** доказывает playback. Владелец может отдельно прикрепить поддерживаемое видео в GitHub UI |
| Игра/интерактивная сцена | PNG результатов и QA, ссылку на кодовый PR/commit | Финальный запуск — в Godot на Windows после проверенного Mirror Pull принятого `main` |

Наличие медиа в `/workspace/repo/Workfiles` **не** делает его GitHub
вложением. Ручная публикация файла владельцем через GitHub UI допустима,
но это отдельное действие, не результат автоматической публикации ИИ.
Любая реальная ссылка на оригинал должна быть отдельно проверена.

### Typed provider calls and current limits

**Current scope:** public `AlexPastukhh/visual-workspace`,
`publish_visual_review` and `append_visual_revision` are in
`c.capabilities(refresh=True)['allowGitHub']`,
`visualReview.publishPolicy=ALLOW` and
`visualReview.appendRevisionPolicy=ALLOW` (2026-11-19). Other operations,
targets and actors retain their own policies; never treat ALLOW as broad
Issue/comment permission. The request must be the exact Fortis-created,
open ordinary Issue with original durable reservation and matching asset.
Both visibility values are accepted **only after** owner/repository identity,
Issues-enabled state and repository ID have been checked by Gateway.
The append action is source-gated and append-only.

For an owner-requested v2 (replace example placeholders with real verified
values; this is **not** a command to write to historical Issue #5 again):

```python
import uuid
from fortis_approvals.workflow.client import default_client

c = default_client()
caps = c.capabilities(refresh=True)
assert 'append_visual_revision' in caps['allowGitHub']
assert caps['visualReview']['appendRevisionPolicy'] == 'ALLOW'

args = dict(
    repository='visual-workspace',
    issue_number=123,                 # Real, verified Fortis-created v1 Issue.
    base_run_id='actual-v1-run-id',
    asset_id='asset-id',
    revision=2,
    run_id='new-unique-v2-run-id',
    source_sha='a' * 40,               # Replace with REAL full Git commit SHA.
    description='Exact owner-requested change and v1 difference',
    media=[{'path': '/workspace/repo/Workfiles/visual-workspace/v2-run/preview.png',
            'name': 'Actual Godot v2 PNG'}],
    qa_summary='Measured QA and actual inspected frames',
    duration_seconds=30,
)
preview = c.github.prepare_visual_revision(**args)  # Local; no remote write.
request_id = str(uuid.uuid4())                       # Persist before submit.
reply = c.github.append_visual_revision(
    **args, request_id=request_id,
    reason='Publish verified owner-requested v2 in the original Issue',
    expected_payload_sha256=preview['payloadSha256'])
# One submission only. Check c.result(request_id), c.details(request_id),
# get_issue and list_issue_comments. No blind replay on UNCERTAIN.
```

**Verified Northlight E2E (2026-11-19, not a general quality benchmark):**

- [v1 Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5):
  original `baseRunId=northlight-beacon-e2e-v3-20261117`, one PNG retained,
  Issue body/run marker unchanged.
- [v2 comment](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589):
  `assetId=northlight-beacon-2d`,
  `runId=northlight-beacon-e2e-v2-20261119`, revision 2, source Git SHA
  `06b0c9fe3ae9ae1ce7effe83e128045c711701b3`.
  Gateway receipt `EXECUTED`, `commentId=7010209589`, `uploadedFiles=1`,
  one v2 comment and new attachment reference. Request ID
  `3a2f326d-b839-46cc-928c-b697cef338c2`.
- Owner requested any visible change; v2 north needle/tick/jewel became
  coral-pink instead of amber. Godot captured six identical static 1280×720
  frames; PNG SHA-256
  `17f14800b2a7d8baccc1861c1fdcafcb59c0ddea7d95948c4b3c667f1e937310`.
  Владелец сообщил: **«все нормально»** после открытия ссылки.
- Evidence: `/workspace/repo/Workfiles/visual-workspace/northlight-beacon-e2e-v2-20261119/`.
  User confirmation establishes browser acceptance as reported; Gateway
  Markdown-link readback **не доказывает побайтовое соответствие удалённой PNG**.
  Source PR, owner merge и Windows Godot/gameplay acceptance остаются
  отдельными этапами. Это `ISSUE_REVIEWED`, не `SOURCE_MERGED`.

### Relation to the production workflow

- [WORKFLOW.md](../../WORKFLOW.md) owns creation, correction, visual QA and
  game integration. This UC owns the owner-facing Issue/revision lifecycle.
- [UC-VIS-001–005](README.md) call this UC only when an owner-facing review is
  requested; one logical asset/order gets one Issue, independent orders get
  separate Issues.
- [UC-VIS-006](README.md) may provide reviewed video/frame evidence, but PNG
  Issue previews do not become video playback evidence.
- [UC-VIS-007](README.md) keeps parallel worktree/path ownership separate;
  each independent owner-review thread has its own Issue.
- [UC-VIS-008](README.md) practical blind tests do not publish fixture answers
  or create Issues by default. Clean-chat owner-review tests are a separate,
  explicitly authorized integration exercise described in
  [Handoff 02](../handoffs/02-validate-workflow-and-cold-chats.md).

## STOP / acceptance

- Check live capabilities before every write. Source code or offline tests do
  not prove a method is live. If `append_visual_revision` is absent, stop the
  same-Issue write path; do not silently substitute a new Issue.
- `PENDING`/`APPROVED` are not a published Issue/comment. Wait for the owner
  decision and verify the final state.
- `DISPATCHED`, `UNCERTAIN`, lost response or `CLOSED_UNCONFIRMED`: investigate
  the **same** request ID and durable evidence using
  [UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009).
  Do not create a replacement UUID or next revision while the effect is unknown.
- For PNG, require `EXECUTED`, matching receipt, exact Issue/comment readback,
  marker, source SHA and attachment references. Readback links do not prove
  remote image bytes; owner browser inspection is still required.
- For video/3D originals, require a separately verified original-file link
  and actual playback/viewer. Otherwise report `PREVIEW_ONLY`.
- For game delivery, source PR/CI/owner merge and Mirror receipt precede the
  owner's actual Godot-on-Windows acceptance. Issue/PNG is not gameplay proof.

## Точные контракты

[Fortis Gateway PNG MVP](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/integrations/github/README.md#visual-review-png-mvp) ·
[Append visual revision source contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/integrations/github/README.md#append-visual-revision-to-an-existing-issue) ·
[UC-GW-003 — typed operation](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003) ·
[UC-GW-005 — owner-managed release](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005) ·
[UC-GW-009 — unknown outcome](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009) ·
[UC-CONT-002/003 (Git/PR/Gateway)](https://github.com/AlexPastukhh/fortis-container/blob/main/docs/use-cases/delivery.md#uc-cont-002) ·
[UC-CONT-005 (Mirror Windows)](https://github.com/AlexPastukhh/fortis-container/blob/main/docs/use-cases/delivery.md#uc-cont-005).
