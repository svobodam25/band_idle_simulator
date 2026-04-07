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
            if lista.menu_rect.collidepoint(event.pos):
                lista.menu_otevrene = not lista.menu_otevrene
                
                lista.animace_start = pygame.time.get_ticks()
                lista.start_vyska = lista.menu_vyska
                lista.cil_vyska = lista.menu_max_vyska if lista.menu_otevrene else 0
    screen.fill((255, 255, 255))

    lista.update()
    lista.nakresli(okno=screen)

    pygame.display.flip()

pygame.quit()
sys.exit()