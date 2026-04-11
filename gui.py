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
prijem_font = pygame.font.SysFont(None, 36)

class Lista():
    def __init__(self, sirka, vyska):
        self.barva = (139, 69, 19)
        self.sirka = sirka
        self.vyska_okna = vyska
        self.vyska = 100
        self.penize = 1000000
        self.prijem = 0
        self.sila_kliku = 1
        self.kliknuti_historie = []
        self.font = pygame.font.SysFont(None, 60)

        self.menu_otevrene = False
        self.odrazu = 0
        self.menu_vyska = 0 
        self.menu_max_vyska = vyska
        self.menu_gravitace = 0.12
        self.menu_rychlost = 0
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        self.kategorie = ["Členové", "Vylepšení"]
        self.aktivni_kategorie = "Členové"

        self.menu_items = {
            "Členové": ["Mikrofon", "Bubeník", "Kytarista", "Pianista", "DJ", "Položka 6", "Položka 7"],
            "Vylepšení": ["Zlaté hlasivky (+1 Klik)", "Lepší paličky (+2 $/s)", "Lepší trsátko (+5 $/s)", "Těžké basy (+8 $/s)", "Lepší mikrofon (+5 Klik)", "Lepší klávesy (+6 $/s)", "Lepší mix pult (+8 $/s)"]
        }
        self.item_prices = {
            "Členové": {0: 25, 1: 75, 2: 150, 3: 400, 4: 1000, 5: 3000, 6: 10000},
            "Vylepšení": {0: 200, 1: 450, 2: 900, 3: 2000, 4: 5000, 5: 3500, 6: 8000}
        }
        self.bought_items = {"Členové": set(), "Vylepšení": set()}
        self.upgrade_tooltips = {
            0: "Silnejsi hlas: +1 klik.",
            1: "Bubenik boost: +2 $/s (jen kdyz je aktivni).",
            2: "Kytara boost: +5 $/s (jen kdyz je aktivni).",
            3: "Bass boost: +8 $/s.",
            4: "Silnejsi mikrofon: +5 klik.",
            5: "Piano boost: +6 $/s (jen kdyz je aktivni).",
            6: "DJ boost: +8 $/s (jen kdyz je aktivni)."
        }
        
        self.item_height = 70
        self.item_spacing = 10
        self.scroll_offset = 0
        self.scrollbar_width = 10
        self.item_color = (120, 70, 30)
        
        self.scrollbar_color = (100, 100, 100)
        self.scrollbar_hover_color = (150, 150, 150)
        self.scrollbar_dragging = False
        
        self.button_color = (34, 139, 34)
        self.button_disabled_color = (150, 150, 150)
        self.button_height = 60
        self.button_width = 80
        self.button_font = pygame.font.SysFont(None, 30)
        self.price_font = pygame.font.SysFont(None, 25)
        self.tooltip_font = pygame.font.SysFont(None, 24)
        self.floating_font = pygame.font.SysFont(None, 28)
        self.combo_font = pygame.font.SysFont(None, 40)
        self.button_text = self.button_font.render("Koupit", True, (255, 255, 255))

        self.singer_x = sirka // 2
        self.singer_y = 300
        self.singer_image = pygame.image.load("obrazky/docasny_zpevak.png")
        self.singer_rect = self.singer_image.get_rect(center=(self.singer_x, self.singer_y))
        self.singer_scale = 1.0
        self.singer_target_scale = 1.0
        self.singer_animation_speed = 0.15
        
        self.background_image = pygame.image.load("obrazky/docasne_pozadi.png")
        self.background_image = pygame.transform.scale(self.background_image, (sirka, vyska))
        
        self.audience_image = pygame.image.load("obrazky/docasny_publikum.png")
        self.audience_image = pygame.transform.scale(self.audience_image, (218, 183))

        self.logo_image = pygame.image.load("obrazky/logo.png")
        self.logo_image = pygame.transform.smoothscale(self.logo_image, (120, 120))
        self.logo_rect = self.logo_image.get_rect(center=(70, 50))

        self.drummer_image = pygame.image.load("obrazky/bubenik.png")
        self.drummer_image = pygame.transform.scale(self.drummer_image, (200, 200))
        self.drummer_rect = self.drummer_image.get_rect(center=(self.sirka // 4, self.singer_y - 30))
        self.drum_image = pygame.image.load("obrazky/docasne_buben.png")
        self.drum_image = pygame.transform.scale(self.drum_image, (60, 60))
        self.drum_rect = self.drum_image.get_rect(center=(self.sirka // 4, self.singer_y + 80))
        self.drummer_active = False

        self.guitarist_image = pygame.image.load("obrazky/kytarista.png")
        self.guitarist_image = pygame.transform.scale(self.guitarist_image, (200, 200))
        self.guitarist_rect = self.guitarist_image.get_rect(center=(self.sirka - (self.sirka // 4), self.singer_y - 30))
        self.guitarist_active = False

        self.pianist_image = pygame.image.load("obrazky/pianista.png")
        self.pianist_image = pygame.transform.scale(self.pianist_image, (200, 200))
        self.pianist_rect = self.pianist_image.get_rect(center=(self.sirka // 6, self.singer_y - 30))
        self.pianist_active = False

        self.dj_image = pygame.image.load("obrazky/DJ.png")
        self.dj_image = pygame.transform.scale(self.dj_image, (200, 200))
        self.dj_rect = self.dj_image.get_rect(center=(self.sirka - (self.sirka // 6), self.singer_y - 30))
        self.dj_active = False

        self.mikrofon_active = False
        try:
            self.mikrofon_image = pygame.image.load("obrazky/mikrofon.png")
            mic_w = self.mikrofon_image.get_width()
            mic_h = self.mikrofon_image.get_height()
            self.mikrofon_image = pygame.transform.smoothscale(self.mikrofon_image, (int(mic_w * 0.5), int(mic_h * 0.5)))
        except:
            self.mikrofon_image = pygame.Surface((30, 80), pygame.SRCALPHA)
        self.mikrofon_rect = self.mikrofon_image.get_rect(center=(self.singer_x - 40, self.singer_y + 70))
        
        self.hlasitost = 0.5 

        self.guitar_scale = 1.0
        self.guitar_target_scale = 1.0
        self.guitar_animation_speed = 0.35
        try:
            self.guitar_sound = pygame.mixer.Sound("zvuky/kytara.wav")
            self.guitar_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání kytara.wav:", e)
            self.guitar_sound = None

        self.drum_scale = 1.0
        self.drum_target_scale = 1.0
        self.drum_animation_speed = 0.2
        try:
            self.drum_sound = pygame.mixer.Sound("zvuky/buben.wav")
            self.drum_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání buben.wav:", e)
            self.drum_sound = None

        self.piano_scale = 1.0
        self.piano_target_scale = 1.0
        self.piano_animation_speed = 0.3

        self.dj_scale = 1.0
        self.dj_target_scale = 1.0
        self.dj_animation_speed = 0.25

        self.button_text_disabled = self.button_font.render("Koupit", True, (100, 100, 100))

        self.settings_otevrene = False
        self.settings_tab = 'Sound'
        self.animations_disabled = False
        self.fps_options = [30, 60, 120, 0]
        self.fps_index = 1
        self.ui_scale = 1.0
        
        self.btn_res_change = pygame.Rect(self.sirka // 2 - 100, self.vyska_okna // 2 + 10, 200, 40)
        self.prepnut_rozliseni_v_hlavnim = False

        self.floating_texts = []
        self.combo_count = 0
        self.combo_until = 0.0
        self.combo_clicks = 0
        self.combo_multiplier = 1.0
        
        self._aktualizovat_rozmery_okna(sirka, vyska)

    def set_ui_scale(self, new_scale):
        self.ui_scale = max(0.5, min(2.0, float(new_scale)))

    def screen_to_ui_pos(self, screen_pos):
        scale = float(getattr(self, 'ui_scale', 1.0))
        if abs(scale - 1.0) < 1e-6:
            return screen_pos

        ui_w = max(1, int(round(self.sirka * scale)))
        ui_h = max(1, int(round(self.vyska_okna * scale)))
        offset_x = (self.sirka - ui_w) // 2
        offset_y = (self.vyska_okna - ui_h) // 2

        x = (screen_pos[0] - offset_x) / scale
        y = (screen_pos[1] - offset_y) / scale
        return (x, y)

    def _aktualizovat_rozmery_okna(self, sirka, vyska):
        self.sirka = sirka
        self.vyska_okna = vyska
        self.menu_max_vyska = vyska
        
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        self.settings_rect = pygame.Rect(self.sirka // 2 - 250, self.vyska_okna // 2 - 220, 500, 460)
        self.btn_zavrit_nastaveni = pygame.Rect(self.settings_rect.right - 40, self.settings_rect.y + 10, 30, 30)
        
        tab_w = 140
        self.btn_tab_sound = pygame.Rect(self.settings_rect.x + 30, self.settings_rect.y + 60, tab_w, 40)
        self.btn_tab_graphics = pygame.Rect(self.btn_tab_sound.right + 10, self.settings_rect.y + 60, tab_w, 40)
        self.btn_tab_developer = pygame.Rect(self.btn_tab_graphics.right + 10, self.settings_rect.y + 60, tab_w, 40)
        
        self.btn_vol_minus = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 180, 50, 50)
        self.btn_vol_plus = pygame.Rect(self.settings_rect.centerx + 50, self.settings_rect.y + 180, 50, 50)
        
        self.btn_res_change = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 130, 200, 40)
        self.btn_anim_toggle = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 185, 200, 40)
        self.btn_fps_change = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 240, 200, 40)
        self.btn_ui_scale_minus = pygame.Rect(self.settings_rect.centerx - 170, self.settings_rect.y + 295, 40, 40)
        self.btn_ui_scale_plus = pygame.Rect(self.settings_rect.centerx + 130, self.settings_rect.y + 295, 40, 40)
        
        self.btn_exit_game = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.bottom - 60, 200, 40)
        
        self.settings_font = pygame.font.SysFont(None, 45)
        self.vol_btn_font = pygame.font.SysFont(None, 60)
        self.res_font = pygame.font.SysFont(None, 35)

        self.menu_gravitace = 0.12 if self.vyska_okna <= 600 else 0.28

        self.singer_x = self.sirka // 2
        self.singer_y = (self.vyska_okna // 2) + 100 if self.vyska_okna > 600 else self.vyska_okna // 2
        self.singer_rect = self.singer_image.get_rect(center=(self.singer_x, self.singer_y))

        if self.vyska_okna <= 600:
            drummer_x = int(self.sirka * 0.30)
            guitarist_x = int(self.sirka * 0.70)
            pianist_x = int(self.sirka * 0.14)
            dj_x = int(self.sirka * 0.86)
        else:
            drummer_x = self.sirka // 4
            guitarist_x = self.sirka - (self.sirka // 4)
            pianist_x = self.sirka // 6
            dj_x = self.sirka - (self.sirka // 6)

        self.drummer_rect = self.drummer_image.get_rect(center=(drummer_x, self.singer_y - 30))
        self.drum_rect = self.drum_image.get_rect(center=(drummer_x, self.singer_y + 80))

        self.guitarist_rect = self.guitarist_image.get_rect(center=(guitarist_x, self.singer_y - 30))
        self.pianist_rect = self.pianist_image.get_rect(center=(pianist_x, self.singer_y - 30))
        self.dj_rect = self.dj_image.get_rect(center=(dj_x, self.singer_y - 30))

        if hasattr(self, 'mikrofon_image'):
            self.mikrofon_rect = self.mikrofon_image.get_rect(center=(self.singer_x - 40, self.singer_y + 70))

        try:
            bg_surface = pygame.image.load("obrazky/docasne_pozadi.png")
            self.background_image = pygame.transform.scale(bg_surface, (self.sirka, self.vyska_okna))
        except:
            pass

        try:
            aud_surf = pygame.image.load("obrazky/docasny_publikum.png")
            if self.vyska_okna > 600:
                self.audience_image = pygame.transform.scale(aud_surf, (int(218 * 1.8), int(183 * 1.8)))
            else:
                self.audience_image = pygame.transform.scale(aud_surf, (218, 183))
        except:
            pass

    def upravit_hlasitost(self, delta):
        self.hlasitost += delta
        self.hlasitost = round(self.hlasitost, 2)
        if self.hlasitost > 1.0: self.hlasitost = 1.0
        if self.hlasitost < 0.0: self.hlasitost = 0.0
        
        real_volume = self.hlasitost ** 2
        
        if self.drum_sound: self.drum_sound.set_volume(real_volume)
        if hasattr(self, 'guitar_sound') and self.guitar_sound: self.guitar_sound.set_volume(real_volume)
        self.update_audio_layers()

    def pridat_floating_text(self, x, y, text, color=(255, 255, 255), life=1.0):
        self.floating_texts.append({
            "x": float(x),
            "y": float(y),
            "text": str(text),
            "color": color,
            "born": time.time(),
            "life": max(0.1, float(life))
        })

    def update_audio_layers(self):
        active_count = sum([
            1 if self.drummer_active else 0,
            1 if self.guitarist_active else 0,
            1 if self.pianist_active else 0,
            1 if self.dj_active else 0,
        ])
        mix = active_count / 4.0
        real_volume = self.hlasitost ** 2

        if self.drum_sound:
            base = 0.08 + (0.27 if self.drummer_active else 0.0)
            self.drum_sound.set_volume(real_volume * base * (0.75 + 0.5 * mix))
        if self.guitar_sound:
            base = 0.08 + (0.30 if self.guitarist_active else 0.0)
            self.guitar_sound.set_volume(real_volume * base * (0.75 + 0.5 * mix))

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

    def zahraj_na_piano(self):
        """Spustí animaci pianisty."""
        self.piano_target_scale = 1.3
        if self.guitar_sound:
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume((self.hlasitost ** 2) * 0.22)
                ch.play(self.guitar_sound)

    def zahraj_dj_set(self):
        """Spustí animaci DJ."""
        self.dj_target_scale = 1.3
        if self.drum_sound:
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume((self.hlasitost ** 2) * 0.18)
                ch.play(self.drum_sound)

    def update(self): 
        self.update_audio_layers()

        now = time.time()
        self.floating_texts = [
            t for t in self.floating_texts
            if (now - t["born"]) <= t["life"]
        ]

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
                if self.odrazu >= 6:
                    self.menu_vyska = self.menu_max_vyska
        elif 0 < self.menu_vyska <= self.menu_max_vyska and not self.menu_otevrene:
            nasobitel_zavirani = 5 if self.vyska_okna > 600 else 2
            self.menu_rychlost -= self.menu_gravitace * nasobitel_zavirani
            self.menu_vyska += self.menu_rychlost
            if self.menu_vyska <= 0:
                self.menu_vyska = 0
                self.menu_rychlost = 0

        # When animations are disabled, keep all performer scales static.
        if getattr(self, 'animations_disabled', False):
            self.drum_scale = 1.0
            self.drum_target_scale = 1.0
            self.guitar_scale = 1.0
            self.guitar_target_scale = 1.0
            self.piano_scale = 1.0
            self.piano_target_scale = 1.0
            self.dj_scale = 1.0
            self.dj_target_scale = 1.0
            self.singer_scale = 1.0
            self.singer_target_scale = 1.0
            return
        

        if hasattr(self, 'drum_scale'):
            if abs(self.drum_scale - self.drum_target_scale) > 0.01:
                self.drum_scale += (self.drum_target_scale - self.drum_scale) * self.drum_animation_speed
            else:
                self.drum_scale = self.drum_target_scale
                if abs(self.drum_target_scale - 1.3) < 0.01 and abs(self.drum_scale - 1.3) < 0.01:
                    self.drum_target_scale = 1.0

        if hasattr(self, 'guitar_scale'):
            if abs(self.guitar_scale - self.guitar_target_scale) > 0.01:
                self.guitar_scale += (self.guitar_target_scale - self.guitar_scale) * self.guitar_animation_speed
            else:
                self.guitar_scale = self.guitar_target_scale
                if abs(self.guitar_target_scale - 1.3) < 0.01 and abs(self.guitar_scale - 1.3) < 0.01:
                    self.guitar_target_scale = 1.0

        if hasattr(self, 'piano_scale'):
            if abs(self.piano_scale - self.piano_target_scale) > 0.01:
                self.piano_scale += (self.piano_target_scale - self.piano_scale) * self.piano_animation_speed
            else:
                self.piano_scale = self.piano_target_scale
                if abs(self.piano_target_scale - 1.3) < 0.01 and abs(self.piano_scale - 1.3) < 0.01:
                    self.piano_target_scale = 1.0

        if hasattr(self, 'dj_scale'):
            if abs(self.dj_scale - self.dj_target_scale) > 0.01:
                self.dj_scale += (self.dj_target_scale - self.dj_scale) * self.dj_animation_speed
            else:
                self.dj_scale = self.dj_target_scale
                if abs(self.dj_target_scale - 1.3) < 0.01 and abs(self.dj_scale - 1.3) < 0.01:
                    self.dj_target_scale = 1.0

        if abs(self.singer_scale - self.singer_target_scale) > 0.01:
            self.singer_scale += (self.singer_target_scale - self.singer_scale) * self.singer_animation_speed
        else:
            self.singer_scale = self.singer_target_scale
            if abs(self.singer_target_scale - 1.15) < 0.01 and abs(self.singer_scale - 1.15) < 0.01:
                self.singer_target_scale = 0.85
            elif abs(self.singer_target_scale - 0.85) < 0.01 and abs(self.singer_scale - 0.85) < 0.01:
                self.singer_target_scale = 1.0


        if abs(self.singer_scale - self.singer_target_scale) > 0.01:
            self.singer_scale += (self.singer_target_scale - self.singer_scale) * self.singer_animation_speed
        else:
            self.singer_scale = self.singer_target_scale
            if abs(self.singer_target_scale - 1.15) < 0.01 and abs(self.singer_scale - 1.15) < 0.01:
                self.singer_target_scale = 0.85
            elif abs(self.singer_target_scale - 0.85) < 0.01 and abs(self.singer_scale - 0.85) < 0.01:
                self.singer_target_scale = 1.0

    def nakresli(self, okno):
        okno.blit(self.background_image, (0, 0))
        
        scaled_width = int(self.singer_image.get_width() * self.singer_scale)
        scaled_height = int(self.singer_image.get_height() * self.singer_scale)
        scaled_singer = pygame.transform.smoothscale(self.singer_image, (scaled_width, scaled_height))
        self.singer_rect = scaled_singer.get_rect(center=(self.singer_x, self.singer_y))
        okno.blit(scaled_singer, self.singer_rect)
        
        if self.mikrofon_active:
            mic_w = int(self.mikrofon_image.get_width() * self.singer_scale)
            mic_h = int(self.mikrofon_image.get_height() * self.singer_scale)
            scaled_mic = pygame.transform.smoothscale(self.mikrofon_image, (mic_w, mic_h))
            temp_mic_rect = scaled_mic.get_rect(center=self.mikrofon_rect.center)
            okno.blit(scaled_mic, temp_mic_rect)
            
        if self.drummer_active:
            scale = getattr(self, 'drum_scale', 1.0)
            y_offset = (scale - 1.0) * -30
            
            temp_drummer_rect = self.drummer_rect.copy()
            temp_drummer_rect.y += int(y_offset)

            scaled_w = int(self.drum_image.get_width() * scale)
            scaled_h = int(self.drum_image.get_height() * scale)
            scaled_drum = pygame.transform.smoothscale(self.drum_image, (scaled_w, scaled_h))
            temp_drum_rect = scaled_drum.get_rect(center=self.drum_rect.center)

            okno.blit(scaled_drum, temp_drum_rect)
            okno.blit(self.drummer_image, temp_drummer_rect)
        
        if self.guitarist_active:
            scale = getattr(self, 'guitar_scale', 1.0)
            y_offset = (scale - 1.0) * -30
            
            temp_guitarist_rect = self.guitarist_rect.copy()
            temp_guitarist_rect.y += int(y_offset)
            
            scaled_w = int(self.guitarist_image.get_width() * scale)
            scaled_h = int(self.guitarist_image.get_height() * scale)
            scaled_guitarist = pygame.transform.smoothscale(self.guitarist_image, (scaled_w, scaled_h))
            
            temp_guitarist_rect = scaled_guitarist.get_rect(center=temp_guitarist_rect.center)
            okno.blit(scaled_guitarist, temp_guitarist_rect)

        if self.pianist_active:
            scale = getattr(self, 'piano_scale', 1.0)
            y_offset = (scale - 1.0) * -30

            temp_pianist_rect = self.pianist_rect.copy()
            temp_pianist_rect.y += int(y_offset)

            scaled_w = int(self.pianist_image.get_width() * scale)
            scaled_h = int(self.pianist_image.get_height() * scale)
            scaled_pianist = pygame.transform.smoothscale(self.pianist_image, (scaled_w, scaled_h))

            temp_pianist_rect = scaled_pianist.get_rect(center=temp_pianist_rect.center)
            okno.blit(scaled_pianist, temp_pianist_rect)

        if self.dj_active:
            scale = getattr(self, 'dj_scale', 1.0)
            y_offset = (scale - 1.0) * -30

            temp_dj_rect = self.dj_rect.copy()
            temp_dj_rect.y += int(y_offset)

            scaled_w = int(self.dj_image.get_width() * scale)
            scaled_h = int(self.dj_image.get_height() * scale)
            scaled_dj = pygame.transform.smoothscale(self.dj_image, (scaled_w, scaled_h))

            temp_dj_rect = scaled_dj.get_rect(center=temp_dj_rect.center)
            okno.blit(scaled_dj, temp_dj_rect)

        ui_layer = pygame.Surface((self.sirka, self.vyska_okna), pygame.SRCALPHA)
        self._draw_ui_layer(ui_layer)

        scale = float(getattr(self, 'ui_scale', 1.0))
        if abs(scale - 1.0) < 1e-6:
            okno.blit(ui_layer, (0, 0))
        else:
            scaled_w = max(1, int(round(self.sirka * scale)))
            scaled_h = max(1, int(round(self.vyska_okna * scale)))
            scaled_ui = pygame.transform.smoothscale(ui_layer, (scaled_w, scaled_h))
            offset_x = (self.sirka - scaled_w) // 2
            offset_y = (self.vyska_okna - scaled_h) // 2
            okno.blit(scaled_ui, (offset_x, offset_y))

    def _draw_ui_layer(self, okno):
        mouse_ui_pos = self.screen_to_ui_pos(pygame.mouse.get_pos())
        hovered_upgrade_index = None

        if self.menu_vyska > 0:
            tmava_hneda = (90, 50, 20)
            pygame.draw.rect(okno, tmava_hneda, (0, self.vyska, self.sirka, self.menu_vyska))
            
            tab_width = (self.sirka - 40) // 2
            tab_y = self.vyska + 5
            
            self.rect_tab_clenove = pygame.Rect(20, tab_y, tab_width, 40)
            self.rect_tab_vylepseni = pygame.Rect(20 + tab_width, tab_y, tab_width, 40)
            
            pygame.draw.rect(okno, (100, 100, 100) if self.aktivni_kategorie != "Členové" else (150, 80, 40), self.rect_tab_clenove)
            pygame.draw.rect(okno, (100, 100, 100) if self.aktivni_kategorie != "Vylepšení" else (150, 80, 40), self.rect_tab_vylepseni)
            
            okno.blit(self.button_font.render("Členové", True, (255, 255, 255)), (self.rect_tab_clenove.x + 20, tab_y + 10))
            okno.blit(self.button_font.render("Vylepšení", True, (255, 255, 255)), (self.rect_tab_vylepseni.x + 20, tab_y + 10))
            
            menu_y = self.vyska + 55
            visible_index = 0
            aktualni_polozky = self.menu_items[self.aktivni_kategorie]
            for i in range(len(aktualni_polozky)):
                if i in self.bought_items[self.aktivni_kategorie]:
                    continue
                
                item = aktualni_polozky[i]
                item_y = menu_y + visible_index * (self.item_height + self.item_spacing) - self.scroll_offset
                visible_index += 1
                
                if self.vyska < item_y + self.item_height < self.vyska + self.menu_vyska:
                    item_rect = pygame.Rect(5, item_y, self.sirka - self.scrollbar_width - 15, self.item_height)
                    if item_rect.bottom <= self.vyska_okna:
                        if self.aktivni_kategorie == "Vylepšení" and item_rect.collidepoint(mouse_ui_pos):
                            hovered_upgrade_index = i

                        pygame.draw.rect(okno, self.item_color, item_rect, border_radius=10)
                        
                        item_text = self.button_font.render(item, True, (255, 255, 255))
                        text_rect = item_text.get_rect(center=(self.sirka // 2 - 55, item_y + self.item_height // 2))
                        okno.blit(item_text, text_rect)
                        
                        price = self.item_prices[self.aktivni_kategorie].get(i, 0)
                        can_afford = self.penize >= price
                        
                        price_text = self.price_font.render(f"{price}$", True, (255, 255, 100))
                        price_rect = price_text.get_rect(center=(40, item_y + self.item_height // 2))
                        okno.blit(price_text, price_rect)
                        
                        button_x = self.sirka - self.scrollbar_width - self.button_width - 20
                        button_y = item_y + (self.item_height - self.button_height) // 2
                        button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
                        
                        button_color = self.button_color if can_afford else self.button_disabled_color
                        button_text_render = self.button_text if can_afford else self.button_text_disabled
                        
                        pygame.draw.rect(okno, button_color, button_rect, border_radius=8)
                        
                        button_text_rect = button_text_render.get_rect(center=button_rect.center)
                        okno.blit(button_text_render, button_text_rect)
            
            self._draw_scrollbar(okno)
            if hovered_upgrade_index is not None:
                tooltip = self.upgrade_tooltips.get(hovered_upgrade_index, "")
                if tooltip:
                    self._draw_tooltip(okno, tooltip, int(mouse_ui_pos[0]), int(mouse_ui_pos[1]))
        
        if not self.menu_otevrene:
            t = time.time()
            animace_vypnute = getattr(self, 'animations_disabled', False)
            
            je_full_hd = self.vyska_okna > 600
            pocet_rad = 2 if je_full_hd else 1
            
            spacing_x = 220 if je_full_hd else 100
            pocet_fanousku = math.ceil(self.sirka / spacing_x) + 2
            
            for row in range(pocet_rad):
                if not je_full_hd:
                    base_y = self.vyska_okna - 163
                    shift_x = 0
                else:
                    base_y = self.vyska_okna - 330 + (row * 90)
                    shift_x = (row % 2) * 80
                
                for i in range(pocet_fanousku):
                    audience_x = (i * spacing_x) - 60 + shift_x
                    
                    if je_full_hd and row == 0:
                        šírka_obrazku = 218 * 1.8
                        stred_fanouska = audience_x + (šírka_obrazku / 2)
                        if abs(stred_fanouska - self.sirka // 2) < 300:
                            continue

                    jump_offset = 0 if animace_vypnute else abs(math.sin(t * 5 + i * 0.5 + row * 2.0)) * 20
                    audience_y = base_y - int(jump_offset)
                    okno.blit(self.audience_image, (audience_x, audience_y))
        
        pygame.draw.rect(okno, self.barva, (0, 0, self.sirka, self.vyska))

        okno.blit(self.logo_image, self.logo_rect)

        text = penize_font.render(f"{self.penize}$", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.sirka // 2, self.vyska // 2))
        okno.blit(text, text_rect)

        aktualni_cas = time.time()
        self.kliknuti_historie = [(cas, hodnota) for cas, hodnota in self.kliknuti_historie if aktualni_cas - cas <= 1.0]
        celkovy_prijem = self.prijem + sum(hodnota for cas, hodnota in self.kliknuti_historie)

        prijem_text = prijem_font.render(f"(+{celkovy_prijem} $/s)", True, (50, 205, 50))
        prijem_rect = prijem_text.get_rect(midleft=(text_rect.right + 10, self.vyska // 2 + 5))
        okno.blit(prijem_text, prijem_rect)

        line_color = (0, 0, 0)
        line_width = 5

        x_start = self.sirka - 80
        x_end = self.sirka - 30

        pygame.draw.line(okno, line_color, (x_start, 35), (x_end, 35), line_width)
        pygame.draw.line(okno, line_color, (x_start, 50), (x_end, 50), line_width)
        pygame.draw.line(okno, line_color, (x_start, 65), (x_end, 65), line_width)

        if time.time() < getattr(self, 'combo_until', 0.0):
            combo_mul = float(getattr(self, 'combo_multiplier', 1.0))
            combo_text = self.combo_font.render(f"COMBO x{combo_mul:.1f}", True, (255, 220, 80))
            combo_rect = combo_text.get_rect(center=(self.singer_x, max(120, self.singer_y - 170)))
            okno.blit(combo_text, combo_rect)

        self._draw_floating_texts(okno)

        if self.settings_otevrene:
            overlay = pygame.Surface((self.sirka, self.vyska_okna))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            okno.blit(overlay, (0, 0))

            pygame.draw.rect(okno, (220, 220, 220), self.settings_rect, border_radius=15)
            pygame.draw.rect(okno, (0, 0, 0), self.settings_rect, 3, border_radius=15)
            
            nadpis_text = self.settings_font.render("Nastavení", True, (0, 0, 0))
            okno.blit(nadpis_text, nadpis_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 30)))

            # Tabs
            def draw_tab(rect, label, is_active):
                color = (255, 255, 255) if is_active else (170, 170, 170)
                pygame.draw.rect(okno, color, rect, border_radius=8)
                pygame.draw.rect(okno, (0, 0, 0), rect, 2, border_radius=8)
                txt = self.res_font.render(label, True, (0, 0, 0))
                okno.blit(txt, txt.get_rect(center=rect.center))

            draw_tab(self.btn_tab_sound, "Zvuk", getattr(self, 'settings_tab', '') == "Sound")
            draw_tab(self.btn_tab_graphics, "Grafika", getattr(self, 'settings_tab', '') == "Graphics")
            draw_tab(self.btn_tab_developer, "Vývojáři", getattr(self, 'settings_tab', '') == "Developer")

            tab = getattr(self, 'settings_tab', 'Sound')
            
            if tab == "Sound":
                vol_text = self.res_font.render("Hlasitost hudby:", True, (0, 0, 0))
                okno.blit(vol_text, vol_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 140)))
                
                vol_val = self.settings_font.render(f"{int(self.hlasitost * 100)}%", True, (0, 0, 0))
                okno.blit(vol_val, vol_val.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 205)))

                pygame.draw.rect(okno, (255, 100, 100), self.btn_vol_minus, border_radius=10)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_vol_minus, 2, border_radius=10)
                okno.blit(self.vol_btn_font.render("-", True, (0, 0, 0)), self.vol_btn_font.render("-", True, (0, 0, 0)).get_rect(center=self.btn_vol_minus.center))

                pygame.draw.rect(okno, (100, 255, 100), self.btn_vol_plus, border_radius=10)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_vol_plus, 2, border_radius=10)
                okno.blit(self.vol_btn_font.render("+", True, (0, 0, 0)), self.vol_btn_font.render("+", True, (0, 0, 0)).get_rect(center=self.btn_vol_plus.center))
            
            elif tab == "Graphics":
                # Resolution
                pygame.draw.rect(okno, (100, 150, 255), self.btn_res_change, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_res_change, 2, border_radius=5)
                res_txt = self.res_font.render("1920x1080" if self.sirka == 1920 else "800x600", True, (0, 0, 0))
                okno.blit(res_txt, res_txt.get_rect(center=self.btn_res_change.center))

                # Animations
                anim_dis = getattr(self, 'animations_disabled', False)
                anim_color = (255, 100, 100) if anim_dis else (100, 255, 100)
                pygame.draw.rect(okno, anim_color, self.btn_anim_toggle, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_anim_toggle, 2, border_radius=5)
                anim_txt = self.res_font.render("Animace: VYP" if anim_dis else "Animace: ZAP", True, (0, 0, 0))
                okno.blit(anim_txt, anim_txt.get_rect(center=self.btn_anim_toggle.center))

                # FPS Limit
                pygame.draw.rect(okno, (200, 200, 100), self.btn_fps_change, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_fps_change, 2, border_radius=5)
                opts = getattr(self, 'fps_options', [30, 60, 120, 0])
                idx = getattr(self, 'fps_index', 1)
                fps_val = opts[idx]
                fps_str = f"FPS Lock: {fps_val}" if fps_val > 0 else "FPS Limit: Bez limitu"
                fps_txt = self.res_font.render(fps_str, True, (0, 0, 0))
                okno.blit(fps_txt, fps_txt.get_rect(center=self.btn_fps_change.center))

                # UI Scale
                scale_val = getattr(self, 'ui_scale', 1.0)
                scale_txt = self.res_font.render(f"UI Scale: {scale_val:.1f}x", True, (0, 0, 0))
                okno.blit(scale_txt, scale_txt.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 315)))
                
                pygame.draw.rect(okno, (255, 150, 150), self.btn_ui_scale_minus, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_ui_scale_minus, 2, border_radius=5)
                okno.blit(self.res_font.render("-", True, (0, 0, 0)), self.res_font.render("-", True, (0, 0, 0)).get_rect(center=self.btn_ui_scale_minus.center))

                pygame.draw.rect(okno, (150, 255, 150), self.btn_ui_scale_plus, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_ui_scale_plus, 2, border_radius=5)
                okno.blit(self.res_font.render("+", True, (0, 0, 0)), self.res_font.render("+", True, (0, 0, 0)).get_rect(center=self.btn_ui_scale_plus.center))

            elif tab == "Developer":
                devs = ["Michal Svoboda", "Štěpán Šitina", "Daniel Wales"]
                dev_title = self.res_font.render("Autoři hry:", True, (0, 0, 0))
                okno.blit(dev_title, dev_title.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 140)))
                
                for idx, dev in enumerate(devs):
                    txt = self.settings_font.render(dev, True, (80, 80, 80))
                    okno.blit(txt, txt.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 200 + (idx * 40))))

            # Close Button
            pygame.draw.rect(okno, (255, 100, 100), self.btn_exit_game, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_exit_game, 2, border_radius=10)
            okno.blit(self.res_font.render("Odejít ze hry", True, (0, 0, 0)), self.res_font.render("Odejít ze hry", True, (0, 0, 0)).get_rect(center=self.btn_exit_game.center))

            pygame.draw.rect(okno, (220, 50, 50), self.btn_zavrit_nastaveni, border_radius=5)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_zavrit_nastaveni, 2, border_radius=5)
            zavrit_text = self.settings_font.render("X", True, (255, 255, 255))
            okno.blit(zavrit_text, zavrit_text.get_rect(center=self.btn_zavrit_nastaveni.center))

    def _draw_tooltip(self, okno, text, x, y):
        render = self.tooltip_font.render(text, True, (255, 255, 255))
        pad = 8
        rect = render.get_rect()
        rect.x = min(max(10, x + 14), self.sirka - rect.width - (pad * 2) - 10)
        rect.y = min(max(self.vyska + 10, y + 14), self.vyska_okna - rect.height - (pad * 2) - 10)
        bg = pygame.Rect(rect.x - pad, rect.y - pad, rect.width + (pad * 2), rect.height + (pad * 2))
        pygame.draw.rect(okno, (20, 20, 20), bg, border_radius=8)
        pygame.draw.rect(okno, (255, 255, 255), bg, 1, border_radius=8)
        okno.blit(render, rect)

    def _draw_floating_texts(self, okno):
        now = time.time()
        for entry in self.floating_texts:
            age = now - entry["born"]
            life = entry["life"]
            progress = max(0.0, min(1.0, age / life))
            alpha = int(255 * (1.0 - progress))

            text_surface = self.floating_font.render(entry["text"], True, entry["color"])
            text_surface.set_alpha(alpha)

            y_offset = int(34 * progress)
            pos = (int(entry["x"]), int(entry["y"] - y_offset))
            okno.blit(text_surface, pos)
    
    def _draw_scrollbar(self, okno):
        """Draw scrollbar on the right side of the menu"""
        if self.menu_vyska <= 0:
            return
        
        if self.menu_vyska < self.menu_max_vyska * 0.999:
            return
        
        aktualni = self.menu_items[self.aktivni_kategorie]
        koupene = self.bought_items[self.aktivni_kategorie]
        visible_items_count = len([i for i in range(len(aktualni)) if i not in koupene])
        total_content_height = visible_items_count * self.item_height + max(0, (visible_items_count - 1) * self.item_spacing)
        visible_height = min(self.menu_vyska, self.vyska_okna - self.vyska)
        max_scroll = max(0, total_content_height + 5 - visible_height)
        
        if total_content_height <= visible_height - 5:
            return
        
        scrollbar_x = self.sirka - self.scrollbar_width - 2
        track_rect = pygame.Rect(scrollbar_x, self.vyska, self.scrollbar_width, visible_height)
        pygame.draw.rect(okno, (50, 50, 50), track_rect)
        
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
        
        aktualni = self.menu_items[self.aktivni_kategorie]
        koupene = self.bought_items[self.aktivni_kategorie]
        visible_items_count = len([i for i in range(len(aktualni)) if i not in koupene])
        total_content_height = visible_items_count * self.item_height + max(0, (visible_items_count - 1) * self.item_spacing)
        visible_height = min(self.menu_vyska, self.vyska_okna - self.vyska)
        max_scroll = max(0, total_content_height + 5 - visible_height)
        
        scroll_amount = 40
        self.scroll_offset += direction * scroll_amount
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

