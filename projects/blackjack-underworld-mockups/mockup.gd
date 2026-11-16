extends Control

@export var mode: String = "roster"

const BG := Color("#111111")
const PANEL := Color("#191919")
const PANEL_ALT := Color("#202020")
const PANEL_SOFT := Color("#262626")
const BORDER := Color("#686868")
const TEXT := Color("#ECE9E2")
const MUTED := Color("#A6A29A")
const GOLD := Color("#C7A96D")
const GREEN := Color("#91B89B")
const RED := Color("#CF8580")
const CARD := Color("#E9E5DC")
const INK := Color("#171717")

func _ready() -> void:
    mouse_filter = Control.MOUSE_FILTER_IGNORE
    queue_redraw()

func _draw() -> void:
    draw_rect(Rect2(0, 0, 1600, 900), BG)
    _box(Rect2(48, 42, 1504, 816), PANEL, BORDER, 26, 1)
    if mode == "roster":
        _draw_roster()
    elif mode == "blackjack":
        _draw_blackjack()
    else:
        _draw_underworld()

func _box(rect: Rect2, fill: Color, border: Color = BORDER, radius: int = 14, border_width: int = 1) -> void:
    var style := StyleBoxFlat.new()
    style.bg_color = fill
    style.border_color = border
    style.set_border_width_all(border_width)
    style.set_corner_radius_all(radius)
    draw_style_box(style, rect)
func _label(x: float, y: float, value: String, size: int = 18, color: Color = TEXT) -> void:
    draw_string(ThemeDB.fallback_font, Vector2(x, y), value, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)

func _center(rect: Rect2, y: float, value: String, size: int = 18, color: Color = TEXT) -> void:
    draw_string(ThemeDB.fallback_font, Vector2(rect.position.x, y), value, HORIZONTAL_ALIGNMENT_CENTER, rect.size.x, size, color)

func _pill(rect: Rect2, value: String, fill: Color, ink: Color = TEXT, size: int = 14) -> void:
    _box(rect, fill, fill, int(rect.size.y / 2.0), 0)
    _center(rect, rect.position.y + rect.size.y * 0.67, value, size, ink)

func _header(title: String, subtitle: String, metrics: Array[String]) -> void:
    _label(88, 91, title, 27, TEXT)
    _label(90, 119, subtitle, 13, MUTED)
    for i in range(metrics.size()):
        var rect := Rect2(934.0 + i * 182.0, 69, 166, 54)
        _box(rect, PANEL_ALT, Color("#484848"), 12, 1)
        _center(rect, 102, metrics[i], 14, GOLD if i == 0 else TEXT)
    draw_line(Vector2(80, 145), Vector2(1520, 145), Color("#3C3C3C"), 1)

func _avatar(cx: float, cy: float, accent: Color = MUTED, scale: float = 1.0) -> void:
    draw_circle(Vector2(cx, cy), 27.0 * scale, Color("#242424"))
    draw_arc(Vector2(cx, cy), 27.0 * scale, 0.0, TAU, 48, accent, 1.5, true)
    draw_circle(Vector2(cx, cy - 8.0 * scale), 7.0 * scale, accent)
    draw_arc(Vector2(cx, cy + 21.0 * scale), 15.0 * scale, PI, TAU, 32, accent, 4.0 * scale, true)

func _card(x: float, y: float, w: float, h: float, rank: String, suit: String, selected: bool = false, back: bool = false) -> void:
    if back:
        _box(Rect2(x, y, w, h), Color("#303030"), Color("#8B8069"), 9, 1)
        draw_rect(Rect2(x + 9, y + 9, w - 18, h - 18), Color("#38342E"), false, 1)
        draw_line(Vector2(x + 12, y + h - 12), Vector2(x + w - 12, y + 12), Color("#71654F"), 1)
        draw_line(Vector2(x + 12, y + 12), Vector2(x + w - 12, y + h - 12), Color("#71654F"), 1)
        _center(Rect2(x, y + h * 0.42, w, 24), y + h * 0.62, "✦", 20, GOLD)
        return
    _box(Rect2(x, y, w, h), CARD, Color("#F5F1E8"), 9, 1)
    var ink := RED if suit == "♥" or suit == "♦" else INK
    var rank_size := 21 if w >= 75.0 else 14
    var suit_size := 19 if w >= 75.0 else 13
    _label(x + 9, y + 25, rank, rank_size, ink)
    _label(x + 9, y + 47, suit, suit_size, ink)
    _label(x + w - 24, y + h - 10, suit, suit_size, ink)
    if selected:
        draw_rect(Rect2(x - 4, y - 4, w + 8, h + 8), GOLD, false, 3)

