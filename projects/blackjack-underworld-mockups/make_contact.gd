extends SceneTree

func _initialize() -> void:
    var out := Image.create(1460, 830, false, Image.FORMAT_RGB8)
    out.fill(Color("#121212"))
    var files := [
        "res://previews/01-human-roster.png",
        "res://previews/02-game-table-blackjack.png",
        "res://previews/03-game-table-underworld.png"
    ]
    var positions := [Vector2i(0, 0), Vector2i(740, 0), Vector2i(0, 425)]
    for i in range(files.size()):
        var img := Image.load_from_file(files[i])
        if img == null:
            push_error("Could not load " + files[i])
            quit(1)
            return
        img.resize(720, 405, Image.INTERPOLATE_LANCZOS)
        out.blit_rect(img, Rect2i(0, 0, 720, 405), positions[i])
    var path := "res://previews/contact-sheet.jpg"
    var err := out.save_jpg(path, 0.58)
    print("CONTACT_SHEET ", path, " err=", err, " size=", out.get_size())
    quit(0 if err == OK else 1)
