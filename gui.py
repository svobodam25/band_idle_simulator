import pygame
import time
import math
import random

try:
    pygame.mixer.init()
except pygame.error:
    import os
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
pygame.init()
pygame.font.init()

penize_font = pygame.font.SysFont(None, 60)
prijem_font = pygame.font.SysFont(None, 36)

class Lista():
    def __init__(self, sirka, vyska):
        self.barva = (139, 69, 19)
        self.sirka = sirka
        self.vyska_okna = vyska
        self.vyska = 100
        self.penize = 0
        self.prijem = 0
        self.sila_kliku = 1000
        self.kliknuti_historie = []
        self.font = pygame.font.SysFont(None, 60)
        self.character_scale = 1.0 + (sirka - 800) / 3000.0  # Mírné škálování - max 1.37x

        self.rebirth_count = 0
        self.rebirth_requirement = 1_000_000
        self.rebirth_confirm_open = False
        self.statistics = {
            "total_clicks": 0,
            "total_earned": 0,
            "total_rebirths": 0,
        }

        self.menu_otevrene = False
        self.odrazu = 0
        self.menu_vyska = 0
        self.menu_max_vyska = vyska
        self.menu_gravitace = 0.35
        self.menu_rychlost = 0
        self._last_menu_update = None
        self._menu_physics_accum = 0.0
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        self.kategorie = ["Členové", "Vylepšení", "Rebirth"]
        self.aktivni_kategorie = "Členové"

        self.menu_items = {
            "Členové": ["Mikrofon", "Bubeník", "Kytarista", "Pianista", "DJ", "Sekuriťák", "Položka 7"],
            "Vylepšení": ["Zlaté hlasivky (+1 Klik)", "Lepší paličky (+3 $/s)", "Lepší trsátko (+5 $/s)", "Těžké basy (+8 $/s)", "Lepší mikrofon (+5 Klik)", "Lepší klávesy (+6 $/s)", "Lepší mix pult (+8 $/s)"],
            "Rebirth": ["Reset runu, trvale 2x prijem"]
        }
        self.menu_items_en = {
            "Členové": ["Microphone", "Drummer", "Guitarist", "Pianist", "DJ", "Security Guard", "Item 7"],
            "Vylepšení": ["Golden Vocal Cords (+1 Click)", "Better Drumsticks (+3 $/s)", "Better Pick (+5 $/s)", "Heavy Bass (+8 $/s)", "Better Microphone (+5 Click)", "Better Keys (+6 $/s)", "Better Mixer (+8 $/s)"],
            "Rebirth": ["Reset run, permanent 2x income"]
        }
        self.item_prices = {
            "Členové": {0: 25, 1: 75, 2: 150, 3: 400, 4: 1000, 5: 3000, 6: 10000},
            "Vylepšení": {0: 200, 1: 450, 2: 900, 3: 2000, 4: 5000, 5: 3500, 6: 8000},
            "Rebirth": {0: 1_000_000}
        }
        self.bought_items = {"Členové": set(), "Vylepšení": set(), "Rebirth": set()}
        self.upgrade_tooltips = {
            0: "Silnejsi hlas: +1 klik.",
            1: "Bubenik boost: +3 $/s (jen kdyz je aktivni).",
            2: "Kytara boost: +5 $/s (jen kdyz je aktivni).",
            3: "Bass boost: +8 $/s.",
            4: "Silnejsi mikrofon: +5 klik.",
            5: "Piano boost: +6 $/s (jen kdyz je aktivni).",
            6: "DJ boost: +8 $/s (jen kdyz je aktivni)."
        }
        self.upgrade_tooltips_en = {
            0: "Stronger voice: +1 click.",
            1: "Drummer boost: +3 $/s (only when active).",
            2: "Guitar boost: +5 $/s (only when active).",
            3: "Bass boost: +8 $/s.",
            4: "Stronger mic: +5 click.",
            5: "Piano boost: +6 $/s (only when active).",
            6: "DJ boost: +8 $/s (only when active)."
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

        self.concert_active = None
        self.concert_buff_mult = 1.0
        self.concert_buff_end = 0.0
        self.concert_spawn_at = time.time() + random.uniform(45.0, 90.0)
        self.concert_font = pygame.font.SysFont(None, 32, bold=True)

        self.singer_x = sirka // 2
        self.singer_y = 300
        self.singer_image = pygame.image.load("obrazky/docasny_zpevak.png")
        singer_scaled_size = int(350 * self.character_scale)
        self.singer_image = pygame.transform.scale(self.singer_image, (singer_scaled_size, singer_scaled_size))
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
        drummer_scaled = int(200 * self.character_scale)
        self.drummer_image = pygame.transform.scale(self.drummer_image, (drummer_scaled, drummer_scaled))
        self.drummer_rect = self.drummer_image.get_rect(center=(self.sirka // 4, self.singer_y - 30))
        self.drum_image = pygame.image.load("obrazky/docasne_buben.png")


        drum_scaled = int(300 * self.character_scale)
        self.drum_image = pygame.transform.smoothscale(self.drum_image, (drum_scaled, drum_scaled))
        self.drum_rect = self.drum_image.get_rect(
            center=(self.drummer_rect.centerx + 30, self.drummer_rect.centery + 35)
        )


        self.drummer_active = False

        self.guitarist_image = pygame.image.load("obrazky/kytarista.png")
        guitarist_scaled = int(200 * self.character_scale)
        self.guitarist_image = pygame.transform.scale(self.guitarist_image, (guitarist_scaled, guitarist_scaled))
        self.guitarist_rect = self.guitarist_image.get_rect(center=(self.sirka - (self.sirka // 4), self.singer_y - 30))
        self.guitarist_active = False

        self.pianist_image = pygame.image.load("obrazky/pianista.png")
        pianist_scaled = int(200 * self.character_scale)
        self.pianist_image = pygame.transform.scale(self.pianist_image, (pianist_scaled, pianist_scaled))
        self.pianist_rect = self.pianist_image.get_rect(center=(self.sirka // 6, self.singer_y - 30))
        self.pianist_active = False

        self.dj_image = pygame.image.load("obrazky/DJ.png")
        dj_scaled = int(200 * self.character_scale)
        self.dj_image = pygame.transform.scale(self.dj_image, (dj_scaled, dj_scaled))
        self.dj_rect = self.dj_image.get_rect(center=(self.sirka - (self.sirka // 6), self.singer_y - 30))
        self.dj_active = False
        self.sekuritak_active = False

        self.mikrofon_active = False
        try:
            self.mikrofon_image = pygame.image.load("obrazky/mikrofon.png")
            mic_w = self.mikrofon_image.get_width()
            mic_h = self.mikrofon_image.get_height()
            mic_scaled_w = int(mic_w * 0.5 * self.character_scale)
            mic_scaled_h = int(mic_h * 0.5 * self.character_scale)
            self.mikrofon_image = pygame.transform.smoothscale(self.mikrofon_image, (mic_scaled_w, mic_scaled_h))
        except:
            self.mikrofon_image = pygame.Surface((30, 80), pygame.SRCALPHA)
        self.mikrofon_rect = self.mikrofon_image.get_rect(center=(self.singer_x - 40, self.singer_y + 70))
        
        try:
            img = pygame.image.load("obrazky/kotlar.png")
            w = img.get_width()
            h = img.get_height()
            self.sekuritak_image = pygame.transform.smoothscale(img, (int(w * 0.45), int(h * 0.45)))
        except:
            self.sekuritak_image = pygame.Surface((80, 80))
            self.sekuritak_image.fill((200, 0, 0))
        self.sekuritak_x = 100.0
        self.sekuritak_y = self.vyska_okna - 100.0
        self.sekuritak_cile_x = 100.0
        self.sekuritak_cile_y = self.vyska_okna - 100.0
        self.sekuritak_scale = 1.0
        self.sekuritak_fight_time = 0.0

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
        try:
            self.piano_sound = pygame.mixer.Sound("zvuky/piano.wav")
            self.piano_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání piano.wav:", e)
            self.piano_sound = None

        self.dj_scale = 1.0
        self.dj_target_scale = 1.0
        self.dj_animation_speed = 0.25
        try:
            self.dj_sound = pygame.mixer.Sound("zvuky/dj.wav")
            self.dj_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání dj.wav:", e)
            self.dj_sound = None

        try:
            self.sekuritak_sound = pygame.mixer.Sound("zvuky/kotlar.wav")
            self.sekuritak_sound.set_volume(self.hlasitost ** 2)
        except Exception as e:
            print("Chyba při načítání kotlar.wav:", e)
            self.sekuritak_sound = None

        self.button_text_disabled = self.button_font.render("Koupit", True, (100, 100, 100))

        self.settings_otevrene = False
        self.settings_tab = 'Sound'
        self.language = 'CZ'
        self.number_format = 'plain'
        self.show_combo_text = True
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
        self.task_font = pygame.font.SysFont(None, 24)
        self.income_font = pygame.font.SysFont(None, 23)
        self.task_income_buff = 1.0
        self.cosmetics_unlocked = set()
        self.daily_tasks = [
            {
                "id": "click_200",
                "title": "Udelej 200 kliku",
                "target": 200,
                "current": 0,
                "reward_type": "money",
                "reward_value": 1500,
                "completed": False,
                "claimed": False,
            },
            {
                "id": "buy_dj",
                "title": "Kup DJ",
                "target": 1,
                "current": 0,
                "reward_type": "buff",
                "reward_value": 0.10,
                "completed": False,
                "claimed": False,
            },
            {
                "id": "reach_10k_ps",
                "title": "Dosahni 100 $/s",
                "target": 100,
                "current": 0,
                "reward_type": "cosmetic",
                "reward_value": "gold_logo",
                "completed": False,
                "claimed": False,
            },
        ]
        self.task_panel_w = 280
        self.task_panel_h = 176
        self.task_panel_open = False
        self.task_panel_x = float(self.sirka + 10)
        self.task_panel_target_x = float(self.sirka + 10)
        self.btn_tasks_toggle = pygame.Rect(self.sirka - 190, 20, 95, 50)
        self.task_claim_buttons = {}
        
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
        
        # Aktualizuj scale faktor pro postavy (fixní základ, mírné škálování)
        self.character_scale = 0.7 + (sirka / 4000.0)
        
        self.menu_rect = pygame.Rect(self.sirka - 90, 20, 70, 60)
        
        settings_w = 640
        settings_h = 560
        settings_x = (self.sirka - settings_w) // 2
        settings_y = max(10, (self.vyska_okna - settings_h) // 2)
        self.settings_rect = pygame.Rect(settings_x, settings_y, settings_w, settings_h)
        self.btn_zavrit_nastaveni = pygame.Rect(self.settings_rect.right - 40, self.settings_rect.y + 10, 30, 30)
        
        tab_w = (self.settings_rect.width - 80 - 30) // 4
        self.btn_tab_sound = pygame.Rect(self.settings_rect.x + 30, self.settings_rect.y + 60, tab_w, 40)
        self.btn_tab_graphics = pygame.Rect(self.btn_tab_sound.right + 10, self.settings_rect.y + 60, tab_w, 40)
        self.btn_tab_ui = pygame.Rect(self.btn_tab_graphics.right + 10, self.settings_rect.y + 60, tab_w, 40)
        self.btn_tab_developer = pygame.Rect(self.btn_tab_ui.right + 10, self.settings_rect.y + 60, tab_w, 40)
        
        self.btn_vol_minus = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 180, 50, 50)
        self.btn_vol_plus = pygame.Rect(self.settings_rect.centerx + 50, self.settings_rect.y + 180, 50, 50)
        
        self.btn_res_change = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 130, 200, 40)
        self.btn_anim_toggle = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 185, 200, 40)
        self.btn_fps_change = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.y + 240, 200, 40)
        self.btn_ui_scale_minus = pygame.Rect(self.settings_rect.centerx - 170, self.settings_rect.y + 295, 40, 40)
        self.btn_ui_scale_plus = pygame.Rect(self.settings_rect.centerx + 130, self.settings_rect.y + 295, 40, 40)

        self.btn_lang_toggle = pygame.Rect(self.settings_rect.centerx - 120, self.settings_rect.y + 130, 240, 40)
        self.btn_num_format_toggle = pygame.Rect(self.settings_rect.centerx - 120, self.settings_rect.y + 185, 240, 40)
        self.btn_combo_toggle = pygame.Rect(self.settings_rect.centerx - 120, self.settings_rect.y + 240, 240, 40)
        self.btn_rebirth = pygame.Rect(self.settings_rect.centerx - 200, self.settings_rect.y + 390, 400, 48)
        self.btn_rebirth_confirm = pygame.Rect(self.settings_rect.centerx - 150, self.settings_rect.y + 472, 140, 40)
        self.btn_rebirth_cancel = pygame.Rect(self.settings_rect.centerx + 10, self.settings_rect.y + 472, 140, 40)
        
        self.btn_exit_game = pygame.Rect(self.settings_rect.centerx - 100, self.settings_rect.bottom - 60, 200, 40)
        self.btn_tasks_toggle = pygame.Rect(self.sirka - 190, 20, 95, 50)
        self.task_panel_target_x = float((self.sirka - self.task_panel_w - 10) if self.task_panel_open else (self.sirka + 10))
        if not hasattr(self, 'task_panel_x'):
            self.task_panel_x = self.task_panel_target_x
        
        self.settings_font = pygame.font.SysFont(None, 45)
        self.vol_btn_font = pygame.font.SysFont(None, 60)
        self.res_font = pygame.font.SysFont(None, 35)

        self.menu_gravitace = 0.5

        self.singer_x = self.sirka // 2
        self.singer_y = (self.vyska_okna // 2) + 100 if self.vyska_okna > 600 else self.vyska_okna // 2
        self.singer_rect = self.singer_image.get_rect(center=(self.singer_x, self.singer_y))
        
        # Škáluj zpěváka na základě velikosti okna
        singer_size = int(280 * self.character_scale)
        try:
            singer_original = pygame.image.load("obrazky/docasny_zpevak.png")
            self.singer_image = pygame.transform.scale(singer_original, (singer_size, singer_size))
        except:
            pass
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
        self.drum_rect = self.drum_image.get_rect(
            center=(self.drummer_rect.centerx + 30, self.drummer_rect.centery + 35)
        )

        self.guitarist_rect = self.guitarist_image.get_rect(center=(guitarist_x, self.singer_y - 30))
        self.pianist_rect = self.pianist_image.get_rect(center=(pianist_x, self.singer_y - 30))
        self.dj_rect = self.dj_image.get_rect(center=(dj_x, self.singer_y - 30))
        
        # Škáluj obrázky postav na základě velikosti okna (ale zachovej pozici)
        drummer_size = int(200 * self.character_scale)
        guitarist_size = int(200 * self.character_scale)
        pianist_size = int(200 * self.character_scale)
        dj_size = int(200 * self.character_scale)
        drum_size = int(300 * self.character_scale)
        
        try:
            drummer_original = pygame.image.load("obrazky/bubenik.png")
            self.drummer_image = pygame.transform.scale(drummer_original, (drummer_size, drummer_size))
        except:
            pass
        
        try:
            guitarist_original = pygame.image.load("obrazky/kytarista.png")
            self.guitarist_image = pygame.transform.scale(guitarist_original, (guitarist_size, guitarist_size))
        except:
            pass
        
        try:
            pianist_original = pygame.image.load("obrazky/pianista.png")
            self.pianist_image = pygame.transform.scale(pianist_original, (pianist_size, pianist_size))
        except:
            pass
        
        try:
            dj_original = pygame.image.load("obrazky/DJ.png")
            self.dj_image = pygame.transform.scale(dj_original, (dj_size, dj_size))
        except:
            pass
        
        try:
            drum_original = pygame.image.load("obrazky/docasne_buben.png")
            self.drum_image = pygame.transform.scale(drum_original, (drum_size, drum_size))
        except:
            pass
        
        # Nastav rect pro škálované obrázky (zachovej pozici)
        self.drummer_rect = self.drummer_image.get_rect(center=(drummer_x, self.singer_y - 30))
        self.drum_rect = self.drum_image.get_rect(
            center=(self.drummer_rect.centerx + 30, self.drummer_rect.centery + 35)
        )
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
        
        if not pygame.mixer.get_init():
            return
            
        if hasattr(self, 'drum_sound') and self.drum_sound: self.drum_sound.set_volume(real_volume)
        if hasattr(self, 'guitar_sound') and self.guitar_sound: self.guitar_sound.set_volume(real_volume)
        if hasattr(self, 'piano_sound') and self.piano_sound: self.piano_sound.set_volume(real_volume)
        if hasattr(self, 'dj_sound') and self.dj_sound: self.dj_sound.set_volume(real_volume)
        if hasattr(self, 'sekuritak_sound') and self.sekuritak_sound: self.sekuritak_sound.set_volume(real_volume)
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
        if not pygame.mixer.get_init():
            return
            
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

    def _txt(self, key):
        cs = {
            "settings": "Nastaveni",
            "tab_sound": "Zvuk",
            "tab_graphics": "Grafika",
            "tab_ui": "UI",
            "tab_developer": "Vyvojari",
            "exit": "Odejit ze hry",
            "volume": "Hlasitost hudby:",
            "authors": "Autori hry:",
            "lang": "Jazyk",
            "num": "Format cisel",
            "combo": "Combo text",
            "on": "ZAP",
            "off": "VYP",
            "buy": "Koupit",
            "tasks": "Ukoly",
            "daily_tasks": "Denni ukoly",
            "claim": "Vyzvednout",
            "claimed": "Vyzvednuto",
            "task": "Ukol",
            "cat_members": "Clenove",
            "cat_upgrades": "Vylepseni",
            "cat_rebirth": "Rebirth",
            "animations": "Animace",
            "fps_lock": "FPS Lock",
            "fps_unlimited": "Bez limitu",
            "rebirth": "Rebirth",
            "income_mult": "Nasobic prijmu",
            "next_rebirth": "Dalsi rebirth: 2x prijem",
            "rebirth_need": "Potrebujes 1 000 000$",
            "rebirth_confirm": "Potvrdit rebirth?",
            "confirm": "Potvrdit",
            "cancel": "Zrusit",
            "task_click_200": "Udelej 200 kliku",
            "task_buy_dj": "Kup DJ",
            "task_reach_100_ps": "Dosahni 100 $/s",
            "task_reward_money": "Ukol odmena +{amount}$",
            "task_reward_buff": "Ukol buff +{pct}%",
            "task_reward_cosmetic": "Nova kosmetika odemcena",
            "rebirth_from": "Rebirth od {need}$",
            "combo_label": "KOMBO",
            "rebirth_done": "Rebirth! Nasobic x{mult}",
            "rebirth_ready": "Pripraveno",
        }
        en = {
            "settings": "Settings",
            "tab_sound": "Sound",
            "tab_graphics": "Graphics",
            "tab_ui": "UI",
            "tab_developer": "Developers",
            "exit": "Exit game",
            "volume": "Music volume:",
            "authors": "Game authors:",
            "lang": "Language",
            "num": "Number format",
            "combo": "Combo text",
            "on": "ON",
            "off": "OFF",
            "buy": "Buy",
            "tasks": "Tasks",
            "daily_tasks": "Daily tasks",
            "claim": "Claim",
            "claimed": "Claimed",
            "task": "Task",
            "cat_members": "Members",
            "cat_upgrades": "Upgrades",
            "cat_rebirth": "Rebirth",
            "animations": "Animations",
            "fps_lock": "FPS Lock",
            "fps_unlimited": "Unlimited",
            "rebirth": "Rebirth",
            "income_mult": "Income multiplier",
            "next_rebirth": "Next rebirth: 2x income",
            "rebirth_need": "You need 1,000,000$",
            "rebirth_confirm": "Confirm rebirth?",
            "confirm": "Confirm",
            "cancel": "Cancel",
            "task_click_200": "Do 200 clicks",
            "task_buy_dj": "Buy DJ",
            "task_reach_100_ps": "Reach 100 $/s",
            "task_reward_money": "Task reward +{amount}$",
            "task_reward_buff": "Task buff +{pct}%",
            "task_reward_cosmetic": "New cosmetic unlocked",
            "rebirth_from": "Rebirth from {need}$",
            "combo_label": "COMBO",
            "rebirth_done": "Rebirth! Mult x{mult}",
            "rebirth_ready": "Ready",
        }
        table = en if getattr(self, 'language', 'CZ') == 'EN' else cs
        return table.get(key, key)

    def format_number(self, value):
        n = float(value)
        mode = getattr(self, 'number_format', 'plain')
        if mode == 'compact':
            absv = abs(n)
            if absv >= 1_000_000_000:
                return f"{n / 1_000_000_000:.2f}B"
            if absv >= 1_000_000:
                return f"{n / 1_000_000:.2f}M"
            if absv >= 1_000:
                return f"{n / 1_000:.2f}K"
            return str(int(round(n)))
        return f"{int(round(n)):,}"

    def get_menu_item_name(self, category, index):
        if getattr(self, 'language', 'CZ') == 'EN':
            return self.menu_items_en.get(category, self.menu_items.get(category, []))[index]
        return self.menu_items.get(category, [])[index]

    def get_upgrade_tooltip(self, index):
        if getattr(self, 'language', 'CZ') == 'EN':
            return self.upgrade_tooltips_en.get(index, "")
        return self.upgrade_tooltips.get(index, "")

    def get_task_title(self, task):
        tid = task.get('id', '')
        if tid == 'click_200':
            return self._txt('task_click_200')
        if tid == 'buy_dj':
            return self._txt('task_buy_dj')
        if tid == 'reach_10k_ps':
            return self._txt('task_reach_100_ps')
        return task.get('title', self._txt('task'))

    def get_rebirth_multiplier(self):
        return float(2 ** int(getattr(self, 'rebirth_count', 0)))

    def can_rebirth(self):
        requirement = int(getattr(self, 'rebirth_requirement', 1_000_000))
        return int(getattr(self, 'penize', 0)) >= requirement

    def perform_rebirth(self):
        self.rebirth_count = int(getattr(self, 'rebirth_count', 0)) + 1
        self.statistics["total_rebirths"] = int(self.statistics.get("total_rebirths", 0)) + 1

        # Reset run progress only.
        self.penize = 0
        self.prijem = 0
        self.sila_kliku = 1
        self.kliknuti_historie.clear()
        self.floating_texts.clear()
        self.combo_count = 0
        self.combo_until = 0.0
        self.combo_clicks = 0
        self.combo_multiplier = 1.0
        self.task_income_buff = 1.0

        self.mikrofon_active = False
        self.drummer_active = False
        self.guitarist_active = False
        self.pianist_active = False
        self.dj_active = False
        self.sekuritak_active = False

        self.bought_items = {"Členové": set(), "Vylepšení": set(), "Rebirth": set()}
        self.upgrade_levels = {i: 0 for i in range(7)}
        self.item_prices = {
            "Členové": {0: 25, 1: 75, 2: 150, 3: 400, 4: 1000, 5: 3000, 6: 10000},
            "Vylepšení": {0: 200, 1: 450, 2: 900, 3: 2000, 4: 5000, 5: 3500, 6: 8000},
            "Rebirth": {0: 1_000_000}
        }

        for task in self.daily_tasks:
            task["current"] = 0
            task["completed"] = False
            task["claimed"] = False

        self.menu_otevrene = False
        self.scroll_offset = 0
        self.rebirth_confirm_open = False
        self.update_audio_layers()

    def get_persistent_data(self):
        # Only long-term progression fields should be persisted here.
        return {
            "settings": {
                "hlasitost": float(getattr(self, 'hlasitost', 0.5)),
                "animations_disabled": bool(getattr(self, 'animations_disabled', False)),
                "fps_index": int(getattr(self, 'fps_index', 1)),
                "ui_scale": float(getattr(self, 'ui_scale', 1.0)),
                "language": str(getattr(self, 'language', 'CZ')),
                "number_format": str(getattr(self, 'number_format', 'plain')),
                "show_combo_text": bool(getattr(self, 'show_combo_text', True)),
            },
            "rebirth": {
                "rebirth_count": int(getattr(self, 'rebirth_count', 0)),
            },
            "cosmetics_unlocked": sorted(list(getattr(self, 'cosmetics_unlocked', set()))),
            "statistics": dict(getattr(self, 'statistics', {})),
        }

    def apply_persistent_data(self, data):
        if not isinstance(data, dict):
            return

        settings = data.get("settings", {})
        self.hlasitost = float(settings.get("hlasitost", getattr(self, 'hlasitost', 0.5)))
        self.animations_disabled = bool(settings.get("animations_disabled", getattr(self, 'animations_disabled', False)))
        self.fps_index = int(settings.get("fps_index", getattr(self, 'fps_index', 1)))
        self.ui_scale = float(settings.get("ui_scale", getattr(self, 'ui_scale', 1.0)))
        self.language = str(settings.get("language", getattr(self, 'language', 'CZ')))
        self.number_format = str(settings.get("number_format", getattr(self, 'number_format', 'plain')))
        self.show_combo_text = bool(settings.get("show_combo_text", getattr(self, 'show_combo_text', True)))

        rebirth = data.get("rebirth", {})
        self.rebirth_count = int(rebirth.get("rebirth_count", getattr(self, 'rebirth_count', 0)))

        unlocked = data.get("cosmetics_unlocked", [])
        self.cosmetics_unlocked = set(unlocked) if isinstance(unlocked, list) else set()

        stats = data.get("statistics", {})
        if isinstance(stats, dict):
            self.statistics.update(stats)

        self.upravit_hlasitost(0.0)

    def get_run_data(self):
        return {
            "penize": int(getattr(self, 'penize', 0)),
            "prijem": int(getattr(self, 'prijem', 0)),
            "sila_kliku": int(getattr(self, 'sila_kliku', 1)),
            "mikrofon_active": bool(getattr(self, 'mikrofon_active', False)),
            "drummer_active": bool(getattr(self, 'drummer_active', False)),
            "guitarist_active": bool(getattr(self, 'guitarist_active', False)),
            "pianist_active": bool(getattr(self, 'pianist_active', False)),
            "dj_active": bool(getattr(self, 'dj_active', False)),
            "sekuritak_active": bool(getattr(self, 'sekuritak_active', False)),
            "combo_clicks": int(getattr(self, 'combo_clicks', 0)),
            "combo_multiplier": float(getattr(self, 'combo_multiplier', 1.0)),
            "task_income_buff": float(getattr(self, 'task_income_buff', 1.0)),
            "upgrade_levels": dict(getattr(self, 'upgrade_levels', {i: 0 for i in range(7)})),
            "bought_items": {
                "Členové": sorted(list(self.bought_items.get("Členové", set()))),
                "Vylepšení": sorted(list(self.bought_items.get("Vylepšení", set()))),
                "Rebirth": sorted(list(self.bought_items.get("Rebirth", set()))),
            },
            "item_prices": {
                "Členové": dict(self.item_prices.get("Členové", {})),
                "Vylepšení": dict(self.item_prices.get("Vylepšení", {})),
                "Rebirth": dict(self.item_prices.get("Rebirth", {})),
            },
            "daily_tasks": [dict(task) for task in getattr(self, 'daily_tasks', [])],
        }

    def apply_run_data(self, data):
        if not isinstance(data, dict):
            return

        self.penize = int(data.get("penize", getattr(self, 'penize', 0)))
        self.prijem = int(data.get("prijem", getattr(self, 'prijem', 0)))
        self.sila_kliku = int(data.get("sila_kliku", getattr(self, 'sila_kliku', 1)))
        self.mikrofon_active = bool(data.get("mikrofon_active", getattr(self, 'mikrofon_active', False)))
        self.drummer_active = bool(data.get("drummer_active", getattr(self, 'drummer_active', False)))
        self.guitarist_active = bool(data.get("guitarist_active", getattr(self, 'guitarist_active', False)))
        self.pianist_active = bool(data.get("pianist_active", getattr(self, 'pianist_active', False)))
        self.dj_active = bool(data.get("dj_active", getattr(self, 'dj_active', False)))
        self.sekuritak_active = bool(data.get("sekuritak_active", getattr(self, 'sekuritak_active', False)))
        self.combo_clicks = int(data.get("combo_clicks", getattr(self, 'combo_clicks', 0)))
        self.combo_multiplier = float(data.get("combo_multiplier", getattr(self, 'combo_multiplier', 1.0)))
        self.task_income_buff = float(data.get("task_income_buff", getattr(self, 'task_income_buff', 1.0)))

        levels = data.get("upgrade_levels", {})
        if isinstance(levels, dict):
            self.upgrade_levels = {int(k): int(v) for k, v in levels.items()}

        bought = data.get("bought_items", {})
        if isinstance(bought, dict):
            self.bought_items = {
                "Členové": set(bought.get("Členové", [])),
                "Vylepšení": set(bought.get("Vylepšení", [])),
                "Rebirth": set(bought.get("Rebirth", [])),
            }

        prices = data.get("item_prices", {})
        if isinstance(prices, dict):
            self.item_prices = {
                "Členové": dict(prices.get("Členové", self.item_prices.get("Členové", {}))),
                "Vylepšení": dict(prices.get("Vylepšení", self.item_prices.get("Vylepšení", {}))),
                "Rebirth": dict(prices.get("Rebirth", self.item_prices.get("Rebirth", {}))),
            }

        tasks = data.get("daily_tasks", None)
        if isinstance(tasks, list):
            self.daily_tasks = [dict(t) for t in tasks if isinstance(t, dict)]

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
        if hasattr(self, 'piano_sound') and self.piano_sound:
            self.piano_sound.play()
        elif self.guitar_sound and pygame.mixer.get_init():
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume((self.hlasitost ** 2) * 0.22)
                ch.play(self.guitar_sound)

    def zahraj_dj_set(self):
        """Spustí animaci DJ."""
        self.dj_target_scale = 1.3
        if hasattr(self, 'dj_sound') and self.dj_sound:
            self.dj_sound.play()
        elif self.drum_sound and pygame.mixer.get_init():
            ch = pygame.mixer.find_channel(True)
            if ch:
                ch.set_volume((self.hlasitost ** 2) * 0.18)
                ch.play(self.drum_sound)

    def update(self): 
        import random
        self.update_audio_layers()

        now = time.time()
        self.floating_texts = [
            t for t in self.floating_texts
            if (now - t["born"]) <= t["life"]
        ]

        self.task_panel_target_x = float((self.sirka - self.task_panel_w - 10) if self.task_panel_open else (self.sirka + 10))
        self.task_panel_x += (self.task_panel_target_x - self.task_panel_x) * 0.22

        if self.concert_buff_mult > 1.0 and now >= self.concert_buff_end:
            self.concert_buff_mult = 1.0

        if self.concert_active is None and not self.menu_otevrene and not self.settings_otevrene and now >= self.concert_spawn_at:
            radius = 55
            margin = radius + 20
            min_y = self.vyska + 80
            max_y = max(min_y + 1, self.vyska_okna - margin - 220)
            self.concert_active = {
                "x": random.randint(margin, max(margin + 1, self.sirka - margin)),
                "y": random.randint(min_y, max_y),
                "radius": radius,
                "spawn": now,
                "life": 14.0,
            }

        if self.concert_active is not None:
            elapsed = now - self.concert_active["spawn"]
            if elapsed >= self.concert_active["life"]:
                self.concert_active = None
                self.concert_spawn_at = now + random.uniform(75.0, 150.0)

        if self.menu_otevrene and self.menu_vyska <= 0:
            self.menu_vyska = 0

        if self._last_menu_update is None:
            self._last_menu_update = now
        dt = now - self._last_menu_update
        self._last_menu_update = now
        self._menu_physics_accum += min(max(dt, 0.0), 0.25)

        fixed_step = 1.0 / 60.0
        max_steps_per_frame = 20
        steps = 0
        while self._menu_physics_accum >= fixed_step and steps < max_steps_per_frame:
            self._menu_physics_accum -= fixed_step
            steps += 1

            if 0 <= self.menu_vyska < self.menu_max_vyska and self.menu_otevrene:
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
                self.menu_rychlost -= self.menu_gravitace * 2
                self.menu_vyska += self.menu_rychlost
                if self.menu_vyska <= 0:
                    self.menu_vyska = 0
                    self.menu_rychlost = 0

        if steps >= max_steps_per_frame:
            self._menu_physics_accum = 0.0

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
                    
        if getattr(self, 'sekuritak_active', False):
            import math
            import random
            
            if not hasattr(self, 'last_sekuritak_fight'):
                self.last_sekuritak_fight = time.time()
                
            if time.time() - self.last_sekuritak_fight >= 5.0:
                self.sekuritak_fight_time = time.time() + 1.0
                self.last_sekuritak_fight = time.time()
                self.penize += 100
                
                # Zkusime zavolat pridat_penize z hrace, pokud ale neni dostupna mame self.penize
                # Plus nejake statistiky jestli chceme. Zde ale to floatuje na obrazovku.
                if hasattr(self, 'pridat_floating_text'):
                    self.pridat_floating_text(
                        self.sekuritak_x + 40, 
                        self.sekuritak_y - 20, 
                        "+100$", 
                        (255, 0, 0), 
                        life=1.0
                    )
                if hasattr(self, 'sekuritak_sound') and self.sekuritak_sound:
                    ch = pygame.mixer.find_channel(True)
                    if ch:
                        ch.set_volume(self.hlasitost ** 2)
                        ch.play(self.sekuritak_sound)
                        
            pad = 100
            y_min = int(self.vyska_okna * 0.65)
            y_max = self.vyska_okna - 50
            
            # Bezpecnostni uprava pro stare ulozene pozice i soucasnou pozici
            self.sekuritak_cile_x = max(pad, min(getattr(self, 'sekuritak_cile_x', self.sekuritak_x), self.sirka - pad))
            self.sekuritak_cile_y = max(y_min, min(getattr(self, 'sekuritak_cile_y', self.sekuritak_y), y_max))
            
            self.sekuritak_x = max(pad, min(self.sekuritak_x, self.sirka - pad))
            self.sekuritak_y = max(y_min, min(self.sekuritak_y, y_max))
            
            dx = self.sekuritak_cile_x - self.sekuritak_x
            dy = self.sekuritak_cile_y - self.sekuritak_y
            
            if time.time() < getattr(self, 'sekuritak_fight_time', 0):
                # Bojuje - tuka rukama (zvetsuje/zmensuje)
                self.sekuritak_scale = 1.0 + math.sin(time.time() * 25) * 0.2
            else:
                dist = math.hypot(dx, dy)
                # Rychlost pohybu ovlivnena kombem (pokud je aktivni, pohybuje se rychleji)
                speed_mult = 2.0
                if hasattr(self, 'combo_multiplier') and self.combo_multiplier > 1.0:
                    speed_mult *= 2.0
                
                if dist > 5:
<<<<<<< HEAD
                    self.sekuritak_x += (dx / dist) * speed_mult
                    self.sekuritak_y += (dy / dist) * speed_mult
=======
                    self.sekuritak_x += (dx / dist) * (2.0 * max(1.0, self.vyska_okna / 600.0))
                    self.sekuritak_y += (dy / dist) * (2.0 * max(1.0, self.vyska_okna / 600.0))
>>>>>>> origin/main
                    self.sekuritak_scale = 1.0 + math.sin(time.time() * 10) * 0.05
                else:
                    # Dosal cile -> vyber novy nahodny cil, aby se neustale zastavoval
                    self.sekuritak_cile_x = random.randint(50, self.sirka - 50)
                    self.sekuritak_cile_y = random.randint(self.vyska_okna // 2, self.vyska_okna - 50)
                    self.sekuritak_scale = 1.0
                    self.sekuritak_scale = 1.0
                    # Zhruba 1 % šance na start cesty na snímek (když dorazí do cíle, chvíli si tam postojí)
                    if random.random() < 0.01:
                        pad = 100
                        y_min = int(self.vyska_okna * 0.65)
                        y_max = self.vyska_okna - 50
                        self.sekuritak_cile_x = random.randint(pad, max(pad, self.sirka - pad))
                        self.sekuritak_cile_y = random.randint(min(y_min, y_max), max(y_min, y_max))

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

            scaled_drummer_w = int(self.drummer_image.get_width() * scale)
            scaled_drummer_h = int(self.drummer_image.get_height() * scale)
            scaled_drummer = pygame.transform.smoothscale(self.drummer_image, (scaled_drummer_w, scaled_drummer_h))
            temp_drummer_rect = scaled_drummer.get_rect(center=temp_drummer_rect.center)

            scaled_w = int(self.drum_image.get_width() * scale)
            scaled_h = int(self.drum_image.get_height() * scale)
            scaled_drum = pygame.transform.smoothscale(self.drum_image, (scaled_w, scaled_h))
            temp_drum_rect = scaled_drum.get_rect(
                center=(self.drum_rect.centerx, self.drum_rect.centery + int(y_offset))
            )

            okno.blit(scaled_drummer, temp_drummer_rect)
            okno.blit(scaled_drum, temp_drum_rect)
        
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

        if self.sekuritak_active:
            scale = self.sekuritak_scale * (self.vyska_okna / 600.0)
            scaled_w = int(self.sekuritak_image.get_width() * scale)
            scaled_h = int(self.sekuritak_image.get_height() * scale)
            scaled_img = pygame.transform.smoothscale(self.sekuritak_image, (scaled_w, scaled_h))
            
            # Oprava aby nevyjizdel z mapy (omezeni na sirku a vysku okna)
            self.sekuritak_x = max(scaled_w // 2, min(self.sekuritak_x, self.sirka - scaled_w // 2))
            self.sekuritak_y = max(scaled_h // 2, min(self.sekuritak_y, self.vyska_okna - scaled_h // 2))
            
            rect = scaled_img.get_rect(center=(int(self.sekuritak_x), int(self.sekuritak_y)))
            okno.blit(scaled_img, rect)
            
            if time.time() < getattr(self, 'sekuritak_fight_time', 0):
                # Kreslit nejaky BAF efekt
                fight_font = pygame.font.SysFont(None, 40, bold=True)
                fight_text = fight_font.render("BUM!", True, (255, 50, 50))
                okno.blit(fight_text, fight_text.get_rect(center=(int(self.sekuritak_x), int(self.sekuritak_y) - 40)))

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
            
            tab_width = (self.sirka - 50) // 3
            tab_y = self.vyska + 5
            
            self.rect_tab_clenove = pygame.Rect(20, tab_y, tab_width, 40)
            self.rect_tab_vylepseni = pygame.Rect(25 + tab_width, tab_y, tab_width, 40)
            self.rect_tab_rebirth = pygame.Rect(30 + (tab_width * 2), tab_y, tab_width, 40)
            
            pygame.draw.rect(okno, (100, 100, 100) if self.aktivni_kategorie != "Členové" else (150, 80, 40), self.rect_tab_clenove)
            pygame.draw.rect(okno, (100, 100, 100) if self.aktivni_kategorie != "Vylepšení" else (150, 80, 40), self.rect_tab_vylepseni)
            pygame.draw.rect(okno, (100, 100, 100) if self.aktivni_kategorie != "Rebirth" else (150, 80, 40), self.rect_tab_rebirth)

            okno.blit(self.button_font.render(self._txt("cat_members"), True, (255, 255, 255)), (self.rect_tab_clenove.x + 20, tab_y + 10))
            okno.blit(self.button_font.render(self._txt("cat_upgrades"), True, (255, 255, 255)), (self.rect_tab_vylepseni.x + 20, tab_y + 10))
            okno.blit(self.button_font.render(self._txt("cat_rebirth"), True, (255, 255, 255)), (self.rect_tab_rebirth.x + 20, tab_y + 10))
            
            menu_y = self.vyska + 55
            visible_index = 0
            aktualni_polozky = self.menu_items[self.aktivni_kategorie]
            for i in range(len(aktualni_polozky)):
                if i in self.bought_items.get(self.aktivni_kategorie, set()):
                    continue
                
                item = self.get_menu_item_name(self.aktivni_kategorie, i)
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
                        
                        price = self.item_prices.get(self.aktivni_kategorie, {}).get(i, 0)
                        can_afford = self.penize >= price
                        
                        if self.aktivni_kategorie == "Rebirth":
                            price_label = self._txt("rebirth_ready") if can_afford else f"{self.format_number(price)}$"
                            price_color = (120, 255, 160) if can_afford else (255, 210, 130)
                        else:
                            price_label = f"{price}$"
                            price_color = (255, 255, 100)
                        price_text = self.price_font.render(price_label, True, price_color)
                        price_rect = price_text.get_rect(center=(40, item_y + self.item_height // 2))
                        okno.blit(price_text, price_rect)
                        
                        button_x = self.sirka - self.scrollbar_width - self.button_width - 20
                        button_y = item_y + (self.item_height - self.button_height) // 2
                        button_rect = pygame.Rect(button_x, button_y, self.button_width, self.button_height)
                        
                        button_color = self.button_color if can_afford else self.button_disabled_color
                        buy_label = self._txt("rebirth") if self.aktivni_kategorie == "Rebirth" else self._txt("buy")
                        button_text_render = self.button_font.render(buy_label, True, (255, 255, 255) if can_afford else (100, 100, 100))
                        
                        pygame.draw.rect(okno, button_color, button_rect, border_radius=8)
                        
                        button_text_rect = button_text_render.get_rect(center=button_rect.center)
                        okno.blit(button_text_render, button_text_rect)
            
            self._draw_scrollbar(okno)
            if hovered_upgrade_index is not None:
                tooltip = self.get_upgrade_tooltip(hovered_upgrade_index)
                if tooltip:
                    self._draw_tooltip(okno, tooltip, int(mouse_ui_pos[0]), int(mouse_ui_pos[1]))

            if self.aktivni_kategorie == "Rebirth" and getattr(self, 'rebirth_confirm_open', False):
                cbox = pygame.Rect(self.sirka // 2 - 180, self.vyska + 135, 360, 110)
                pygame.draw.rect(okno, (245, 245, 245), cbox, border_radius=10)
                pygame.draw.rect(okno, (0, 0, 0), cbox, 2, border_radius=10)
                ctext = self.res_font.render(self._txt("rebirth_confirm"), True, (20, 20, 20))
                okno.blit(ctext, ctext.get_rect(center=(cbox.centerx, cbox.y + 30)))

                self.menu_btn_rebirth_confirm = pygame.Rect(cbox.x + 22, cbox.bottom - 45, 150, 34)
                self.menu_btn_rebirth_cancel = pygame.Rect(cbox.right - 172, cbox.bottom - 45, 150, 34)

                pygame.draw.rect(okno, (100, 220, 130), self.menu_btn_rebirth_confirm, border_radius=8)
                pygame.draw.rect(okno, (0, 0, 0), self.menu_btn_rebirth_confirm, 2, border_radius=8)
                conf_txt = self.task_font.render(self._txt("confirm"), True, (0, 0, 0))
                okno.blit(conf_txt, conf_txt.get_rect(center=self.menu_btn_rebirth_confirm.center))

                pygame.draw.rect(okno, (240, 140, 140), self.menu_btn_rebirth_cancel, border_radius=8)
                pygame.draw.rect(okno, (0, 0, 0), self.menu_btn_rebirth_cancel, 2, border_radius=8)
                cancel_txt = self.task_font.render(self._txt("cancel"), True, (0, 0, 0))
                okno.blit(cancel_txt, cancel_txt.get_rect(center=self.menu_btn_rebirth_cancel.center))
        
        if not self.menu_otevrene:
            t = time.time()
            animace_vypnute = getattr(self, 'animations_disabled', False)

            je_full_hd = self.vyska_okna > 600
            pocet_rad = 2 if je_full_hd else 1

            spacing_x = 150 if je_full_hd else 70
            pocet_fanousku = math.ceil(self.sirka / spacing_x) + 4

            progress_income = max(0, int(getattr(self, 'prijem', 0)))
            if progress_income <= 0:
                fan_ratio = 0.0
            else:
                fan_ratio = min(1.0, math.log10(progress_income + 1) / 3.6)

            fan_image_w = (218 * 1.8) if je_full_hd else 218
            screen_center_x = self.sirka / 2.0

            for row in range(pocet_rad):
                if not je_full_hd:
                    base_y = self.vyska_okna - 163
                    shift_x = 0
                else:
                    base_y = self.vyska_okna - 330 + (row * 90)
                    shift_x = (row % 2) * 80

                for i in range(pocet_fanousku):
                    audience_x = (i * spacing_x) - 60 + shift_x
                    fan_center_x = audience_x + fan_image_w / 2.0

                    if je_full_hd and row == 0:
                        if abs(fan_center_x - screen_center_x) < 300:
                            continue

                    dist_ratio = min(1.0, abs(fan_center_x - screen_center_x) / (self.sirka / 2.0))
                    if dist_ratio > fan_ratio + 0.2:
                        continue

                    jump_offset = 0 if animace_vypnute else abs(math.sin(t * 5 + i * 0.5 + row * 2.0)) * 20
                    audience_y = base_y - int(jump_offset)
                    okno.blit(self.audience_image, (audience_x, audience_y))

        if self.concert_active is not None and not self.menu_otevrene:
            now_draw = time.time()
            elapsed = now_draw - self.concert_active["spawn"]
            life = self.concert_active["life"]
            remaining = max(0.0, 1.0 - elapsed / life)
            alpha = int(80 + 175 * remaining)
            pulse = 1.0 + 0.08 * math.sin(now_draw * 6.0)
            base_r = self.concert_active["radius"]
            r = int(base_r * pulse)
            cx = self.concert_active["x"]
            cy = self.concert_active["y"]
            surf_size = r * 2 + 20
            surf = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 215, 0, alpha), (surf_size // 2, surf_size // 2), r)
            pygame.draw.circle(surf, (180, 120, 0, alpha), (surf_size // 2, surf_size // 2), r, 4)
            okno.blit(surf, (cx - surf_size // 2, cy - surf_size // 2))
            label = self.concert_font.render(self._txt("concert_label") if False else "KONCERT", True, (60, 30, 0))
            okno.blit(label, label.get_rect(center=(cx, cy)))

        pygame.draw.rect(okno, self.barva, (0, 0, self.sirka, self.vyska))

        okno.blit(self.logo_image, self.logo_rect)
        if "gold_logo" in getattr(self, 'cosmetics_unlocked', set()):
            pygame.draw.circle(okno, (255, 215, 0), self.logo_rect.center, 62, 4)

        text = penize_font.render(f"{self.format_number(self.penize)}$", True, (0, 0, 0))
        text_rect = text.get_rect(center=(self.sirka // 2, self.vyska // 2))
        okno.blit(text, text_rect)

        aktualni_cas = time.time()
        self.kliknuti_historie = [(cas, hodnota) for cas, hodnota in self.kliknuti_historie if aktualni_cas - cas <= 1.0]
        celkovy_prijem = self.prijem + sum(hodnota for cas, hodnota in self.kliknuti_historie)

        prijem_text = prijem_font.render(f"(+{self.format_number(celkovy_prijem)} $/s)", True, (50, 205, 50))
        prijem_rect = prijem_text.get_rect(midleft=(text_rect.right + 10, self.vyska // 2 + 5))
        okno.blit(prijem_text, prijem_rect)

        self._draw_daily_tasks(okno)

        line_color = (0, 0, 0)
        line_width = 5

        x_start = self.sirka - 80
        x_end = self.sirka - 30

        pygame.draw.line(okno, line_color, (x_start, 35), (x_end, 35), line_width)
        pygame.draw.line(okno, line_color, (x_start, 50), (x_end, 50), line_width)
        pygame.draw.line(okno, line_color, (x_start, 65), (x_end, 65), line_width)

        if getattr(self, 'show_combo_text', True) and time.time() < getattr(self, 'combo_until', 0.0):
            combo_mul = float(getattr(self, 'combo_multiplier', 1.0))
            combo_text = self.combo_font.render(f"{self._txt('combo_label')} x{combo_mul:.1f}", True, (255, 220, 80))
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
            
            nadpis_text = self.settings_font.render(self._txt("settings"), True, (0, 0, 0))
            okno.blit(nadpis_text, nadpis_text.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 30)))

            # Tabs
            def draw_tab(rect, label, is_active):
                color = (255, 255, 255) if is_active else (170, 170, 170)
                pygame.draw.rect(okno, color, rect, border_radius=8)
                pygame.draw.rect(okno, (0, 0, 0), rect, 2, border_radius=8)
                txt = self.res_font.render(label, True, (0, 0, 0))
                okno.blit(txt, txt.get_rect(center=rect.center))

            draw_tab(self.btn_tab_sound, self._txt("tab_sound"), getattr(self, 'settings_tab', '') == "Sound")
            draw_tab(self.btn_tab_graphics, self._txt("tab_graphics"), getattr(self, 'settings_tab', '') == "Graphics")
            draw_tab(self.btn_tab_ui, self._txt("tab_ui"), getattr(self, 'settings_tab', '') == "UI")
            draw_tab(self.btn_tab_developer, self._txt("tab_developer"), getattr(self, 'settings_tab', '') == "Developer")

            tab = getattr(self, 'settings_tab', 'Sound')
            
            if tab == "Sound":
                vol_text = self.res_font.render(self._txt("volume"), True, (0, 0, 0))
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
                anim_state = self._txt("off") if anim_dis else self._txt("on")
                anim_txt = self.res_font.render(f"{self._txt('animations')}: {anim_state}", True, (0, 0, 0))
                okno.blit(anim_txt, anim_txt.get_rect(center=self.btn_anim_toggle.center))

                # FPS Limit
                pygame.draw.rect(okno, (200, 200, 100), self.btn_fps_change, border_radius=5)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_fps_change, 2, border_radius=5)
                opts = getattr(self, 'fps_options', [30, 60, 120, 0])
                idx = getattr(self, 'fps_index', 1)
                fps_val = opts[idx]
                fps_str = f"{self._txt('fps_lock')}: {fps_val}" if fps_val > 0 else f"{self._txt('fps_lock')}: {self._txt('fps_unlimited')}"
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

            elif tab == "UI":
                pygame.draw.rect(okno, (120, 170, 255), self.btn_lang_toggle, border_radius=6)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_lang_toggle, 2, border_radius=6)
                lang_label = "CZ" if getattr(self, 'language', 'CZ') == 'CZ' else "EN"
                lang_txt = self.res_font.render(f"{self._txt('lang')}: {lang_label}", True, (0, 0, 0))
                okno.blit(lang_txt, lang_txt.get_rect(center=self.btn_lang_toggle.center))

                pygame.draw.rect(okno, (120, 220, 170), self.btn_num_format_toggle, border_radius=6)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_num_format_toggle, 2, border_radius=6)
                mode = "1,234,567" if getattr(self, 'number_format', 'plain') == 'plain' else "1.23M"
                num_txt = self.res_font.render(f"{self._txt('num')}: {mode}", True, (0, 0, 0))
                okno.blit(num_txt, num_txt.get_rect(center=self.btn_num_format_toggle.center))

                pygame.draw.rect(okno, (220, 190, 120), self.btn_combo_toggle, border_radius=6)
                pygame.draw.rect(okno, (0, 0, 0), self.btn_combo_toggle, 2, border_radius=6)
                combo_state = self._txt('on') if getattr(self, 'show_combo_text', True) else self._txt('off')
                combo_txt = self.res_font.render(f"{self._txt('combo')}: {combo_state}", True, (0, 0, 0))
                okno.blit(combo_txt, combo_txt.get_rect(center=self.btn_combo_toggle.center))

            elif tab == "Developer":
                devs = ["Michal Svoboda", "Štěpán Šitina", "Daniel Wales"]
                dev_title = self.res_font.render(self._txt("authors"), True, (0, 0, 0))
                okno.blit(dev_title, dev_title.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 140)))
                dev_font = pygame.font.SysFont(None, 52)
                
                for idx, dev in enumerate(devs):
                    txt = dev_font.render(dev, True, (80, 80, 80))
                    okno.blit(txt, txt.get_rect(center=(self.settings_rect.centerx, self.settings_rect.y + 200 + (idx * 44))))

            # Close Button
            pygame.draw.rect(okno, (255, 100, 100), self.btn_exit_game, border_radius=10)
            pygame.draw.rect(okno, (0, 0, 0), self.btn_exit_game, 2, border_radius=10)
            exit_text = self.res_font.render(self._txt("exit"), True, (0, 0, 0))
            okno.blit(exit_text, exit_text.get_rect(center=self.btn_exit_game.center))

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

    def _draw_daily_tasks(self, okno):
        has_unclaimed = any(t.get("completed", False) and not t.get("claimed", False) for t in getattr(self, 'daily_tasks', []))
        bg_color = (40, 160, 40) if has_unclaimed else (40, 40, 40)
        
        pygame.draw.rect(okno, bg_color, self.btn_tasks_toggle, border_radius=8)
        pygame.draw.rect(okno, (230, 230, 230), self.btn_tasks_toggle, 1, border_radius=8)
        toggle_text = self.task_font.render(self._txt("tasks"), True, (255, 255, 255))
        okno.blit(toggle_text, toggle_text.get_rect(center=self.btn_tasks_toggle.center))

        x, y = int(self.task_panel_x), self.vyska + 8
        w, h = self.task_panel_w, self.task_panel_h
        panel = pygame.Rect(x, y, w, h)
        pygame.draw.rect(okno, (18, 18, 18), panel, border_radius=10)
        pygame.draw.rect(okno, (230, 230, 230), panel, 1, border_radius=10)

        title = self.task_font.render(self._txt("daily_tasks"), True, (255, 255, 255))
        okno.blit(title, (x + 10, y + 8))

        tasks = getattr(self, 'daily_tasks', [])
        self.task_claim_buttons = {}
        row_y = y + 34
        for task in tasks[:3]:
            target = int(task.get("target", 1))
            current = int(task.get("current", 0))
            done = bool(task.get("completed", False))
            claimed = bool(task.get("claimed", False))
            mark = "[OK]" if done else "[ ]"
            short = f"{mark} {self.get_task_title(task)}"
            txt = self.income_font.render(short, True, (200, 255, 200) if done else (230, 230, 230))
            okno.blit(txt, (x + 10, row_y))
            progress = self.income_font.render(f"{min(current, target)}/{target}", True, (170, 170, 170))
            okno.blit(progress, (x + w - 75, row_y))

            if done and not claimed:
                claim_rect = pygame.Rect(x + w - 140, row_y + 16, 126, 18)
                self.task_claim_buttons[task.get("id")] = claim_rect
                pygame.draw.rect(okno, (70, 130, 70), claim_rect, border_radius=5)
                pygame.draw.rect(okno, (220, 220, 220), claim_rect, 1, border_radius=5)
                claim_txt = self.income_font.render(self._txt("claim"), True, (255, 255, 255))
                okno.blit(claim_txt, claim_txt.get_rect(center=claim_rect.center))
            elif claimed:
                done_txt = self.income_font.render(self._txt("claimed"), True, (170, 210, 170))
                okno.blit(done_txt, (x + w - 120, row_y + 16))
            row_y += 36

    def handle_task_panel_click(self, ui_pos):
        if self.btn_tasks_toggle.collidepoint(ui_pos):
            self.task_panel_open = not self.task_panel_open
            return ("toggle", None)

        if not self.task_panel_open:
            return None

        for task_id, rect in self.task_claim_buttons.items():
            if rect.collidepoint(ui_pos):
                return ("claim", task_id)

        return None
    
    def _draw_scrollbar(self, okno):
        """Draw scrollbar on the right side of the menu"""
        if self.menu_vyska <= 0:
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

