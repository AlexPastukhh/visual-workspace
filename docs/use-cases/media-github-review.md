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
- **GitHub Issue:** удобная приватная **витрина обратной связи** для владельца:
  PNG/кадры, описание различий, статус ревизии, проверенные ссылки; ранние
  опубликованные варианты остаются видимыми как история, не подменяют файлы
  проекта. Issue и Git-исходники имеют **разную идентичность и назначение**.
- **Gateway:** авторизация, policy per operation (`ALLOW`/`ASK`/`DENY`),
  одноразовые writes, durable receipts и обработка неопределённого исхода.
  На 2026-11-17 v1 publisher live `ALLOW`; revision source policy — отдельный
  `ASK` для `visual-workspace`, но append API ещё не live. Всегда читать
  capabilities перед write. Прямой GitHub PAT/CLI/HTTP upload со стороны ИИ
  не является разрешённым fallback.
- **Owner:** оценивает изображение/анимацию по ссылке и задаёт изменения;
  для игры принимает Source PR/merge, выполняет защищённый Mirror Pull Windows
  `main` и самостоятельно проверяет проект в Godot.

### Как открывается Issue: сейчас и в желаемом цикле

| Событие | Текущее live-состояние (2026-11-17) | Целевая модель после активации revision API |
| --- | --- | --- |
| ИИ сделал внутренний draft/QA | Issue не создаётся автоматически | То же: публиковать только выбранную QA-проверенную версию |
| Показ первой ревизии `v1` | `client.github.publish_visual_review()` создаёт новый приватный Issue с PNG. Live policy сейчас `ALLOW` для `visual-workspace`; всегда перепроверять capabilities | Один Issue на логический ассет/заказ; сохранить `issueNumber` и `baseRunId` |
| Владелец просит изменить `v1` | `append_visual_revision` в live capabilities отсутствует. Текущий publisher создаст новый Issue; делать это только если владелец явно согласовал отдельный Issue. Иначе дождаться активации revision API | `client.github.append_visual_revision()` добавляет новую версию комментарием в **тот же Issue** с отдельными PNG/QA/source SHA |
| `v1` устарела, `v2` актуальна | Автоматического общего version index/latest pointer нет; версии связаны только явными ссылками между Issue | Сохранять v1 и все комментарии; маркировать статусы/изменения в ревизионном комментарии. Центральный latest pointer пока не входит в минимальный API |
| Результат неопределён | `DISPATCHED`/`UNCERTAIN`: STOP, разбор того же UUID, не создавать новую заявку | То же; плюс durable reservation по Issue/revision/run до upstream effect |

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
5. **Запросить первую публикацию.** Только если владелец запросил показ
   или согласована контрольная точка: через
   `client.github.publish_visual_review()` для `visual-workspace`. Клиент
   отправляет PNG по machine TLS; фактическая policy зависит от live Gateway.
   На проверке 2026-11-17 `visualReview.publishPolicy=ALLOW` и операция была
   в `allowGitHub`, а не `askGitHub`. Не обещать Owner ASK для v1 и не
   предполагать, что policy останется такой: перед каждым новым действием
   читать live capabilities. Если policy вернёт `ASK`, ждать owner decision;
   `PENDING`/`APPROVED` сами по себе не являются опубликованным Issue.
   После `EXECUTED` проверить Issue/receipt/readback. **Не публиковать каждый
   промежуточный кадр автоматически.**
6. **Проверить выдачу ссылки.** Получить `EXECUTED`, `url`,
   `uploadedFiles`, проверить Issue и превью через разрешённый Gateway READ;
   приватная ссылка должна открываться владельцу с доступом к репозиторию.
   При отсутствии receipt или `DISPATCHED`/`UNCERTAIN` не повторять действие:
   подробный безопасный разбор — [UC-GW-009](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009).
7. **Принять комментарии и создать следующую версию.** Сохранить исходный
   текст/задачу владельца, связать с `asset_id` и конкретной `vN`; изменить
   **Docker-исходник**, а не вложенный PNG. Запустить необходимые QA,
   получить новый `run_id`, сохранить точный `sourceSha` и подготовить 1–5 PNG.
   До появления `append_visual_revision` в live capabilities не обещать
   добавление в прежний Issue. Отдельный новый Issue — только временный
   вариант при явном согласии владельца; иначе остановиться после подготовки
   v2 и дождаться API. После активации revision API v2+ отправлять
   `client.github.append_visual_revision()` в тот же проверенный Issue:
   это новый comment с отдельными вложениями, а не редактирование Issue body
   или старых комментариев. Для каждой ревизии требуется отдельный owner ASK;
   v1 `ALLOW` не наследуется. При `PENDING` ждать, при `UNCERTAIN` расследовать
   тот же requestId, не создавать новый UUID и не продвигать следующую версию.
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
| GitHub Issue + PNG-вложения | Issue #5 — проверенная первая публикация v1; текущий live publisher создаёт отдельный Issue на каждый run. Same-Issue revision пока не live | Не удалять автоматически. После активации append API новые версии добавлять отдельными комментариями; старые Issue/комментарии/вложения сохранять |
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

