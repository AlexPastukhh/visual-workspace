extends SceneTree

var manifest: Dictionary = {}
var scene: Node
var output_dir := ""
var fps := 24
var selected_phases: Array[String] = []
var viewports: Dictionary = {}
var cameras: Dictionary = {}
var previous_positions: Dictionary = {}
var phase_samples: Dictionary = {}
var phase_multiview_slots: Dictionary = {}

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    var manifest_path := _option(args, "--manifest", "")
    output_dir = _absolute(_option(args, "--output-dir", ""))
    var phases_arg := _option(args, "--phases", "")
    if manifest_path.is_empty() or output_dir.is_empty():
        push_error("ASSET_CAPTURE_ARGUMENTS_MISSING")
        quit(2)
        return
    var file := FileAccess.open(_absolute(manifest_path), FileAccess.READ)
    if file == null:
        push_error("ASSET_CAPTURE_MANIFEST_OPEN_FAILED")
        quit(2)
        return
    var parsed: Variant = JSON.parse_string(file.get_as_text())
    file.close()
    if not parsed is Dictionary:
        push_error("ASSET_CAPTURE_MANIFEST_INVALID")
        quit(2)
        return
    manifest = parsed
    var capture: Dictionary = manifest.get("capture", {})
    fps = int(capture.get("fps", 24))
    var resolution: Array = capture.get("resolution", [1280, 720])
    root.size = Vector2i(int(resolution[0]), int(resolution[1]))
    Engine.physics_ticks_per_second = fps
    Engine.max_fps = fps
    for phase in manifest.get("phases", []):
        var phase_id := str(phase.get("id", ""))
        if phases_arg.is_empty() or phase_id in phases_arg.split(","):
            selected_phases.append(phase_id)
            phase_samples[phase_id] = []
    if selected_phases.is_empty():
        push_error("ASSET_CAPTURE_NO_SELECTED_PHASES")
        quit(3)
        return

    var packed := load(str(manifest.get("scene", ""))) as PackedScene
    if packed == null:
        push_error("ASSET_CAPTURE_SCENE_LOAD_FAILED")
        quit(4)
        return
    scene = packed.instantiate()
    root.add_child(scene)
    await process_frame
    if not scene.has_method("qa_set_time"):
        push_error("ASSET_CAPTURE_SCENE_MUST_IMPLEMENT_QA_SET_TIME")
        quit(5)
        return
    Engine.time_scale = 0.0
    if scene.has_method("qa_reset"):
        scene.call("qa_reset")
    else:
        scene.call("qa_set_time", 0.0)
    previous_positions.clear()
    if not _validate_actors():
        Engine.time_scale = 1.0
        quit(5)
        return
    await RenderingServer.frame_post_draw
    if manifest.get("kind") == "3d_scene" and int(capture.get("multiview_samples_per_phase", 0)) > 0:
        _create_multiview()
    _build_multiview_slots()
    DirAccess.make_dir_recursive_absolute(output_dir)
    var total_frames := int(ceil(float(capture.get("duration_seconds", 1.0)) * float(fps)))
    var previous_frame_index := -2
    for frame_index in range(total_frames):
        var timestamp := float(frame_index) / float(fps)
        var active_phases: Array = []
        for phase in manifest.get("phases", []):
            var phase_id := str(phase.get("id", ""))
            if phase_id not in selected_phases:
                continue
            if timestamp + 0.00001 >= float(phase.get("start", 0.0)) and timestamp < float(phase.get("end", 0.0)):
                active_phases.append(phase)
        if active_phases.is_empty():
            continue
        if frame_index != previous_frame_index + 1 and timestamp > 0.0:
            scene.call("qa_set_time", maxf(0.0, timestamp - 1.0 / float(fps)))
            await process_frame
            await RenderingServer.frame_post_draw
            _snapshot_actors()
        previous_frame_index = frame_index
        scene.call("qa_set_time", timestamp)
        await process_frame
        await RenderingServer.frame_post_draw
        var actor_metrics := _snapshot_actors()
        for phase in active_phases:
            var phase_id := str(phase.get("id", ""))
            var phase_dir := output_dir.path_join(phase_id)
            var expected_clip := str(phase.get("expected_clip", ""))
            var actual_clip := str(scene.call("qa_current_clip")) if scene.has_method("qa_current_clip") else ""
            if not expected_clip.is_empty() and actual_clip != expected_clip:
                push_error("ASSET_CAPTURE_CLIP_MISMATCH: phase=%s t=%.4f expected=%s actual=%s" % [phase_id, timestamp, expected_clip, actual_clip])
                Engine.time_scale = 1.0
                quit(8)
                return
            var frames_dir := phase_dir.path_join("frames")
            DirAccess.make_dir_recursive_absolute(frames_dir)
            var filename := "frame_%04d.png" % frame_index
            var image := scene.get_viewport().get_texture().get_image()
            var image_path := frames_dir.path_join(filename)
            if image == null or image.save_png(image_path) != OK:
                push_error("ASSET_CAPTURE_FRAME_SAVE_FAILED: " + image_path)
                quit(5)
                return
            var record := {
                "sequence_index": frame_index,
                "timestamp_seconds": snapped(timestamp, 0.0001),
                "phase": phase_id,
                "animation_clip": actual_clip,
                "actors": actor_metrics,
                "image": "frames/" + filename,
                "multiview_image": null
            }

            var phase_start_frame := int(ceil((float(phase.get("start", 0.0)) - 0.00001) * float(fps)))
            var local_index := frame_index - phase_start_frame
            if phase_multiview_slots.get(phase_id, {}).has(local_index):
                paused = true
                var multiview_image := await _capture_multiview(manifest.get("actors", []))
                paused = false
                if multiview_image == null or multiview_image.is_empty():
                    push_error("ASSET_CAPTURE_MULTIVIEW_FAILED: " + phase_id)
                    quit(6)
                    return
                var multiview_dir := phase_dir.path_join("multiview")
                DirAccess.make_dir_recursive_absolute(multiview_dir)
                var multiview_path := multiview_dir.path_join(filename)
                if multiview_image.save_png(multiview_path) != OK:
                    push_error("ASSET_CAPTURE_MULTIVIEW_SAVE_FAILED")
                    quit(6)
                    return
                record["multiview_image"] = "multiview/" + filename
            phase_samples[phase_id].append(record)
    for phase_id in selected_phases:
        var phase_dir := output_dir.path_join(phase_id)
        var report := {
            "schema_version": 1,
            "asset_id": manifest.get("asset_id"),
            "kind": manifest.get("kind"),
            "phase": phase_id,
            "fps": fps,
            "sample_count": phase_samples[phase_id].size(),
            "samples": phase_samples[phase_id]
        }
        var metrics_file := FileAccess.open(phase_dir.path_join("metrics.json"), FileAccess.WRITE)
        if metrics_file == null:
            push_error("ASSET_CAPTURE_METRICS_OPEN_FAILED")
            quit(7)
            return
        metrics_file.store_string(JSON.stringify(report, "\t"))
        metrics_file.close()
        print("ASSET_PHASE_CAPTURE_PASS | ", phase_id, " | frames=", phase_samples[phase_id].size())
    Engine.time_scale = 1.0
    quit(0)

