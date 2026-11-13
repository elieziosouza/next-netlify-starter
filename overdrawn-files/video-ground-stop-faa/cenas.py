"""Cenas do vídeo: frase da narração em que cada cena começa, vídeos de fundo e o desenho dos gráficos."""
from motor import *

B = "/home/user/next-netlify-starter/overdrawn-files/video-ground-stop-faa/broll/"
BR = {
    "taxi": B + "01-abertura_airplane-moving-trough-the-airport-track-in-the-morning.mp4",
    "gate": B + "01-abertura_flight-getting-ready-for-departure.mp4",
    "landing": B + "02-o-que-aconteceu_airplane-landing-in-illuminated-airport-tracks.mp4",
    "citynight": B + "02-o-que-aconteceu_plane-flying-over-a-city-at-night.mp4",
    "map": B + "02-o-que-aconteceu_world-map-in-a-digital-world.mp4",
    "code": B + "03-ataque_computer-code-in-the-screen.mp4",
    "flicker": B + "03-ataque_server-lights-flickering.mp4",
    "attack": B + "03-ataque_server-room-under-attack.mp4",
    "angry": B + "04-estrago_angry-passengers-in-the-airplane-boarding-gates.mp4",
    "checkin": B + "04-estrago_checking-in-at-the-airport-counter.mp4",
    "cart": B + "04-estrago_empty-airport-luggage-cart-close-up.mp4",
    "walking": B + "04-estrago_people-walking-around-an-airport.mp4",
    "falling": B + "05-custo_banknotes-falling-on-a-dark-background.mp4",
    "clock": B + "05-custo_little-clock-over-bills-background.mp4",
    "counting": B + "05-custo_money-counting-machine-counting-up-money.mp4",
    "burn": B + "05-custo_tower-of-100-dollars-being-burned-with-a-flame.mp4",
    "baggage": B + "06-quem-paga_baggage-claim-inside-a-modern-airport.mp4",
    "broke": B + "06-quem-paga_person-realizes-that-they-no-longer-have-money-in-his.mp4",
    "suitcase": B + "06-quem-paga_woman-walking-slowly-towards-a-terminal.mp4",
    "cables": B + "07-por-que_cables-in-a-datacenter.mp4",
    "fiber": B + "07-por-que_close-up-of-fiber-optics-in-a-server-room.mp4",
    "racks": B + "07-por-que_server-room-cables.mp4",
    "dusk": B + "08-fechamento_dusk-from-the-boarding-area-of-an-airport.mp4",
    "takeoff": B + "08-fechamento_plane-taking-off-at-dusk.mp4",
}

X0 = 120  # margem esquerda dos textos


def headline(img, lines, t, y=300, size=96, t0=0.25, color=WHITE, gap=1.08):
    f = F("black", size)
    for i, ln in enumerate(lines):
        c = RED if ln.startswith("!") else color
        rise(img, ln.lstrip("!"), f, X0, y + i * int(size * gap), t, t0 + i * 0.14, c)
    return y + len(lines) * int(size * gap)


# ---------------------------------------------------------------- cenas

def c_open(img, t, d):
    # painel de partidas que vira GROUND STOP
    kicker(img, "FRIDAY · NOV 13, 2026", X0, 170, t)
    rows = ["CHICAGO", "ATLANTA", "DALLAS", "DENVER", "NEW YORK", "LOS ANGELES", "SEATTLE"]
    times = ["3:05P", "3:10P", "3:15P", "3:20P", "3:25P", "3:35P", "3:40P"]
    fm = F("mono", 44)
    panel(img, (X0 - 30, 250, X0 + 1080, 250 + 80 + len(rows) * 74), 0.82, 14)
    text(img, "DEPARTURES", F("xbold", 30), X0, 290, AMBER, prog(t, 0.2), "lm")
    for i, (c, tm) in enumerate(zip(rows, times)):
        y = 360 + i * 74
        a = prog(t, 0.35 + i * 0.07, 0.3)
        text(img, tm, fm, X0, y, WHITE, a, "lm")
        text(img, c, fm, X0 + 190, y, WHITE, a, "lm")
        flip = 2.6 + i * 0.22
        if t < flip:
            text(img, "ON TIME", fm, X0 + 760, y, (120, 220, 120), a, "lm")
        else:
            pf = prog(t, flip, 0.15)
            text(img, "STOPPED", fm, X0 + 760, y, RED, pf, "lm")
    # relógio
    p = prog(t, 1.0, 0.5)
    text(img, "2:54 PM", F("black", 120), W - 120, 420, WHITE, p, "ra")
    text(img, "CENTRAL TIME", F("bold", 30), W - 120, 560, GREY, p, "ra")
    stamp(img, "NATIONWIDE GROUND STOP", W - 400, 820, t, 4.6, RED, 40)


