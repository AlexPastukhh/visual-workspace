# Fortis Game Animation Lab

Небольшой Godot-проект для проверки полного workflow создания игровых ассетов:
**создали ассет → сделали анимации → экспортировали → подключили в Godot → проверили в работающей сцене**.

Целевой движок: **Godot 4.7.2**.

Общий производственный процесс и правила визуальной приёмки: [Visual Workspace workflow](../../WORKFLOW.md).

## Что уже есть

### 2D pipeline
- tools/make_2d_assets.py рисует персонажа и восемь кадров: 2 Idle, 4 Walk, 2 Jump.
- assets/2d/robot_animation_source.ora — редактируемый OpenRaster-файл, кадры разнесены по слоям (открывается в Krita).
- assets/2d/robot_atlas.png — горизонтальный atlas 8 × 64 px.
- assets/2d/robot_atlas.json — координаты кадров и описание анимаций.
- Godot импортирует PNG штатным texture importer, собирает SpriteFrames из atlas и проигрывает их через AnimatedSprite2D.
- Run пока использует ускоренную последовательность Walk-кадров — это проверка state machine, не отдельный production run-cycle.

### 3D pipeline
- tools/make_3d_robot.py создаёт персонажа, armature и четыре Action в Blender.
- assets/3d/source/gamebot_rigged.blend — редактируемый Blender-исходник с ригом и Action.
- assets/3d/gamebot_animated.glb — экспорт для игрового движка: mesh, skin/skeleton и клипы Idle / Walk / Run / Jump.
- Godot импортирует GLB как PackedScene, создаёт AnimationPlayer и управляет клипами через AnimationTree / AnimationNodeStateMachinePlayback.

## Запуск

В Fortis Repo открой редактор командой из корня репозитория: `./tools/godot-xvfb.sh --editor --path projects/game-animation-mvp`. Затем запусти главную сцену и выбери в стартовом меню 2D или 3D стенд. Для автоматической проверки используй `./tools/run_tests.sh` из каталога этого проекта.

В обеих сценах:
- A / D или стрелки — движение;
- Space — прыжок;
- R — переключение автоматической демонстрации и ручного управления.

Автодемонстрация сама проходит Idle → Walk → Run → Jump.

## Повторная генерация ассетов

Из корня этого проекта:

~~~bash
./tools/build_assets.sh
# если Blender не в PATH:
BLENDER_BIN=/path/to/blender ./tools/build_assets.sh
~~~

Нужны Python 3 и Blender 5.2.x. Для тестов нужен Godot 4.7.2; путь к бинарнику можно передать через GODOT_BIN.

## Автоматические проверки

~~~bash
./tools/run_tests.sh
~~~

Проверка выполняет:
1. импорт PNG и GLB штатным Godot editor importer;
2. целостность PNG, atlas JSON и слоёв OpenRaster;
3. структуру GLB, наличие mesh/skin и четырёх анимационных клипов;
4. запуск 2D-сцены в Godot и проверку, что в каждом из четырёх состояний реально сменились как минимум два sprite frame;
5. запуск 3D-сцены в Godot и проверку, что все четыре узла AnimationTree реально достигнуты, все клипы продвинулись, а Idle / Walk / Run повторили как минимум один цикл. Контроллер явно задаёт им LOOP_LINEAR, а Jump — LOOP_NONE.

Эти тесты проверяют импорт, базовое воспроизведение и фактическое повторение 3D locomotion-клипов, но не оценивают визуальную плавность циклов, художественное качество, совпадение facing/velocity, скольжение ступней или качество переходов. Для более глубокой проверки используй отдельный Visual QA runner ниже. Game Animation Lab остаётся учебным испытательным примером, а не эталоном качества.

Логи сохраняются в `tests/results/` (каталог исключён из Git). Тесты используют `--headless`, поэтому для CI не нужен монитор.

## Visual QA: runtime capture и review package

Полный capture workflow запускается из каталога проекта:

~~~bash
python3 tools/visual_qa/run_visual_qa.py
~~~

Профиль съёмки: `tools/visual_qa/profile.json`. Можно указать отдельный профиль, папку результатов и timeout через `--profile`, `--output-dir` и `--timeout`. Каталог результатов должен быть новым; по умолчанию он создаётся в `.fortis-state/visual-qa/`.

Runner выполняет полный аудит всех состояний, но по умолчанию работает инкрементально: повторно использует только те кадры, метрики и contact sheets, чьи зависимости и контрольные суммы не изменились. Если изменён один клип, переснимается соответствующее состояние и зависимый переход; общие изменения сцены, рига, контроллера или настроек инвалидируют все затронутые состояния. Полный пакет всё равно содержит все 2D/3D состояния, а bundle verifier запускается при каждом прогоне.

Для принудительного чистого прогона без переиспользования результатов:

~~~bash
python3 tools/visual_qa/run_visual_qa.py --force-rebuild
~~~

--force-rebuild также повторно запускает structural/smoke tests. Отдельный --force-tests принудительно запускает только эти тесты. Локальный кэш состояний хранится в .fortis-state/visual-qa/state-cache/.

Стандартное покрытие не уменьшается: 123 кадра 2D, 96 кадров 3D perspective и 48 четырёхракурсных 3D composite PNG. Все временные данные, кэш и логи остаются в .fortis-state/ и не попадают в Git.

`findings.json` содержит детерминированные технические сигналы. Они не заменяют визуальный аудит GPT и не являются автоматическим художественным PASS/FAIL. Передавать изображения следует через Fortis Repo image reader пакетами, следуя `review_manifest.json` и `review_prompt.md`. Полная документация: [Visual QA README](tools/visual_qa/README.md).

Для локального запуска скрипты используют tools/godot.sh. Путь к исполняемому файлу Godot можно задать через переменную окружения GODOT_BIN.

## Previews

**2D — Godot AnimatedSprite2D**

![2D animation preview](previews/godot_2d_preview.png)

**3D — Godot AnimationTree**

![3D animation preview](previews/godot_3d_preview.png)

## Структура

~~~text
assets/
  2d/   # ORA source, individual frames, atlas, manifest
  3d/   # Blender source, animated GLB, render preview
scenes/ # menu, 2D demo, 3D demo
scripts/ # runtime controllers and state machines
tools/  # asset generators and launch/build scripts
tests/  # asset validation and test logs
previews/ # screenshots captured from the actual Godot scenes
~~~

## Границы MVP

Это технический стенд для проверки передачи ассетов и анимаций между инструментами, а не готовая игровая система. Пока нет root motion, IK, полноценного боевого контроллера, камеры с follow, ретаргетинга и production-grade locomotion blending. Следующий этап — менять тестовые ассеты на созданные художественные ассеты и повторять те же проверки без изменения runtime-контрактов.