func _snapshot_actors() -> Array[Dictionary]:
    var result: Array[Dictionary] = []
    for config in manifest.get("actors", []):
        var actor_id := str(config.get("id", ""))
        var node := scene.get_node_or_null(NodePath(str(config.get("node_path", ""))))
        if node == null:
            push_error("ASSET_CAPTURE_ACTOR_NODE_MISSING: " + actor_id)
            continue
        var position: Variant
        var forward: Variant
        var rotation_degrees: Variant
        if node is Node2D:
            position = node.global_position
            var axis: Array = config.get("forward_axis", [1.0, 0.0])
            forward = (node.global_transform.x * float(axis[0]) + node.global_transform.y * float(axis[1])).normalized()
            rotation_degrees = rad_to_deg(node.global_rotation)
        elif node is Node3D:
            position = node.global_position
            var axis3: Array = config.get("forward_axis", [0.0, 0.0, 1.0])
            forward = (node.global_transform.basis * Vector3(axis3[0], axis3[1], axis3[2])).normalized()
            rotation_degrees = node.global_rotation_degrees
        else:
            push_error("ASSET_CAPTURE_ACTOR_TYPE_UNSUPPORTED: " + actor_id)
            continue
        var previous: Variant = previous_positions.get(actor_id)
        var velocity: Variant = null
        if previous != null:
            velocity = (position - previous) * float(fps)
        previous_positions[actor_id] = position

        var alignment: Variant = null
        if velocity != null and velocity.length() > 0.001:
            alignment = forward.dot(velocity.normalized())
        var record := {
            "id": actor_id,
            "dimension": str(config.get("dimension", "")),
            "position": _vector(position),
            "velocity": _vector(velocity) if velocity != null else null,
            "forward": _vector(forward),
            "rotation_degrees": _vector(rotation_degrees) if rotation_degrees is Vector3 else snapped(float(rotation_degrees), 0.01),
            "facing_alignment_dot": snapped(float(alignment), 0.0001) if alignment != null else null
        }
        if node is Node3D:
            record["height"] = snapped(node.global_position.y, 0.0001)
            if config.has("ground_y"):
                record["grounded"] = node.global_position.y <= float(config["ground_y"]) + float(config.get("ground_tolerance", 0.08))
        var tracked_metrics: Array[Dictionary] = []
        for child_name in config.get("tracked_children", []):
            var child := node.find_child(str(child_name), true, false) as Node3D
            if child != null:
                tracked_metrics.append({
                    "id": str(child_name),
                    "local_rotation_degrees": _vector(child.rotation_degrees),
                    "world_rotation_degrees": _vector(child.global_rotation_degrees)
                })
        if not tracked_metrics.is_empty():
            record["tracked_children"] = tracked_metrics
        if config.has("character"):
            record["character"] = _snapshot_character(node as Node3D, config.get("character", {}))
        result.append(record)
    return result