def c_notstorm(img, t, d):
    items = [("NOT A STORM", 0.3), ("NOT AN ATTACK", 1.6)]
    f = F("black", 92)
    for i, (s, t0) in enumerate(items):
        y = 300 + i * 140
        rise(img, s, f, X0 + 120, y, t, t0)
        cross(img, X0 + 40, y + 48, 34, t, t0 + 0.4)
    rise(img, "A COMMUNICATION FAILURE", F("black", 92), X0 + 120, 600, t, 3.2, RED)
    p = prog(t, 3.6, 0.6)
    rect(img, (X0 + 120, 715, X0 + 120 + int(1330 * p), 727), RED, 1)


def c_chapters(img, t, d):
    kicker(img, "IN THIS VIDEO", X0, 230, t)
    items = ["What we know about the outage", "Why it keeps happening", "What a day like this costs"]
    for i, s in enumerate(items):
        t0 = 0.6 + i * d * 0.22
        y = 340 + i * 150
        rise(img, f"0{i+1}", F("black", 90), X0, y, t, t0, RED)
        rise(img, s, F("xbold", 64), X0 + 150, y + 14, t, t0 + 0.1)


def c_confirmed(img, t, d):
    kicker(img, "CONFIRMED", X0, 230, t)
    y = headline(img, ["NATIONWIDE", "!GROUND STOP"], t, 300, 120)
    rise(img, "The FAA called it a", F("med", 44), X0, y + 30, t, 1.0, GREY)
    rise(img, "“temporary telecommunications outage.”", F("serif", 72), X0, y + 90, t, 1.3)
    source(img, "Source: FAA statement, Nov 13, 2026", t)


def c_duffy(img, t, d):
    kicker(img, "SEAN DUFFY · TRANSPORTATION SECRETARY", X0, 200, t)
    yq = quote(img, "a communication issue impacting all Air Route Traffic Control Centers", "Statement, Nov 13, 2026",
               X0 + 40, 290, 1100, t, 0.4, 66)
    # grade de centros acendendo
    gx, gy = 1360, 300
    for i in range(20):
        cx, cy = gx + (i % 4) * 110, gy + (i // 4) * 110
        lit = t > d * 0.45 + i * 0.08
        d_ = ImageDraw.Draw(img)
        c = RED if lit else (90, 90, 90)
        r = 26 if lit and int(t * 4) % 2 == 0 else 22
        d_.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col(c, 0.95 * prog(t, 0.5 + i * 0.03, 0.3)))
    text(img, "EN-ROUTE CENTERS", F("bold", 26), gx - 26, gy + 560, GREY, prog(t, d * 0.45), "la")
    text(img, "ALL AFFECTED", F("black", 40), gx - 26, gy + 600, RED, prog(t, d * 0.55), "la")


def c_scale(img, t, d):
    kicker(img, "ON A NORMAL DAY", X0, 200, t)
    stats = [(44000, "{:,.0f}+", "FLIGHTS"), (3000000, "{:,.0f}+", "AIRLINE PASSENGERS"),
             (29000000, "{:,.0f}", "SQUARE MILES OF AIRSPACE")]
    for i, (v, fmt, lab) in enumerate(stats):
        t0 = 0.6 + i * d * 0.2
        y = 290 + i * 210
        if t >= t0:
            n = count(t, t0, 1.6, v)
            rise(img, fmt.format(n), F("black", 120), X0, y, t, t0, WHITE if i else RED)
            rise(img, lab, F("xbold", 40), X0 + 8, y + 140, t, t0 + 0.2, GREY)
    rise(img, "EVERY", F("black", 60), W - 120, 470, t, d * 0.75, WHITE, "ra")
    rise(img, "SINGLE DAY", F("black", 60), W - 120, 540, t, d * 0.78, RED, "ra")
    source(img, "Source: FAA, Air Traffic by the Numbers", t)