func _human_panel(x: float, y: float, title: String, role: String, status: String, cards: Array, status_color: Color) -> void:
    _box(Rect2(x, y, 335, 150), PANEL_ALT, Color("#555555"), 16, 1)
    _avatar(x + 39, y + 76, status_color, 0.9)
    _label(x + 78, y + 34, title, 15, TEXT)
    _label(x + 78, y + 55, role, 11, MUTED)
    _label(x + 78, y + 77, status, 12, status_color)
    var card_x := x + 78.0
    for card_data in cards:
        _card(card_x, y + 88, 39, 52, str(card_data[0]), str(card_data[1]))
        card_x += 46.0

func _empty_seat(x: float, y: float) -> void:
    _box(Rect2(x, y, 335, 150), Color("#171717"), Color("#444444"), 16, 1)
    draw_circle(Vector2(x + 39, y + 76), 25, Color("#202020"))
    draw_arc(Vector2(x + 39, y + 76), 25, 0, TAU, 48, Color("#666666"), 1, true)
    draw_line(Vector2(x + 29, y + 76), Vector2(x + 49, y + 76), MUTED, 2)
    draw_line(Vector2(x + 39, y + 66), Vector2(x + 39, y + 86), MUTED, 2)
    _label(x + 78, y + 65, "OPEN SEAT", 14, MUTED)
    _label(x + 78, y + 88, "Add a 4th person", 11, Color("#777777"))

func _people_row(show_results: bool = false) -> void:
    _label(92, 661, "HUMAN PLAYERS", 12, MUTED)
    var first_status := "LOSS · 16" if show_results else "STAND · 16"
    var second_status := "WIN · 18" if show_results else "STAND · 18"
    _human_panel(95, 678, "PERSON 01", "CAUTIOUS · THRESHOLD 16", first_status, [["10", "♥"], ["6", "♣"]], RED if show_results else GREEN)
    _human_panel(450, 678, "PERSON 02", "NORMAL · THRESHOLD 17", second_status, [["9", "♦"], ["9", "♣"]], GREEN)
    _human_panel(805, 678, "PERSON 03", "RISKY · THRESHOLD 18", "BUST · 24", [["10", "♠"], ["8", "♦"], ["6", "♥"]], RED)
    _empty_seat(1160, 678)
func _draw_roster() -> void:
    _header("HUMAN ROSTER", "Choose the people who will play Blackjack for you.", ["3 / 4 SELECTED", "6 AVAILABLE", "NEW RUN"])
    var names := ["PERSON 01", "PERSON 02", "PERSON 03", "PERSON 04", "PERSON 05", "PERSON 06"]
    var roles := ["CAUTIOUS", "NORMAL", "RISKY", "CAUTIOUS", "NORMAL", "RISKY"]
    var thresholds := ["STANDS AT 16", "STANDS AT 17", "STANDS AT 18", "STANDS AT 16", "STANDS AT 17", "STANDS AT 18"]
    var selected := [true, true, true, false, false, false]
    var accents := [GREEN, GOLD, RED, GREEN, GOLD, RED]
    for i in range(6):
        var col := i % 3
        var row := int(i / 3)
        var x := 95.0 + col * 470.0
        var y := 190.0 + row * 215.0
        _roster_card(x, y, names[i], roles[i], thresholds[i], selected[i], accents[i], i + 1)

    _box(Rect2(95, 635, 1410, 170), PANEL_ALT, Color("#555555"), 18, 1)
    _label(125, 672, "YOUR TEAM", 13, MUTED)
    _label(125, 697, "3 selected · 1 open slot", 17, TEXT)
    for i in range(3):
        _avatar(480 + i * 95, 715, [GREEN, GOLD, RED][i], 0.85)
        _label(458 + i * 95, 765, "P0" + str(i + 1), 11, MUTED)
    draw_circle(Vector2(770, 715), 23, Color("#222222"))
    draw_arc(Vector2(770, 715), 23, 0, TAU, 48, Color("#666666"), 1, true)
    _center(Rect2(747, 700, 46, 30), 722, "+", 22, MUTED)
    _label(830, 718, "Select 3 or 4 people. Their cards become your hand.", 14, MUTED)
    _pill(Rect2(1260, 687, 205, 58), "START RUN", GOLD, Color("#171717"), 15)

