# visual-workspace — Use Cases

Локальный реестр для передачи **готовых визуальных результатов** владельцу.
Общие операции GitHub, Docker и инциденты определяет Fortis, не этот реестр.

| ID | Когда | Проверяемый результат | Статус |
| --- | --- | --- | --- |
| [UC-VIS-001](media-github-review.md#uc-vis-001) | Созданы изображения, рендер 3D, анимация или видео; требуется удобный просмотр в GitHub | Проверенная ссылка на GitHub Issue с превью и QA; для видео/3D — отдельная подтверждённая ссылка на *сам файл* либо явно отмеченный preview-only | PNG: реализован в Gateway, живой положительный E2E ещё не подтверждён; видео/3D: частично, см. [backlog](../BACKLOG-IMPROVEMENTS.md) |

**Границы ответственности:** создание/QA медиа — в проекте-источнике;
представление результата и критерии доставки — здесь; GitHub-эффекты,
credentials, ASK/receipt/UNCERTAIN — в Fortis Gateway.

Связанные источники: [Fortis GitHub PNG contract](https://github.com/AlexPastukhh/fortis-approvals/blob/main/fortis_approvals/integrations/github/README.md#visual-review-png-mvp), [UC-GW-009 — инциденты](https://github.com/AlexPastukhh/fortis-approvals/blob/main/docs/use-cases/incidents.md#uc-gw-009), [UC-CONT-003 — GitHub через Gateway](https://github.com/AlexPastukhh/fortis-container/blob/main/docs/use-cases/delivery.md#uc-cont-003).
