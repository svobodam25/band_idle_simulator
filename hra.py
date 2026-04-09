import pygame
import sys
import time
pygame.init()

import gui

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Band Idle Simulator")

lista = gui.Lista(width, height)
last_income_update = time.time()
last_drum_hit = time.time()
last_guitar_strum = time.time()

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
                    lista.penize += lista.sila_kliku
                    lista.kliknuti_historie.append((time.time(), lista.sila_kliku))
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
                                            lista.prijem += 1
                                            lista.sila_kliku += 1
                                        elif i == 1:
                                            lista.drummer_active = True
                                            lista.prijem += 2
                                        elif i == 2:
                                            lista.guitarist_active = True
                                            lista.prijem += 3
                                            
                                    elif lista.aktivni_kategorie == "Vylepšení":
                                        lista.item_prices["Vylepšení"][i] *= 3
                                        if i == 0: 
                                            lista.sila_kliku += 1
                                        elif i == 1: 
                                            if lista.drummer_active:
                                                lista.prijem += 2
                                        elif i == 2: 
                                            if lista.guitarist_active:
                                                lista.prijem += 5
                                        elif i == 3:
                                            lista.prijem += 8
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
    if current_time - last_income_update >= 1.0:
        lista.penize += lista.prijem
        if lista.mikrofon_active:
            lista.singer_target_scale = 1.15
        last_income_update = current_time

    if lista.drummer_active and current_time - last_drum_hit >= 2.5:
        lista.zahraj_na_buben()
        last_drum_hit = current_time

    if lista.guitarist_active and current_time - last_guitar_strum >= 1.5:
        lista.zahraj_na_kytaru()
        last_guitar_strum = current_time
    
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