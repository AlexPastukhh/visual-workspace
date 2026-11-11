extends Node3D

const CAR_SCENE: PackedScene = preload("res://assets/car-jump-turn-reverse/car.glb")

var elapsed := 0.0
var car: Node3D
var car_model: Node3D
var camera: Camera3D
var wheel_pivots: Array[Node3D] = []
var phase_label: Label

func _ready() -> void:
    _build_world()
    car = Node3D.new()
    car.name = "Car"
    add_child(car)
    car_model = CAR_SCENE.instantiate() as Node3D
    car_model.name = "CarModel"
    car.add_child(car_model)
    _find_wheels(car_model)
    _build_hud()
    qa_reset()

func _build_world() -> void:
    var world := WorldEnvironment.new()
    var environment := Environment.new()
    environment.background_mode = Environment.BG_COLOR
    environment.background_color = Color("#172c3b")
    environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
    environment.ambient_light_color = Color("#9ab6c4")
    environment.ambient_light_energy = 0.72
    world.environment = environment
    add_child(world)

    var ground := MeshInstance3D.new()
    ground.name = "Ground"
    var ground_mesh := PlaneMesh.new()
    ground_mesh.size = Vector2(100, 100)
    ground.mesh = ground_mesh
    var ground_material := StandardMaterial3D.new()
    ground_material.albedo_color = Color("#263c43")
    ground_material.roughness = 0.9
    ground.material_override = ground_material
    add_child(ground)

    _add_box("TestLane", Vector3(0, 0.025, 18), Vector3(10, 0.05, 70), Color("#344f58"))
    for x in [-4.2, 4.2]:
        _add_box("LaneEdge", Vector3(x, 0.06, 18), Vector3(0.10, 0.04, 70), Color("#d6e0d7"))
    for z in range(-12, 54, 6):
        _add_box("CentreDash", Vector3(0, 0.065, float(z)), Vector3(0.16, 0.035, 2.8), Color("#e6c77c"))

    var sun := DirectionalLight3D.new()
    sun.rotation_degrees = Vector3(-48, -28, 0)
    sun.light_energy = 1.55
    sun.shadow_enabled = true
    add_child(sun)

    camera = Camera3D.new()
    camera.name = "FollowCamera"
    camera.current = true
    camera.fov = 48.0
    add_child(camera)

func _add_box(node_name: String, position: Vector3, dimensions: Vector3, tint: Color) -> void:
    var mesh_instance := MeshInstance3D.new()
    mesh_instance.name = node_name
    var mesh := BoxMesh.new()
    mesh.size = dimensions
    mesh_instance.mesh = mesh
    var material := StandardMaterial3D.new()
    material.albedo_color = tint
    material.roughness = 0.82
    mesh_instance.material_override = material
    mesh_instance.position = position
    add_child(mesh_instance)

func _build_hud() -> void:
    var layer := CanvasLayer.new()
    add_child(layer)
    phase_label = Label.new()
    phase_label.position = Vector2(34, 28)
    phase_label.add_theme_font_size_override("font_size", 22)
    phase_label.add_theme_color_override("font_color", Color("#f2f6f4"))
    layer.add_child(phase_label)

func _find_wheels(node: Node) -> void:
    for wheel_name in ["Wheel_LF", "Wheel_RF", "Wheel_LR", "Wheel_RR"]:
        var wheel := node.find_child(wheel_name, true, false) as Node3D
        if wheel != null:
            wheel_pivots.append(wheel)

func qa_reset() -> void:
    qa_set_time(0.0)

func qa_set_time(seconds: float) -> void:
    elapsed = maxf(0.0, seconds)
    _update_motion()

func _physics_process(delta: float) -> void:
    elapsed += delta
    _update_motion()

func _process(_delta: float) -> void:
    if car == null or camera == null:
        return
    var target := car.global_position + Vector3(0.0, 0.72, 0.0)
    camera.global_position = car.global_position + Vector3(7.0, 5.2, -8.5)
    camera.look_at(target, Vector3.UP)

func _update_motion() -> void:
    if car == null:
        return
    var z_position := 0.0
    var y_position := 0.0
    var yaw := 0.0
    var pitch := 0.0
    var phase_name := "DRIVE FORWARD"
    var wheel_roll_distance := 0.0

    if elapsed < 2.0:
        z_position = elapsed * 4.4
        wheel_roll_distance = z_position
    elif elapsed < 2.875:
        phase_name = "JUMP"
        # Include a grounded landing sample at 2.8333s (24 FPS) before turning.
        var jump_progress := clampf((elapsed - 2.0) / (5.0 / 6.0), 0.0, 1.0)
        z_position = 8.8 + (elapsed - 2.0) * 4.4
        y_position = sin(jump_progress * PI) * 1.25
        pitch = -sin(jump_progress * PI) * 0.055
        wheel_roll_distance = z_position
    elif elapsed < 4.0:
        phase_name = "TURN 180"
        var turn_progress := smoothstep(0.0, 1.0, (elapsed - 2.875) / 1.125)
        z_position = 12.4666667
        yaw = lerpf(0.0, PI, turn_progress)
        wheel_roll_distance = 12.4666667
    else:
        phase_name = "REVERSE"
        z_position = 12.4666667 + (elapsed - 4.0) * 4.4
        yaw = PI
        wheel_roll_distance = 12.4666667 - (elapsed - 4.0) * 4.4

    car.position = Vector3(0.0, y_position, z_position)
    car.rotation = Vector3(pitch, yaw, 0.0)
    for wheel in wheel_pivots:
        wheel.rotation.x = wheel_roll_distance / 0.42
    if phase_label != null:
        phase_label.text = "VEHICLE MOTION TEST     /     " + phase_name
