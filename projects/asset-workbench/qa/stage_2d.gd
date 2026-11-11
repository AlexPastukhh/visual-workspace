extends Node2D
const ClipSampler = preload("res://qa/clip_sampler.gd")

@export var content_scene: PackedScene
@export var texture: Texture2D
@export var content_scale := Vector2.ONE
@export var clips: Array[String] = []
@export var animation_player_path: NodePath
@export var seconds_per_phase := 2.0
var sampler = ClipSampler.new()
var elapsed := 0.0

func _ready() -> void:
    RenderingServer.set_default_clear_color(Color("#203040"))
    var subject := Node2D.new()
    subject.name = "Subject"
    subject.position = get_viewport_rect().size / 2.0
    subject.scale = content_scale
    add_child(subject)
    var content: Node2D
    if content_scene != null:
        content = content_scene.instantiate() as Node2D
    elif texture != null:
        var sprite := Sprite2D.new()
        sprite.texture = texture
        content = sprite
    if content == null:
        push_error("QA_STAGE: expected a 2D scene or texture")
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

func qa_current_clip() -> String:
    return str(sampler.player.assigned_animation) if sampler.player != null else ""