func _snapshot_character(actor: Node3D, character: Dictionary) -> Dictionary:
    var skeleton := actor.get_node_or_null(NodePath(str(character.get("skeleton_path", "")))) as Skeleton3D
    if skeleton == null:
        return {}
    var bones: Dictionary = character.get("foot_bones", {})
    var left_name := str(bones.get("left", ""))
    var right_name := str(bones.get("right", ""))
    var left_index := skeleton.find_bone(left_name)
    var right_index := skeleton.find_bone(right_name)
    var left_world := skeleton.global_transform * skeleton.get_bone_global_pose(left_index)
    var right_world := skeleton.global_transform * skeleton.get_bone_global_pose(right_index)
    var inverse_actor := actor.global_transform.affine_inverse()
    var result := {
        "motion_mode": str(character.get("motion_mode", "forward")),
        "skeleton_bone_count": skeleton.get_bone_count(),
        "foot_bones": {
            "left": {
                "name": left_name,
                "world_position": _vector(left_world.origin),
                "actor_position": _vector(inverse_actor * left_world.origin)
            },
            "right": {
                "name": right_name,
                "world_position": _vector(right_world.origin),
                "actor_position": _vector(inverse_actor * right_world.origin)
            }
        },
        "loop_states": character.get("loop_states", []),
        "jump_state": character.get("jump_state", ""),
        "landing_policy": character.get("landing_policy", "not_applicable")
    }
    var player_path := str(character.get("animation_player_path", ""))
    if not player_path.is_empty():
        var player := actor.get_node_or_null(NodePath(player_path)) as AnimationPlayer
        if player != null:
            var clip_name := str(player.current_animation)
            if clip_name.is_empty():
                clip_name = str(player.assigned_animation)
            var clip: Animation = player.get_animation(clip_name) if player.has_animation(clip_name) else null
            result["animation_player"] = {
                "current_animation": clip_name,
                "position_seconds": snapped(player.get_current_animation_position(), 0.0001),
                "length_seconds": clip.length if clip != null else null,
                "loop_mode": clip.loop_mode if clip != null else null,
                "is_playing": player.is_playing()
            }
    var tree_path := str(character.get("animation_tree_path", ""))
    if not tree_path.is_empty():
        var tree := actor.get_node_or_null(NodePath(tree_path)) as AnimationTree
        if tree != null:
            var playback_property := str(character.get("playback_property", "parameters/playback"))
            var playback_value: Variant = tree.get(playback_property)
            var tree_state := ""
            var tree_position: Variant = null
            if playback_value is AnimationNodeStateMachinePlayback:
                tree_state = playback_value.get_current_node()
                tree_position = snapped(playback_value.get_current_play_position(), 0.0001)
            result["animation_tree"] = {
                "active": tree.active,
                "current_state": tree_state,
                "position_seconds": tree_position
            }
            # When an AnimationTree drives the player, AnimationPlayer.current_animation
            # is often empty. Resolve state-machine states back to clip metadata where possible.
            var player_path_for_tree := str(character.get("animation_player_path", ""))
            if not player_path_for_tree.is_empty() and not tree_state.is_empty():
                var tree_player := actor.get_node_or_null(NodePath(player_path_for_tree)) as AnimationPlayer
                if tree_player != null and tree_player.has_animation(tree_state):
                    var state_clip: Animation = tree_player.get_animation(tree_state)
                    result["animation_player"] = {
                        "current_animation": tree_state,
                        "position_seconds": tree_position,
                        "length_seconds": state_clip.length,
                        "loop_mode": state_clip.loop_mode,
                        "is_playing": tree.active
                    }
    return result