Первая версия (`v1`) использует существующий
`client.github.publish_visual_review(...)`. Он создаёт Issue и прикрепляет
1–5 PNG. Это единственный визуальный write, который подтверждён в live
capabilities на 2026-11-17; его фактическая policy на эту дату — `ALLOW`
для `visual-workspace`. Перед каждым использованием перечитывать capabilities.

Для следующих версий предусмотрен typed метод
`client.github.append_visual_revision(...)`. В исходниках Fortis Approvals
уже есть `prepare_visual_revision(...)`, `append_visual_revision(...)`,
строгий контракт, adapter, runtime policy `ASK` и offline-тесты. Но метод
**не объявлен в live Gateway capabilities** на 2026-11-17. До его активации
не вызывать его и не считать same-Issue revision работающей. Полный контракт
и handoff активации — в [Handoff 01](../handoffs/01-activate-append-visual-revision.md).

Будущий вызов v2+ имеет такой shape (пример для понимания контракта, не
инструкция вызывать его до live activation):

```python
import uuid
from fortis_approvals.workflow.client import default_client

c = default_client()
preview = c.github.prepare_visual_revision(
    repository='visual-workspace',
    issue_number=5,
    base_run_id='northlight-beacon-e2e-v3-20261117',
    asset_id='northlight-beacon-2d',
    revision=2,
    run_id='northlight-beacon-v2-<unique-run-suffix>',
    source_sha='<full-40-character-source-commit>',
    description='Owner-requested visual corrections',
    media=[{'path': '/workspace/repo/Workfiles/<run-id>/preview.png',
            'name': 'Northlight Beacon v2'}],
    qa_summary='QA findings and inspected evidence',
    duration_seconds=120,
)
request_id = str(uuid.uuid4())  # Persist this exact ID before submitting.
reply = c.github.append_visual_revision(
    repository='visual-workspace', issue_number=5,
    base_run_id='northlight-beacon-e2e-v3-20261117',
    asset_id='northlight-beacon-2d', revision=2,
    run_id='northlight-beacon-v2-<unique-run-suffix>',
    source_sha='<full-40-character-source-commit>',
    description='Owner-requested visual corrections',
    media=[{'path': '/workspace/repo/Workfiles/<run-id>/preview.png',
            'name': 'Northlight Beacon v2'}],
    qa_summary='QA findings and inspected evidence', duration_seconds=120,
    request_id=request_id, reason='Show owner the requested v2 revision',
    expected_payload_sha256=preview['payloadSha256'],
)
# PENDING => wait for owner ASK. Never submit a new UUID after an unknown outcome.
```

The revision action performs a GitHub Issue **comment creation** with a stable
revision marker and uploaded PNG references. It does not create a second Issue,
edit the Issue body, replace v1, or delete earlier comments. Its source contract
requires the exact open private ordinary Issue created by the same Gateway,
original `baseRunId`/durable reservation, same `assetId`, next revision number,
unique `runId`, full source Git SHA and 1–5 valid PNGs. The revision policy is
`ASK` for `visual-workspace` and `DENY` elsewhere; it never inherits v1's
`ALLOW`. A lost POST response / `UNCERTAIN` requires read-only investigation
of the same request and durable evidence; never blind-replay or advance to v3.

### Verified implementation snapshot — 2026-11-17

- Live `default_client().capabilities(refresh=True)` advertises
  `publish_visual_review` under `allowGitHub`, `visualReview.publishPolicy=ALLOW`,
  and the typed Issue reads `list_issues`, `get_issue`, `list_issue_comments`.
  It does **not** advertise `append_visual_revision` under `askGitHub`.
- Live Issue [#5 — Northlight Beacon v1](https://github.com/AlexPastukhh/visual-workspace/issues/5)
  is open and its readback contains one PNG attachment reference and zero
  comments. Its run marker is `northlight-beacon-e2e-v3-20261117`; a run marker
  identifies a publication run, **not** the human-facing revision number.
- Fortis Approvals source already contains the typed prepare/append methods,
  strict contract, adapter and ASK policy. The focused offline suite
  `test_visual_revisions.py` passes 9/9 on the inspected source checkout.
  These source tests are not a live Gateway test and do not activate the image.
- Therefore v1 publication/readback has a positive live E2E; v2 same-Issue
  comment delivery has **not** yet passed live E2E. Do not claim the full
  versioned workflow is production-ready until that test passes.

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
[Append visual revision source contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/integrations/github/README.md#append-visual-revision-to-an-existing-issue--source-candidate-not-live) ·
[UC-GW-003 — typed operation](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/integrations.md#uc-gw-003) ·
[UC-GW-005 — owner-managed release](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/releases.md#uc-gw-005) ·
[UC-GW-009 — unknown outcome](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009) ·
[UC-CONT-002/003 (Git/PR/Gateway)](https://github.com/AlexPastukhh/fortis-container/blob/main/docs/use-cases/delivery.md#uc-cont-002) ·
[UC-CONT-005 (Mirror Windows)](https://github.com/AlexPastukhh/fortis-container/blob/main/docs/use-cases/delivery.md#uc-cont-005).
