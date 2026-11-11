extends Node2D

var upper_texture: Texture2D
var lower_texture: Texture2D

var elapsed := 0.0
var upper_plane: Sprite2D
var lower_plane: Sprite2D
var phase_label: Label

func _ready() -> void:
    _build_background()
    _build_planes()
    _build_hud()
    qa_reset()

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1280, 720), Color("#102b4a"))
    draw_circle(Vector2(1080, 118), 58, Color("#f8c77b"))
    draw_circle(Vector2(1080, 118), 72, Color(0.98, 0.78, 0.45, 0.10))
    for index in range(38):
        var x := float((index * 197 + 53) % 1260)
        var y := float((index * 83 + 31) % 700)
        draw_circle(Vector2(x, y), 1.5 if index % 3 else 2.4, Color(0.78, 0.89, 1.0, 0.55))
    for x in range(0, 1280, 64):
        draw_line(Vector2(x, 0), Vector2(x, 720), Color(0.42, 0.66, 0.82, 0.055), 1.0)
    for y in range(0, 720, 64):
        draw_line(Vector2(0, y), Vector2(1280, y), Color(0.42, 0.66, 0.82, 0.055), 1.0)
    _draw_cloud(Vector2(330, 130), 1.0)
    _draw_cloud(Vector2(840, 585), 0.78)
    _draw_cloud(Vector2(600, 350), 0.56)
    _draw_dashed_line(Vector2(40, 260), Vector2(1240, 260), Color("#e18a5c"))
    _draw_dashed_line(Vector2(40, 470), Vector2(1240, 470), Color("#58c9d2"))

func _draw_cloud(center: Vector2, scale_value: float) -> void:
    var tint := Color(0.73, 0.84, 0.91, 0.15)
    draw_circle(center, 28 * scale_value, tint)
    draw_circle(center + Vector2(25, -8) * scale_value, 34 * scale_value, tint)
    draw_circle(center + Vector2(55, 2) * scale_value, 24 * scale_value, tint)

func _draw_dashed_line(start: Vector2, finish: Vector2, tint: Color) -> void:
    var direction := (finish - start).normalized()
    for step in range(0, 1200, 28):
        var a := start + direction * float(step)
        var b := start + direction * float(step + 13)
        draw_line(a, b, Color(tint.r, tint.g, tint.b, 0.34), 2.0)

func _build_background() -> void:
    queue_redraw()

func _load_svg_texture(path: String) -> Texture2D:
    var image := Image.new()
    var error := image.load_svg_from_buffer(FileAccess.get_file_as_bytes(path), 1.0)
    if error != OK:
        push_error("PLANE_SVG_LOAD_FAILED: " + path)
        return null
    return ImageTexture.create_from_image(image)

func _build_planes() -> void:
    upper_texture = _load_svg_texture("res://assets/planes-dual-pass/source/upper-plane.svg")
    lower_texture = _load_svg_texture("res://assets/planes-dual-pass/source/lower-plane.svg")
    upper_plane = Sprite2D.new()
    upper_plane.name = "UpperPlane"
    upper_plane.texture = upper_texture
    upper_plane.scale = Vector2(0.84, 0.84)
    upper_plane.z_index = 10
    add_child(upper_plane)

    lower_plane = Sprite2D.new()
    lower_plane.name = "LowerPlane"
    lower_plane.texture = lower_texture
    lower_plane.scale = Vector2(0.78, 0.78)
    lower_plane.z_index = 10
    add_child(lower_plane)

func _build_hud() -> void:
    var upper_tag := _make_label("01  /  UPPER FLIGHT", Vector2(42, 190), Color("#ffcf9a"))
    add_child(upper_tag)
    var lower_tag := _make_label("02  /  LOWER FLIGHT", Vector2(42, 590), Color("#a7f1ed"))
    add_child(lower_tag)
    phase_label = _make_label("", Vector2(42, 34), Color("#f4f7fb"))
    phase_label.add_theme_font_size_override("font_size", 22)
    add_child(phase_label)

func _make_label(value: String, at: Vector2, tint: Color) -> Label:
    var label := Label.new()
    label.text = value
    label.position = at
    label.add_theme_font_size_override("font_size", 16)
    label.add_theme_color_override("font_color", tint)
    return label

func qa_reset() -> void:
    qa_set_time(0.0)

func qa_set_time(seconds: float) -> void:
    elapsed = maxf(0.0, seconds)
    _update_motion()

func _physics_process(delta: float) -> void:
    elapsed += delta
    _update_motion()

func _update_motion() -> void:
    var upper_x := 130.0
    var lower_x := 1150.0
    var upper_y := 260.0
    var lower_y := 470.0
    var upper_angle := 0.0
    var lower_angle := PI
    var phase_name := "OUTBOUND"

    if elapsed < 3.0:
        var progress := clampf(elapsed / 3.0, 0.0, 1.0)
        upper_x = lerpf(130.0, 1150.0, progress)
        lower_x = lerpf(1150.0, 130.0, progress)
        upper_y += sin(elapsed * 2.0) * 5.0
        lower_y += sin(elapsed * 1.8 + 0.7) * 5.0
    elif elapsed < 4.0:
        phase_name = "TURNAROUND"
        var turn_progress := smoothstep(0.0, 1.0, elapsed - 3.0)
        upper_x = 1150.0
        lower_x = 130.0
        upper_y -= sin((elapsed - 3.0) * PI) * 13.0
        lower_y += sin((elapsed - 3.0) * PI) * 13.0
        upper_angle = PI * turn_progress
        lower_angle = PI + PI * turn_progress
    else:
        phase_name = "RETURN"
        var progress := clampf((elapsed - 4.0) / 3.0, 0.0, 1.0)
        upper_x = lerpf(1150.0, 130.0, progress)
        lower_x = lerpf(130.0, 1150.0, progress)
        upper_angle = PI
        lower_angle = TAU
        upper_y += sin(elapsed * 2.0) * 5.0
        lower_y += sin(elapsed * 1.8 + 0.7) * 5.0

    upper_plane.position = Vector2(upper_x, upper_y)
    lower_plane.position = Vector2(lower_x, lower_y)
    upper_plane.rotation = upper_angle
    lower_plane.rotation = lower_angle
    phase_label.text = "DUAL FLIGHT TEST     /     " + phase_name
