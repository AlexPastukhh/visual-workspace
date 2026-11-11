extends Node3D

const MODEL_SCENE: PackedScene = preload("res://assets/3d/gamebot_animated.glb")
const DURATION_SECONDS := 8.0
const JUMP_CLIP_LENGTH := 1.0416667

var actor: Node3D
var model: Node3D
var animation_player: AnimationPlayer
var animation_tree: AnimationTree
var playback: AnimationNodeStateMachinePlayback
var camera: Camera3D
var current_clip := ""

func _ready() -> void:
    _build_world()
    _build_actor()
    qa_reset()

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

    var floor := MeshInstance3D.new()
    floor.name = "Ground"
    var plane := PlaneMesh.new()
    plane.size = Vector2(40.0, 40.0)
    floor.mesh = plane
    var material := StandardMaterial3D.new()
    material.albedo_color = Color(0.10, 0.19, 0.22)
    material.roughness = 0.86
    floor.material_override = material
    add_child(floor)

    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-48.0, -28.0, 0.0)
    light.light_energy = 1.45
    light.shadow_enabled = true
    add_child(light)

    camera = Camera3D.new()
    camera.name = "ReviewCamera"
    camera.fov = 42.0
    add_child(camera)

func _build_actor() -> void:
    actor = Node3D.new()
    actor.name = "Character"
    actor.rotation.y = PI / 2.0
    add_child(actor)

    model = MODEL_SCENE.instantiate() as Node3D
    if model == null:
        push_error("QA_CHARACTER_MODEL_LOAD_FAILED")
        return
    model.name = "gamebot_animated"
    actor.add_child(model)
    animation_player = _find_animation_player(model)
    if animation_player == null:
        push_error("QA_CHARACTER_ANIMATION_PLAYER_MISSING")
        return
    for clip_name in ["Idle", "Walk", "Run", "Jump"]:
        if not animation_player.has_animation(clip_name):
            push_error("QA_CHARACTER_CLIP_MISSING: " + clip_name)
            return
        var clip: Animation = animation_player.get_animation(clip_name)
        clip.loop_mode = Animation.LOOP_NONE if clip_name == "Jump" else Animation.LOOP_LINEAR

    var state_machine := AnimationNodeStateMachine.new()
    var state_names := ["Idle", "Walk", "Run", "Jump"]
    for index in range(state_names.size()):
        var animation_node := AnimationNodeAnimation.new()
        animation_node.animation = state_names[index]
        state_machine.add_node(state_names[index], animation_node, Vector2(float(index) * 180.0, 0.0))
    animation_tree = AnimationTree.new()
    animation_tree.name = "AnimationTree"
    animation_tree.anim_player = NodePath("../gamebot_animated/AnimationPlayer")
    animation_tree.tree_root = state_machine
    actor.add_child(animation_tree)
    animation_tree.active = true
    playback = animation_tree.get("parameters/playback") as AnimationNodeStateMachinePlayback
    if playback == null:
        push_error("QA_CHARACTER_STATE_MACHINE_PLAYBACK_MISSING")

func _find_animation_player(node: Node) -> AnimationPlayer:
    if node is AnimationPlayer:
        return node
    for child in node.get_children():
        var found := _find_animation_player(child)
        if found != null:
            return found
    return null

func qa_reset() -> void:
    current_clip = ""
    qa_set_time(0.0)

func qa_set_time(seconds: float) -> void:
    var t := clampf(seconds, 0.0, DURATION_SECONDS)
    var clip_name := "Idle"
    var clip_time := t
    var x := 0.0
    var y := 0.0

    if t < 2.0:
        clip_name = "Idle"
        clip_time = t
    elif t < 4.0:
        clip_name = "Walk"
        clip_time = t - 2.0
        x = (t - 2.0) * 0.6
    elif t < 6.0:
        clip_name = "Run"
        clip_time = t - 4.0
        x = 1.2 + (t - 4.0) * 1.2
    else:
        clip_name = "Jump"
        clip_time = t - 6.0
        x = 3.6 + clip_time * 0.25
        var jump_progress := clampf(clip_time / JUMP_CLIP_LENGTH, 0.0, 1.0)
        y = 1.25 * sin(PI * jump_progress)

    actor.position = Vector3(x, y, 0.0)
    _seek_clip(clip_name, clip_time)
    _update_camera()

func _seek_clip(clip_name: String, requested_time: float) -> void:
    var clip: Animation = animation_player.get_animation(clip_name)
    var sample_time := requested_time
    if clip.loop_mode == Animation.LOOP_LINEAR:
        sample_time = fposmod(requested_time, clip.length)
    else:
        # Keep the one-shot state selected at its final pose for deterministic review.
        sample_time = clampf(requested_time, 0.0, maxf(0.0, clip.length - 0.0001))
    if animation_tree != null and playback != null:
        playback.start(clip_name, true)
        animation_tree.advance(0.0)
        animation_tree.advance(sample_time)
    else:
        if current_clip != clip_name:
            animation_player.play(clip_name)
            current_clip = clip_name
        animation_player.seek(sample_time, true)
        animation_player.advance(0.0)

func _update_camera() -> void:
    if camera == null or actor == null:
        return
    var target := actor.global_position + Vector3(0.0, 1.05, 0.0)
    camera.global_position = target + Vector3(3.4, 2.65, 6.4)
    camera.look_at(target, Vector3.UP)
