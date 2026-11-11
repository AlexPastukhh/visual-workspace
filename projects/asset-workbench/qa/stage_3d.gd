extends Node3D
const ClipSampler = preload("res://qa/clip_sampler.gd")

@export var content_scene: PackedScene
@export var content_scale := Vector3.ONE
@export var clips: Array[String] = []
@export var animation_player_path: NodePath
@export var seconds_per_phase := 2.0
@export var camera_distance := 6.0
@export var target_offset := Vector3(0, 1, 0)
var sampler = ClipSampler.new()
var elapsed := 0.0
var subject: Node3D
var camera: Camera3D

func _ready() -> void:
    var world := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("#203040")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("#a8bdd0")
    environment.ambient_light_energy = 0.65
    world.environment = environment
    add_child(world)
    var floor_mesh := MeshInstance3D.new()
    var plane := PlaneMesh.new()
    plane.size = Vector2(40, 40)
    floor_mesh.mesh = plane
    var material := StandardMaterial3D.new()
    material.albedo_color = Color("#344653")
    material.roughness = 0.85
    floor_mesh.material_override = material
    add_child(floor_mesh)
    var light := DirectionalLight3D.new()
    light.rotation_degrees = Vector3(-45, -25, 0)
    light.light_energy = 1.3
    light.shadow_enabled = true
    add_child(light)
    camera = Camera3D.new()
    camera.current = true
    camera.fov = 42
    add_child(camera)
    subject = Node3D.new()
    subject.name = "Subject"
    subject.scale = content_scale
    add_child(subject)
    var content := content_scene.instantiate() as Node3D if content_scene != null else null
    if content == null:
        push_error("QA_STAGE: expected a 3D scene")
        get_tree().quit(10)
        return
    content.name = "Content"
    subject.add_child(content)
    sampler.configure(content, clips, animation_player_path, seconds_per_phase)
    qa_reset()

func qa_reset() -> void:
    qa_set_time(0.0)

func _process(delta: float) -> void:
    if delta > 0.0:
        qa_set_time(elapsed + delta)

func qa_set_time(seconds: float) -> void:
    elapsed = maxf(0.0, seconds)
    sampler.sample(elapsed)
    if subject != null and camera != null:
        var target := subject.global_position + target_offset
        camera.global_position = target + Vector3(0.65, 0.45, 1).normalized() * camera_distance
        camera.look_at(target, Vector3.UP)

func qa_current_clip() -> String:
    return str(sampler.player.assigned_animation) if sampler.player != null else ""
