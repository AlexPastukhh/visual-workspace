extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    var profile_path := _option(args, "--profile", "res://tools/visual_qa/profile.json")
    var output_dir := _option(args, "--output-dir", "res://.fortis-state/visual-qa/2d")
    var profile := _load_profile(profile_path)
    if profile.is_empty():
        quit(2)
        return
    var config: Dictionary = profile.get("2d", {})
    var capture: Dictionary = profile.get("capture", {})
    var scene_path: String = profile.get("scenes", {}).get("2d", "")
    var duration := float(capture.get("duration_seconds", 12.0))
    var schedule := _build_schedule(
        capture.get("2d_segments", {}),
        capture.get("2d_samples_per_segment", {})
    )
    var selected_states := _selected_states(args)
    if selected_states.has("__invalid__"):
        push_error("INVALID_2D_QA_STATE_FILTER")
        quit(3)
        return
    if scene_path.is_empty() or duration <= 0.0 or schedule.is_empty():
        push_error("INVALID_2D_QA_PROFILE")
        quit(3)
        return
    var packed := load(scene_path) as PackedScene
    if packed == null:
        push_error("2D_SCENE_LOAD_FAILED: " + scene_path)
        quit(4)
        return
    var demo := packed.instantiate()
    root.add_child(demo)
    if not await _wait_for_demo(demo, config):
        push_error("2D_DEMO_INITIALIZATION_TIMEOUT")
        quit(5)
        return
    var actor := demo.get(config.get("actor_property", "actor")) as CharacterBody2D
    var sprite := demo.get(config.get("sprite_property", "sprite")) as AnimatedSprite2D
    var state_property: String = config.get("state_property", "current_state")
    var elapsed_property: String = config.get("elapsed_property", "elapsed")
    demo.set(elapsed_property, 0.0)
    demo.set(config.get("auto_demo_property", "auto_demo"), true)
    var absolute_output := _absolute(output_dir)
    DirAccess.make_dir_recursive_absolute(absolute_output)
    var start_elapsed := float(demo.get(elapsed_property))
    var samples: Array[Dictionary] = []
    for sample_index in range(schedule.size()):
        var schedule_item: Dictionary = schedule[sample_index]
        if not selected_states.is_empty() and not selected_states.has(str(schedule_item["state"]).to_lower()):
            continue
        var target_elapsed := start_elapsed + float(schedule_item["time"])
        while float(demo.get(elapsed_property)) + 0.000001 < target_elapsed:
            await physics_frame
        await RenderingServer.frame_post_draw
        paused = true
        var captured_elapsed := float(demo.get(elapsed_property))
        var expected_state := str(schedule_item["state"])
        var state_name := str(demo.get(state_property)).to_lower()
        if state_name.is_empty():
            state_name = str(sprite.animation).to_lower()
        var capture_state := expected_state.to_lower()
        var state_dir := absolute_output.path_join(capture_state)
        DirAccess.make_dir_recursive_absolute(state_dir)
        var filename := "%s_%04d.png" % [capture_state, sample_index]
        var image := demo.get_viewport().get_texture().get_image()
        var image_path := state_dir.path_join(filename)
        var image_error := image.save_png(image_path)
        if image_error != OK:
            paused = false
            push_error("2D_FRAME_SAVE_FAILED: " + image_path)
            quit(6)
            return
        samples.append({
            "sequence_index": sample_index,
            "timestamp_seconds": snapped(captured_elapsed - start_elapsed, 0.0001),
            "state": state_name,
            "expected_state": expected_state,
            "sprite_animation": str(sprite.animation),
            "sprite_frame": sprite.frame,
            "sprite_frame_count": sprite.sprite_frames.get_frame_count(sprite.animation),
            "sprite_animation_looping": sprite.sprite_frames.get_animation_loop(sprite.animation),
            "sprite_frame_progress": snapped(sprite.frame_progress, 0.0001),
            "sprite_is_playing": sprite.is_playing(),
            "actor_position": _vector(actor.global_position),
            "actor_velocity": _vector(actor.velocity),
            "actor_is_on_floor": actor.is_on_floor(),
            "image": image_path
        })
        paused = false
    var report := {
        "schema_version": 1,
        "scene": scene_path,
        "godot_version": Engine.get_version_info(),
        "duration_seconds": duration,
        "sampling_schedule": capture.get("2d_segments", {}),
        "sample_count": samples.size(),
        "captured_states": selected_states if not selected_states.is_empty() else ["idle", "walk", "run", "jump"],
        "samples": samples
    }
    var metrics_path := absolute_output.path_join("metrics.json")
    var file := FileAccess.open(metrics_path, FileAccess.WRITE)
    if file == null:
        push_error("2D_METRICS_OPEN_FAILED: " + metrics_path)
        quit(7)
        return
    file.store_string(JSON.stringify(report, "\t"))
    file.close()
    print("2D_QA_CAPTURE_COMPLETE | samples=", samples.size(), " | ", metrics_path)
    quit(0)
func _wait_for_demo(demo: Node, config: Dictionary) -> bool:
    var actor_property: String = config.get("actor_property", "actor")
    var sprite_property: String = config.get("sprite_property", "sprite")
    for _index in range(120):
        if demo.get(actor_property) != null and demo.get(sprite_property) != null:
            return true
        await process_frame
    return false

func _load_profile(path: String) -> Dictionary:
    var file := FileAccess.open(_absolute(path), FileAccess.READ)
    if file == null:
        push_error("QA_PROFILE_OPEN_FAILED: " + path)
        return {}
    var parsed: Variant = JSON.parse_string(file.get_as_text())
    file.close()
    if not parsed is Dictionary:
        push_error("QA_PROFILE_INVALID_JSON")
        return {}
    return parsed

func _selected_states(args: PackedStringArray) -> PackedStringArray:
    var value := _option(args, "--states", "")
    if value.is_empty():
        return PackedStringArray()
    var result := PackedStringArray()
    for item in value.split(","):
        var state := item.strip_edges().to_lower()
        if state not in ["idle", "walk", "run", "jump"]:
            return PackedStringArray(["__invalid__"])
        if not result.has(state):
            result.append(state)
    return result

func _option(args: PackedStringArray, key: String, fallback: String) -> String:
    for index in range(args.size() - 1):
        if args[index] == key:
            return args[index + 1]
    return fallback
func _absolute(path: String) -> String:
    return ProjectSettings.globalize_path(path) if path.begins_with("res://") else path

func _vector(value: Vector2) -> Array:
    return [snapped(value.x, 0.0001), snapped(value.y, 0.0001)]

func _build_schedule(segments: Dictionary, counts: Dictionary) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    for state_name in segments.keys():
        var intervals: Array = segments[state_name]
        var total_length := 0.0
        for interval in intervals:
            total_length += float(interval[1]) - float(interval[0])
        var count := int(counts.get(state_name, 24))
        if total_length <= 0.0 or count < 1:
            continue
        for sample_index in range(count):
            var remaining := (float(sample_index) + 0.5) * total_length / float(count)
            var target_time := 0.0
            for interval in intervals:
                var interval_length := float(interval[1]) - float(interval[0])
                if remaining < interval_length:
                    target_time = float(interval[0]) + remaining
                    break
                remaining -= interval_length
            result.append({"state": str(state_name), "time": target_time})
    result.sort_custom(func(a: Dictionary, b: Dictionary): return float(a["time"]) < float(b["time"]))
    return result
