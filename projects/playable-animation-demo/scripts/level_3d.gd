extends Node3D
const MODEL=preload("res://assets/gamebot_animated.glb")
var actor: CharacterBody3D
var model: Node3D
var player: AnimationPlayer
var tree: AnimationTree
var playback: AnimationNodeStateMachinePlayback
var gate: Node3D
var gate_shape: CollisionShape3D
var state:="idle"
var door_open:=false
var opening:=false
var won:=false
var queued_jump:=false
var queued_action:=false
var action_count:=0

func _ready() -> void:
    var world:=WorldEnvironment.new()
    var env:=Environment.new()
    env.background_mode=Environment.BG_COLOR
    env.background_color=Color("#122533")
    env.ambient_light_source=Environment.AMBIENT_SOURCE_COLOR
    env.ambient_light_color=Color("#9ebfce")
    env.ambient_light_energy=0.7
    world.environment=env
    add_child(world)
    var light:=DirectionalLight3D.new()
    light.rotation_degrees=Vector3(-45,-25,0)
    light.light_energy=1.3
    light.shadow_enabled=true
    add_child(light)
    _box(Vector3(1,-0.2,0),Vector3(19,0.4,6),Color("#28434f"),true)
    for x in range(-6,9):
        _box(Vector3(x,0.012,1.9),Vector3(0.5,0.024,0.08),Color("#6b8e99"),false)
    _box(Vector3(1.4,0.45,-1.15),Vector3(0.55,0.9,0.55),Color("#edaf4d"),false)
    _box(Vector3(5.5,0.02,0),Vector3(1.2,0.04,3.7),Color("#41c6ae"),false)
    gate=Node3D.new()
    gate.position=Vector3(3.2,1.5,0)
    add_child(gate)
    var body:=StaticBody3D.new()
    gate.add_child(body)
    gate_shape=CollisionShape3D.new()
    var gate_box:=BoxShape3D.new()
    gate_box.size=Vector3(0.22,3,4)
    gate_shape.shape=gate_box
    body.add_child(gate_shape)
    var mesh:=MeshInstance3D.new()
    var box:=BoxMesh.new()
    box.size=gate_box.size
    mesh.mesh=box
    var mat:=StandardMaterial3D.new()
    mat.albedo_color=Color("#d97055")
    mesh.material_override=mat
    gate.add_child(mesh)
    var camera:=Camera3D.new()
    camera.position=Vector3(1,5.6,12.8)
    camera.fov=48
    add_child(camera)
    camera.look_at(Vector3(1,0.9,0))
    camera.current=true
    actor=CharacterBody3D.new()
    actor.name="Player"
    actor.position=Vector3(-4,0.02,0)
    var collider:=CollisionShape3D.new()
    var capsule:=CapsuleShape3D.new()
    capsule.radius=0.35
    capsule.height=2.4
    collider.shape=capsule
    collider.position.y=1.2
    actor.add_child(collider)
    add_child(actor)
    model=MODEL.instantiate()
    actor.add_child(model)
    player=_find_player(model)
    for name in ["Idle","Walk","Run","Jump"]:
        player.get_animation(name).loop_mode=Animation.LOOP_NONE if name=="Jump" else Animation.LOOP_LINEAR
    var machine:=AnimationNodeStateMachine.new()
    for name in ["Idle","Walk","Run","Jump"]:
        var clip:=AnimationNodeAnimation.new()
        clip.animation=name
        machine.add_node(name,clip)
    for a in ["Idle","Walk","Run","Jump"]:
        for b in ["Idle","Walk","Run","Jump"]:
            if a==b: continue
            var transition:=AnimationNodeStateMachineTransition.new()
            transition.xfade_time=0.12
            machine.add_transition(a,b,transition)
    tree=AnimationTree.new()
    tree.tree_root=machine
    model.add_child(tree)
    tree.anim_player=tree.get_path_to(player)
    tree.root_node=NodePath("..")
    tree.active=true
    playback=tree.get("parameters/playback")
    playback.start("Idle")

func _physics_process(delta:float) -> void:
    if playback==null: return
    var direction:=Input.get_axis("left","right")
    var running:=Input.is_action_pressed("run")
    actor.velocity.x=direction*(4.2 if running else 2.4)
    actor.velocity.z=0
    actor.velocity.y-=9.8*delta
    if (Input.is_action_just_pressed("jump") or queued_jump) and actor.is_on_floor():
        actor.velocity.y=5.0
    queued_jump=false
    if Input.is_action_just_pressed("interact") or queued_action:
        _interact()
    queued_action=false
    actor.move_and_slide()
    actor.position.x=clampf(actor.position.x,-6,7)
    if direction!=0:
        # Imported mesh visibly faces local +Z, so locomotion faces world +/-X.
        model.rotation.y=PI/2 if direction>0 else -PI/2
    var next:="jump" if not actor.is_on_floor() else ("run" if running and absf(direction)>0.01 else ("walk" if absf(direction)>0.01 else "idle"))
    if next!=state:
        state=next
        playback.travel(state.capitalize())
    if door_open and actor.position.x>5.0:
        won=true

func _interact() -> void:
    if absf(actor.position.x-1.4)>1.6 or opening or door_open: return
    action_count+=1
    opening=true
    var tween:=create_tween()
    tween.tween_property(gate,"position:y",4.9,0.6).set_trans(Tween.TRANS_CUBIC)
    tween.tween_callback(func():
        gate_shape.set_deferred("disabled",true)
        door_open=true
        opening=false)

func _find_player(node:Node) -> AnimationPlayer:
    if node is AnimationPlayer: return node
    for child in node.get_children():
        var found:=_find_player(child)
        if found!=null: return found
    return null

func _box(at:Vector3,size:Vector3,color:Color,collision:bool) -> void:
    var mesh:=MeshInstance3D.new()
    var box:=BoxMesh.new()
    box.size=size
    mesh.mesh=box
    mesh.position=at
    var mat:=StandardMaterial3D.new()
    mat.albedo_color=color
    mat.roughness=0.8
    mesh.material_override=mat
    add_child(mesh)
    if collision:
        var body:=StaticBody3D.new()
        body.position=at
        var shape:=CollisionShape3D.new()
        var bounds:=BoxShape3D.new()
        bounds.size=size
        shape.shape=bounds
        body.add_child(shape)
        add_child(body)

func observation() -> Dictionary:
    return {"mode":"3d","position":[actor.position.x,actor.position.y,actor.position.z],
        "velocity":[actor.velocity.x,actor.velocity.y,actor.velocity.z],"state":state,
        "grounded":actor.is_on_floor(),"clip":playback.get_current_node(),
        "clip_time":playback.get_current_play_position(),"door_open":door_open,
        "opening":opening,"won":won,"action_count":action_count,
        "can_interact":absf(actor.position.x-1.4)<=1.6,"goal_x":5.0}
