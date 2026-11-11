extends Control

const DEMO_2D := "res://scenes/demo_2d.tscn"
const DEMO_3D := "res://scenes/demo_3d.tscn"

func _ready() -> void:
    var args := OS.get_cmdline_user_args()
    if "--demo-2d" in args:
        call_deferred("_open_demo", DEMO_2D)
        return
    if "--demo-3d" in args:
        call_deferred("_open_demo", DEMO_3D)
        return
    _build_menu()

func _build_menu() -> void:
    var bg := ColorRect.new()
    bg.color = Color(0.025, 0.045, 0.07)
    bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(bg)
    var center := CenterContainer.new()
    center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    add_child(center)
    var stack := VBoxContainer.new()
    stack.custom_minimum_size = Vector2(540, 0)
    stack.add_theme_constant_override("separation", 18)
    center.add_child(stack)
    var title := Label.new()
    title.text = "FORTIS  /  GAME ANIMATION LAB"
    title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    title.add_theme_font_size_override("font_size", 30)
    stack.add_child(title)
    var subtitle := Label.new()
    subtitle.text = "Asset creation → animation → Godot import → gameplay"
    subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    subtitle.add_theme_font_size_override("font_size", 16)
    stack.add_child(subtitle)
    var b2 := Button.new()
    b2.text = "Open 2D animation test"
    b2.custom_minimum_size = Vector2(0, 54)
    b2.pressed.connect(func(): get_tree().change_scene_to_file(DEMO_2D))
    stack.add_child(b2)
    var b3 := Button.new()
    b3.text = "Open 3D animation test"
    b3.custom_minimum_size = Vector2(0, 54)
    b3.pressed.connect(func(): get_tree().change_scene_to_file(DEMO_3D))
    stack.add_child(b3)
    var hint := Label.new()
    hint.text = "2D: layered sprite source  |  3D: Blender rig + GLB actions"
    hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
    hint.add_theme_font_size_override("font_size", 13)
    stack.add_child(hint)

func _open_demo(path: String) -> void:
    get_tree().change_scene_to_file(path)
