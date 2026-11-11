extends SceneTree

func _initialize() -> void:
    call_deferred("_run")

func _run() -> void:
    var args := OS.get_cmdline_user_args()
    var jobs_path := _option(args, "--jobs-json", "")
    if not jobs_path.is_empty():
        var jobs_file := FileAccess.open(_absolute(jobs_path), FileAccess.READ)
        if jobs_file == null:
            push_error("CONTACT_SHEET_JOBS_OPEN_FAILED: " + jobs_path)
            quit(9)
            return
        var parsed: Variant = JSON.parse_string(jobs_file.get_as_text())
        jobs_file.close()
        if not parsed is Array or parsed.is_empty():
            push_error("CONTACT_SHEET_JOBS_INVALID")
            quit(9)
            return
        for job_value in parsed:
            if not job_value is Dictionary:
                push_error("CONTACT_SHEET_JOB_INVALID")
                quit(9)
                return
            var error_code := _build_job(job_value)
            if error_code != OK:
                quit(error_code)
                return
        print("CONTACT_SHEET_BATCH_PASS | jobs=", parsed.size())
        quit(0)
        return

    var job := {
        "input_dir": _option(args, "--input-dir", ""),
        "output": _option(args, "--output", ""),
        "prefix": _option(args, "--prefix", ""),
        "start_index": int(_option(args, "--start-index", "-1")),
        "end_index": int(_option(args, "--end-index", "-1")),
        "max_frames": int(_option(args, "--max-frames", "24")),
        "columns": int(_option(args, "--columns", "6")),
        "tile_width": int(_option(args, "--tile-width", "320")),
        "tile_height": int(_option(args, "--tile-height", "180")),
        "fps": float(_option(args, "--fps", "0")),
        "metrics": _option(args, "--metrics", ""),
        "selected_dir": _option(args, "--selected-dir", "")
    }
    quit(_build_job(job))