func _create_multiview() -> void:
    for view_name in ["front", "side", "top", "perspective"]:
        var viewport := SubViewport.new()
        viewport.name = "AssetQA_" + view_name
        viewport.size = Vector2i(640, 360)
        viewport.world_3d = scene.get_world_3d()
        viewport.own_world_3d = false
        viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
        scene.add_child(viewport)
        var camera := Camera3D.new()
        camera.name = "Camera"
        camera.fov = float(manifest.get("capture", {}).get("multiview", {}).get("fov", 42.0))
        camera.near = 0.05
        camera.far = 200.0
        viewport.add_child(camera)
        camera.current = true
        var label := Label.new()
        label.text = view_name.to_upper()
        label.position = Vector2(12.0, 10.0)
        label.add_theme_font_size_override("font_size", 18)
        label.add_theme_color_override("font_color", Color("#f4f7fb"))
        viewport.add_child(label)
        viewports[view_name] = viewport
        cameras[view_name] = camera

func _build_multiview_slots() -> void:
    var count := int(manifest.get("capture", {}).get("multiview_samples_per_phase", 0))
    if count <= 0:
        return
    for phase in manifest.get("phases", []):
        var phase_id := str(phase.get("id", ""))
        var start_frame := int(ceil((float(phase.get("start", 0.0)) - 0.00001) * float(fps)))
        var end_frame := int(ceil((float(phase.get("end", 0.0)) - 0.00001) * float(fps)))
        var total := maxi(0, end_frame - start_frame)
        var selected := mini(count, maxi(1, total))
        var slots: Dictionary = {}
        for index in range(selected):
            var slot := 0 if selected == 1 else int(round(float(index) * float(total - 1) / float(selected - 1)))
            slots[slot] = true
        phase_multiview_slots[phase_id] = slots

func _capture_multiview(actor_configs: Array) -> Image:
    var actor: Node3D = null
    var config: Dictionary = {}
    var framing: Dictionary = manifest.get("capture", {}).get("multiview", {})
    var target_id := str(framing.get("actor_id", ""))
    for item in actor_configs:
        if item.get("dimension") == "3d" and (target_id.is_empty() or item.get("id") == target_id):
            actor = scene.get_node_or_null(NodePath(str(item.get("node_path", "")))) as Node3D
            config = item
            break
    if actor == null:
        return null
    var axis: Array = config.get("forward_axis", [0.0, 0.0, 1.0])
    var forward := (actor.global_transform.basis * Vector3(axis[0], axis[1], axis[2])).normalized()
    var right := actor.global_transform.basis.x.normalized()
    var center: Array = framing.get("target_offset", [0.0, 0.8, 0.0])
    var target := actor.global_position + Vector3(center[0], center[1], center[2])
    var distance := float(framing.get("distance", 7.0))
    var height := float(framing.get("height", 1.5))

    var offsets := {
        "front": forward * distance + Vector3(0.0, height, 0.0),
        "side": right * distance + Vector3(0.0, height, 0.0),
        "top": Vector3(0.0, distance * 8.0 / 7.0, 0.0),
        "perspective": forward * distance * 6.0 / 7.0 + right * distance * 4.0 / 7.0 + Vector3(0.0, height * 2.0, 0.0)
    }
    for view_name in ["front", "side", "top", "perspective"]:
        var camera: Camera3D = cameras[view_name]
        camera.global_position = target + offsets[view_name]
        camera.look_at(target, -forward if view_name == "top" else Vector3.UP)
        var viewport: SubViewport = viewports[view_name]
        viewport.render_target_update_mode = SubViewport.UPDATE_ONCE
    await RenderingServer.frame_post_draw
    var result := Image.create(1280, 720, false, Image.FORMAT_RGBA8)
    var positions := {
        "front": Vector2i(0, 0), "side": Vector2i(640, 0),
        "top": Vector2i(0, 360), "perspective": Vector2i(640, 360)
    }
    for view_name in ["front", "side", "top", "perspective"]:
        var frame := (viewports[view_name] as SubViewport).get_texture().get_image()
        if frame == null or frame.is_empty():
            return null
        result.blit_rect(frame, Rect2i(0, 0, 640, 360), positions[view_name])
        (viewports[view_name] as SubViewport).render_target_update_mode = SubViewport.UPDATE_DISABLED
    return result

