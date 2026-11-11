extends SceneTree

var demo: Node3D
var actor: CharacterBody3D
var model: Node3D
var cameras: Dictionary = {}
var viewports: Dictionary = {}
var status: Label
var animation_player: AnimationPlayer
var playback: AnimationNodeStateMachinePlayback
var skeleton: Skeleton3D
var left_foot_index := -1
var right_foot_index := -1
var front_local_axis := Vector3(0.0, 0.0, 1.0)
var output_dir := ""
var elapsed_property := "elapsed"
var state_property := "current_state"

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    var profile_path := _option(args, "--profile", "res://tools/visual_qa/profile.json")
    output_dir = _absolute(_option(args, "--output-dir", "res://.fortis-state/visual-qa/3d"))
    var profile := _load_profile(profile_path)
    if profile.is_empty():
        quit(2)
        return
    var config: Dictionary = profile.get("3d", {})
    var capture: Dictionary = profile.get("capture", {})
    var scene_path: String = profile.get("scenes", {}).get("3d", "")
    var duration := float(capture.get("duration_seconds", 12.0))
    var schedule := _build_schedule(
        capture.get("3d_segments", {}),
        capture.get("3d_samples_per_segment", {}),
        int(capture.get("3d_multiview_samples_per_state", 3))
    )
    var selected_states := _selected_states(args)
    if selected_states.has("__invalid__"):
        push_error("INVALID_3D_QA_STATE_FILTER")
        quit(3)
        return
    if scene_path.is_empty() or duration <= 0.0 or schedule.is_empty():
        push_error("INVALID_3D_QA_PROFILE")
        quit(3)
        return
    elapsed_property = config.get("elapsed_property", "elapsed")
    state_property = config.get("state_property", "current_state")
    var axis_values: Array = config.get("front_local_axis", [0.0, 0.0, 1.0])
    front_local_axis = Vector3(axis_values[0], axis_values[1], axis_values[2]).normalized()
    var packed := load(scene_path) as PackedScene
    if packed == null:
        push_error("3D_SCENE_LOAD_FAILED: " + scene_path)
        quit(4)
        return
    demo = packed.instantiate() as Node3D
    root.add_child(demo)
    if not await _wait_for_demo(config):
        push_error("3D_DEMO_INITIALIZATION_TIMEOUT")
        quit(5)
        return
    actor = demo.get(config.get("actor_property", "actor")) as CharacterBody3D
    model = demo.get(config.get("model_property", "model")) as Node3D
    animation_player = demo.get(config.get("animation_player_property", "animation_player")) as AnimationPlayer
    playback = demo.get(config.get("playback_property", "playback")) as AnimationNodeStateMachinePlayback
    status = demo.get(config.get("status_property", "status")) as Label
    skeleton = _find_skeleton(model)
    if skeleton == null or playback == null or animation_player == null:
        push_error("3D_QA_REQUIRED_NODES_MISSING")
        quit(6)
        return
    var foot_bones: Array = config.get("foot_bones", ["Foot.L", "Foot.R"])
    left_foot_index = skeleton.find_bone(str(foot_bones[0]))
    right_foot_index = skeleton.find_bone(str(foot_bones[1]))
    if left_foot_index < 0 or right_foot_index < 0:
        push_error("3D_QA_FOOT_BONES_NOT_FOUND")
        quit(7)
        return
    _create_viewports()
    demo.set(elapsed_property, 0.0)
    demo.set("auto_demo", true)
    DirAccess.make_dir_recursive_absolute(output_dir)
    var start_elapsed := float(demo.get(elapsed_property))
    var samples: Array[Dictionary] = []
    var multiview_sample_count := 0
    for sample_index in range(schedule.size()):
        var schedule_item: Dictionary = schedule[sample_index]
        if not selected_states.is_empty() and not selected_states.has(str(schedule_item["state"]).to_lower()):
            continue
        var target_elapsed := start_elapsed + float(schedule_item["time"])
        while float(demo.get(elapsed_property)) + 0.000001 < target_elapsed:
            await physics_frame
        var record := _snapshot(sample_index, start_elapsed)
        record["expected_state"] = str(schedule_item["state"])
        var state_name := str(record["state"])
        if state_name not in ["idle", "walk", "run", "jump"]:
            state_name = str(record["animation_tree_node"]).to_lower()
        var capture_state := str(schedule_item["state"]).to_lower()
        var include_multiview := bool(schedule_item.get("multiview", false))
        var captures := await _capture_sample(state_name, include_multiview)
        record["animation_position_after_capture"] = captures.get("animation_position_after")
        record["animation_advanced_during_capture"] = bool(captures.get("animation_advanced"))
        var perspective: Image = captures.get("perspective")
        if perspective == null or perspective.is_empty():
            push_error("3D_PERSPECTIVE_CAPTURE_FAILED: " + state_name)
            paused = false
            quit(8)
            return
        var filename := "%s_%04d.png" % [capture_state, sample_index]
        var perspective_dir := output_dir.path_join("perspective").path_join(capture_state)
        DirAccess.make_dir_recursive_absolute(perspective_dir)
        var perspective_path := perspective_dir.path_join(filename)
        if perspective.save_png(perspective_path) != OK:
            push_error("3D_PERSPECTIVE_SAVE_FAILED: " + perspective_path)
            quit(9)
            return
        record["image"] = perspective_path
        record["multiview_image"] = null
        record["multiview_captured"] = include_multiview
        if include_multiview:
            var composite: Image = captures.get("multiview")
            var multiview_dir := output_dir.path_join("multiview").path_join(capture_state)
            DirAccess.make_dir_recursive_absolute(multiview_dir)
            var multiview_path := multiview_dir.path_join(filename)
            if composite == null or composite.save_png(multiview_path) != OK:
                push_error("3D_MULTIVIEW_SAVE_FAILED: " + multiview_path)
                quit(10)
                return
            record["multiview_image"] = multiview_path
            multiview_sample_count += 1
        samples.append(record)
    var report := {
        "schema_version": 1,
        "scene": str(profile.get("scenes", {}).get("3d", "")),
        "godot_version": Engine.get_version_info(),
        "duration_seconds": duration,
        "sampling_schedule": capture.get("3d_segments", {}),
        "sample_count": samples.size(),
        "multiview_sample_count": multiview_sample_count,
        "captured_states": selected_states if not selected_states.is_empty() else ["idle", "walk", "run", "jump"],
        "camera_views": config.get("camera_views", ["front", "side", "top", "perspective"]),
        "front_local_axis": [front_local_axis.x, front_local_axis.y, front_local_axis.z],
        "samples": samples
    }
    var metrics_path := output_dir.path_join("metrics.json")
    var file := FileAccess.open(metrics_path, FileAccess.WRITE)
    if file == null:
        push_error("3D_METRICS_OPEN_FAILED: " + metrics_path)
        quit(10)
        return
    file.store_string(JSON.stringify(report, "\t"))
    file.close()
    print("3D_QA_CAPTURE_COMPLETE | samples=", samples.size(), " | ", metrics_path)
    quit(0)

