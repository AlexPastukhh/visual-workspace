extends Node2D

const ATLAS: Texture2D = preload("res://assets/2d/robot_atlas.png")
const FLOOR_Y := 610.0

var actor: CharacterBody2D
var sprite: AnimatedSprite2D
var status: Label
var elapsed := 0.0
var current_state := ""
var seen_states: Dictionary = {}
var seen_animation_frames: Dictionary = {}
var auto_demo := true
var test_mode := false
var capture_mode := false
var capture_started := false
var jump_started := false

func _ready() -> void:
    test_mode = "--test" in OS.get_cmdline_user_args()
    capture_mode = "--capture" in OS.get_cmdline_user_args()
    _configure_input()
    _build_world()
    _build_actor()
    _build_hud()
    print("2D_DEMO_READY | sprite atlas imported | AnimatedSprite2D created")

func _configure_input() -> void:
    _add_key_action("move_left", KEY_A)
    _add_key_action("move_left", KEY_LEFT)
    _add_key_action("move_right", KEY_D)
    _add_key_action("move_right", KEY_RIGHT)
    _add_key_action("jump", KEY_SPACE)
    _add_key_action("run", KEY_SHIFT)
    _add_key_action("toggle_demo", KEY_R)

func _add_key_action(action: String, keycode: Key) -> void:
    if not InputMap.has_action(action):
        InputMap.add_action(action)
    var event := InputEventKey.new()
    event.physical_keycode = keycode
    InputMap.action_add_event(action, event)

func _build_world() -> void:
    var bg := ColorRect.new()
    bg.color = Color(0.055, 0.105, 0.16)
    bg.position = Vector2.ZERO
    bg.size = Vector2(1280, 720)
    add_child(bg)
    for i in range(6):
        var hill := Polygon2D.new()
        var x := float(i) * 250.0 - 70.0
        hill.polygon = PackedVector2Array([
            Vector2(x, 550), Vector2(x + 100, 440 + (i % 2) * 45),
            Vector2(x + 230, 550), Vector2(x + 250, 620), Vector2(x - 10, 620)
        ])
        hill.color = Color(0.07 + float(i % 2) * 0.02, 0.17, 0.22)
        add_child(hill)
    var floor_visual := ColorRect.new()
    floor_visual.color = Color(0.10, 0.20, 0.22)
    floor_visual.position = Vector2(0, FLOOR_Y)
    floor_visual.size = Vector2(1280, 110)
    add_child(floor_visual)
    var floor := StaticBody2D.new()
    floor.position = Vector2(640, FLOOR_Y + 18)
    var floor_shape := CollisionShape2D.new()
    var rect := RectangleShape2D.new()
    rect.size = Vector2(1600, 36)
    floor_shape.shape = rect
    floor.add_child(floor_shape)
    add_child(floor)
    var platform := StaticBody2D.new()
    platform.position = Vector2(920, 510)
    var platform_shape := CollisionShape2D.new()
    var platform_rect := RectangleShape2D.new()
    platform_rect.size = Vector2(170, 22)
    platform_shape.shape = platform_rect
    platform.add_child(platform_shape)
    add_child(platform)
    var platform_visual := ColorRect.new()
    platform_visual.color = Color(0.25, 0.43, 0.43)
    platform_visual.position = Vector2(835, 499)
    platform_visual.size = Vector2(170, 22)
    add_child(platform_visual)

func _build_actor() -> void:
    actor = CharacterBody2D.new()
    actor.position = Vector2(300, FLOOR_Y - 22)
    actor.motion_mode = CharacterBody2D.MOTION_MODE_GROUNDED
    var collider := CollisionShape2D.new()
    var capsule := CapsuleShape2D.new()
    capsule.radius = 12.0
    capsule.height = 44.0
    collider.shape = capsule
    actor.add_child(collider)
    sprite = AnimatedSprite2D.new()
    sprite.sprite_frames = _make_sprite_frames()
    sprite.position = Vector2(0, -21)
    sprite.scale = Vector2(1.5, 1.5)
    sprite.play("idle")
    actor.add_child(sprite)
    add_child(actor)

func _make_sprite_frames() -> SpriteFrames:
    var result := SpriteFrames.new()
    result.remove_animation("default")
    _add_animation(result, "idle", [0, 1], 4.0, true)
    _add_animation(result, "walk", [2, 3, 4, 5], 10.0, true)
    _add_animation(result, "run", [2, 4], 15.0, true)
    _add_animation(result, "jump", [6, 7], 7.0, false)
    return result