def c_links(img, t, d):
    kicker(img, "HOW IT WORKS", X0, 200, t)
    d_ = ImageDraw.Draw(img)
    # torre (esquerda) e avião (direita)
    p = prog(t, 0.4, 0.5)
    tx, ty, px, py = 420, 620, 1500, 420
    d_.polygon([(tx - 34, ty + 220), (tx + 34, ty + 220), (tx + 22, ty - 20), (tx - 22, ty - 20)], fill=col(WHITE, p * 0.9))
    d_.polygon([(tx - 70, ty - 20), (tx + 70, ty - 20), (tx + 95, ty - 110), (tx - 95, ty - 110)], fill=col(WHITE, p * 0.9))
    d_.rectangle((tx - 80, ty - 92, tx + 80, ty - 52), fill=col(DARK, p * 0.9))
    d_.rectangle((tx - 60, ty - 140, tx + 60, ty - 110), fill=col(WHITE, p * 0.9))
    text(img, "CONTROLLER", F("xbold", 34), tx, ty + 270, GREY, p, "mm")
    d_.polygon([(px - 130, py), (px + 130, py - 10), (px + 160, py), (px + 130, py + 10)], fill=col(WHITE, p))
    d_.polygon([(px - 10, py - 5), (px + 40, py - 5), (px - 40, py - 90), (px - 70, py - 90)], fill=col(WHITE, p))
    d_.polygon([(px - 10, py + 5), (px + 40, py + 5), (px - 40, py + 90), (px - 70, py + 90)], fill=col(WHITE, p))
    text(img, "PILOT", F("xbold", 34), px, py + 150, GREY, p, "mm")
    # ondas / linha de dados
    broken = t > d * 0.68
    n = 9
    for i in range(n):
        x = tx + 130 + i * (px - tx - 330) / (n - 1)
        y = ty - 80 + (py - ty + 80) * i / (n - 1)
        ph = (t * 2 - i * 0.2) % 1
        if broken and i in (4, 5):
            continue
        a = prog(t, 1.0 + i * 0.08, 0.2) * (0.4 + 0.6 * (1 - ph))
        d_.ellipse((x - 10, y - 10, x + 10, y + 10), fill=col(RED if broken else WHITE, a))
    rise(img, "RADIO VOICE", F("xbold", 40), 760, 330, t, 1.6)
    rise(img, "+ DATA LINES", F("xbold", 40), 760, 385, t, 2.2, GREY)
    if broken:
        cross(img, (tx + px) / 2 - 40, (ty + py) / 2 - 30, 46, t, d * 0.68)
        rise(img, "LINK LOST", F("black", 64), 960, 820, t, d * 0.7, RED, "mm")


def c_groundstop(img, t, d):
    kicker(img, "DEFINITION", X0, 230, t)
    rise(img, "GROUND", F("black", 200), X0, 300, t, 0.3)
    rise(img, "STOP", F("black", 200), X0, 500, t, 0.5, RED)
    f = F("med", 46)
    for i, ln in enumerate(["Nothing new takes off", "until every flight", "can be guided safely."]):
        rise(img, ln, f, 1140, 420 + i * 64, t, d * 0.45 + i * 0.15, WHITE)


def c_status(img, t, d):
    kicker(img, "THE ORDER", X0, 200, t)
    rows = [("IN THE AIR", "KEEP FLYING, LAND", WHITE), ("DEPARTURES", "STOPPED", RED),
            ("INTERNATIONAL", "CASE BY CASE", AMBER)]
    for i, (a_, b_, c) in enumerate(rows):
        t0 = 0.4 + i * d * 0.16
        y = 300 + i * 150
        p = prog(t, t0, 0.4)
        panel(img, (X0 - 20, y - 20, X0 - 20 + int(1500 * p), y + 110), 0.75, 12)
        rise(img, a_, F("xbold", 44), X0 + 20, y + 22, t, t0 + 0.15, GREY)
        rise(img, b_, F("black", 64), X0 + 560, y + 12, t, t0 + 0.25, c)
    t0 = d * 0.72
    rise(img, "UNTIL AT LEAST", F("xbold", 40), X0, 790, t, t0, GREY)
    rise(img, "11 PM EASTERN", F("black", 84), X0 + 380, 770, t, t0 + 0.15, WHITE)
    source(img, "Source: FAA advisories, Nov 13, 2026", t)


def c_attack_q(img, t, d):
    s = "CYBERATTACK?"
    f = F("black", 190)
    p = prog(t, 0.2, 0.6)
    jitter = (math.sin(t * 40) * 6) if t < 1.0 else 0
    text(img, s, f, W / 2 + jitter, H / 2, RED, p, "mm")


