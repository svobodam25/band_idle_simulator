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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Only left mouse button
                if lista.settings_otevrene:
                    if hasattr(lista, 'btn_zavrit_nastaveni') and lista.btn_zavrit_nastaveni.collidepoint(event.pos):
                        lista.settings_otevrene = False
                    elif lista.btn_vol_minus.collidepoint(event.pos):
                        lista.upravit_hlasitost(-0.1)  # Snížit hlasitost o 10 %
                    elif lista.btn_vol_plus.collidepoint(event.pos):
                        lista.upravit_hlasitost(0.1)   # Zvýšit hlasitost o 10 %
                    elif hasattr(lista, 'btn_res_change') and lista.btn_res_change.collidepoint(event.pos):
                        if width == 800:
                            width, height = 1920, 1080
                            screen = pygame.display.set_mode((width, height), pygame.FULLSCREEN)
                        else:
                            width, height = 800, 600
                            screen = pygame.display.set_mode((width, height))
                        lista._aktualizovat_rozmery_okna(width, height)
                    elif hasattr(lista, 'btn_exit_game') and lista.btn_exit_game.collidepoint(event.pos):
                        running = False
                    continue

                # Check if logo was clicked
                if lista.logo_rect.collidepoint(event.pos):
                    lista.settings_otevrene = True
                    continue

                # Check if singer was clicked
                if lista.singer_rect.collidepoint(event.pos) or (lista.mikrofon_active and lista.mikrofon_rect.collidepoint(event.pos)):
                    lista.penize += lista.sila_kliku
                    lista.singer_target_scale = 1.15  # Animate singer
                # Check if menu button was clicked
                elif lista.menu_rect.collidepoint(event.pos):
                    lista.menu_otevrene = not lista.menu_otevrene
                    lista.odrazu = 0
                    lista.menu_rychlost = 0  # Restarts velocity for immediate stop/reverse
                    if not lista.menu_otevrene:  # Reset scroll only when closing
                        lista.scroll_offset = 0
                # Check for buy button clicks
                elif lista.menu_vyska > 0:
                    menu_y = lista.vyska + 5
                    visible_index = 0
                    for i in range(len(lista.menu_items)):
                        # Skip bought items
                        if i in lista.bought_items:
                            continue
                        
                        item_y = menu_y + visible_index * (lista.item_height + lista.item_spacing) - lista.scroll_offset
                        visible_index += 1
                        
                        if lista.vyska < item_y + lista.item_height < lista.vyska + lista.menu_vyska:
                            button_x = lista.sirka - lista.scrollbar_width - lista.button_width - 20
                            button_y = item_y + (lista.item_height - lista.button_height) // 2
                            button_rect = pygame.Rect(button_x, button_y, lista.button_width, lista.button_height)
                            
                            if button_rect.collidepoint(event.pos):
                                price = lista.item_prices.get(i, 0)
                                if lista.penize >= price:
                                    lista.penize -= price


                                    lista.bought_items.add(i)

                                    # If item 0 (Microphone) is purchased
                                    if i == 0:
                                        lista.mikrofon_active = True
                                        lista.prijem += 1  # Mikrofon vydělává automaticky 1$ za vteřinu
                                        lista.sila_kliku += 1 # A také přidává hodnotu pro ruční klikání
                                    
                                    # If item 1 (drummer) is purchased
                                    elif i == 1:
                                        lista.drummer_active = True
                                        lista.prijem += 2
                                    
                                    # If item 2 (guitarist) is purchased
                                    elif i == 2:
                                        lista.guitarist_active = True
                                        lista.prijem += 3

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
    
    # Update income (every second)
    current_time = time.time()
    if current_time - last_income_update >= 1.0:
        lista.penize += lista.prijem
        last_income_update = current_time

    # Drummer hit frequency (e.g. every 2.5 seconds)
    if lista.drummer_active and current_time - last_drum_hit >= 2.5:
        lista.zahraj_na_buben()
        last_drum_hit = current_time

    # Guitarist strum frequency (e.g. every 1.5 seconds)
    if lista.guitarist_active and current_time - last_guitar_strum >= 1.5:
        lista.zahraj_na_kytaru()
        last_guitar_strum = current_time
    
    lista.nakresli(okno=screen)

    pygame.display.flip()

pygame.quit()
sys.exit()