func _create_viewports() -> void:
    for view_name in ["front", "side", "top", "perspective"]:
        var viewport := SubViewport.new()
        viewport.name = "VisualQA_" + view_name
        viewport.size = Vector2i(640, 360)
        viewport.world_3d = demo.get_world_3d()
        viewport.own_world_3d = false
        viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
        demo.add_child(viewport)
        var view_camera := Camera3D.new()
        view_camera.name = "Camera"
        view_camera.fov = 42.0
        view_camera.near = 0.05
        view_camera.far = 100.0
        viewport.add_child(view_camera)
        view_camera.current = true
        viewports[view_name] = viewport
        cameras[view_name] = view_camera

func _capture_sample(state_name: String, include_multiview: bool) -> Dictionary:
    var result: Image = null
    var positions := {
        "front": Vector2i(0, 0),
        "side": Vector2i(640, 0),
        "top": Vector2i(0, 360),
        "perspective": Vector2i(640, 360)
    }
    var animation_position_before := playback.get_current_play_position()
    paused = true
    status.text = "%s | %s" % [
        state_name.to_upper(),
        "SYNCHRONIZED MULTIVIEW" if include_multiview else "PERSPECTIVE"
    ]
    _position_camera("perspective")
    var perspective_viewport: SubViewport = viewports["perspective"]
    perspective_viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    if include_multiview:
        for view_name in ["front", "side", "top"]:
            _position_camera(view_name)
            var viewport: SubViewport = viewports[view_name]
            viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    await RenderingServer.frame_post_draw
    var perspective := perspective_viewport.get_texture().get_image()
    if perspective == null or perspective.is_empty():
        paused = false
        return {}
    if include_multiview:
        result = Image.create(1280, 720, false, Image.FORMAT_RGBA8)
        for view_name in ["front", "side", "top", "perspective"]:
            var viewport: SubViewport = viewports[view_name]
            var frame := viewport.get_texture().get_image()
            if frame == null or frame.is_empty():
                paused = false
                return {}
            result.blit_rect(frame, Rect2i(0, 0, 640, 360), positions[view_name])
    for view_name in ["front", "side", "top", "perspective"]:
        var viewport: SubViewport = viewports[view_name]
        viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
    var animation_position_after := playback.get_current_play_position()
    var animation_advanced := absf(animation_position_after - animation_position_before) > 0.0001
    paused = false
    return {
        "perspective": perspective,
        "multiview": result,
        "animation_position_after": snapped(animation_position_after, 0.0001),
        "animation_advanced": animation_advanced
    }