func _add_animation(frames: SpriteFrames, name: String, indices: Array, fps: float, looping: bool) -> void:
    frames.add_animation(name)
    frames.set_animation_speed(name, fps)
    frames.set_animation_loop(name, looping)
    for index in indices:
        var atlas_frame := AtlasTexture.new()
        atlas_frame.atlas = ATLAS
        atlas_frame.region = Rect2(float(index) * 64.0, 0.0, 64.0, 64.0)
        frames.add_frame(name, atlas_frame)

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    status = Label.new()
    status.position = Vector2(26, 22)
    status.add_theme_font_size_override("font_size", 20)
    status.text = "2D GAME ANIMATION  |  Idle / Walk / Run / Jump"
    layer.add_child(status)
    var hint := Label.new()
    hint.position = Vector2(26, 54)
    hint.add_theme_font_size_override("font_size", 14)
    hint.text = "A/D or ←/→ move  ·  Space jump  ·  Shift run  ·  R toggle auto demo"
    layer.add_child(hint)

func _physics_process(delta: float) -> void:
    elapsed += delta
    var direction := 0.0
    var next_state := "idle"
    var speed := 0.0
    var want_jump := false
    if auto_demo:
        var phase := fmod(elapsed, 12.0)
        if phase < 2.0:
            next_state = "idle"
        elif phase < 5.0:
            next_state = "walk"
            direction = 1.0
            speed = 105.0
        elif phase < 8.0:
            next_state = "run"
            direction = 1.0
            speed = 185.0
        elif phase < 10.0:
            next_state = "jump"
            direction = 0.55
            speed = 100.0
            want_jump = not jump_started
            jump_started = true
        else:
            next_state = "idle"
            jump_started = false
    else:
        direction = Input.get_axis("move_left", "move_right")
        var is_running := Input.is_action_pressed("run")
        speed = 185.0 if is_running else 105.0
        if direction != 0.0:
            next_state = "run" if is_running else "walk"
        if Input.is_action_just_pressed("jump"):
            want_jump = true
            next_state = "jump"
    if Input.is_action_just_pressed("toggle_demo"):
        auto_demo = not auto_demo
        jump_started = false
    actor.velocity.x = direction * speed
    if not actor.is_on_floor():
        actor.velocity.y += 1100.0 * delta
    elif want_jump:
        actor.velocity.y = -430.0
    elif next_state != "jump":
        actor.velocity.y = 0.0
    actor.move_and_slide()
    if not actor.is_on_floor():
        next_state = "jump"
    elif next_state == "jump" and not auto_demo:
        next_state = "idle"
    if direction != 0.0:
        sprite.flip_h = direction < 0.0
    _set_state(next_state)
    if auto_demo and actor.position.x > 1120.0:
        actor.position.x = 150.0
    status.text = "2D GAME ANIMATION  |  %s  |  %s" % [current_state.to_upper(), "AUTO" if auto_demo else "MANUAL"]

func _set_state(state: String) -> void:
    if state == current_state:
        return
    current_state = state
    seen_states[state] = true
    sprite.play(state)
    print("2D_STATE:", state)

func _process(_delta: float) -> void:
    if sprite != null and current_state != "":
        var frames: Dictionary = seen_animation_frames.get(current_state, {})
        frames[sprite.frame] = true
        seen_animation_frames[current_state] = frames
    if capture_mode and not capture_started and elapsed > 2.2:
        capture_started = true
        _capture_preview()
    if test_mode:
        var required := ["idle", "walk", "run", "jump"]
        var missing_states := required.filter(func(s): return not seen_states.has(s))
        var static_animations := required.filter(func(s): return seen_animation_frames.get(s, {}).size() < 2)
        if missing_states.is_empty() and static_animations.is_empty():
            print("2D_TEST_PASS | states=", seen_states.keys(), " | animated frames=", seen_animation_frames)
            get_tree().quit(0)
        elif elapsed > 14.0:
            push_error("2D_TEST_FAIL | missing states=%s | animations with fewer than 2 frames=%s" % [str(missing_states), str(static_animations)])
            get_tree().quit(1)

func _capture_preview() -> void:
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    var path := ProjectSettings.globalize_path("res://previews/godot_2d_preview.png")
    var error := image.save_png(path)
    print("2D_GODOT_CAPTURE:", path, " size=", image.get_size(), " error=", error)
    get_tree().quit(0 if error == OK else 2)