def c_officials(img, t, d):
    kicker(img, "WHAT OFFICIALS SAY", X0, 190, t)
    y = quote(img, "no indication of a nefarious act", "The White House", X0 + 40, 270, 1500, t, 0.4, 72)
    f = F("xbold", 44)
    t0 = d * 0.42
    rise(img, "DHS SECRETARY MARKWAYNE MULLIN:", F("bold", 30), X0, y + 10, t, t0, GREY)
    rise(img, "• Not a threat to the country", f, X0, y + 60, t, t0 + 0.3)
    rise(img, "• Not linked to this week's Microsoft outage", f, X0, y + 125, t, t0 + 0.6)
    stamp(img, "NO SIGN OF ATTACK — SO FAR", W - 560, 860, t, d * 0.8, AMBER, 46)


def c_software(img, t, d):
    kicker(img, "REPORTED BY BLOOMBERG", X0, 230, t)
    headline(img, ["SOFTWARE", "!UPDATE?"], t, 300, 150)
    stamp(img, "NOT CONFIRMED", W - 400, 330, t, d * 0.4, AMBER, 60)
    rise(img, "Official cause will be pinned in the description", F("med", 40), X0, 700, t, d * 0.7, GREY)


def c_damage(img, t, d):
    kicker(img, "BY FRIDAY AFTERNOON", X0, 200, t)
    n = count(t, 0.5, 2.2, 7000)
    rise(img, f"~{n:,.0f}", F("black", 210), X0, 260, t, 0.4, RED)
    rise(img, "FLIGHTS DELAYED OR CANCELED", F("black", 56), X0 + 10, 500, t, 0.8)
    t0 = d * 0.55
    p = prog(t, t0, 0.4)
    panel(img, (X0 - 20, 640, X0 + 1000, 800), 0.8 * p, 14)
    rise(img, "CHICAGO O'HARE + MIDWAY", F("xbold", 36), X0 + 10, 660, t, t0 + 0.1, GREY)
    rise(img, f"{count(t, t0 + 0.2, 1.2, 1000):,.0f}+ DELAYS", F("black", 64), X0 + 10, 710, t, t0 + 0.2)
    source(img, "Source: FlightAware via CNBC; Daily Herald", t)


def c_domino(img, t, d):
    kicker(img, "THE RIPPLE EFFECT", X0, 200, t)
    steps = ["PLANES IN THE\nWRONG CITIES", "CREWS HIT\nWORK-HOUR LIMITS", "MORNING FLIGHTS\nWITH NO PLANE", "A RUINED\nWEEKEND"]
    bw, gap = 390, 40
    for i, s in enumerate(steps):
        t0 = 0.6 + i * d * 0.2
        x = X0 + i * (bw + gap)
        p = prog(t, t0, 0.45)
        if p <= 0:
            continue
        y = 420 + (1 - p) * 60
        rect(img, (x, y, x + bw, y + 240), RED if i == 3 else DARK, 0.85 * p, 16)
        for j, ln in enumerate(s.split("\n")):
            text(img, ln, F("black", 34), x + bw / 2, y + 98 + j * 46, WHITE, p, "mm")
        if i:
            arrow(img, x - gap + 8, 540, x - 8, p, WHITE)


def c_cost_q(img, t, d):
    rise(img, "HOW MUCH", F("black", 170), W / 2, 330, t, 0.2, WHITE, "ma")
    rise(img, "DOES THIS COST?", F("black", 130), W / 2, 530, t, 0.5, RED, "ma")


def c_noanswer(img, t, d):
    kicker(img, "OFFICIAL COST ESTIMATE", X0, 300, t)
    rise(img, "NONE YET", F("black", 220), X0, 380, t, 0.6)
    rise(img, "Any exact number today is a guess.", F("med", 48), X0, 660, t, d * 0.55, GREY)


def c_yard(img, t, d):
    kicker(img, "THE YARDSTICK", X0, 170, t)
    v = count(t, 0.8, 1.8, 33)
    rise(img, f"${v:,.0f} BILLION", F("black", 170), X0, 240, t, 0.6, RED)
    rise(img, "A YEAR · COST OF FLIGHT DELAYS TO THE U.S. ECONOMY (2019)", F("xbold", 38), X0 + 6, 450, t, 1.0)
    chips = ["AIRLINES", "PASSENGERS' TIME", "LOST BOOKINGS", "WIDER ECONOMY"]
    x = X0
    for i, c in enumerate(chips):
        t0 = d * 0.45 + i * 0.35
        f = F("xbold", 36)
        w_ = tw(c, f) + 50
        p = prog(t, t0, 0.35)
        rect(img, (x, 580, x + w_, 650), DARK, 0.85 * p, 35)
        text(img, c, f, x + w_ / 2, 615, WHITE, p, "mm")
        x += w_ + 24
    source(img, "Source: FAA / NEXTOR estimate, via Airlines for America", t)


