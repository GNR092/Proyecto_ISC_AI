import pygame
import sys
import textwrap

SCREEN_W, SCREEN_H = 1024, 640
BG = (18,18,20)
PANEL = (28,28,30)
ACCENT = (230,100,80)
TEXT = (220,220,220)

pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption('Boceto Invernadero - UI v2')
# helper to load images safely
def load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except Exception:
        return None

# load images using helper
invernadero_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\invernadero.jpg")
regadera_off_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\regadera-off.png")
regadera_on_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\regadera-on.png")
calefactor_off_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\calefactor-off.png")
calefactor_on_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\calefactor-on.png")
ventilador_off_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\ventilador-off.png")
ventilador_on_img = load_image(r"C:\Users\akelo\OneDrive\Escritorio\Nueva carpeta (2)\ventilado1-on.png")

clock = pygame.time.Clock()
font_s = pygame.font.Font(None,20)
font_m = pygame.font.Font(None,24)

# UI state
profiles = ['Invernadero A', 'Invernadero B', 'Invernadero C']
profile_idx = 0
profile_open = False

# input fields (strings); only numeric characters accepted
fields = {
    'temperatura': '20.0',
    'humedad': '50',
    'temp_objetivo': '22.0',
    'tiempo': '60'
}
focused_field = None

# toggles
heater_on = False
fan_on = False
humid_on = False

# logs
log_lines = []
max_logs = 8

# rects cache for event handling
RECTS = {}


def clamp_numeric(s):
    s2 = ''.join(c for c in s if (c.isdigit() or c=='.'))
    parts = s2.split('.')
    if len(parts) <= 2:
        return '.'.join(parts)
    return parts[0] + '.' + ''.join(parts[1:])


def append_log(text):
    log_lines.append(text)
    if len(log_lines) > max_logs:
        del log_lines[0]


