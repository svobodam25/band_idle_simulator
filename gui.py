import pygame
import time
import math

penize_font = pygame.font.SysFont(None, 60)

class Lista():
    def __init__(self, sirka, vyska):
        self.barva = (139, 69, 19)
        self.sirka = sirka
        self.vyska_okna = vyska  # Store window height
        self.vyska = 100
        self.penize = 0
        self.prijem = 0  # 1$ per second
        self.font = pygame.font.SysFont(None, 60)

        self.menu_otevrene = False
        self.odrazu = 0
        self.menu_vyska = 0 
        self.menu_max_vyska = vyska
        self.menu_gravitace = 0.005
        self.menu_rychlost = 0
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        # Menu items
        self.menu_items = ["Bubeník", "Položka 2", "Položka 3", "Položka 4", "Položka 5", "Položka 6", "Položka 7", "Položka 8"]
        self.item_prices = {0: 25, 1: 75, 2: 150, 3: 300, 4: 600, 5: 1000, 6: 1800, 7: 3000}  # Price for each item
        self.bought_items = set()  # Track bought items
        self.item_height = 70
        self.item_spacing = 10
        self.scroll_offset = 0
        self.scrollbar_width = 10
        self.item_color = (120, 70, 30)
        
        # Scrollbar properties
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_hover_color = (150, 150, 150)
        self.scrollbar_dragging = False
        
        # Button properties
        self.button_color = (34, 139, 34)
        self.button_disabled_color = (150, 150, 150)  # Gray color for disabled button
        self.button_height = 60
        self.button_width = 80
        self.button_font = pygame.font.SysFont(None, 30)
        self.price_font = pygame.font.SysFont(None, 25)
        self.button_text = self.button_font.render("Koupit", True, (255, 255, 255))

        # Singer properties
        self.singer_x = sirka // 2
        self.singer_y = 300
        self.singer_image = pygame.image.load("obrazky/docasny_zpevak.png")
        self.singer_rect = self.singer_image.get_rect(center=(self.singer_x, self.singer_y))
        self.singer_scale = 1.0  # Current scale factor
        self.singer_target_scale = 1.0  # Target scale factor
        self.singer_animation_speed = 0.15  # How fast to animate
        
        # Background
        self.background_image = pygame.image.load("obrazky/docasne_pozadi.png")
        self.background_image = pygame.transform.scale(self.background_image, (sirka, vyska))
        
        # Audience properties
        self.audience_image = pygame.image.load("obrazky/docasny_publikum.png")
        self.audience_image = pygame.transform.scale(self.audience_image, (218, 183))

        # Logo properties
        self.logo_image = pygame.image.load("obrazky/logo.png")
        self.logo_image = pygame.transform.smoothscale(self.logo_image, (120, 120))  # Resize logo to 120x120 with better quality
        self.logo_rect = self.logo_image.get_rect(center=(70, 50))

        # Drummer properties
        self.drummer_image = pygame.image.load("obrazky/bubenik.png")
        self.drummer_image = pygame.transform.scale(self.drummer_image, (200, 200))  # Resize drummer to 200x200
        self.drummer_rect = self.drummer_image.get_rect(center=(180, self.singer_y - 30))
        self.drum_image = pygame.image.load("obrazky/docasne_buben.png")
        self.drum_image = pygame.transform.scale(self.drum_image, (60, 60))  # Resize drum to 60x60
        self.drum_rect = self.drum_image.get_rect(center=(180, self.singer_y + 80))
        self.drummer_active = False  # Becomes True when purchased
        
        # Animace a zvuk bubnu
        self.drum_scale = 1.0
        self.drum_target_scale = 1.0
        self.drum_animation_speed = 0.2
        try:
            pygame.mixer.init()
            self.drum_sound = pygame.mixer.Sound("zvuky/buben.wav")
        except:
            self.drum_sound = None

        self.button_text_disabled = self.button_font.render("Koupit", True, (100, 100, 100))

    def zahraj_na_buben(self):
        """Spustí animaci a popř. zvuk úderu do bubnu."""
        self.drum_target_scale = 1.3
        if self.drum_sound:
            self.drum_sound.play()



    def update(self): 
        if not self.menu_otevrene and self.menu_vyska >= 600:
            self.menu_vyska = 600
        if self.menu_otevrene and self.menu_vyska <= 0:
            self.menu_vyska = 0

        if 0 <=self.menu_vyska < self.menu_max_vyska and self.menu_otevrene:
            self.menu_rychlost += self.menu_gravitace
            self.menu_vyska += self.menu_rychlost
            if self.menu_vyska > self.menu_max_vyska:
                self.odrazu += 1
                self.menu_vyska -= self.menu_rychlost
                self.menu_rychlost = self.menu_rychlost * -0.5
                self.menu_vyska += self.menu_rychlost
                if self.odrazu >= 10:
                    self.menu_vyska = self.menu_max_vyska
        elif 0 < self.menu_vyska <= self.menu_max_vyska and not self.menu_otevrene:
            self.menu_rychlost -= self.menu_gravitace
            self.menu_vyska += self.menu_rychlost
            if self.menu_vyska <= 0:
                self.menu_vyska = 0
                self.menu_rychlost = 0
        

        # Drummer stays active permanently once purchased (no timer countdown)
        if hasattr(self, 'drum_scale'):
            if abs(self.drum_scale - self.drum_target_scale) > 0.01:
                self.drum_scale += (self.drum_target_scale - self.drum_scale) * self.drum_animation_speed
            else:
                self.drum_scale = self.drum_target_scale
                # Pokud buben dosáhl maximálního zvětšení, vrátí se zpět
                if abs(self.drum_target_scale - 1.3) < 0.01 and abs(self.drum_scale - 1.3) < 0.01:
                    self.drum_target_scale = 1.0

        # Update singer animation
        if abs(self.singer_scale - self.singer_target_scale) > 0.01:
            self.singer_scale += (self.singer_target_scale - self.singer_scale) * self.singer_animation_speed
        else:
            self.singer_scale = self.singer_target_scale
            # Sequence animation: 1.0 -> 1.15 -> 0.85 -> 1.0
            if abs(self.singer_target_scale - 1.15) < 0.01 and abs(self.singer_scale - 1.15) < 0.01:
                self.singer_target_scale = 0.85
            elif abs(self.singer_target_scale - 0.85) < 0.01 and abs(self.singer_scale - 0.85) < 0.01:
                self.singer_target_scale = 1.0


        # Update singer animation
        if abs(self.singer_scale - self.singer_target_scale) > 0.01:
            self.singer_scale += (self.singer_target_scale - self.singer_scale) * self.singer_animation_speed
        else:
            self.singer_scale = self.singer_target_scale
            # Sequence animation: 1.0 -> 1.15 -> 0.85 -> 1.0
            if abs(self.singer_target_scale - 1.15) < 0.01 and abs(self.singer_scale - 1.15) < 0.01:
                self.singer_target_scale = 0.85
            elif abs(self.singer_target_scale - 0.85) < 0.01 and abs(self.singer_scale - 0.85) < 0.01:
                self.singer_target_scale = 1.0

    def nakresli(self, okno):
        # Draw background always
        okno.blit(self.background_image, (0, 0))
        
        # Draw singer in the middle (background) with animation
        # Scale the singer image
        scaled_width = int(self.singer_image.get_width() * self.singer_scale)
        scaled_height = int(self.singer_image.get_height() * self.singer_scale)
        scaled_singer = pygame.transform.smoothscale(self.singer_image, (scaled_width, scaled_height))
        self.singer_rect = scaled_singer.get_rect(center=(self.singer_x, self.singer_y))
        okno.blit(scaled_singer, self.singer_rect)
        
        # Draw drummer and drum if active
        if self.drummer_active:
            # Efekt poskoku pro bubeníka a zvětšení bubnu
            scale = getattr(self, 'drum_scale', 1.0)
            y_offset = (scale - 1.0) * -30  # Zvedne bubeníka, když se buben zvětší
            
            temp_drummer_rect = self.drummer_rect.copy()
            temp_drummer_rect.y += int(y_offset)

            scaled_w = int(self.drum_image.get_width() * scale)
            scaled_h = int(self.drum_image.get_height() * scale)
            scaled_drum = pygame.transform.smoothscale(self.drum_image, (scaled_w, scaled_h))
            temp_drum_rect = scaled_drum.get_rect(center=self.drum_rect.center)

            okno.blit(scaled_drum, temp_drum_rect)
            okno.blit(self.drummer_image, temp_drummer_rect)
        
        # Draw menu (above singer)
        if self.menu_vyska > 0:
            tmava_hneda = (90, 50, 20)
            pygame.draw.rect(okno, tmava_hneda, (0, self.vyska, self.sirka, self.menu_vyska))
            
            # Draw menu items
            menu_y = self.vyska + 5
            visible_index = 0
            for i in range(len(self.menu_items)):
                # Skip bought items
                if i in self.bought_items:
                    continue
                
                item = self.menu_items[i]
                item_y = menu_y + visible_index * (self.item_height + self.item_spacing) - self.scroll_offset
                visible_index += 1
                
                if self.vyska < item_y + self.item_height < self.vyska + self.menu_vyska:
                    # Draw item background with rounded corners
                    item_rect = pygame.Rect(5, item_y, self.sirka - self.scrollbar_width - 15, self.item_height)
                    pygame.draw.rect(okno, self.item_color, item_rect, border_radius=10)
                    
                    # Draw centered text moved 50px to the left
                    item_text = self.font.render(item, True, (255, 255, 255))
                    text_rect = item_text.get_rect(center=(self.sirka // 2 - 55, item_y + self.item_height // 2))
                    okno.blit(item_text, text_rect)
                    
                    # Check if player can afford this item
                    price = self.item_prices.get(i, 0)
                    can_afford = self.penize >= price
                    
                    # Draw price on the left side
                    price_text = self.price_font.render(f"{price}$", True, (255, 255, 100))
                    price_rect = price_text.get_rect(center=(40, item_y + self.item_height // 2))
                    okno.blit(price_text, price_rect)
                    
                    # Draw buy button on the right (gray if can't afford)
                    button_x = self.sirka - self.scrollbar_width - self.button_width - 20
                    button_y = item_y + (self.item_height - self.button_height) // 2
                    button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
                    
                    button_color = self.button_color if can_afford else self.button_disabled_color
                    button_text_render = self.button_text if can_afford else self.button_text_disabled
                    
                    pygame.draw.rect(okno, button_color, button_rect, border_radius=8)
                    
                    # Draw "Koupit" text on button
                    button_text_rect = button_text_render.get_rect(center=button_rect.center)
                    okno.blit(button_text_render, button_text_rect)
            
            # Draw scrollbar
            self._draw_scrollbar(okno)
        
        # Draw audience at the bottom (centered) with jumping effect
        t = time.time()
        # Jumping: absolute sine wave makes it bounce. Multiply by 20 for height, 5 for speed
        jump_offset = abs(math.sin(t * 5)) * 20
        audience_y = self.vyska_okna - 163 - int(jump_offset)
        audience_x = (self.sirka - 218) // 2
        okno.blit(self.audience_image, (audience_x, audience_y))
        
        # Draw header bar on top (always on top)
        pygame.draw.rect(okno, self.barva, (0, 0, self.sirka, self.vyska))

        # Draw logo in top-left corner
        okno.blit(self.logo_image, self.logo_rect)

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
    
    def _draw_scrollbar(self, okno):
        """Draw scrollbar on the right side of the menu"""
        if self.menu_vyska <= 0:
            return
        
        # Only draw scrollbar when menu is fully expanded
        if self.menu_vyska < self.menu_max_vyska * 0.999:
            return
        
        # Count visible items (not bought)
        visible_items_count = len([i for i in range(len(self.menu_items)) if i not in self.bought_items])
        # Total content height = items height + spacing between items (not after last item)
        total_content_height = visible_items_count * self.item_height + max(0, (visible_items_count - 1) * self.item_spacing)
        # Visible height is limited by window height
        visible_height = min(self.menu_vyska, self.vyska_okna - self.vyska)
        # Account for the 5px offset at the top
        max_scroll = max(0, total_content_height + 5 - visible_height)
        
        if total_content_height <= visible_height - 5:
            return
        
        # Scrollbar track
        scrollbar_x = self.sirka - self.scrollbar_width - 2
        track_rect = pygame.Rect(scrollbar_x, self.vyska, self.scrollbar_width, visible_height)
        pygame.draw.rect(okno, (50, 50, 50), track_rect)
        
        # Scrollbar handle
        handle_height = max(20, (visible_height / (total_content_height + 5)) * visible_height)
        handle_y = self.vyska + (self.scroll_offset / max_scroll) * (visible_height - handle_height) if max_scroll > 0 else self.vyska
        handle_rect = pygame.Rect(scrollbar_x, handle_y, self.scrollbar_width, handle_height)
        
        mouse_pos = pygame.mouse.get_pos()
        color = self.scrollbar_hover_color if handle_rect.collidepoint(mouse_pos) else self.scrollbar_color
        pygame.draw.rect(okno, color, handle_rect)
    
    def handle_scroll(self, direction):
        """Handle scroll wheel or scrollbar interaction"""
        if self.menu_vyska <= 0:
            return
        
        # Count visible items (not bought)
        visible_items_count = len([i for i in range(len(self.menu_items)) if i not in self.bought_items])
        # Total content height = items height + spacing between items (not after last item)
        total_content_height = visible_items_count * self.item_height + max(0, (visible_items_count - 1) * self.item_spacing)
        # Visible height is limited by window height
        visible_height = min(self.menu_vyska, self.vyska_okna - self.vyska)
        # Account for the 5px offset at the top
        max_scroll = max(0, total_content_height + 5 - visible_height)
        
        scroll_amount = 40  # pixels to scroll per wheel event
        self.scroll_offset += direction * scroll_amount
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

