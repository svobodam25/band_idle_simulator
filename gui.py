import pygame
import time
import math

pygame.init()
pygame.font.init()
try:
    pygame.mixer.init()
except Exception as e:
    print("Zvuk nemohl být inicializován:", e)

penize_font = pygame.font.SysFont(None, 60)

class Lista():
    def __init__(self, sirka, vyska):
        self.barva = (139, 69, 19)
        self.sirka = sirka
        self.vyska_okna = vyska  # Store window height
        self.vyska = 100
        self.penize = 0
        self.prijem = 0  # Pasivní příjem za sekundu
        self.sila_kliku = 1  # Peníze za jedno kliknutí na zpěváka
        self.font = pygame.font.SysFont(None, 60)

        self.menu_otevrene = False
        self.odrazu = 0
        self.menu_vyska = 0 
        self.menu_max_vyska = vyska
        self.menu_gravitace = 0.005
        self.menu_rychlost = 0
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        # Menu items
        self.menu_items = ["Mikrofon", "Bubeník", "Kytarista", "Položka 4", "Položka 5", "Položka 6", "Položka 7", "Položka 8"]
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
        self.drummer_rect = self.drummer_image.get_rect(center=(self.sirka // 4, self.singer_y - 30))
        self.drum_image = pygame.image.load("obrazky/docasne_buben.png")
        self.drum_image = pygame.transform.scale(self.drum_image, (60, 60))  # Resize drum to 60x60
        self.drum_rect = self.drum_image.get_rect(center=(self.sirka // 4, self.singer_y + 80))
        self.drummer_active = False  # Becomes True when purchased

        # Guitarist properties
        self.guitarist_image = pygame.image.load("obrazky/kytarista.png")
        self.guitarist_image = pygame.transform.scale(self.guitarist_image, (200, 200))
        self.guitarist_rect = self.guitarist_image.get_rect(center=(self.sirka - (self.sirka // 4), self.singer_y - 30))
        self.guitarist_active = False

        # Mikrofon properties
        self.mikrofon_active = False
        try:
            self.mikrofon_image = pygame.image.load("obrazky/mikrofon.png")
            # Zmenšení mikrofonu na 50 % původní velikosti obrázku
            mic_w = self.mikrofon_image.get_width()
            mic_h = self.mikrofon_image.get_height()
            self.mikrofon_image = pygame.transform.smoothscale(self.mikrofon_image, (int(mic_w * 0.5), int(mic_h * 0.5)))
        except:
            # Fallback prázdný obrázek, než uživatel do složky obrázek skutečně vloží
            self.mikrofon_image = pygame.Surface((30, 80), pygame.SRCALPHA)
        # Posunutí mikrofonu ještě o kousek více doleva (z -30 na -40)
        self.mikrofon_rect = self.mikrofon_image.get_rect(center=(self.singer_x - 40, self.singer_y + 70))
        
        # Nastavení výchozí hlasitosti před načtením zvuků
        self.hlasitost = 0.5 

        # Animace a zvuk kytary
        self.guitar_scale = 1.0
        self.guitar_target_scale = 1.0
        self.guitar_animation_speed = 0.35  # Rychlejší animace než u bubnu
        try:
            self.guitar_sound = pygame.mixer.Sound("zvuky/kytara.wav")
            # Pro inicializaci bereme z výchozí proměnné (hlasitost umocníme na druhou)
            self.guitar_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání kytara.wav:", e)
            self.guitar_sound = None

        # Animace a zvuk bubnu
        self.drum_scale = 1.0
        self.drum_target_scale = 1.0
        self.drum_animation_speed = 0.2
        try:
            self.drum_sound = pygame.mixer.Sound("zvuky/buben.wav")
            # Pro inicializaci bereme z výchozí proměnné (hlasitost umocníme na druhou)
            self.drum_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání buben.wav:", e)
            self.drum_sound = None

        self.button_text_disabled = self.button_font.render("Koupit", True, (100, 100, 100))

        # Settings
        self.settings_otevrene = False
        
        self.btn_res_change = pygame.Rect(self.sirka // 2 - 100, self.vyska_okna // 2 + 10, 200, 40)
        self.prepnut_rozliseni_v_hlavnim = False
        
        self._aktualizovat_rozmery_okna(sirka, vyska)

    def _aktualizovat_rozmery_okna(self, sirka, vyska):
        self.sirka = sirka
        self.vyska_okna = vyska
        self.menu_max_vyska = vyska
        
        # Menu elements
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        # Settings window dimensions
        self.settings_rect = pygame.Rect(self.sirka // 2 - 200, self.vyska_okna // 2 - 175, 400, 350)
        self.btn_vol_minus = pygame.Rect(self.settings_rect.x + 50, self.settings_rect.y + 60, 50, 50)
        self.btn_vol_plus = pygame.Rect(self.settings_rect.x + 300, self.settings_rect.y + 60, 50, 50)
        self.btn_zavrit_nastaveni = pygame.Rect(self.settings_rect.right - 40, self.settings_rect.y + 10, 30, 30)
        self.btn_res_change = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 200, 200, 40)
        self.btn_exit_game = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 270, 200, 40)
        
        self.settings_font = pygame.font.SysFont(None, 45)
        self.vol_btn_font = pygame.font.SysFont(None, 60)
        self.res_font = pygame.font.SysFont(None, 35)

        self.menu_gravitace = 0.005 if self.vyska_okna <= 600 else 0.015

        # Singer positioning
        self.singer_x = self.sirka // 2
        self.singer_y = self.vyska_okna // 2
        self.singer_rect = self.singer_image.get_rect(center=(self.singer_x, self.singer_y))

        # Drummer positioning
        self.drummer_rect = self.drummer_image.get_rect(center=(self.sirka // 4, self.singer_y - 30))
        self.drum_rect = self.drum_image.get_rect(center=(self.sirka // 4, self.singer_y + 80))

        # Guitarist positioning
        self.guitarist_rect = self.guitarist_image.get_rect(center=(self.sirka - (self.sirka // 4), self.singer_y - 30))

        # Microphone positioning
        if hasattr(self, 'mikrofon_image'):
            # Držíme nové odsazení -40 (malinko více doleva od zpěváka) a +70 (více dolů) i na fullscreenu
            self.mikrofon_rect = self.mikrofon_image.get_rect(center=(self.singer_x - 40, self.singer_y + 70))

        # Background update
        try:
            bg_surface = pygame.image.load("obrazky/docasne_pozadi.png")
            self.background_image = pygame.transform.scale(bg_surface, (self.sirka, self.vyska_okna))
        except:
            pass

    def upravit_hlasitost(self, delta):
        self.hlasitost += delta
        self.hlasitost = round(self.hlasitost, 2) # Prevents floating point errors like 0.10000000000000002
        if self.hlasitost > 1.0: self.hlasitost = 1.0
        if self.hlasitost < 0.0: self.hlasitost = 0.0
        
        # Umocníme na druhou pro logaritmický pociťový průběh hlasitosti - 10 % bude tiše ale slyšet
        real_volume = self.hlasitost ** 2
        
        if self.drum_sound: self.drum_sound.set_volume(real_volume)
        if hasattr(self, 'guitar_sound') and self.guitar_sound: self.guitar_sound.set_volume(real_volume)

    def zahraj_na_buben(self):
        """Spustí animaci a popř. zvuk úderu do bubnu."""
        self.drum_target_scale = 1.3
        if self.drum_sound:
            self.drum_sound.play()

    def zahraj_na_kytaru(self):
        """Spustí animaci a popř. zvuk kytary."""
        self.guitar_target_scale = 1.3
        if self.guitar_sound:
            self.guitar_sound.play()

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
            # Zavíráme menu - padá nahoru
            # Pokud jsme ve Full HD (vyska_okna > 600), zavíráme ještě mnohem rychleji
            nasobitel_zavirani = 5 if self.vyska_okna > 600 else 2
            self.menu_rychlost -= self.menu_gravitace * nasobitel_zavirani
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

        # Update guitar animation
        if hasattr(self, 'guitar_scale'):
            if abs(self.guitar_scale - self.guitar_target_scale) > 0.01:
                self.guitar_scale += (self.guitar_target_scale - self.guitar_scale) * self.guitar_animation_speed
            else:
                self.guitar_scale = self.guitar_target_scale
                if abs(self.guitar_target_scale - 1.3) < 0.01 and abs(self.guitar_scale - 1.3) < 0.01:
                    self.guitar_target_scale = 1.0

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
        
        # Draw mikrofon
        if self.mikrofon_active:
            okno.blit(self.mikrofon_image, self.mikrofon_rect)
            
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
        
        # Draw guitarist if active
        if self.guitarist_active:
            scale = getattr(self, 'guitar_scale', 1.0)
            y_offset = (scale - 1.0) * -30  # Poskok nahoru
            
            temp_guitarist_rect = self.guitarist_rect.copy()
            temp_guitarist_rect.y += int(y_offset)
            
            scaled_w = int(self.guitarist_image.get_width() * scale)
            scaled_h = int(self.guitarist_image.get_height() * scale)
            scaled_guitarist = pygame.transform.smoothscale(self.guitarist_image, (scaled_w, scaled_h))
            
            # Use the moved rect center
            temp_guitarist_rect = scaled_guitarist.get_rect(center=temp_guitarist_rect.center)
            okno.blit(scaled_guitarist, temp_guitarist_rect)

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
        
        # Draw audience at the bottom with jumping effect (multiple instances to cover width)
        if not self.menu_otevrene:
            t = time.time()
            pocet_fanousku = math.ceil(self.sirka / 100) + 2  # Nahustí fanoušky více k sobě
            
            # V normálním režimu (800x600) kreslíme jako předtím jen 1 řadu, ve Full HD 4 řady
            pocet_rad = 1 if self.vyska_okna <= 600 else 4
            
            for row in range(pocet_rad):
                if pocet_rad == 1:
                    # Původní jedná řada pro normální okno
                    base_y = self.vyska_okna - 163
                    shift_x = 0
                else:
                    # 4 řady pro Full HD
                    base_y = self.vyska_okna - 300 + (row * 45)
                    shift_x = (row % 2) * 40  # Každá sudá řada je lehce posunutá
                
                for i in range(pocet_fanousku):
                    audience_x = (i * 100) - 60 + shift_x
                    
                    # Odstraníme pár fanoušků pouze nahoře uprostřed u pódia ve Full HD
                    if pocet_rad == 4 and row < 2:
                        stred_fanouska = audience_x + 109  # Obrázek publika má na šířku 218px
                        # Odebere fanoušky blízko pódia jen v horních (zadních) 2 řadách 
                        if abs(stred_fanouska - self.sirka // 2) < 250:
                            continue

                    # Každá řada a každý fanoušek má trochu jinou frekvenci/ofset výskoku
                    jump_offset = abs(math.sin(t * 5 + i * 0.5 + row * 2.0)) * 20
                    audience_y = base_y - int(jump_offset)
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

        if self.settings_otevrene:
            # Poloprůhledné pozadí
            overlay = pygame.Surface((self.sirka, self.vyska_okna))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            okno.blit(overlay, (0, 0))

            pygame.draw.rect(okno, (200, 200, 200), self.settings_rect, border_radius=15)
            pygame.draw.rect(okno, (0, 0, 0), self.settings_rect, 3, border_radius=15)
            
            nadpis_text = self.settings_font.render("Nastavení", True, (0, 0, 0))
            nadpis_rect = nadpis_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 30))
            okno.blit(nadpis_text, nadpis_rect)

            vol_text = self.res_font.render(f"Hlasitost hudby:", True, (0, 0, 0))
            vol_rect = vol_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 60))
            okno.blit(vol_text, vol_rect)

            vol_val = self.settings_font.render(f"{int(self.hlasitost * 100)}%", True, (0, 0, 0))
            vol_val_rect = vol_val.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 85))
            okno.blit(vol_val, vol_val_rect)

            pygame.draw.rect(okno, (255, 100, 100), self.btn_vol_minus, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_vol_minus, 2, border_radius=10)
            minus_text = self.vol_btn_font.render("-", True, (0, 0, 0))
            minus_rect = minus_text.get_rect(center=self.btn_vol_minus.center)
            okno.blit(minus_text, minus_rect)

            pygame.draw.rect(okno, (100, 255, 100), self.btn_vol_plus, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_vol_plus, 2, border_radius=10)
            plus_text = self.vol_btn_font.render("+", True, (0, 0, 0))
            plus_rect = plus_text.get_rect(center=self.btn_vol_plus.center)
            okno.blit(plus_text, plus_rect)

            res_text = self.res_font.render("Rozlišení okna:", True, (0, 0, 0))
            res_rect = res_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 160))
            okno.blit(res_text, res_rect)

            pygame.draw.rect(okno, (100, 150, 255), self.btn_res_change, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_res_change, 2, border_radius=10)
            
            rezim_text_str = "1920x1080 (FullHD)" if self.sirka == 800 else "800x600 (Normal)"
            res_btn_text = self.res_font.render(rezim_text_str, True, (0, 0, 0))
            res_btn_rect = res_btn_text.get_rect(center=self.btn_res_change.center)
            okno.blit(res_btn_text, res_btn_rect)

            # Odejít ze hry button
            pygame.draw.rect(okno, (255, 100, 100), self.btn_exit_game, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_exit_game, 2, border_radius=10)
            exit_btn_text = self.res_font.render("Odejít ze hry", True, (0, 0, 0))
            exit_btn_rect = exit_btn_text.get_rect(center=self.btn_exit_game.center)
            okno.blit(exit_btn_text, exit_btn_rect)

            # Close button
            self.btn_zavrit_nastaveni = pygame.Rect(self.settings_rect.right - 40, self.settings_rect.y + 10, 30, 30)
            pygame.draw.rect(okno, (220, 50, 50), self.btn_zavrit_nastaveni, border_radius=5)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_zavrit_nastaveni, 2, border_radius=5)
            zavrit_text = self.settings_font.render("X", True, (255, 255, 255))
            zavrit_rect = zavrit_text.get_rect(center=self.btn_zavrit_nastaveni.center)
            okno.blit(zavrit_text, zavrit_rect)
    
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

