extends SceneTree
var failures := 0

func _initialize() -> void:
    call_deferred("_run")

func check(condition: bool, label: String) -> void:
    if condition:
        print("PASS | ", label)
    else:
        failures += 1
        push_error("FAIL | " + label)

func _run() -> void:
    Engine.time_scale = 0.0
    var car_scene = load("res://scenes/car_jump_turn_reverse.tscn").instantiate()
    root.add_child(car_scene)
    await process_frame
    for t in [1.0, 5.0]:
        car_scene.qa_set_time(t - 1.0 / 24.0)
        var car: Node3D = car_scene.get_node("Car")
        var wheel: Node3D = car.find_child("Wheel_LF", true, false)
        var previous_position := car.global_position
        var previous_roll := wheel.rotation.x
        car_scene.qa_set_time(t)
        var front: Node3D = car.find_child("FrontBumper", true, false)
        var rear: Node3D = car.find_child("RearBumper", true, false)
        var visible_forward := (front.global_position - rear.global_position).normalized()
        var velocity := (car.global_position - previous_position) * 24.0
        check(visible_forward.dot(velocity.normalized()) * (1.0 if t < 2 else -1.0) > 0.99,
              "visible car nose matches forward/reverse intent at " + str(t))
        var world_roll := wheel.global_transform.basis.x.normalized() * (wheel.rotation.x - previous_roll)
        check(world_roll.x > 0, "wheel rotation agrees with world +Z travel at " + str(t))
    car_scene.free()

    var stage = load("res://assets/pulse-beacon-2d/preview.tscn").instantiate()
    root.add_child(stage)
    await process_frame
    var content = stage.get_node("Subject/Content")
    var beacon: Node2D = content.get_node("Beacon")
    stage.qa_set_time(0.0)
    var first := beacon.position
    stage.qa_set_time(1.0)
    check(beacon.position.distance_to(first) > 200, "shared 2D stage actually samples clip")
    stage.qa_set_time(2.0)
    check(beacon.position.distance_to(first) < 0.01, "loop clip returns to first pose")
    var player: AnimationPlayer = content.get_node("AnimationPlayer")
    check(player.get_animation("Pulse").loop_mode == Animation.LOOP_LINEAR, "source loop preserved")
    var once := player.get_animation("Pulse").duplicate() as Animation
    once.loop_mode = Animation.LOOP_NONE
    player.get_animation_library("").add_animation("Once", once)
    stage.sampler.clips.assign(["Once"])
    stage.qa_set_time(1.0)
    var middle := beacon.position
    stage.qa_set_time(3.0)
    check(beacon.position.distance_to(first) < 0.01 and beacon.position.distance_to(middle) > 200,
          "one-shot holds final pose beyond clip duration")
    check(once.loop_mode == Animation.LOOP_NONE, "one-shot loop policy not repaired by sampler")
    var mirrored := once.duplicate() as Animation
    mirrored.loop_mode = Animation.LOOP_PINGPONG
    player.get_animation_library("").add_animation("PingPong", mirrored)
    stage.sampler.clips.assign(["PingPong"])
    stage.qa_set_time(1.0)
    middle = beacon.position
    stage.qa_set_time(3.0)
    check(beacon.position.distance_to(middle) < 0.01, "ping-pong policy reverses second traversal")
    stage.free()

    stage = load("res://qa/stage_2d.gd").new()
    stage.texture = load("res://assets/planes-dual-pass/source/upper-plane.svg")
    root.add_child(stage)
    await process_frame
    stage.qa_set_time(5.0)
    check(stage.get_node("Subject/Content") is Sprite2D, "shared 2D stage accepts a static texture")
    stage.free()

    stage = load("res://qa/stage_3d.gd").new()
    stage.content_scene = load("res://assets/rotor-beacon-3d/source/beacon.tscn")
    root.add_child(stage)
    await process_frame
    stage.qa_set_time(5.0)
    check(is_zero_approx(stage.get_node("Subject/Content/Rotor").rotation.y), "3D stage accepts static content without requested clips")
    stage.free()

    stage = load("res://assets/rotor-beacon-3d/preview.tscn").instantiate()
    root.add_child(stage)
    await process_frame
    var rotor: Node3D = stage.get_node("Subject/Content/Rotor")
    stage.qa_set_time(0.0)
    var start := rotor.rotation.y
    stage.qa_set_time(0.5)
    check(absf(rotor.rotation.y - start) > 1.0, "shared 3D stage actually samples clip")
    check(stage.camera.global_position.distance_to(stage.subject.global_position) > 3,
          "neutral 3D stage provides camera and environment")
    Engine.time_scale = 1.0
    stage.qa_reset()
    await create_timer(0.25).timeout
    check(absf(rotor.rotation.y) > 0.2, "neutral preview animates during normal runtime")
    Engine.time_scale = 0.0
    stage.free()
    print("RUNTIME_READINESS_", "PASS" if failures == 0 else "FAIL", " | failures=", failures)
    quit(0 if failures == 0 else 1)