func _position_camera(view_name: String) -> void:
    var view_camera: Camera3D = cameras[view_name]
    var front := (model.global_transform.basis * front_local_axis).normalized()
    var right := model.global_transform.basis.x.normalized()
    var target := actor.global_position + Vector3(0.0, 1.1, 0.0)
    var offset := front * 6.2 + Vector3(0.0, 0.8, 0.0)
    var up := Vector3.UP
    match view_name:
        "side":
            offset = right * 6.2 + Vector3(0.0, 0.8, 0.0)
        "top":
            offset = Vector3(0.0, 7.8, 0.0)
            up = -front
        "perspective":
            offset = front * 6.4 + right * 3.4 + Vector3(0.0, 1.55, 0.0)
    view_camera.global_position = target + offset
    view_camera.look_at(target, up)
func _snapshot(sample_index: int, start_elapsed: float) -> Dictionary:
    var active_node := playback.get_current_node()
    var clip: Animation = null
    if animation_player.has_animation(active_node):
        clip = animation_player.get_animation(active_node)
    var forward := (model.global_transform.basis * front_local_axis).normalized()
    var horizontal_velocity := Vector3(actor.velocity.x, 0.0, actor.velocity.z)
    var alignment: Variant = null
    if horizontal_velocity.length() > 0.001:
        alignment = forward.dot(horizontal_velocity.normalized())
    var left_world := skeleton.global_transform * skeleton.get_bone_global_pose(left_foot_index)
    var right_world := skeleton.global_transform * skeleton.get_bone_global_pose(right_foot_index)
    var inverse_actor := actor.global_transform.affine_inverse()
    return {
        "sequence_index": sample_index,
        "timestamp_seconds": snapped(float(demo.get(elapsed_property)) - start_elapsed, 0.0001),
        "state": str(demo.get(state_property)).to_lower(),
        "animation_tree_node": active_node,
        "animation_position_seconds": snapped(playback.get_current_play_position(), 0.0001),
        "animation_length_seconds": clip.length if clip != null else null,
        "animation_loop_mode": clip.loop_mode if clip != null else null,
        "actor_position": _vector(actor.global_position),
        "actor_velocity": _vector(actor.velocity),
        "actor_is_on_floor": actor.is_on_floor(),
        "model_position": _vector(model.global_position),
        "model_yaw_degrees": snapped(rad_to_deg(model.global_rotation.y), 0.01),
        "model_forward": _vector(forward),
        "movement_direction": _vector(horizontal_velocity.normalized()) if horizontal_velocity.length() > 0.001 else null,
        "facing_alignment_dot": snapped(float(alignment), 0.0001) if alignment != null else null,
        "foot_left_world": _vector(left_world.origin),
        "foot_right_world": _vector(right_world.origin),
        "foot_left_actor": _vector(inverse_actor * left_world.origin),
        "foot_right_actor": _vector(inverse_actor * right_world.origin)
    }

func _wait_for_demo(config: Dictionary) -> bool:
    for _index in range(180):
        if demo.get(config.get("actor_property", "actor")) != null and demo.get(config.get("playback_property", "playback")) != null:
            return true
        await process_frame
    return false

func _find_skeleton(node: Node) -> Skeleton3D:
    if node is Skeleton3D:
        return node
    for child in node.get_children():
        var found := _find_skeleton(child)
        if found != null:
            return found
    return null

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

func _vector(value: Vector3) -> Array:
    return [snapped(value.x, 0.0001), snapped(value.y, 0.0001), snapped(value.z, 0.0001)]

func _build_schedule(segments: Dictionary, counts: Dictionary, multiview_count: int) -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    for state_name in segments.keys():
        var intervals: Array = segments[state_name]
        var total_length := 0.0
        for interval in intervals:
            total_length += float(interval[1]) - float(interval[0])
        var count := int(counts.get(state_name, 24))
        if total_length <= 0.0 or count < 1:
            continue
        var multiview_slots: Dictionary = {}
        var selected_count := mini(multiview_count, count)
        for view_slot in range(selected_count):
            var slot := 0 if selected_count == 1 else int(round(float(view_slot) * float(count - 1) / float(selected_count - 1)))
            multiview_slots[slot] = true
        for sample_index in range(count):
            var remaining := (float(sample_index) + 0.5) * total_length / float(count)
            var target_time := 0.0
            for interval in intervals:
                var interval_length := float(interval[1]) - float(interval[0])
                if remaining < interval_length:
                    target_time = float(interval[0]) + remaining
                    break
                remaining -= interval_length
            result.append({
                "state": str(state_name),
                "time": target_time,
                "multiview": multiview_slots.has(sample_index)
            })
    result.sort_custom(func(a: Dictionary, b: Dictionary): return float(a["time"]) < float(b["time"]))
    return result