func _build_job(job: Dictionary) -> int:
    var input_dir := _absolute(str(job.get("input_dir", "")))
    var output := _absolute(str(job.get("output", "")))
    var prefix := str(job.get("prefix", ""))
    var start_index := int(job.get("start_index", -1))
    var end_index := int(job.get("end_index", -1))
    var max_frames := int(job.get("max_frames", 24))
    var columns := int(job.get("columns", 6))
    var tile_width := int(job.get("tile_width", 320))
    var tile_height := int(job.get("tile_height", 180))
    var fps := float(job.get("fps", 0))
    var metrics_path := str(job.get("metrics", ""))
    var selected_dir_value := str(job.get("selected_dir", ""))
    if selected_dir_value.is_empty():
        selected_dir_value = output.get_base_dir().path_join("selected")
    var selected_dir := _absolute(selected_dir_value)
    if input_dir.is_empty() or output.is_empty() or max_frames < 1 or columns < 1 or tile_width < 1 or tile_height < 1:
        push_error("CONTACT_SHEET_ARGUMENTS_INVALID")
        return 2

    var names := DirAccess.get_files_at(input_dir)
    var records: Array[Dictionary] = []
    for name in names:
        if name.get_extension().to_lower() != "png":
            continue
        var frame_index := _frame_index(name, prefix)
        if frame_index < 0 or (start_index >= 0 and frame_index < start_index):
            continue
        if end_index >= 0 and frame_index >= end_index:
            continue
        records.append({"name": name, "index": frame_index})
    records.sort_custom(func(a, b): return int(a["index"]) < int(b["index"]))
    if records.is_empty():
        push_error("CONTACT_SHEET_NO_INPUT_FRAMES: " + input_dir)
        return 3

    var selected := _sample(records, max_frames)
    var timestamps: Dictionary = {}
    if not metrics_path.is_empty():
        var metrics_file := FileAccess.open(_absolute(metrics_path), FileAccess.READ)
        if metrics_file == null:
            push_error("CONTACT_SHEET_METRICS_OPEN_FAILED: " + metrics_path)
            return 8
        var metrics_data: Variant = JSON.parse_string(metrics_file.get_as_text())
        metrics_file.close()
        if not metrics_data is Dictionary:
            push_error("CONTACT_SHEET_METRICS_INVALID")
            return 8
        for sample in metrics_data.get("samples", []):
            timestamps[int(sample.get("sequence_index", -1))] = float(sample.get("timestamp_seconds", 0.0))

    var rows := int(ceil(float(selected.size()) / float(columns)))
    var sheet := Image.create(columns * tile_width, rows * tile_height, false, Image.FORMAT_RGBA8)
    sheet.fill(Color(0.025, 0.035, 0.05, 1.0))
    DirAccess.make_dir_recursive_absolute(output.get_base_dir())
    DirAccess.make_dir_recursive_absolute(selected_dir)
    var manifest_frames: Array[Dictionary] = []
    for slot in range(selected.size()):
        var record: Dictionary = selected[slot]
        var source_path := input_dir.path_join(str(record["name"]))
        var frame := Image.load_from_file(source_path)
        if frame == null or frame.is_empty():
            push_error("CONTACT_SHEET_FRAME_LOAD_FAILED: " + source_path)
            return 4
        var scale: float = minf(float(tile_width) / float(frame.get_width()), float(tile_height) / float(frame.get_height()))
        var width: int = maxi(1, int(round(frame.get_width() * scale)))
        var height: int = maxi(1, int(round(frame.get_height() * scale)))
        frame.resize(width, height, Image.INTERPOLATE_LANCZOS)
        var col := slot % columns
        var row := int(slot / columns)
        var destination := Vector2i(
            col * tile_width + int((tile_width - width) / 2),
            row * tile_height + int((tile_height - height) / 2)
        )
        sheet.blit_rect(frame, Rect2i(0, 0, width, height), destination)
        var selected_name := "frame_%03d.png" % slot
        var selected_path := selected_dir.path_join(selected_name)
        var copy_error := DirAccess.copy_absolute(source_path, selected_path)
        if copy_error != OK:
            push_error("CONTACT_SHEET_FRAME_COPY_FAILED: " + source_path)
            return 5
        var frame_index := int(record["index"])
        var timestamp: Variant = timestamps.get(frame_index)
        if timestamp == null and fps > 0.0:
            timestamp = snapped(float(frame_index) / fps, 0.0001)
        manifest_frames.append({
            "slot": slot,
            "frame_index": frame_index,
            "timestamp_seconds": timestamp,
            "source": source_path,
            "selected": selected_path
        })

    var save_error := sheet.save_png(output)
    if save_error != OK:
        push_error("CONTACT_SHEET_SAVE_FAILED: " + output)
        return 6
    var manifest := {
        "schema_version": 1,
        "input_dir": input_dir,
        "prefix": prefix,
        "source_frame_count": records.size(),
        "selected_frame_count": selected.size(),
        "fps": fps,
        "metrics": metrics_path,
        "columns": columns,
        "tile_size": [tile_width, tile_height],
        "contact_sheet": output,
        "selected_dir": selected_dir,
        "frames": manifest_frames
    }
    var manifest_path := output.get_basename() + ".json"
    var file := FileAccess.open(manifest_path, FileAccess.WRITE)
    if file == null:
        push_error("CONTACT_SHEET_MANIFEST_OPEN_FAILED")
        return 7
    file.store_string(JSON.stringify(manifest, "\t"))
    file.close()
    print("CONTACT_SHEET_PASS | source=", records.size(), " | selected=", selected.size(), " | ", output)
    return OK

func _sample(records: Array[Dictionary], maximum: int) -> Array[Dictionary]:
    if records.size() <= maximum:
        return records
    var result: Array[Dictionary] = []
    if maximum == 1:
        result.append(records[int(records.size() / 2)])
        return result
    for slot in range(maximum):
        var index := int(round(float(slot) * float(records.size() - 1) / float(maximum - 1)))
        result.append(records[index])
    return result

func _frame_index(filename: String, prefix: String) -> int:
    var stem := filename.get_basename()
    if not prefix.is_empty():
        if not stem.begins_with(prefix):
            return -1
        var suffix := stem.substr(prefix.length())
        return int(suffix) if suffix.is_valid_int() else -1
    var position := stem.length() - 1
    while position >= 0 and stem.substr(position, 1).is_valid_int():
        position -= 1
    var digits := stem.substr(position + 1)
    return int(digits) if digits.is_valid_int() else -1

func _option(args: PackedStringArray, key: String, fallback: String) -> String:
    for index in range(args.size() - 1):
        if args[index] == key:
            return args[index + 1]
    return fallback

func _absolute(path: String) -> String:
    if path.begins_with("res://"):
        return ProjectSettings.globalize_path(path)
    return path
