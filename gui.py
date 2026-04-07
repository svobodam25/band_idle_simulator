import pygame

penize_font = pygame.font.SysFont(None, 60)

class Lista():
    def __init__(self, sirka, vyska):
        self.barva = (139, 69, 19)
        self.sirka = sirka
        self.vyska = 100
        self.penize = 0
        self.font = pygame.font.SysFont(None, 60)

        self.menu_otevrene = False 
        self.menu_vyska = 0 
        self.menu_max_vyska = vyska 
        self.rychlost = 1 
        self.animace_trvani = 500 # ms (0.5 sekundy) 
        self.animace_start = 0 
        self.start_vyska = 0 
        self.cil_vyska = 0
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)


    def update(self): 
        ted = pygame.time.get_ticks() 
        t = (ted - self.animace_start) / self.animace_trvani 
        # clamp 0–1 
        if t > 1: 
            t = 1 
        t = t * t * (3 - 2 * t) 
        self.menu_vyska = self.start_vyska + (self.cil_vyska - self.start_vyska) * t


    def nakresli(self, okno):
        pygame.draw.rect(okno, self.barva, (0, 0, self.sirka, self.vyska))

        text = penize_font.render(f"{self.penize}$", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.sirka // 2, self.vyska // 2))
        okno.blit(text, text_rect)

        line_color = (0, 0, 0)
        line_width = 5

        x_start = self.sirka - 80
        x_end = self.sirka - 30

        pygame.draw.line(okno, line_color, (x_start, 35), (x_end, 35), line_width)
        pygame.draw.line(okno, line_color, (x_start, 50), (x_end, 50), line_width)
        pygame.draw.line(okno, line_color, (x_start, 65), (x_end, 65), line_width)

        if self.menu_vyska > 0:
            tmava_hneda = (90, 50, 20)
            pygame.draw.rect(okno, tmava_hneda, (0, self.vyska, self.sirka, self.menu_vyska))

