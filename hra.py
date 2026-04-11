import pygame
import sys
import time
pygame.init()

import gui

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Band Idle Simulator")

lista = gui.Lista(width, height)
if not hasattr(lista, 'upgrade_levels'):
    lista.upgrade_levels = {i: 0 for i in range(7)}


def vypocitat_vydelky(l):
    levels = getattr(l, 'upgrade_levels', {i: 0 for i in range(7)})

    global_mult = 1.0 + (levels.get(3, 0) * 0.12)
    dj_team_mult = (1.10 + levels.get(6, 0) * 0.04) if l.dj_active else 1.0
    total_mult = global_mult * dj_team_mult

    # Passive je jen od mikrofonu a DJ aury, ne od kazde postavy zvlast.
    base_passive = (1 if l.mikrofon_active else 0) + (1 if l.dj_active else 0)

    auto_income = int(round(base_passive * total_mult))
    # Role economics: drummer = rychly tick, guitarist = mensi burst,
    # pianist = stabilne nejsilnejsi DPS, DJ = buff + stredni vlastni tick.
    drum_tick_income = int(round((1.2 + levels.get(1, 0) * 1.6) * total_mult))
    guitar_burst_income = int(round((2.0 + levels.get(2, 0) * 1.8) * total_mult))
    piano_tick_income = int(round((2.4 + levels.get(5, 0) * 2.2) * total_mult))
    dj_tick_income = int(round((4.0 + levels.get(6, 0) * 2.2) * global_mult))

    drum_tick_income = max(1, drum_tick_income)
    guitar_burst_income = max(1, guitar_burst_income)
    piano_tick_income = max(1, piano_tick_income)
    dj_tick_income = max(1, dj_tick_income)

    estimated_per_sec = float(auto_income)
    if l.drummer_active:
        estimated_per_sec += drum_tick_income / 0.6
    if l.guitarist_active:
        estimated_per_sec += guitar_burst_income / 4.0
    if l.pianist_active:
        estimated_per_sec += piano_tick_income / 0.5
    if l.dj_active:
        estimated_per_sec += dj_tick_income / 1.2

    l.prijem = int(round(estimated_per_sec))
    return auto_income, drum_tick_income, guitar_burst_income, piano_tick_income, dj_tick_income


last_income_update = time.time()
last_drum_hit = time.time()
last_guitar_strum = time.time()
last_piano_play = time.time()
last_dj_play = time.time()
last_drum_tick = time.time()
last_piano_tick = time.time()
last_dj_tick = time.time()
last_guitar_burst = time.time()

clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                ui_pos = lista.screen_to_ui_pos(event.pos) if hasattr(lista, 'screen_to_ui_pos') else event.pos

                if lista.settings_otevrene:
                    if hasattr(lista, 'btn_zavrit_nastaveni') and lista.btn_zavrit_nastaveni.collidepoint(ui_pos):
                        lista.settings_otevrene = False
                    elif hasattr(lista, 'btn_exit_game') and lista.btn_exit_game.collidepoint(ui_pos):
                        running = False
                        
                    elif hasattr(lista, 'btn_tab_sound') and lista.btn_tab_sound.collidepoint(ui_pos):
                        lista.settings_tab = 'Sound'
                    elif hasattr(lista, 'btn_tab_graphics') and lista.btn_tab_graphics.collidepoint(ui_pos):
                        lista.settings_tab = 'Graphics'
                    elif hasattr(lista, 'btn_tab_developer') and lista.btn_tab_developer.collidepoint(ui_pos):
                        lista.settings_tab = 'Developer'

                    if getattr(lista, 'settings_tab', 'Sound') == 'Sound':
                        if hasattr(lista, 'btn_vol_minus') and lista.btn_vol_minus.collidepoint(ui_pos):
                            lista.upravit_hlasitost(-0.1)
                        elif hasattr(lista, 'btn_vol_plus') and lista.btn_vol_plus.collidepoint(ui_pos):
                            lista.upravit_hlasitost(0.1)

                    elif getattr(lista, 'settings_tab', 'Sound') == 'Graphics':
                        if hasattr(lista, 'btn_res_change') and lista.btn_res_change.collidepoint(ui_pos):
                            if width == 800:
                                width, height = 1920, 1080
                                screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                            else:
                                width, height = 800, 600
                                screen = pygame.display.set_mode((width, height))
                            lista._aktualizovat_rozmery_okna(width, height)
                            
                        elif hasattr(lista, 'btn_anim_toggle') and lista.btn_anim_toggle.collidepoint(ui_pos):
                            lista.animations_disabled = not getattr(lista, 'animations_disabled', False)
                            
                        elif hasattr(lista, 'btn_fps_change') and lista.btn_fps_change.collidepoint(ui_pos):
                            opts = getattr(lista, 'fps_options', [30, 60, 120, 0])
                            lista.fps_index = (getattr(lista, 'fps_index', 1) + 1) % len(opts)
                            
                        elif hasattr(lista, 'btn_ui_scale_minus') and lista.btn_ui_scale_minus.collidepoint(ui_pos):
                            if hasattr(lista, 'set_ui_scale'):
                                lista.set_ui_scale(getattr(lista, 'ui_scale', 1.0) - 0.1)
                            else:
                                lista.ui_scale = max(0.5, getattr(lista, 'ui_scale', 1.0) - 0.1)
                        elif hasattr(lista, 'btn_ui_scale_plus') and lista.btn_ui_scale_plus.collidepoint(ui_pos):
                            if hasattr(lista, 'set_ui_scale'):
                                lista.set_ui_scale(getattr(lista, 'ui_scale', 1.0) + 0.1)
                            else:
                                lista.ui_scale = min(2.0, getattr(lista, 'ui_scale', 1.0) + 0.1)

                    continue

                if lista.logo_rect.collidepoint(ui_pos):
                    lista.settings_otevrene = True
                    continue

                if not lista.menu_otevrene and (lista.singer_rect.collidepoint(event.pos) or (lista.mikrofon_active and lista.mikrofon_rect.collidepoint(event.pos))):
                    now = time.time()
                    lista.combo_clicks = int(getattr(lista, 'combo_clicks', 0)) + 1
                    lista.combo_multiplier = 1.0 + (lista.combo_clicks // 10) * 0.1
                    lista.combo_count = lista.combo_clicks
                    lista.combo_until = now + 1.2

                    click_income = max(1, int(round(lista.sila_kliku * lista.combo_multiplier)))
                    lista.penize += click_income
                    lista.kliknuti_historie.append((now, click_income))
                    if hasattr(lista, 'pridat_floating_text'):
                        lista.pridat_floating_text(
                            lista.singer_rect.centerx - 20,
                            lista.singer_rect.top - 10,
                            f"+{click_income}$",
                            (255, 230, 120),
                            life=0.9
                        )
                    lista.singer_target_scale = 1.15
                elif lista.menu_rect.collidepoint(ui_pos):
                    lista.menu_otevrene = not lista.menu_otevrene
                    lista.odrazu = 0
                    lista.menu_rychlost = 0
                    if not lista.menu_otevrene:
                        lista.scroll_offset = 0
                elif lista.menu_vyska > 0:
                    if hasattr(lista, 'rect_tab_clenove') and lista.rect_tab_clenove.collidepoint(ui_pos):
                        lista.aktivni_kategorie = "Členové"
                        lista.scroll_offset = 0
                        continue
                    if hasattr(lista, 'rect_tab_vylepseni') and lista.rect_tab_vylepseni.collidepoint(ui_pos):
                        lista.aktivni_kategorie = "Vylepšení"
                        lista.scroll_offset = 0
                        continue

                    menu_obsah_y = lista.vyska + 55
                    visible_index = 0
                    aktualni_polozky = lista.menu_items[lista.aktivni_kategorie]
                    
                    for i in range(len(aktualni_polozky)):
                        if i in lista.bought_items[lista.aktivni_kategorie]:
                            continue
                        
                        item_y = menu_obsah_y + visible_index * (lista.item_height + lista.item_spacing) - lista.scroll_offset
                        visible_index += 1
                        
                        if lista.vyska < item_y + lista.item_height < lista.vyska + lista.menu_vyska:
                            button_x = lista.sirka - lista.scrollbar_width - lista.button_width - 20
                            button_y = item_y + (lista.item_height - lista.button_height) // 2
                            button_rect = pygame.Rect(button_x, button_y, lista.button_width, lista.button_height)
                            
                            if button_rect.collidepoint(ui_pos):
                                price = lista.item_prices[lista.aktivni_kategorie].get(i, 0)
                                if lista.penize >= price:
                                    lista.penize -= price

                                    if lista.aktivni_kategorie == "Členové":
                                        lista.bought_items[lista.aktivni_kategorie].add(i)
                                        if i == 0:
                                            lista.mikrofon_active = True
                                            lista.sila_kliku += 1
                                        elif i == 1:
                                            lista.drummer_active = True
                                        elif i == 2:
                                            lista.guitarist_active = True
                                        elif i == 3:
                                            lista.pianist_active = True
                                        elif i == 4:
                                            lista.dj_active = True
                                            
                                    elif lista.aktivni_kategorie == "Vylepšení":
                                        lista.item_prices["Vylepšení"][i] *= 3
                                        lista.upgrade_levels[i] = int(getattr(lista, 'upgrade_levels', {}).get(i, 0)) + 1
                                        if i == 0: 
                                            lista.sila_kliku += 1
                                        elif i == 4:
                                            lista.sila_kliku += 5

        if event.type == pygame.MOUSEWHEEL:
            if lista.menu_vyska > 0:
                lista.handle_scroll(-event.y)
                
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F11:
                if width == 800:
                    width, height = 1920, 1080
                    screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                else:
                    width, height = 800, 600
                    screen = pygame.display.set_mode((width, height))
                lista._aktualizovat_rozmery_okna(width, height)
            elif event.key == pygame.K_ESCAPE:
                lista.settings_otevrene = not lista.settings_otevrene
                
    screen.fill((255, 255, 255))

    lista.update()
    
    current_time = time.time()
    auto_income, drum_tick_income, guitar_burst_income, piano_tick_income, dj_tick_income = vypocitat_vydelky(lista)

    if current_time - last_income_update >= 1.0:
        lista.penize += auto_income
        if auto_income > 0 and hasattr(lista, 'pridat_floating_text'):
            lista.pridat_floating_text(
                lista.sirka // 2 - 10,
                95,
                f"+{auto_income}$",
                (120, 255, 120),
                life=1.0
            )
        if lista.mikrofon_active:
            lista.singer_target_scale = 1.15
        last_income_update = current_time

    if lista.drummer_active and current_time - last_drum_tick >= 0.6:
        drum_income = drum_tick_income
        lista.penize += drum_income
        if hasattr(lista, 'pridat_floating_text'):
            lista.pridat_floating_text(
                lista.drummer_rect.centerx - 8,
                lista.drummer_rect.top + 10,
                f"+{drum_income}$",
                (180, 255, 180),
                life=0.7
            )
        last_drum_tick = current_time

    if lista.drummer_active and current_time - last_drum_hit >= 0.75:
        lista.zahraj_na_buben()
        last_drum_hit = current_time

    if lista.guitarist_active and current_time - last_guitar_burst >= 4.0:
        burst_income = guitar_burst_income
        lista.penize += burst_income
        if hasattr(lista, 'pridat_floating_text'):
            lista.pridat_floating_text(
                lista.guitarist_rect.centerx - 14,
                lista.guitarist_rect.top,
                f"+{burst_income}$",
                (120, 220, 255),
                life=1.0
            )
        lista.zahraj_na_kytaru()
        last_guitar_burst = current_time

    if lista.pianist_active and current_time - last_piano_tick >= 0.5:
        piano_income = piano_tick_income
        lista.penize += piano_income
        if hasattr(lista, 'pridat_floating_text'):
            lista.pridat_floating_text(
                lista.pianist_rect.centerx - 10,
                lista.pianist_rect.top + 8,
                f"+{piano_income}$",
                (190, 220, 255),
                life=0.7
            )
        last_piano_tick = current_time

    if lista.pianist_active and current_time - last_piano_play >= 1.0:
        lista.zahraj_na_piano()
        last_piano_play = current_time

    if lista.dj_active and current_time - last_dj_play >= 2.2:
        lista.zahraj_dj_set()
        last_dj_play = current_time

    if lista.dj_active and current_time - last_dj_tick >= 1.2:
        dj_income = dj_tick_income
        lista.penize += dj_income
        if hasattr(lista, 'pridat_floating_text'):
            lista.pridat_floating_text(
                lista.dj_rect.centerx - 8,
                lista.dj_rect.top + 8,
                f"+{dj_income}$",
                (255, 200, 140),
                life=0.8
            )
        last_dj_tick = current_time
    
    lista.nakresli(okno=screen)

    pygame.display.flip()
    
    # FPS Lock
    if hasattr(lista, 'fps_options'):
        fps_opt = lista.fps_options[lista.fps_index]
        if fps_opt > 0:
            clock.tick(fps_opt)
        else:
            clock.tick()
    else:
        clock.tick()

pygame.quit()
sys.exit()