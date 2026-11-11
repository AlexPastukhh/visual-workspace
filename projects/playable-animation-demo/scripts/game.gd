extends Node
const LEVEL_2D=preload("res://scripts/level_2d.gd")
const LEVEL_3D=preload("res://scripts/level_3d.gd")
var level: Node
var buttons: Dictionary={}
var status: Label
var mode:="2d"

func _ready() -> void:
    _inputs()
    _ui()
    load_mode("2d")

func _inputs() -> void:
    for spec in [["left",KEY_A],["left",KEY_LEFT],["right",KEY_D],["right",KEY_RIGHT],["run",KEY_SHIFT],["jump",KEY_SPACE],["interact",KEY_E]]:
        if not InputMap.has_action(spec[0]): InputMap.add_action(spec[0])
        var event:=InputEventKey.new()
        event.physical_keycode=spec[1]
        InputMap.action_add_event(spec[0],event)

func _ui() -> void:
    var layer:=CanvasLayer.new()
    add_child(layer)
    var title:=Label.new()
    title.text="FORTIS  /  ANIMATION RELAY"
    title.position=Vector2(32,20)
    title.add_theme_font_size_override("font_size",28)
    layer.add_child(title)
    var hints:=Label.new()
    hints.text="A/D or arrows: move    Shift: run    Space: jump    E: relay switch"
    hints.position=Vector2(34,61)
    hints.add_theme_font_size_override("font_size",17)
    layer.add_child(hints)
    status=Label.new()
    status.position=Vector2(34,94)
    status.add_theme_font_size_override("font_size",18)
    layer.add_child(status)
    _button(layer,"Mode2D","2D LEVEL",Vector2(914,24),Vector2(150,46),func(): load_mode("2d"))
    _button(layer,"Mode3D","3D LEVEL",Vector2(1080,24),Vector2(150,46),func(): load_mode("3d"))
    _button(layer,"Jump","JUMP  /  SPACE",Vector2(32,650),Vector2(230,46),func(): level.queued_jump=true)
    _button(layer,"Action","ACTIVATE RELAY  /  E",Vector2(278,650),Vector2(290,46),func(): level.queued_action=true)
    _button(layer,"Restart","RESTART",Vector2(1080,650),Vector2(150,46),func(): load_mode(mode))

func _button(parent:Node,id:String,text:String,at:Vector2,size:Vector2,callback:Callable) -> void:
    var button:=Button.new()
    button.name=id
    button.text=text
    button.position=at
    button.size=size
    button.focus_mode=Control.FOCUS_NONE
    button.pressed.connect(callback)
    parent.add_child(button)
    buttons[id]=button

func load_mode(next:String) -> void:
    if level!=null:
        remove_child(level)
        level.queue_free()
    mode=next
    level=LEVEL_2D.new() if mode=="2d" else LEVEL_3D.new()
    add_child(level)
    print("LEVEL_READY | ",mode)

func _process(_delta:float) -> void:
    if level==null or status==null: return
    var o:Dictionary=level.observation()
    status.text="%s  |  %s  |  %s" % [mode.to_upper(),str(o["state"]).to_upper(),
        "EXIT REACHED!" if o["won"] else ("RELAY ONLINE - REACH THE EXIT" if o["door_open"] else ("PRESS E / ACTIVATE RELAY" if o["can_interact"] else "REACH THE AMBER RELAY, OPEN THE GATE, FIND THE EXIT"))]
    status.modulate=Color("#70e5c4") if o["won"] else Color("#d5e5ef")

func observation() -> Dictionary:
    var data:Dictionary=level.observation()
    var controls:Dictionary={}
    for key in buttons:
        var rect:Rect2=buttons[key].get_global_rect()
        controls[key]=[rect.get_center().x,rect.get_center().y]
    data["buttons"]=controls
    return data