def c_divide(img, t, d):
    kicker(img, "SIMPLE MATH", X0, 220, t)
    f = F("black", 130)
    rise(img, "$33B", f, X0, 320, t, 0.3)
    rise(img, "÷ 365", f, X0 + 470, 320, t, 1.0, GREY)
    rise(img, "≈ $90M", f, X0 + 1000, 320, t, 2.0, RED)
    rise(img, "PER ORDINARY DAY", F("black", 66), X0, 560, t, d * 0.55)
    rise(img, "with ordinary delays", F("med", 46), X0, 650, t, d * 0.7, GREY)


def c_friday(img, t, d):
    kicker(img, "FRIDAY WAS NOT ORDINARY", X0, 190, t)
    base_y = 830
    # barra dia normal
    p1 = prog(t, 0.6, 0.8)
    rect(img, (X0 + 80, base_y - int(260 * p1), X0 + 360, base_y), GREY, 0.9)
    text(img, "≈ $90M", F("black", 54), X0 + 220, base_y - 260 * p1 - 50, WHITE, p1, "mm")
    text(img, "NORMAL DAY", F("xbold", 34), X0 + 220, base_y + 40, GREY, p1, "mm")
    # barra sexta, crescendo além
    p2 = prog(t, d * 0.3, 2.2)
    hh = int(440 * p2)
    rect(img, (X0 + 520, base_y - hh, X0 + 800, base_y), RED, 0.95)
    if p2 > 0.9:
        text(img, "?", F("black", 140), X0 + 660, base_y - hh - 90, RED, 1, "mm")
    text(img, "NOV 13", F("xbold", 34), X0 + 660, base_y + 40, WHITE, p2, "mm")
    stamp(img, "ESTIMATE — NOT OFFICIAL", 1450, 420, t, d * 0.55, AMBER, 46)


def c_whopays(img, t, d):
    kicker(img, "WHO PAYS?", X0, 190, t)
    # meio a meio
    cx, cy, r = 1460, 520, 250
    p = prog(t, 0.5, 1.2)
    d_ = ImageDraw.Draw(img)
    d_.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=col((70, 70, 70), 0.9))
    d_.pieslice((cx - r, cy - r, cx + r, cy + r), -90, -90 + 180 * p, fill=col(RED, 0.95))
    text(img, "≈ HALF", F("black", 64), cx + 120, cy - 30, WHITE, prog(t, 1.4), "mm")
    text(img, "PASSENGERS", F("xbold", 30), cx + 120, cy + 30, WHITE, prog(t, 1.5), "mm")
    rise(img, "About half the cost of delays", F("xbold", 52), X0, 270, t, 0.8)
    rise(img, "falls on passengers,", F("xbold", 52), X0, 335, t, 1.0)
    rise(img, "not airlines.", F("xbold", 52), X0, 400, t, 1.15, RED)
    items = ["Missed meetings", "Extra hotel nights", "Lost work hours", "A wedding you missed"]
    for i, s in enumerate(items):
        rise(img, "— " + s, F("med", 46), X0, 530 + i * 72, t, d * 0.4 + i * d * 0.12, WHITE)
    source(img, "Source: NEXTOR Total Delay Impact Study (FAA-funded)", t)


def c_three(img, t, d):
    kicker(img, "WHO LOSES MONEY", X0, 180, t)
    cols = [("AIRLINES", ["Crews", "Fuel while waiting", "Rebooking", "Hotel vouchers"]),
            ("PASSENGERS", ["Time", "Money", "Plans"]),
            ("EVERYONE ELSE", ["Hotels", "Rental cars", "Businesses waiting"])]
    for i, (h, its) in enumerate(cols):
        t0 = 0.3 + i * d * 0.22
        x = X0 + i * 570
        p = prog(t, t0, 0.4)
        rect(img, (x, 260, x + 520, 860), DARK, 0.82 * p, 18)
        rect(img, (x, 260, x + 520, 272), RED, p)
        rise(img, h, F("black", 50), x + 36, 310, t, t0 + 0.1)
        for j, s in enumerate(its):
            rise(img, s, F("med", 42), x + 36, 420 + j * 80, t, t0 + 0.3 + j * 0.15, GREY)


def c_atcfault(img, t, d):
    kicker(img, "IF IT'S AN AIR TRAFFIC CONTROL PROBLEM", X0, 220, t)
    rise(img, "HOTEL & MEALS:", F("black", 90), X0, 310, t, 0.5)
    rise(img, "NOT REQUIRED", F("black", 120), X0, 420, t, 1.0, RED)
    rise(img, "Some airlines pay anyway. Check your airline's policy.", F("med", 46), X0, 620, t, d * 0.55, GREY)


