import pygame
import sys
import time
import random
pygame.init()

import gui

width, height = 800, 600
screen = pygame.display.set_mode((width, height))

pygame.display.set_caption("Band Idle Simulator")

lista = gui.Lista(width, height)
if not hasattr(lista, 'upgrade_levels'):
    lista.upgrade_levels = {i: 0 for i in range(7)}
if not hasattr(lista, 'daily_tasks'):
    lista.daily_tasks = []


def can_rebirth(l):
    requirement = int(getattr(l, 'rebirth_requirement', 1_000_000))
    return int(getattr(l, 'penize', 0)) >= requirement


def get_rebirth_multiplier(l):
    return float(2 ** int(getattr(l, 'rebirth_count', 0)))


def perform_rebirth(l):
    if not can_rebirth(l):
        return False
    if hasattr(l, 'perform_rebirth'):
        l.perform_rebirth()
    else:
        l.rebirth_count = int(getattr(l, 'rebirth_count', 0)) + 1
    return True


def pridat_penize(l, amount):
    gain = int(amount)
    if gain <= 0:
        return
    l.penize += gain
    if hasattr(l, 'statistics') and isinstance(l.statistics, dict):
        l.statistics['total_earned'] = int(l.statistics.get('total_earned', 0)) + gain


def txt(l, key, fallback):
    if hasattr(l, '_txt'):
        return l._txt(key)
    return fallback


def aktualizovat_ukol(l, task_id, value=None, add=0):
    for task in getattr(l, 'daily_tasks', []):
        if task.get("id") != task_id:
            continue
        if value is not None:
            task["current"] = max(int(task.get("current", 0)), int(value))
        if add:
            task["current"] = int(task.get("current", 0)) + int(add)
        if int(task.get("current", 0)) >= int(task.get("target", 1)):
            task["completed"] = True
        return


def zpracovat_odmeny(l):
    for task in getattr(l, 'daily_tasks', []):
        if not task.get("completed", False) or task.get("claimed", False):
            continue

        rtype = task.get("reward_type")
        rval = task.get("reward_value")

        if rtype == "money":
            amount = int(rval)
            l.penize += amount
            if hasattr(l, 'pridat_floating_text'):
                msg = txt(l, "task_reward_money", "Ukol odmena +{amount}$").format(amount=amount)
                l.pridat_floating_text(25, 130, msg, (140, 255, 140), life=1.5)
        elif rtype == "buff":
            l.task_income_buff = float(getattr(l, 'task_income_buff', 1.0)) * (1.0 + float(rval))
            if hasattr(l, 'pridat_floating_text'):
                pct = int(round(float(rval) * 100))
                msg = txt(l, "task_reward_buff", "Ukol buff +{pct}%").format(pct=pct)
                l.pridat_floating_text(25, 130, msg, (140, 220, 255), life=1.5)
        elif rtype == "cosmetic":
            unlocked = getattr(l, 'cosmetics_unlocked', set())
            unlocked.add(str(rval))
            l.cosmetics_unlocked = unlocked
            if hasattr(l, 'pridat_floating_text'):
                l.pridat_floating_text(25, 130, txt(l, "task_reward_cosmetic", "Nova kosmetika odemcena"), (255, 220, 140), life=1.5)

        task["claimed"] = True


def vyzvednout_odmenu_ukolu(l, task_id):
    for task in getattr(l, 'daily_tasks', []):
        if task.get("id") != task_id:
            continue
        if not task.get("completed", False) or task.get("claimed", False):
            return False

        rtype = task.get("reward_type")
        rval = task.get("reward_value")

        if rtype == "money":
            amount = int(rval)
            l.penize += amount
            if hasattr(l, 'pridat_floating_text'):
                msg = txt(l, "task_reward_money", "Ukol odmena +{amount}$").format(amount=amount)
                l.pridat_floating_text(25, 130, msg, (140, 255, 140), life=1.5)
        elif rtype == "buff":
            l.task_income_buff = float(getattr(l, 'task_income_buff', 1.0)) * (1.0 + float(rval))
            if hasattr(l, 'pridat_floating_text'):
                pct = int(round(float(rval) * 100))
                msg = txt(l, "task_reward_buff", "Ukol buff +{pct}%").format(pct=pct)
                l.pridat_floating_text(25, 130, msg, (140, 220, 255), life=1.5)
        elif rtype == "cosmetic":
            unlocked = getattr(l, 'cosmetics_unlocked', set())
            unlocked.add(str(rval))
            l.cosmetics_unlocked = unlocked
            if hasattr(l, 'pridat_floating_text'):
                l.pridat_floating_text(25, 130, txt(l, "task_reward_cosmetic", "Nova kosmetika odemcena"), (255, 220, 140), life=1.5)

        task["claimed"] = True
        return True

    return False