def draw_ui():
    global RECTS
    screen.fill(BG)
    margin = 20
    outer = pygame.Rect(margin, margin, SCREEN_W-2*margin, SCREEN_H-2*margin)
    pygame.draw.rect(screen, ACCENT, outer, 4, border_radius=6)

    main_w = int(outer.w*0.68)
    # reserve larger footer for logs
    footer_height = 140
    main_rect_h = outer.h - footer_height - 30
    main_rect = pygame.Rect(outer.x+10, outer.y+10, main_w-20, main_rect_h)
    pygame.draw.rect(screen, PANEL, main_rect)
    pygame.draw.rect(screen, ACCENT, main_rect, 2, border_radius=6)

    # top image placeholder removed to allow center image to occupy full area

    # side panels removed so center image can occupy full area

    # center box occupies the entire main_rect area (with small padding)
    center_box = pygame.Rect(main_rect.x + 8, main_rect.y + 8, main_rect.w - 16, main_rect.h - 16)
    pygame.draw.rect(screen, PANEL, center_box, border_radius=10)
    pygame.draw.rect(screen, ACCENT, center_box, 2, border_radius=10)
    if invernadero_img:
        img = pygame.transform.smoothscale(invernadero_img, (center_box.w, center_box.h))
        screen.blit(img, center_box.topleft)
    else:
        center_label = font_m.render('Invernadero', True, TEXT)
        screen.blit(center_label, (center_box.centerx - center_label.get_width()//2, center_box.centery - center_label.get_height()//2))
    # top regadera overlay selected by humid_on
    reg_img = regadera_on_img if humid_on else regadera_off_img
    if reg_img:
        ow = int(center_box.w * 0.2)
        if reg_img.get_width() != 0:
            oh = int(reg_img.get_height() * (ow / reg_img.get_width()))
        else:
            oh = reg_img.get_height()
        oimg = pygame.transform.smoothscale(reg_img, (ow, oh))
        ox = center_box.centerx - ow//2
        oy = center_box.y + 12
        screen.blit(oimg, (ox, oy))
    # left overlay for calefactor selected by heater_on
    left_img = calefactor_on_img if heater_on else calefactor_off_img
    if left_img:
        lw = int(center_box.w * 0.15)
        if left_img.get_width() != 0:
            lh = int(left_img.get_height() * (lw / left_img.get_width()))
        else:
            lh = left_img.get_height()
        limg = pygame.transform.smoothscale(left_img, (lw, lh))
        lx = center_box.x + 12
        ly = center_box.centery - lh//2
        screen.blit(limg, (lx, ly))
    # right overlay for ventilador: show ventilador-on when fan_on else ventilador-off
    right_img = ventilador_on_img if fan_on else ventilador_off_img
    if right_img:
        rw = int(center_box.w * 0.15)
        if right_img.get_width() != 0:
            rh = int(right_img.get_height() * (rw / right_img.get_width()))
        else:
            rh = right_img.get_height()
        rimg = pygame.transform.smoothscale(right_img, (rw, rh))
        rx = center_box.right - 12 - rw
        ry = center_box.centery - rh//2
        screen.blit(rimg, (rx, ry))

    # footer (logs)
    footer = pygame.Rect(main_rect.x, outer.y+outer.h-footer_height-10, main_rect.w, footer_height)
    pygame.draw.rect(screen, PANEL, footer, border_radius=16)
    pygame.draw.rect(screen, ACCENT, footer,2,border_radius=16)
    lf = font_s.render('Logs', True, TEXT)
    screen.blit(lf, (footer.x+10, footer.y+8))

    # draw log lines with wrapping to fit inside footer
    lx = footer.x + 10
    ly = footer.y + 30
    char_w, char_h = font_s.size('A')
    max_chars = max(10, (footer.w - 20) // max(1,char_w))
    wrapped = []
    for line in log_lines:
        wrapped.extend(textwrap.wrap(line, width=max_chars))
    # only keep lines that fit vertically
    max_lines = (footer.h - 30) // char_h
    wrapped = wrapped[-max_lines:]
    for i,line in enumerate(wrapped):
        txt = font_s.render(line, True, TEXT)
        screen.blit(txt, (lx, ly + i*char_h))

    # right column controls
    right_x = main_rect.right + 20
    rx = right_x
    y = outer.y + 18

    # PROFILE combobox
    prof_label = font_s.render('Perfil', True, TEXT)
    screen.blit(prof_label, (rx+6, y))
    prof_rect = pygame.Rect(rx+90, y-6, 160, 26)
    pygame.draw.rect(screen, PANEL, prof_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, prof_rect,2,border_radius=6)
    prof_text = font_s.render(profiles[profile_idx], True, TEXT)
    screen.blit(prof_text, (prof_rect.x+8, prof_rect.y+5))
    pygame.draw.polygon(screen, TEXT, [(prof_rect.right-18, prof_rect.y+10),(prof_rect.right-8, prof_rect.y+10),(prof_rect.right-13, prof_rect.y+18)])

    y += 42

    # TEMPERATURE numeric input
    lab = font_s.render('Temperatura', True, TEXT)
    screen.blit(lab, (rx+6, y))
    temp_rect = pygame.Rect(rx+120, y-6, 130, 26)
    pygame.draw.rect(screen, PANEL, temp_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, temp_rect,2,border_radius=6)
    temp_text = font_s.render(fields['temperatura'] + ('_' if focused_field=='temperatura' and (pygame.time.get_ticks()//500)%2==0 else ''), True, TEXT)
    screen.blit(temp_text, (temp_rect.x+8, temp_rect.y+4))

    y += 42

    # HUMIDITY numeric input
    lab = font_s.render('Humedad', True, TEXT)
    screen.blit(lab, (rx+6, y))
    hum_rect = pygame.Rect(rx+120, y-6, 130, 26)
    pygame.draw.rect(screen, PANEL, hum_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, hum_rect,2,border_radius=6)
    hum_text = font_s.render(fields['humedad'] + ('_' if focused_field=='humedad' and (pygame.time.get_ticks()//500)%2==0 else ''), True, TEXT)
    screen.blit(hum_text, (hum_rect.x+8, hum_rect.y+4))

    y += 42

    # TOGGLES: Heater, Fan, Humidifier (aligned vertically)
    lab = font_s.render('Calefactor', True, TEXT)
    screen.blit(lab, (rx+6, y))
    heater_rect = pygame.Rect(rx+100, y-6, 180, 28)
    pygame.draw.rect(screen, (60,120,60) if heater_on else PANEL, heater_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, heater_rect,2,border_radius=6)
    screen.blit(font_s.render('ON' if heater_on else 'OFF', True, TEXT), (heater_rect.x+8, heater_rect.y+4))

    y += 42

    lab = font_s.render('Ventilar', True, TEXT)
    screen.blit(lab, (rx+6, y))
    fan_rect = pygame.Rect(rx+100, y-6, 180, 28)
    pygame.draw.rect(screen, (60,120,60) if fan_on else PANEL, fan_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, fan_rect,2,border_radius=6)
    screen.blit(font_s.render('ON' if fan_on else 'OFF', True, TEXT), (fan_rect.x+8, fan_rect.y+4))

    y += 42

    lab = font_s.render('Humidificador', True, TEXT)
    screen.blit(lab, (rx+6, y))
    humid_rect = pygame.Rect(rx+100, y-6, 180, 28)
    pygame.draw.rect(screen, (60,120,60) if humid_on else PANEL, humid_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, humid_rect,2,border_radius=6)
    screen.blit(font_s.render('ON' if humid_on else 'OFF', True, TEXT), (humid_rect.x+8, humid_rect.y+4))

    y += 42

    # TEMP OBJETIVO
    lab = font_s.render('Temp objetivo', True, TEXT)
    screen.blit(lab, (rx+6, y))
    to_rect = pygame.Rect(rx+120, y-6, 130, 26)
    pygame.draw.rect(screen, PANEL, to_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, to_rect,2,border_radius=6)
    to_text = font_s.render(fields['temp_objetivo'] + ('_' if focused_field=='temp_objetivo' and (pygame.time.get_ticks()//500)%2==0 else ''), True, TEXT)
    screen.blit(to_text, (to_rect.x+8, to_rect.y+4))

    y += 42

    # SIMULATION TIME numeric
    lab = font_s.render('Tiempo simulación (s)', True, TEXT)
    screen.blit(lab, (rx+6, y))
    time_rect = pygame.Rect(rx+170, y-6, 80, 26)
    pygame.draw.rect(screen, PANEL, time_rect, border_radius=6)
    pygame.draw.rect(screen, ACCENT, time_rect,2,border_radius=6)
    time_text = font_s.render(fields['tiempo'] + ('_' if focused_field=='tiempo' and (pygame.time.get_ticks()//500)%2==0 else ''), True, TEXT)
    screen.blit(time_text, (time_rect.x+8, time_rect.y+4))

    # SIMULATE button
    btn = pygame.Rect(rx+90, time_rect.bottom+12, 160, 36)
    pygame.draw.rect(screen, PANEL, btn, border_radius=8)
    pygame.draw.rect(screen, ACCENT, btn,2,border_radius=8)
    bt = font_m.render('Simular', True, TEXT)
    screen.blit(bt, bt.get_rect(center=btn.center))

    # small right border accent
    pygame.draw.rect(screen, ACCENT, (outer.right-6, outer.y+12, 4, outer.h-24))

    # store rects
    RECTS = {
        'prof_rect': prof_rect,
        'prof_dropdown': pygame.Rect(prof_rect.x, prof_rect.bottom, prof_rect.w, min(120, len(profiles)*28)),
        'temp_rect': temp_rect,
        'hum_rect': hum_rect,
        'heater_rect': heater_rect,
        'fan_rect': fan_rect,
        'humid_rect': humid_rect,
        'to_rect': to_rect,
        'time_rect': time_rect,
        'btn_simulate': btn,
        'footer': footer
    }


def handle_mouse(pos):
    global profile_open, profile_idx, focused_field, heater_on, fan_on, humid_on
    if RECTS.get('prof_rect') and RECTS['prof_rect'].collidepoint(pos):
        profile_open = not profile_open
        focused_field = None
        return
    if profile_open and RECTS.get('prof_dropdown') and RECTS['prof_dropdown'].collidepoint(pos):
        rel_y = pos[1] - RECTS['prof_dropdown'].y
        idx = rel_y // 28
        if 0 <= idx < len(profiles):
            profile_idx = int(idx)
        profile_open = False
        return
    # inputs
    if RECTS.get('temp_rect') and RECTS['temp_rect'].collidepoint(pos):
        focused_field = 'temperatura';
        # start editing with empty to type
        fields['temperatura'] = '';
        return
    if RECTS.get('hum_rect') and RECTS['hum_rect'].collidepoint(pos):
        focused_field = 'humedad';
        fields['humedad'] = '';
        return
    if RECTS.get('to_rect') and RECTS['to_rect'].collidepoint(pos):
        focused_field = 'temp_objetivo';
        fields['temp_objetivo'] = '';
        return
    if RECTS.get('time_rect') and RECTS['time_rect'].collidepoint(pos):
        focused_field = 'tiempo';
        fields['tiempo'] = '';
        return
    # toggles
    if RECTS.get('heater_rect') and RECTS['heater_rect'].collidepoint(pos):
        heater_on = not heater_on; focused_field=None; return
    if RECTS.get('fan_rect') and RECTS['fan_rect'].collidepoint(pos):
        fan_on = not fan_on; focused_field=None; return
    if RECTS.get('humid_rect') and RECTS['humid_rect'].collidepoint(pos):
        humid_on = not humid_on; focused_field=None; return
    # simulate
    if RECTS.get('btn_simulate') and RECTS['btn_simulate'].collidepoint(pos):
        summary = f"Perfil={profiles[profile_idx]} | Temp={fields['temperatura']}C | Hum={fields['humedad']}% | Heater={'ON' if heater_on else 'OFF'} | Fan={'ON' if fan_on else 'OFF'} | Humid={'ON' if humid_on else 'OFF'} | TempObj={fields['temp_objetivo']}C | Tiempo={fields['tiempo']}s"
        append_log(summary)
        focused_field = None
        return
    # if clicking footer area, ignore (console only displays logs)
    if RECTS.get('footer') and RECTS['footer'].collidepoint(pos):
        return
    profile_open = False
    focused_field = None


def handle_key(event):
    global fields
    if focused_field is None:
        return
    if event.key == pygame.K_BACKSPACE:
        fields[focused_field] = fields[focused_field][:-1]
        return
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        # fill empty numeric fields with 0
        for k in ('temperatura','humedad','temp_objetivo','tiempo'):
            if fields[k] == '':
                fields[k] = '0'
        summary = f"Perfil={profiles[profile_idx]} | Temp={fields['temperatura']}C | Hum={fields['humedad']}% | Heater={'ON' if heater_on else 'OFF'} | Fan={'ON' if fan_on else 'OFF'} | Humid={'ON' if humid_on else 'OFF'} | TempObj={fields['temp_objetivo']}C | Tiempo={fields['tiempo']}s"
        append_log(summary)
        return
    c = event.unicode
    if c.isdigit() or c == '.':
        fields[focused_field] = clamp_numeric(fields[focused_field] + c)
    else:
        # ignore other keys
        return


def main():
    try:
        while True:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:
                    pygame.quit(); sys.exit()
                if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:
                    handle_mouse(e.pos)
                if e.type==pygame.KEYDOWN:
                    handle_key(e)

            draw_ui()

            # if dropdown open, draw it on top
            if profile_open:
                dd = RECTS.get('prof_dropdown')
                if dd:
                    pygame.draw.rect(screen, PANEL, dd, border_radius=6)
                    pygame.draw.rect(screen, ACCENT, dd,2,border_radius=6)
                    for i,p in enumerate(profiles):
                        txt = font_s.render(p, True, TEXT)
                        screen.blit(txt, (dd.x+8, dd.y + i*28 + 6))

            pygame.display.flip()
            clock.tick(30)
    except KeyboardInterrupt:
        pygame.quit(); sys.exit()

if __name__=='__main__':
    main()
