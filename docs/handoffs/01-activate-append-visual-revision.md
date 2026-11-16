# Handoff 01 — довести append visual revision до LIVE

**Для отдельного чистого чата.** Задача выполняется в репозитории
`fortis-approvals`, а не в `visual-workspace`.

## Цель

Сделать доступным через Fortis Repo/Gateway безопасный typed метод
`client.github.append_visual_revision(...)`, который добавляет новую
PNG-ревизию комментарием в существующий Fortis-created GitHub Issue.
Целевая модель Visual Workspace: один Issue на логический ассет/заказ,
v1 создаёт Issue, v2+ добавляются комментариями в тот же Issue; отдельный
Source PR нужен только после принятия результата владельцем.

## Важное исходное состояние — не дублируй работу

На 2026-11-17 в Fortis Approvals main уже были обнаружены:

- `GitHubClient.prepare_visual_revision()` и
  `GitHubClient.append_visual_revision()` в
  `fortis_approvals/integrations/github/repo_client/client.py`;
- строгий contract в `integrations/github/contract.py`;
- native adapter / durable revision reservations в
  `workflow/adapters.py`;
- runtime ASK policy для `visual-workspace` и capability projection в
  `workflow/runtime.py` / `workflow/ingress.py`;
- отдельный `tests/test_visual_revisions.py`: 9/9 offline tests PASS.

Проверенный тогда source HEAD:
`bdb3ec581db7157b05f5d6c5282c7d3a7b6d0a35`.
Это только baseline: обязательно перечитай актуальный main и live Gateway.
## Bootstrap — обязательно прочитай

1. `/workspace/repo/README.md` — общие правила Fortis.
2. `/workspace/repo/Repos/fortis-approvals/README.md` и `AGENTS.md`.
3. `docs/use-cases/README.md`.
4. UC-GW-003: `docs/use-cases/integrations.md`.
5. UC-GW-005: `docs/use-cases/releases.md`.
6. UC-GW-009: `docs/use-cases/incidents.md`.
7. `fortis_approvals/integrations/github/README.md`, раздел
   **Append visual revision to an existing Issue**.
8. `fortis_approvals/tests/test_visual_revisions.py` и связанный
   contract, adapter, runtime, ingress, transport и Repo client.

Проверь чистоту main, точный HEAD, актуальные PR/CI и live capabilities
через `default_client().capabilities(refresh=True)`. На baseline
2026-11-17 live Gateway объявлял `publish_visual_review` в
`allowGitHub`, но **не** объявлял `append_visual_revision` в
`askGitHub`. Не считать локальный source методом, доступным в production.

## Твоя работа

1. Аудитируй весь существующий candidate end-to-end. Сначала выясни,
   что именно не хватает: client surface, Gateway ingress/allowlist,
   Core policy, adapter, route allowlist, durable state, image build
   inputs или release. Не создавай второй метод/контракт, если текущий
   уже покрывает требование.
2. Убедись, что внешний typed call доступен как
   `default_client().github.append_visual_revision(...)` и что
   `prepare_visual_revision(...)` остаётся чистым локальным preview,
   который ничего не stage-ит и не пишет в GitHub.
3. Сохрани узкую семантику: v2+ — **POST comment** к исходному Issue,
   не создание нового Issue, не редактирование Issue body и не замена
   старых вложений. Target — только `visual-workspace`.
4. Сохрани строгие preconditions: open private ordinary Issue, созданный
   тем же Gateway; исходный run marker и durable reservation; exact
   `issueNumber`, `baseRunId`, `assetId`, следующая `revision >= 2`,
   уникальный `runId`, полный source Git SHA, 1–5 PNG.
5. Revision write требует отдельный owner ASK/WebAuthn. Никогда
   не наследовать v1 `publish_visual_review=ALLOW`; другие репозитории
   должны получать DENY. Unknown fields, чужой Issue/PR, wrong asset,
   неправильный base run, повтор revision/run и stale/missing prior
   comment должны fail closed до нового эффекта.
6. **Не включай append в общий automatic-retry путь.** GitHub comment POST
   может пройти upstream, даже если ответ потерян. Сохраняй one-shot
   requestId и durable reservation. При timeout/`UNCERTAIN` — только
   read-only investigation исходного UUID и durable evidence; никаких
   новых UUID, слепого replay или перехода к v3.
7. Проверь точные GitHub REST routes/methods: разрешить только нужный
   upload и `POST /repos/{owner}/{repo}/issues/{issue_number}/comments`,
   плюс точный readback comment. Запретить DELETE/PATCH и произвольный
   issue/comment URL. Attachment readback по Markdown URL не является
   byte-level proof.
8. Добавь недостающие unit/negative/adapter/ingress/client tests.
   Существующий `test_visual_revisions.py` — baseline, а не достаточная
   гарантия полного live пути. Проверить совместимость старого
   `publish_visual_review`, Issue READ и других GitHub actions.
9. Выполни обязательные source manifest checks, профильные тесты,
   `scripts/test-source.sh` и exact-HEAD CI согласно UC-GW-003.
   Изменения — в отдельной task-ветке и PR через Fortis Gateway.
10. После owner merge синхронизируй source через штатный Gateway.
    Если затронуты server/image-baked файлы, пройди UC-GW-005:
    owner-managed Build/Apply, backup/promote, rollback readiness и live
    readback. Не меняй контейнер вручную, не копируй secrets/volumes,
    не запускай прямой Docker deploy и не используй PAT/gh/REST из чата.
11. После релиза перечитай live capabilities. Требуемое доказательство:
    `append_visual_revision` присутствует в `askGitHub` именно для
    `visual-workspace`; generic targets остаются DENY; v1 publisher и
    Issue reads продолжают работать. Сверь policy, live identity и
    активный image/build SHA, а не только source HEAD.

## Не делай в этом handoff

- Не публикуй v2/v3 и не создавай тестовый Issue: это E2E второго handoff.
- Не меняй Visual Workspace production briefs, artwork или practical fixtures.
- Не обещай video/GIF/GLB/BLEND uploads: этот метод PNG-only.
- Не превращай добавление revision в общий GitHub comments API.
- Не считай source merge, CI или наличие Python метода live activation.

## Критерии завершения

Отчёт должен отдельно подтвердить:

- source PR URL/merge SHA и CI exact-head result;
- какие source gaps были и какие файлы изменены;
- результаты positive и negative tests;
- точный активный Gateway image/build identity и owner release evidence;
- live capabilities, включая ASK scope;
- успешный typed client preview call (без side effect);
- что **live v2 E2E ещё не выполнялся** — не заявляй его PASS.

Если live release/approval недоступен, остановись на последнем доказанном
этапе и явно передай блокер. Следующий чат (Handoff 02) начнёт работу
только после live capability verification.