func _load_profile(path: String) -> Dictionary:
    var file := FileAccess.open(_absolute(path), FileAccess.READ)
    if file == null:
        return {}
    var value: Variant = JSON.parse_string(file.get_as_text())
    file.close()
    return value if value is Dictionary else {}

func _option(args: PackedStringArray, key: String, fallback: String) -> String:
    for index in range(args.size() - 1):
        if args[index] == key:
            return args[index + 1]
    return fallback

func _absolute(path: String) -> String:
    return ProjectSettings.globalize_path(path) if path.begins_with("res://") else path

func _vector(value: Variant) -> Array:
    if value is Vector2:
        return [snapped(value.x, 0.0001), snapped(value.y, 0.0001)]
    if value is Vector3:
        return [snapped(value.x, 0.0001), snapped(value.y, 0.0001), snapped(value.z, 0.0001)]
    return []

func _validate_actors() -> bool:
    for config in manifest.get("actors", []):
        var actor_id := str(config.get("id", ""))
        var node := scene.get_node_or_null(NodePath(str(config.get("node_path", ""))))
        if node == null:
            push_error("ASSET_CAPTURE_ACTOR_NODE_MISSING: " + actor_id)
            return false
        if config.get("dimension") == "2d" and not node is Node2D:
            push_error("ASSET_CAPTURE_ACTOR_EXPECTED_NODE2D: " + actor_id)
            return false
        if config.get("dimension") == "3d" and not node is Node3D:
            push_error("ASSET_CAPTURE_ACTOR_EXPECTED_NODE3D: " + actor_id)
            return false
        for child_name in config.get("tracked_children", []):
            var child := node.find_child(str(child_name), true, false)
            if child == null or not child is Node3D:
                push_error("ASSET_CAPTURE_TRACKED_CHILD_MISSING: " + actor_id + "/" + str(child_name))
                return false
        var character: Dictionary = config.get("character", {})
        if not character.is_empty():
            var skeleton := node.get_node_or_null(NodePath(str(character.get("skeleton_path", "")))) as Skeleton3D
            if skeleton == null:
                push_error("ASSET_CAPTURE_CHARACTER_SKELETON_MISSING: " + actor_id)
                return false
            var foot_bones: Dictionary = character.get("foot_bones", {})
            for side in ["left", "right"]:
                var bone_name := str(foot_bones.get(side, ""))
                if bone_name.is_empty() or skeleton.find_bone(bone_name) < 0:
                    push_error("ASSET_CAPTURE_CHARACTER_FOOT_BONE_MISSING: " + actor_id + "/" + side + "/" + bone_name)
                    return false
            var player_path := str(character.get("animation_player_path", ""))
            if not player_path.is_empty():
                var player := node.get_node_or_null(NodePath(player_path)) as AnimationPlayer
                if player == null:
                    push_error("ASSET_CAPTURE_CHARACTER_ANIMATION_PLAYER_MISSING: " + actor_id)
                    return false
            var tree_path := str(character.get("animation_tree_path", ""))
            if not tree_path.is_empty():
                var tree := node.get_node_or_null(NodePath(tree_path)) as AnimationTree
                if tree == null:
                    push_error("ASSET_CAPTURE_CHARACTER_ANIMATION_TREE_MISSING: " + actor_id)
                    return false
    return true
