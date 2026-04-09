import pygame
import sys
pygame.init()

import gui

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Band Idle Simulator")

lista = gui.Lista(width, height)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Only left mouse button
                if lista.menu_rect.collidepoint(event.pos):
                    lista.menu_otevrene = not lista.menu_otevrene
                    lista.odrazu = 0
                    if not lista.menu_otevrene:  # Reset scroll only when closing
                        lista.scroll_offset = 0
                # Check for buy button clicks
                elif lista.menu_vyska > 0:
                    menu_y = lista.vyska + 5
                    for i in range(len(lista.menu_items)):
                        item_y = menu_y + i * (lista.item_height + lista.item_spacing) - lista.scroll_offset
                        if lista.vyska < item_y + lista.item_height < lista.vyska + lista.menu_vyska:
                            button_x = lista.sirka - lista.scrollbar_width - lista.button_width - 20
                            button_y = item_y + (lista.item_height - lista.button_height) // 2
                            button_rect = pygame.Rect(button_x, button_y, lista.button_width, lista.button_height)
                            
                            if button_rect.collidepoint(event.pos):
                                price = lista.item_prices.get(i, 0)
                                if lista.penize >= price:
                                    lista.penize -= price
        if event.type == pygame.MOUSEWHEEL:
            if lista.menu_vyska > 0:
                lista.handle_scroll(-event.y)
    screen.fill((255, 255, 255))

    lista.update()
    lista.nakresli(okno=screen)

    pygame.display.flip()

pygame.quit()
sys.exit()