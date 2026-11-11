extends Node3D

const GLB_SCENE: PackedScene = preload("res://assets/3d/gamebot_animated.glb")

var actor: CharacterBody3D
var model: Node3D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var playback: AnimationNodeStateMachinePlayback
var status: Label
var elapsed := 0.0
var current_state := ""
var seen_states: Dictionary = {}
var seen_tree_nodes: Dictionary = {}
var seen_clip_playback: Dictionary = {}
var seen_loop_cycles: Dictionary = {}
var last_tree_node := ""
var last_loop_node := ""
var last_loop_position := -1.0
var auto_demo := true
var test_mode := false
var capture_mode := false
var capture_started := false
var jump_started := false
var is_jumping := false

func _ready() -> void:
    test_mode = "--test" in OS.get_cmdline_user_args()
    capture_mode = "--capture" in OS.get_cmdline_user_args()
    _configure_input()
    _build_world()
    await _build_actor()
    _build_hud()
    print("3D_DEMO_READY | GLB loaded | AnimationTree active")
    print("3D_ANIMATIONS:", animation_player.get_animation_list())

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
    var environment_node := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color(0.035, 0.065, 0.095)
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color(0.48, 0.62, 0.72)
    environment.ambient_light_energy = 0.65
    environment_node.environment = environment
    add_child(environment_node)

    var floor := StaticBody3D.new()
    floor.name = "GameFloor"
    var floor_mesh := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(30, 30)
    floor_mesh.mesh = plane
    var floor_mat := StandardMaterial3D.new()
    floor_mat.albedo_color = Color(0.10, 0.19, 0.22)
    floor_mat.roughness = 0.86
    floor_mesh.material_override = floor_mat
    floor.add_child(floor_mesh)
    var floor_collision := CollisionShape3D.new()
    var plane_shape := WorldBoundaryShape3D.new()
    floor_collision.shape = plane_shape
    floor.add_child(floor_collision)
    add_child(floor)

    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-48, -28, 0)
    light.light_energy = 1.45
    light.shadow_enabled = true
    add_child(light)

    var camera := Camera3D.new()
    camera.position = Vector3(3.4, 2.65, 6.4)
    camera.current = true
    camera.fov = 42.0
    add_child(camera)
    camera.look_at(Vector3(0, 1.1, 0), Vector3.UP)

func _build_actor() -> void:
    actor = CharacterBody3D.new()
    actor.name = "PlayerCharacter"
    actor.position = Vector3(0, 0.04, 0)
    var collider := CollisionShape3D.new()
    var capsule := CapsuleShape3D.new()
    capsule.radius = 0.38
    capsule.height = 2.42
    collider.shape = capsule
    collider.position = Vector3(0, 1.20, 0)
    actor.add_child(collider)
    add_child(actor)

    model = GLB_SCENE.instantiate() as Node3D
    if model == null:
        push_error("GLB_SCENE_GENERATION_FAILED")
        get_tree().quit(2)
        return
    model.name = "GameBot"
    actor.add_child(model)
    animation_player = _find_animation_player(model)
    if animation_player == null:
        push_error("GLB_HAS_NO_ANIMATION_PLAYER")
        get_tree().quit(2)
        return
    var required := ["Idle", "Walk", "Run", "Jump"]
    for clip in required:
        if not animation_player.has_animation(clip):
            push_error("MISSING_ANIMATION: " + clip)
            get_tree().quit(2)
            return
    if not _configure_animation_loop_modes():
        get_tree().quit(2)
        return
    await _create_animation_tree()
    print("3D_IMPORT_OK | mesh + skeleton + 4 animation clips")

func _find_animation_player(node: Node) -> AnimationPlayer:
    if node is AnimationPlayer:
        return node
    for child in node.get_children():
        var found := _find_animation_player(child)
        if found != null:
            return found
    return null

# GLB does not carry Godot's loop mode; configure the imported clips before building the AnimationTree.
func _configure_animation_loop_modes() -> bool:
    var expected_modes := {
        "Idle": Animation.LOOP_LINEAR,
        "Walk": Animation.LOOP_LINEAR,
        "Run": Animation.LOOP_LINEAR,
        "Jump": Animation.LOOP_NONE
    }
    for clip_name in expected_modes.keys():
        var clip: Animation = animation_player.get_animation(clip_name)
        if clip == null:
            push_error("ANIMATION_LOOP_CONFIG_MISSING_CLIP: " + str(clip_name))
            return false
        clip.loop_mode = int(expected_modes[clip_name])
        if clip.loop_mode != int(expected_modes[clip_name]):
            push_error("ANIMATION_LOOP_CONFIG_FAILED: " + str(clip_name))
            return false
    print("3D_LOOP_MODES_OK | Idle=linear | Walk=linear | Run=linear | Jump=one-shot")
    return true

