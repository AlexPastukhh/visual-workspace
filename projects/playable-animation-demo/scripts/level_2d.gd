extends Node2D
const ATLAS = preload("res://assets/robot_atlas.png")
var actor: CharacterBody2D
var sprite: AnimatedSprite2D
var gate: Node2D
var gate_shape: CollisionShape2D
var state := "idle"
var door_open := false
var opening := false
var won := false
var queued_jump := false
var queued_action := false
var action_count := 0
const FLOOR := 566.0

func _ready() -> void:
    _box(Vector2(640, FLOOR + 70), Vector2(1280,140), Color("#203a49"), true)
    for x in range(30, 1270, 64):
        _box(Vector2(x, FLOOR+7),Vector2(35,3),Color("#557680"),false)
    _box(Vector2(728,FLOOR-24),Vector2(42,48),Color("#eeae45"),false)
    _label("RELAY SWITCH  [E]",Vector2(638,FLOOR+35),Color("#ffcf81"))
    _box(Vector2(1130,FLOOR-6),Vector2(140,12),Color("#4ed8bb"),false)
    _label("EXIT",Vector2(1107,FLOOR+35),Color("#6af2d3"))
    gate = Node2D.new()
    gate.position=Vector2(870,FLOOR-112)
    add_child(gate)
    var body := StaticBody2D.new()
    gate.add_child(body)
    gate_shape=CollisionShape2D.new()
    var shape:=RectangleShape2D.new()
    shape.size=Vector2(26,224)
    gate_shape.shape=shape
    body.add_child(gate_shape)
    var visual:=ColorRect.new()
    visual.position=Vector2(-13,-112)
    visual.size=Vector2(26,224)
    visual.color=Color("#df7759")
    visual.mouse_filter=Control.MOUSE_FILTER_IGNORE
    gate.add_child(visual)
    actor=CharacterBody2D.new()
    actor.name="Player"
    actor.position=Vector2(150,FLOOR)
    var collider:=CollisionShape2D.new()
    var capsule:=CapsuleShape2D.new()
    capsule.radius=13
    capsule.height=74
    collider.shape=capsule
    collider.position.y=-37
    actor.add_child(collider)
    sprite=AnimatedSprite2D.new()
    sprite.position=Vector2(0,-46.5)
    sprite.scale=Vector2(1.5,1.5)
    sprite.sprite_frames=SpriteFrames.new()
    sprite.sprite_frames.remove_animation("default")
    for spec in [["idle",[0,1],4.0,true],["walk",[2,3,4,5],10.0,true],["run",[2,4],15.0,true],["jump",[6,7],7.0,false]]:
        sprite.sprite_frames.add_animation(spec[0])
        sprite.sprite_frames.set_animation_speed(spec[0],spec[2])
        sprite.sprite_frames.set_animation_loop(spec[0],spec[3])
        for index in spec[1]:
            var frame:=AtlasTexture.new()
            frame.atlas=ATLAS
            frame.region=Rect2(index*64,0,64,64)
            sprite.sprite_frames.add_frame(spec[0],frame)
    actor.add_child(sprite)
    add_child(actor)
    sprite.play("idle")

func _physics_process(delta:float) -> void:
    var direction:=Input.get_axis("left","right")
    var running:=Input.is_action_pressed("run")
    actor.velocity.x=direction*(280.0 if running else 160.0)
    actor.velocity.y+=1100.0*delta
    if (Input.is_action_just_pressed("jump") or queued_jump) and actor.is_on_floor():
        actor.velocity.y=-430.0
    queued_jump=false
    if Input.is_action_just_pressed("interact") or queued_action:
        _interact()
    queued_action=false
    actor.move_and_slide()
    actor.position.x=clampf(actor.position.x,35,1240)
    var next:="jump" if not actor.is_on_floor() else ("run" if running and absf(direction)>0.01 else ("walk" if absf(direction)>0.01 else "idle"))
    if next!=state:
        state=next
        sprite.play(state)
    if direction!=0:
        sprite.flip_h=direction<0
    if door_open and actor.position.x>1080:
        won=true

func _interact() -> void:
    if absf(actor.position.x-728)>140 or opening or door_open:
        return
    action_count+=1
    opening=true
    var tween:=create_tween()
    tween.tween_property(gate,"position:y",FLOOR-370,0.6).set_trans(Tween.TRANS_CUBIC)
    tween.tween_callback(func():
        gate_shape.set_deferred("disabled",true)
        door_open=true
        opening=false)

func _box(at:Vector2,size:Vector2,color:Color,collision:bool) -> void:
    var rect:=ColorRect.new()
    rect.position=at-size/2
    rect.size=size
    rect.color=color
    rect.mouse_filter=Control.MOUSE_FILTER_IGNORE
    add_child(rect)
    if collision:
        var body:=StaticBody2D.new()
        body.position=at
        var shape:=CollisionShape2D.new()
        var box:=RectangleShape2D.new()
        box.size=size
        shape.shape=box
        body.add_child(shape)
        add_child(body)

func _label(text:String,at:Vector2,color:Color) -> void:
    var label:=Label.new()
    label.text=text
    label.position=at
    label.modulate=color
    label.add_theme_font_size_override("font_size",16)
    add_child(label)

func observation() -> Dictionary:
    return {"mode":"2d","position":[actor.position.x,actor.position.y],"velocity":[actor.velocity.x,actor.velocity.y],
        "state":state,"grounded":actor.is_on_floor(),"sprite_frame":sprite.frame,
        "door_open":door_open,"opening":opening,"won":won,"action_count":action_count,
        "can_interact":absf(actor.position.x-728)<=140,"goal_x":1080.0}