func _roster_card(x: float, y: float, name: String, role: String, threshold: String, chosen: bool, accent: Color, index: int) -> void:
    _box(Rect2(x, y, 440, 190), PANEL_ALT, accent if chosen else Color("#555555"), 18, 1)
    _avatar(x + 65, y + 92, accent, 1.25)
    _label(x + 120, y + 66, name, 20, TEXT)
    _label(x + 120, y + 95, role, 13, accent)
    _label(x + 120, y + 121, threshold, 12, MUTED)
    _label(x + 120, y + 153, "AUTONOMOUS BLACKJACK", 10, Color("#777777"))
    _pill(Rect2(x + 320, y + 25, 92, 32), "SELECTED" if chosen else "AVAILABLE", accent if chosen else Color("#333333"), Color("#171717") if chosen else MUTED, 10)
    _label(x + 25, y + 177, "ID 0" + str(index), 9, Color("#777777"))
func _draw_blackjack() -> void:
    _header("GAME TABLE", "HUMAN CASINO  /  ROUND 01  /  AUTONOMOUS BLACKJACK", ["ANTE 01", "TARGET 300", "SCORE 140"])
    _box(Rect2(80, 160, 1440, 475), Color("#171717"), Color("#565656"), 22, 1)
    _label(112, 198, "DEALER", 13, MUTED)
    _label(112, 224, "Plays after all people finish.", 11, Color("#777777"))

    _box(Rect2(555, 202, 490, 190), PANEL_ALT, Color("#777777"), 18, 1)
    _center(Rect2(555, 215, 490, 28), 236, "DEALER HAND", 14, MUTED)
    _card(700, 250, 86, 122, "10", "♦")
    _card(810, 250, 86, 122, "?", "?", false, true)
    _pill(Rect2(920, 267, 100, 30), "WAITING", Color("#38342D"), GOLD, 11)
    _label(920, 327, "1 card up", 11, MUTED)

    _center(Rect2(160, 430, 1280, 35), 455, "PEOPLE PLAY AUTONOMOUSLY", 19, TEXT)
    _center(Rect2(160, 466, 1280, 25), 485, "Each person follows their own threshold. You do not choose Hit or Stand.", 13, MUTED)
    _draw_phase_steps()

    _people_row(false)

func _draw_phase_steps() -> void:
    var labels := ["INITIAL DEAL", "HIT / STAND", "DEALER PLAYS", "OUTCOMES"]
    for i in range(4):
        var x := 320.0 + i * 250.0
        var active := i == 1
        _pill(Rect2(x, 535, 205, 38), labels[i], GOLD if active else Color("#2B2B2B"), Color("#171717") if active else MUTED, 11)
        if i < 3:
            draw_line(Vector2(x + 208, 554), Vector2(x + 244, 554), Color("#5C5C5C"), 2)

func _draw_underworld() -> void:
    _header("GAME TABLE", "UNDERWORLD  /  ROUND 01  /  CHOOSE YOUR PLAY", ["ANTE 01", "HANDS 3 / 4", "140 / 300"])
    _box(Rect2(80, 160, 1440, 475), Color("#171717"), Color("#565656"), 22, 1)
    _label(112, 198, "YOUR UNDERWORLD HAND  ·  7 CARDS", 14, MUTED)
    _box(Rect2(1200, 178, 270, 88), PANEL_ALT, Color("#555555"), 12, 1)
    _label(1220, 208, "DEALER RESULT", 10, MUTED)
    _label(1220, 238, "17  ·  STAND", 18, GREEN)

    var cards := [["10", "♥"], ["6", "♣"], ["9", "♦"], ["9", "♣"], ["10", "♠"], ["8", "♦"], ["6", "♥"]]
    var sources := ["P01", "P01", "P02", "P02", "P03", "P03", "P03"]
    for i in range(cards.size()):
        var x := 275.0 + i * 116.0
        var selected := i == 0 or i == 4
        var y := 272.0 if selected else 286.0
        _card(x, y, 96, 142, cards[i][0], cards[i][1], selected)
        _center(Rect2(x, 432, 96, 20), 449, sources[i], 10, GOLD if selected else MUTED)

    _box(Rect2(190, 478, 1080, 112), PANEL_ALT, Color("#555555"), 16, 1)
    _label(218, 510, "SELECTED", 10, MUTED)
    _label(218, 545, "10♥  +  10♠", 21, TEXT)
    _pill(Rect2(490, 500, 135, 42), "PAIR", Color("#3A3326"), GOLD, 13)
    _label(665, 510, "CHIPS", 10, MUTED)
    _label(665, 550, "30", 24, TEXT)
    _label(790, 510, "MULT", 10, MUTED)
    _label(790, 550, "× 2", 24, TEXT)
    _label(930, 510, "PREVIEW SCORE", 10, MUTED)
    _label(930, 550, "60", 24, GOLD)
    _pill(Rect2(1310, 500, 175, 72), "PLAY HAND", GOLD, Color("#171717"), 15)

    _people_row(true)
