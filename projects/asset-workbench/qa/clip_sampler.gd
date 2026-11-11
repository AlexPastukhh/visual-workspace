extends RefCounted
# Only ordinary AnimationPlayer clips; custom controllers keep their own adapter.
var player: AnimationPlayer
var clips: Array[String] = []
var segment_seconds := 2.0

func configure(content: Node, requested: Array[String], player_path: NodePath, seconds: float) -> void:
    clips = requested
    segment_seconds = seconds
    if clips.is_empty():
        return
    if not player_path.is_empty():
        player = content.get_node_or_null(player_path) as AnimationPlayer
    else:
        var candidates: Array[AnimationPlayer] = []
        _find_players(content, candidates)
        if candidates.size() == 1:
            player = candidates[0]
    if player == null:
        push_error("QA_STAGE: supply animation_player_path when the player is missing or ambiguous")
        content.get_tree().quit(10)
        return
    if _has_active_tree(content):
        push_error("QA_STAGE: active AnimationTree needs a task-specific controller adapter")
        content.get_tree().quit(10)
        return
    for clip in clips:
        if not player.has_animation(clip):
            push_error("QA_STAGE: missing clip " + clip)
            content.get_tree().quit(10)
            return

func sample(seconds: float) -> void:
    if player == null or clips.is_empty():
        return
    var segment := mini(int(maxf(seconds, 0.0) / segment_seconds), clips.size() - 1)
    var name := clips[segment]
    var animation := player.get_animation(name)
    var local_time := maxf(0.0, seconds - float(segment) * segment_seconds)
    # Preserve imported loop policy and playback direction, including ping-pong.
    if animation.loop_mode == Animation.LOOP_LINEAR:
        local_time = fposmod(local_time, animation.length)
    elif animation.loop_mode == Animation.LOOP_PINGPONG:
        local_time = pingpong(local_time, animation.length)
    else:
        local_time = minf(local_time, animation.length)
    player.play(name)
    player.seek(local_time, true)
    player.pause()

func _find_players(node: Node, found: Array[AnimationPlayer]) -> void:
    if node is AnimationPlayer:
        found.append(node)
    for child in node.get_children():
        _find_players(child, found)

func _has_active_tree(node: Node) -> bool:
    if node is AnimationTree and node.active:
        return true
    for child in node.get_children():
        if _has_active_tree(child):
            return true
    return false