def c_refund(img, t, d):
    kicker(img, "WHAT YOU ARE OWED — WHOEVER'S FAULT", X0, 170, t)
    rise(img, "AUTOMATIC", F("black", 110), X0, 240, t, 0.4)
    rise(img, "CASH REFUND", F("black", 110), X0, 360, t, 0.6, RED)
    rows = [("CANCELED", "any flight"), ("DOMESTIC", "3+ hours late"), ("INTERNATIONAL", "6+ hours late")]
    for i, (a_, b_) in enumerate(rows):
        t0 = d * 0.45 + i * d * 0.12
        y = 540 + i * 95
        p = prog(t, t0, 0.4)
        panel(img, (X0 - 20, y - 10, X0 + 1100, y + 75), 0.8 * p, 12)
        rise(img, a_, F("xbold", 40), X0 + 10, y + 8, t, t0 + 0.1, WHITE)
        rise(img, b_, F("med", 40), X0 + 480, y + 8, t, t0 + 0.2, GREY)
    rise(img, "...and you choose not to fly", F("serif", 52), X0, 850, t, d * 0.82, WHITE)
    source(img, "Source: U.S. DOT refund rule, 2024", t)


def c_fast(img, t, d):
    kicker(img, "HOW FAST", X0, 200, t)
    rise(img, "7", F("black", 240), X0, 250, t, 0.4, RED)
    rise(img, "BUSINESS DAYS", F("black", 54), X0 + 200, 330, t, 0.6)
    rise(img, "credit card", F("med", 40), X0 + 200, 400, t, 0.7, GREY)
    rise(img, "20", F("black", 240), X0 + 900, 250, t, 1.4, RED)
    rise(img, "DAYS", F("black", 54), X0 + 1270, 330, t, 1.6)
    rise(img, "other payments", F("med", 40), X0 + 1270, 400, t, 1.7, GREY)
    t0 = d * 0.5
    rise(img, "VOUCHER", F("black", 100), X0, 620, t, t0, GREY)
    if t > t0 + 0.6:
        p = prog(t, t0 + 0.6, 0.3)
        rect(img, (X0 - 10, 680, X0 - 10 + int(560 * p), 694), RED, 1)
    rise(img, "CASH", F("black", 100), X0 + 700, 620, t, t0 + 1.0, WHITE)
    source(img, "Source: U.S. DOT refund rule, 2024", t)


def c_dont(img, t, d):
    rise(img, "DON'T ACCEPT", F("black", 120), X0, 330, t, 0.3)
    rise(img, "A CREDIT YOU", F("black", 120), X0, 460, t, 0.5)
    rise(img, "DIDN'T ASK FOR", F("black", 120), X0, 590, t, 0.7, RED)


TL = [("JAN 2023", "NOTAM SYSTEM CRASHES"), ("2025", "NEWARK LOSES RADAR & RADIO"),
      ("SEP 2026", "PHILADELPHIA: MAIN + BACKUP LINES DOWN"), ("NOV 13, 2026", "ALL EN-ROUTE CENTERS")]


def timeline(img, t, d, upto, detail):
    y = 330
    x0, x1 = X0 + 40, W - 160
    p = prog(t, 0.2, 0.6)
    rect(img, (x0, y - 3, x0 + int((x1 - x0) * p), y + 3), (120, 120, 120), 0.9)
    xs = [x0 + i * (x1 - x0) / 3 for i in range(4)]
    for i, (dt, lab) in enumerate(TL):
        if i > upto:
            break
        cur = i == upto
        c = RED if cur else WHITE
        a = 1.0 if cur else 0.55
        pi = prog(t, 0.3 + (0.3 if cur else 0), 0.4)
        d_ = ImageDraw.Draw(img)
        r = 18 if cur else 12
        if cur and i == 3:
            r = 18 + 4 * (1 + math.sin(t * 6)) / 2
        d_.ellipse((xs[i] - r, y - r, xs[i] + r, y + r), fill=col(c, pi))
        anchor = "ma" if 0 < i < 3 else ("la" if i == 0 else "ra")
        xx = xs[i] - (0 if i else 18) + (18 if i == 3 else 0)
        text(img, dt, F("black", 40), xx, y - 90, c, pi * a, anchor)
    detail(img, t, d)