func _create_animation_tree() -> void:
    var state_machine := AnimationNodeStateMachine.new()
    for clip in ["Idle", "Walk", "Run", "Jump"]:
        var animation_node := AnimationNodeAnimation.new()
        animation_node.animation = clip
        state_machine.add_node(clip, animation_node)
    var names := ["Idle", "Walk", "Run", "Jump"]
    for from_state in names:
        for to_state in names:
            if from_state == to_state:
                continue
            var transition := AnimationNodeStateMachineTransition.new()
            transition.xfade_time = 0.16
            transition.switch_mode = AnimationNodeStateMachineTransition.SWITCH_MODE_IMMEDIATE
            state_machine.add_transition(from_state, to_state, transition)
    animation_tree = AnimationTree.new()
    animation_tree.name = "AnimationTree"
    animation_tree.tree_root = state_machine
    animation_tree.anim_player = NodePath("../AnimationPlayer")
    animation_tree.root_node = NodePath("..")
    model.add_child(animation_tree)
    animation_tree.active = true
    await get_tree().process_frame
    playback = animation_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
    print("ANIMATION_TREE_READY | state machine playback available")
    if playback == null:
        push_error("ANIMATION_TREE_PLAYBACK_MISSING")
        get_tree().quit(2)
        return
    playback.start("Idle")

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    status = Label.new()
    status.position = Vector2(26, 22)
    status.add_theme_font_size_override("font_size", 20)
    status.text = "3D GAME ANIMATION  |  Idle / Walk / Run / Jump"
    layer.add_child(status)
    var hint := Label.new()
    hint.position = Vector2(26, 54)
    hint.add_theme_font_size_override("font_size", 14)
    hint.text = "A/D or ←/→ move  ·  Space jump  ·  Shift run  ·  R toggle auto demo"
    layer.add_child(hint)

func _physics_process(delta: float) -> void:
    if playback == null or status == null:
        return
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
            speed = 1.0
        elif phase < 8.0:
            next_state = "run"
            direction = 1.0
            speed = 2.0
        elif phase < 10.0:
            next_state = "jump"
            direction = 0.45
            speed = 0.8
            want_jump = not jump_started
            jump_started = true
        else:
            next_state = "idle"
            jump_started = false
    else:
        direction = Input.get_axis("move_left", "move_right")
        var is_running := Input.is_action_pressed("run")
        speed = 2.0 if is_running else 1.0
        if direction != 0.0:
            next_state = "run" if is_running else "walk"
        if Input.is_action_just_pressed("jump"):
            want_jump = true
            next_state = "jump"

    if Input.is_action_just_pressed("toggle_demo"):
        auto_demo = not auto_demo
        jump_started = false

    actor.velocity.x = direction * speed
    actor.velocity.z = 0.0
    if not actor.is_on_floor():
        actor.velocity.y -= 9.8 * delta
    elif want_jump:
        actor.velocity.y = 5.0
        is_jumping = true
    elif not is_jumping:
        actor.velocity.y = 0.0
    actor.move_and_slide()
    if is_jumping:
        if actor.is_on_floor() and not want_jump:
            is_jumping = false
        else:
            next_state = "jump"
    _set_state(next_state)
    if auto_demo and actor.position.x > 2.7:
        actor.position.x = -2.7
    status.text = "3D GAME ANIMATION  |  %s  |  %s" % [current_state.to_upper(), "AUTO" if auto_demo else "MANUAL"]

func _set_state(state: String) -> void:
    if state == current_state:
        return
    current_state = state
    seen_states[state] = true
    var clip := state.capitalize()
    playback.travel(clip)
    print("3D_STATE_REQUEST:", state)

func _process(_delta: float) -> void:
    if playback != null:
        var active_node := playback.get_current_node()
        if active_node != "" and active_node != last_tree_node:
            last_tree_node = active_node
            seen_tree_nodes[active_node.to_lower()] = true
            print("3D_TREE_NODE:", active_node)
        var current_position := playback.get_current_play_position()
        if active_node in ["Idle", "Walk", "Run", "Jump"] and current_position > 0.02:
            seen_clip_playback[active_node.to_lower()] = true
        if active_node != last_loop_node:
            last_loop_node = active_node
            last_loop_position = current_position
        elif active_node in ["Idle", "Walk", "Run"]:
            var active_clip: Animation = animation_player.get_animation(active_node)
            if active_clip != null and last_loop_position > active_clip.length * 0.75 and current_position < active_clip.length * 0.25:
                seen_loop_cycles[active_node.to_lower()] = true
            last_loop_position = current_position
    if capture_mode and not capture_started and elapsed > 2.6:
        capture_started = true
        _capture_preview()
    if test_mode:
        var required := ["idle", "walk", "run", "jump"]
        var missing_requests := required.filter(func(s): return not seen_states.has(s))
        var missing_playback := required.filter(func(s): return not seen_tree_nodes.has(s))
        var missing_clips := required.filter(func(s): return not seen_clip_playback.has(s))
        var required_loops := ["idle", "walk", "run"]
        var missing_loops := required_loops.filter(func(s): return not seen_loop_cycles.has(s))
        if missing_requests.is_empty() and missing_playback.is_empty() and missing_clips.is_empty() and missing_loops.is_empty():
            print("3D_TEST_PASS | requested=", seen_states.keys(), " | reached AnimationTree nodes=", seen_tree_nodes.keys(), " | clips advanced=", seen_clip_playback.keys(), " | loop cycles=", seen_loop_cycles.keys())
            get_tree().quit(0)
        elif elapsed > 15.0:
            push_error("3D_TEST_FAIL | missing requests=%s | missing AnimationTree nodes=%s | clips not advanced=%s | loop cycles not observed=%s" % [str(missing_requests), str(missing_playback), str(missing_clips), str(missing_loops)])
            get_tree().quit(1)

func _capture_preview() -> void:
    await RenderingServer.frame_post_draw
    var image := get_viewport().get_texture().get_image()
    var path := ProjectSettings.globalize_path("res://previews/godot_3d_preview.png")
    var error := image.save_png(path)
    print("3D_GODOT_CAPTURE:", path, " size=", image.get_size(), " error=", error)
    get_tree().quit(0 if error == OK else 2)
