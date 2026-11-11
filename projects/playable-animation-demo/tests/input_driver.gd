extends SceneTree
var game: Node
var output := ""
var agent_dir := ""
var capture := true
var index := 0
var samples: Array = []
var results: Array = []
var keys_held: Array = []
const KEYS={"A":KEY_A,"D":KEY_D,"LEFT":KEY_LEFT,"RIGHT":KEY_RIGHT,"SHIFT":KEY_SHIFT,"SPACE":KEY_SPACE,"E":KEY_E}
const FPS=24

func _initialize() -> void:
    call_deferred("_run")

func option(args:PackedStringArray,name:String,fallback:String="") -> String:
    for n in range(args.size()-1):
        if args[n]==name: return args[n+1]
    return fallback

func _run() -> void:
    var args:=OS.get_cmdline_user_args()
    output=option(args,"--output")
    agent_dir=option(args,"--agent-dir")
    capture=not "--no-images" in args
    root.size=Vector2i(1280,720)
    DirAccess.make_dir_recursive_absolute(output.path_join("frames"))
    game=load("res://game.tscn").instantiate()
    root.add_child(game)
    await process_frame
    await process_frame
    paused=true
    if not agent_dir.is_empty():
        DirAccess.make_dir_recursive_absolute(agent_dir)
        _write(agent_dir.path_join("state.json"),{"ready":true,"id":0,"observation":game.observation()})
        var last_id:=0
        var idle_since:=Time.get_ticks_msec()
        while Time.get_ticks_msec()-idle_since<300000:
            await create_timer(0.1,true).timeout
            var command_path:=agent_dir.path_join("command.json")
            if not FileAccess.file_exists(command_path): continue
            var command:Variant=JSON.parse_string(FileAccess.get_file_as_string(command_path))
            if not command is Dictionary: continue
            var id:=int(command.get("id",0))
            if id<=last_id: continue
            last_id=id
            idle_since=Time.get_ticks_msec()
            if command.get("quit",false): break
            var result:=await execute(command)
            _write(agent_dir.path_join("state.json"),{"ready":true,"id":id,"result":result,"observation":game.observation()})
        finish()
        return
    var scenario:Variant=JSON.parse_string(FileAccess.get_file_as_string(option(args,"--scenario")))
    if not scenario is Array:
        push_error("Invalid scenario"); quit(2); return
    for step in scenario:
        await execute(step)
    finish()

func key(name:String,pressed:bool) -> void:
    var event:=InputEventKey.new()
    event.physical_keycode=KEYS[name]
    event.keycode=KEYS[name]
    event.pressed=pressed
    Input.parse_input_event(event)

func mouse(at:Vector2,pressed:bool) -> void:
    var motion:=InputEventMouseMotion.new()
    motion.position=at
    motion.global_position=at
    Input.parse_input_event(motion)
    var event:=InputEventMouseButton.new()
    event.position=at
    event.global_position=at
    event.button_index=MOUSE_BUTTON_LEFT
    event.button_mask=MOUSE_BUTTON_MASK_LEFT if pressed else 0
    event.pressed=pressed
    Input.parse_input_event(event)

func execute(command:Dictionary) -> Dictionary:
    var start_observation:Dictionary=game.observation()
    var first:=index
    var frames:=clampi(int(command.get("frames",12)),3,240)
    var id:Variant=command.get("id",results.size()+1)
    var pressed: Array=command.get("keys",[])
    for name in pressed:
        if not KEYS.has(name):
            push_error("Unknown key: "+str(name)); quit(2); return {}
    paused=false
    for name in pressed: key(name,true)
    keys_held=pressed
    var click:Vector2=Vector2.ZERO
    if command.has("click"):
        var button:Button=game.buttons.get(command["click"])
        if button==null:
            push_error("Unknown button"); quit(2); return {}
        click=button.get_global_rect().get_center()
        mouse(click,true)
    var observed:Array=[]
    for n in range(frames):
        if n==1 and command.has("click"): mouse(click,false)
        await process_frame
        if capture: await RenderingServer.frame_post_draw
        var observation:Dictionary=game.observation()
        observed.append(observation)
        var filename:="frame_%04d.png" % index
        if capture:
            var error:=root.get_texture().get_image().save_png(output.path_join("frames").path_join(filename))
            if error!=OK:
                push_error("Frame save failed"); quit(3); return {}
        samples.append({"sequence_index":index,"timestamp_seconds":float(index)/FPS,
            "image":"frames/"+filename,"command":id,"game":observation})
        index+=1
    for name in pressed: key(name,false)
    keys_held=[]
    paused=true
    var after:Dictionary=game.observation()
    var failures:Array=[]
    var expected:Dictionary=command.get("expect",{})
    for field in expected:
        var value:Variant=expected[field]
        var pass_check:=true
        match field:
            "x_min": pass_check=float(after["position"][0])>=float(value)
            "x_max": pass_check=float(after["position"][0])<=float(value)
            "seen_state": pass_check=observed.any(func(o): return o["state"]==value)
            "sprite_changed":
                var values:Dictionary={}
                for o in observed: values[o.get("sprite_frame",-1)]=true
                pass_check=values.size()>1
            "clip_advanced":
                var values:Dictionary={}
                for o in observed: values[str(o.get("clip_time",0))]=true
                pass_check=values.size()>1
            _:
                pass_check=after.get(field)==value
        if not pass_check: failures.append(field)
    var result:={"id":id,"label":command.get("label","agent step"),"input":command,
        "first_frame":first,"last_frame":index-1,"before":start_observation,"after":after,
        "failures":failures,"passed":failures.is_empty(),
        "image":output.path_join("frames/frame_%04d.png" % (index-1))}
    results.append(result)
    _write(output.path_join("metrics.json"),{"fps":FPS,"sample_count":samples.size(),"samples":samples})
    _write(output.path_join("steps.json"),results)
    print("STEP_", "PASS" if failures.is_empty() else "FAIL"," | ",result["label"]," | ",JSON.stringify(after))
    return result

func finish() -> void:
    var failed:=results.filter(func(r): return not r["passed"]).size()
    _write(output.path_join("result.json"),{"passed":failed==0,"failed_steps":failed,
        "steps":results.size(),"frames":index,"fps":FPS,"input_method":"Input.parse_input_event",
        "state_control":"sequential runtime, no pose seek","capture":capture})
    paused=false
    print("GAMEPLAY_E2E_", "PASS" if failed==0 else "FAIL")
    quit(0 if failed==0 else 1)

func _write(path:String,data:Variant) -> void:
    # Atomic snapshots let the agent poll without observing partial JSON.
    var temp:=path+".tmp"
    var file:=FileAccess.open(temp,FileAccess.WRITE)
    file.store_string(JSON.stringify(data,"  "))
    file.close()
    DirAccess.rename_absolute(temp,path)