def d_notam(img, t, d):
    rise(img, "NOTAM", F("black", 150), X0, 460, t, 0.6, RED)
    rise(img, "the safety-notice system for pilots crashed", F("xbold", 44), X0, 640, t, 1.0)
    rise(img, "Cause: a damaged database file", F("med", 40), X0, 710, t, d * 0.4, GREY)
    rise(img, f"{count(t, d*0.6, 1.0, 1000):,.0f}+ CANCELED", F("black", 56), X0, 810, t, d * 0.6, WHITE)
    rise(img, f"~{count(t, d*0.7, 1.0, 10000):,.0f} DELAYED", F("black", 56), X0 + 640, 810, t, d * 0.7, WHITE)
    source(img, "Source: Congressional Research Service; FlightAware", t)


def d_newark(img, t, d):
    rise(img, "NEWARK", F("black", 150), X0, 460, t, 0.5, RED)
    rise(img, "radar and radio lost more than once", F("xbold", 44), X0, 640, t, 0.9)
    rise(img, "Data traveling over old copper telecom wires", F("med", 40), X0, 710, t, d * 0.45, GREY)
    source(img, "Source: AP; FAA", t)


def d_phl(img, t, d):
    rise(img, "PHILADELPHIA", F("black", 130), X0, 460, t, 0.5, RED)
    for i, s in enumerate(["MAIN LINE", "BACKUP LINE"]):
        y = 650 + i * 90
        rise(img, s, F("black", 60), X0 + 90, y, t, 0.9 + i * 0.5)
        cross(img, X0 + 35, y + 32, 24, t, 1.3 + i * 0.5, RED, 8)
    rise(img, "Newark: almost no commercial landings for much of the day", F("med", 40), X0, 870, t, d * 0.55, GREY)
    source(img, "Source: AP, Sept 22, 2026", t)


def d_now(img, t, d):
    rise(img, "EVERY CENTER", F("black", 150), X0, 460, t, 0.4, RED)
    rise(img, "IN THE COUNTRY", F("black", 100), X0, 630, t, 0.7)


def c_tl1(img, t, d): timeline(img, t, d, 0, d_notam)
def c_tl2(img, t, d): timeline(img, t, d, 1, d_newark)
def c_tl3(img, t, d): timeline(img, t, d, 2, d_phl)
def c_tl4(img, t, d): timeline(img, t, d, 3, d_now)


def c_pattern(img, t, d):
    kicker(img, "THE PATTERN", X0, 260, t)
    rise(img, "OLD EQUIPMENT", F("black", 120), X0, 340, t, 0.4)
    rise(img, "+ BACKUPS THAT FAIL", F("black", 100), X0, 490, t, 1.4, RED)


def c_vintage(img, t, d):
    kicker(img, "THE FAA, DESCRIBING ITSELF", X0, 240, t)
    quote(img, "failing vintage hardware", "FAA budget estimate, fiscal year 2023 — on the NOTAM system",
          X0 + 40, 330, 1600, t, 0.5, 150)


def c_money(img, t, d):
    kicker(img, "THE FIX", X0, 170, t)
    v = count(t, 0.5, 1.5, 12.5)
    rise(img, f"${v:,.1f}B", F("black", 150), X0, 230, t, 0.4, RED)
    rise(img, "APPROVED BY CONGRESS FOR MODERNIZATION", F("xbold", 40), X0 + 6, 420, t, 0.8)
    t0 = d * 0.3
    rise(img, f"{count(t, t0, 1.4, 3346):,.0f}", F("black", 90), X0, 520, t, t0, WHITE)
    rise(img, "COMMUNICATION LINES REPLACED", F("xbold", 32), X0 + 6, 630, t, t0 + 0.2, GREY)
    rise(img, f"{count(t, t0 + 0.4, 1.2, 190):,.0f}", F("black", 90), X0 + 760, 520, t, t0 + 0.4, WHITE)
    rise(img, "VOICE SWITCHES REPLACED", F("xbold", 32), X0 + 766, 630, t, t0 + 0.6, GREY)
    t1 = d * 0.68
    p = prog(t, t1, 1.0)
    rise(img, "STILL NEEDED: TENS OF BILLIONS MORE", F("black", 50), X0, 730, t, t1, AMBER)
    bar(img, X0, 815, 1600, 30, 0.3 * p, RED)
    text(img, "FUNDED SO FAR", F("bold", 24), X0, 870, GREY, p, "la")
    source(img, "Sources: FAA; Sec. Sean Duffy", t)


def c_running(img, t, d):
    rise(img, "REPAIRING THE SYSTEM", F("black", 110), W / 2, 380, t, 0.3, WHITE, "ma")
    rise(img, "WHILE IT'S RUNNING", F("black", 110), W / 2, 510, t, 0.6, RED, "ma")