def vypocitat_vydelky(l):
    levels = getattr(l, 'upgrade_levels', {i: 0 for i in range(7)})
    rebirth_mult = get_rebirth_multiplier(l)

    global_mult = 1.0 + (levels.get(3, 0) * 0.12)
    dj_team_mult = (1.10 + levels.get(6, 0) * 0.04) if l.dj_active else 1.0
    task_mult = float(getattr(l, 'task_income_buff', 1.0))
    concert_mult = float(getattr(l, 'concert_buff_mult', 1.0))
    total_mult = global_mult * dj_team_mult * task_mult * concert_mult

    # Passive je jen od mikrofonu a DJ aury, ne od kazde postavy zvlast.
    base_passive = (1 if l.mikrofon_active else 0) + (1 if l.dj_active else 0)

    auto_income = int(round(base_passive * total_mult * rebirth_mult))
    # Role economics: drummer = rychly tick, guitarist = mensi burst,
    # pianist = stabilne nejsilnejsi DPS, DJ = buff + stredni vlastni tick.
    drum_tick_income = int(round((1.2 + levels.get(1, 0) * 1.6) * total_mult * rebirth_mult))
    guitar_burst_income = int(round((2.0 + levels.get(2, 0) * 1.8) * total_mult * rebirth_mult))
    piano_tick_income = int(round((2.4 + levels.get(5, 0) * 2.2) * total_mult * rebirth_mult))
    dj_tick_income = int(round((4.0 + levels.get(6, 0) * 2.2) * global_mult * rebirth_mult * concert_mult))

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
                    elif hasattr(lista, 'btn_tab_ui') and lista.btn_tab_ui.collidepoint(ui_pos):
                        lista.settings_tab = 'UI'
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

                    elif getattr(lista, 'settings_tab', 'Sound') == 'UI':
                        if hasattr(lista, 'btn_lang_toggle') and lista.btn_lang_toggle.collidepoint(ui_pos):
                            lista.language = 'EN' if getattr(lista, 'language', 'CZ') == 'CZ' else 'CZ'
                        elif hasattr(lista, 'btn_num_format_toggle') and lista.btn_num_format_toggle.collidepoint(ui_pos):
                            lista.number_format = 'compact' if getattr(lista, 'number_format', 'plain') == 'plain' else 'plain'
                        elif hasattr(lista, 'btn_combo_toggle') and lista.btn_combo_toggle.collidepoint(ui_pos):
                            lista.show_combo_text = not getattr(lista, 'show_combo_text', True)

                    elif getattr(lista, 'settings_tab', 'Sound') == 'Developer':
                        pass

                    continue

                if lista.logo_rect.collidepoint(ui_pos):
                    lista.settings_otevrene = True
                    continue

                concert = getattr(lista, 'concert_active', None)
                if concert is not None and not lista.menu_otevrene:
                    dx = ui_pos[0] - concert["x"]
                    dy = ui_pos[1] - concert["y"]
                    if dx * dx + dy * dy <= concert["radius"] * concert["radius"]:
                        now = time.time()
                        lista.concert_buff_mult = 5.0
                        lista.concert_buff_end = now + 20.0
                        lista.concert_active = None
                        lista.concert_spawn_at = now + random.uniform(90.0, 150.0)
                        if hasattr(lista, 'pridat_floating_text'):
                            msg = "Koncert! x5 prijem 20s"
                            lista.pridat_floating_text(concert["x"] - 80, concert["y"] - 40, msg, (255, 215, 0), life=2.2)
                        continue

                task_action = lista.handle_task_panel_click(ui_pos) if hasattr(lista, 'handle_task_panel_click') else None
                if task_action:
                    action, task_id = task_action
                    if action == "claim" and task_id:
                        vyzvednout_odmenu_ukolu(lista, task_id)
                    continue

                if not lista.menu_otevrene and (lista.singer_rect.collidepoint(event.pos) or (lista.mikrofon_active and lista.mikrofon_rect.collidepoint(event.pos))):
                    now = time.time()
                    lista.combo_clicks = int(getattr(lista, 'combo_clicks', 0)) + 1
                    lista.combo_multiplier = 1.0 + (lista.combo_clicks // 10) * 0.1
                    lista.combo_count = lista.combo_clicks
                    lista.combo_until = now + 1.2

                    click_income = max(1, int(round(lista.sila_kliku * lista.combo_multiplier * get_rebirth_multiplier(lista) * float(getattr(lista, 'concert_buff_mult', 1.0)))))
                    pridat_penize(lista, click_income)
                    if hasattr(lista, 'statistics') and isinstance(lista.statistics, dict):
                        lista.statistics['total_clicks'] = int(lista.statistics.get('total_clicks', 0)) + 1
                    lista.kliknuti_historie.append((now, click_income))
                    aktualizovat_ukol(lista, "click_200", add=1)
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
                        lista.rebirth_confirm_open = False
                elif lista.menu_vyska > 0:
                    if getattr(lista, 'aktivni_kategorie', '') == "Rebirth" and getattr(lista, 'rebirth_confirm_open', False):
                        if hasattr(lista, 'menu_btn_rebirth_confirm') and lista.menu_btn_rebirth_confirm.collidepoint(ui_pos):
                            if perform_rebirth(lista):
                                now = time.time()
                                last_income_update = now
                                last_drum_hit = now
                                last_guitar_strum = now
                                last_piano_play = now
                                last_dj_play = now
                                last_drum_tick = now
                                last_piano_tick = now
                                last_dj_tick = now
                                last_guitar_burst = now
                                if hasattr(lista, 'pridat_floating_text'):
                                    mult = get_rebirth_multiplier(lista)
                                    msg = txt(lista, "rebirth_done", "Rebirth! Mult x{mult}").format(mult=int(mult))
                                    lista.pridat_floating_text(25, 130, msg, (255, 220, 120), life=1.6)
                            continue
                        if hasattr(lista, 'menu_btn_rebirth_cancel') and lista.menu_btn_rebirth_cancel.collidepoint(ui_pos):
                            lista.rebirth_confirm_open = False
                            continue

                    if hasattr(lista, 'rect_tab_clenove') and lista.rect_tab_clenove.collidepoint(ui_pos):
                        lista.aktivni_kategorie = "Členové"
                        lista.scroll_offset = 0
                        lista.rebirth_confirm_open = False
                        continue
                    if hasattr(lista, 'rect_tab_vylepseni') and lista.rect_tab_vylepseni.collidepoint(ui_pos):
                        lista.aktivni_kategorie = "Vylepšení"
                        lista.scroll_offset = 0
                        lista.rebirth_confirm_open = False
                        continue
                    if hasattr(lista, 'rect_tab_rebirth') and lista.rect_tab_rebirth.collidepoint(ui_pos):
                        lista.aktivni_kategorie = "Rebirth"
                        lista.scroll_offset = 0
                        continue

                    menu_obsah_y = lista.vyska + 55
                    visible_index = 0
                    aktualni_polozky = lista.menu_items[lista.aktivni_kategorie]
                    
                    for i in range(len(aktualni_polozky)):
                        if i in lista.bought_items.get(lista.aktivni_kategorie, set()):
                            continue
                        
                        item_y = menu_obsah_y + visible_index * (lista.item_height + lista.item_spacing) - lista.scroll_offset
                        visible_index += 1
                        
                        if lista.vyska < item_y + lista.item_height < lista.vyska + lista.menu_vyska:
                            button_x = lista.sirka - lista.scrollbar_width - lista.button_width - 20
                            button_y = item_y + (lista.item_height - lista.button_height) // 2
                            button_rect = pygame.Rect(button_x, button_y, lista.button_width, lista.button_height)
                            
                            if button_rect.collidepoint(ui_pos):
                                price = lista.item_prices.get(lista.aktivni_kategorie, {}).get(i, 0)

                                if lista.aktivni_kategorie == "Rebirth":
                                    if can_rebirth(lista):
                                        lista.rebirth_confirm_open = True
                                    elif hasattr(lista, 'pridat_floating_text'):
                                        need = int(getattr(lista, 'rebirth_requirement', 1_000_000))
                                        msg = txt(lista, "rebirth_from", "Rebirth od {need}$").format(need=need)
                                        lista.pridat_floating_text(25, 130, msg, (255, 190, 190), life=1.2)
                                    continue

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
                                            aktualizovat_ukol(lista, "buy_dj", value=1)
                                            
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
    aktualizovat_ukol(lista, "reach_10k_ps", value=int(getattr(lista, 'prijem', 0)))

    if current_time - last_income_update >= 1.0:
        pridat_penize(lista, auto_income)
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
        pridat_penize(lista, drum_income)
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
        pridat_penize(lista, burst_income)
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
        pridat_penize(lista, piano_income)
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
        pridat_penize(lista, dj_income)
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