def c_unknown(img, t, d):
    kicker(img, "WHAT WE STILL DON'T KNOW", X0, 210, t)
    qs = ["THE OFFICIAL CAUSE", "THE FINAL COUNT", "THE BILL"]
    for i, s in enumerate(qs):
        t0 = d * 0.25 + i * d * 0.2
        y = 310 + i * 170
        rise(img, "?", F("black", 130), X0, y - 10, t, t0, RED)
        rise(img, s, F("black", 90), X0 + 120, y, t, t0 + 0.1)


def c_close(img, t, d):
    f = F("serif", 76)
    lines = ["Billions to build the safest", "air system in the world.", "", "Lost for an afternoon",
             "to a line that stopped working."]
    for i, ln in enumerate(lines):
        if ln:
            rise(img, ln, f, X0, 280 + i * 100, t, 0.3 + i * d * 0.12, RED if i >= 3 else WHITE)


def c_end(img, t, d):
    p = prog(t, 0.2, 0.6)
    logo(img, W / 2, 330, int(110 * (0.6 + 0.4 * p)), p, 14)
    text(img, "OVERDRAWN FILES", F("black", 90), W / 2, 520, WHITE, p, "mm")
    rise(img, "STORY DEVELOPING · FACTS AS OF NOV 13, 2026", F("xbold", 34), W / 2, 590, t, 0.8, GREY, "ma")
    t0 = d * 0.45
    rise(img, "Were you stuck in an airport on Friday?", F("serif", 64), W / 2, 700, t, t0, WHITE, "ma")
    p2 = prog(t, t0 + 0.8, 0.4)
    if p2 > 0:
        f = F("black", 40)
        wv = tw("SUBSCRIBE FOR THE FOLLOW-UP", f) + 80
        rect(img, (W / 2 - wv / 2, 820, W / 2 + wv / 2, 900), RED, p2, 40)
        text(img, "SUBSCRIBE FOR THE FOLLOW-UP", f, W / 2, 860, WHITE, p2, "mm")


# (frase em que a cena começa, vídeos de fundo, desenho)
CENAS = [
    ("On Friday, November 13th", ["taxi", "gate"], c_open),
    ("Not because of a storm", ["citynight"], c_notstorm),
    ("In this video", ["map"], c_chapters),
    ("Here's what's confirmed", ["landing"], c_confirmed),
    ("Transportation Secretary Sean Duffy", ["citynight"], c_duffy),
    ("To understand how big that is", ["gate", "walking"], c_scale),
    ("Every one of those flights depends", ["racks"], c_links),
    ("And when controllers can't safely", ["taxi"], c_groundstop),
    ("Planes already in the air", ["landing", "dusk"], c_status),
    ("The first question everyone asked", ["attack"], c_attack_q),
    ("So far, officials say no", ["flicker"], c_officials),
    ("Bloomberg reported", ["code"], c_software),
    ("By the afternoon", ["angry", "checkin"], c_damage),
    ("And a ground stop doesn't end", ["walking", "cart"], c_domino),
    ("Now, the question this channel", ["falling"], c_cost_q),
    ("Here's the honest answer", ["clock"], c_noanswer),
    ("But we do have a yardstick", ["counting", "falling"], c_yard),
    ("Divide that by three hundred", ["counting"], c_divide),
    ("Friday was not an ordinary day", ["burn"], c_friday),
    ("So who pays?", ["broke", "suitcase"], c_whopays),
    ("Airlines pay for crews", ["baggage"], c_three),
    ("One more thing passengers should know", ["suitcase", "checkin"], c_atcfault),
    ("But there is one thing you are owed", ["checkin", "angry"], c_refund),
    ("And the money has to come back fast", ["counting"], c_fast),
    ("So if your flight was canceled", ["cart"], c_dont),
    ("This isn't the first time", ["racks", "code"], c_tl1),
    ("In 2025, controllers handling Newark", ["cables"], c_tl2),
    ("In September of this year", ["fiber"], c_tl3),
    ("And now, every air route", ["map"], c_tl4),
    ("The pattern is the same every time", ["flicker"], c_pattern),
    ("Back in 2023, the FAA's own budget", ["racks"], c_vintage),
    ("Congress approved twelve and a half", ["fiber", "cables"], c_money),
    ("So the money is moving", ["takeoff"], c_running),
    ("Here's what we still don't know", ["dusk", "baggage"], c_unknown),
    ("A country can spend billions", ["takeoff"], c_close),
    ("This story is still developing", ["dusk", "takeoff"], c_end),
]
