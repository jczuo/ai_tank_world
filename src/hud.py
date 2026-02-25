import pygame
from constants import *


class HUD:
    """侧边栏 HUD 显示"""

    def __init__(self):
        self.font_large = None
        self.font_medium = None
        self.font_small = None
        self._init_fonts()

    def _init_fonts(self):
        self.font_large = pygame.font.Font(None, 32)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 20)

    def draw(self, surface, game_state):
        sidebar = pygame.Rect(GAME_WIDTH, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT)
        pygame.draw.rect(surface, HUD_BG, sidebar)
        pygame.draw.line(surface, GRAY, (GAME_WIDTH, 0), (GAME_WIDTH, SCREEN_HEIGHT), 2)

        x = GAME_WIDTH + 15
        y = 15

        # 关卡标题
        title = self.font_large.render(
            f"STAGE {game_state.get('level', 1)}", True, HUD_ACCENT)
        surface.blit(title, (x, y))
        y += 30

        level_name = game_state.get("level_name", "")
        if level_name:
            name_surf = self.font_small.render(level_name, True, HUD_TEXT)
            surface.blit(name_surf, (x, y))
        y += 30

        # 分割线
        pygame.draw.line(surface, DARK_GRAY, (x, y), (x + SIDEBAR_WIDTH - 30, y), 1)
        y += 15

        # 玩家信息
        surface.blit(self.font_medium.render("PLAYER", True, GREEN), (x, y))
        y += 25

        # 生命
        lives = game_state.get("lives", 0)
        surface.blit(self.font_small.render(f"Lives: {lives}", True, HUD_TEXT), (x, y))
        y += 22

        # 血量条
        health = game_state.get("health", 0)
        max_health = game_state.get("max_health", PLAYER_HEALTH)
        self._draw_bar(surface, x, y, 140, 12, health, max_health, GREEN, DARK_RED)
        y += 20

        # 星级
        star_level = game_state.get("star_level", 0)
        stars = "★" * star_level + "☆" * (3 - star_level)
        surface.blit(self.font_small.render(f"Level: {stars}", True, YELLOW), (x, y))
        y += 30

        # 分割线
        pygame.draw.line(surface, DARK_GRAY, (x, y), (x + SIDEBAR_WIDTH - 30, y), 1)
        y += 15

        # 敌人信息
        surface.blit(self.font_medium.render("ENEMIES", True, RED), (x, y))
        y += 25

        remaining = game_state.get("enemies_remaining", 0)
        active = game_state.get("enemies_active", 0)
        surface.blit(self.font_small.render(
            f"Remaining: {remaining}", True, HUD_TEXT), (x, y))
        y += 20
        surface.blit(self.font_small.render(
            f"Active: {active}", True, HUD_TEXT), (x, y))
        y += 20

        # 敌方坦克类型图标
        queue = game_state.get("enemy_queue_types", {})
        for etype, count in queue.items():
            if count <= 0:
                continue
            cfg = ENEMY_TYPES.get(etype, {})
            color = cfg.get("color", GRAY)
            name = cfg.get("name", etype)
            pygame.draw.rect(surface, color, (x, y + 2, 10, 10))
            surface.blit(self.font_small.render(
                f" {name}: {count}", True, HUD_TEXT), (x + 14, y))
            y += 18
        y += 15

        # 分割线
        pygame.draw.line(surface, DARK_GRAY, (x, y), (x + SIDEBAR_WIDTH - 30, y), 1)
        y += 15

        # 分数
        score = game_state.get("score", 0)
        surface.blit(self.font_medium.render("SCORE", True, HUD_ACCENT), (x, y))
        y += 25
        surface.blit(self.font_large.render(str(score), True, WHITE), (x, y))
        y += 40

        # 操作提示
        pygame.draw.line(surface, DARK_GRAY, (x, y), (x + SIDEBAR_WIDTH - 30, y), 1)
        y += 10
        hints = [
            ("Arrow", "Move"),
            ("Space", "Fire"),
            ("P", "Pause"),
            ("ESC", "Quit"),
        ]
        for key, action in hints:
            surface.blit(self.font_small.render(
                f"{key}: {action}", True, (120, 120, 120)), (x, y))
            y += 16

    def _draw_bar(self, surface, x, y, w, h, value, max_value, fg_color, bg_color):
        pygame.draw.rect(surface, bg_color, (x, y, w, h))
        if max_value > 0:
            fill_w = int(w * value / max_value)
            pygame.draw.rect(surface, fg_color, (x, y, fill_w, h))
        pygame.draw.rect(surface, GRAY, (x, y, w, h), 1)

    def draw_level_transition(self, surface, level_num, level_name):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render(f"STAGE {level_num}", True, HUD_ACCENT)
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        surface.blit(title, tr)

        if level_name:
            sub = self.font_medium.render(level_name, True, WHITE)
            sr = sub.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 15))
            surface.blit(sub, sr)

    def draw_game_over(self, surface, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("GAME OVER", True, RED)
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        surface.blit(title, tr)

        sc = self.font_medium.render(f"Score: {score}", True, YELLOW)
        sr = sc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(sc, sr)

        hint = self.font_medium.render("Press SPACE to restart", True, WHITE)
        hr = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        surface.blit(hint, hr)

    def draw_victory(self, surface, score):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("VICTORY!", True, YELLOW)
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        surface.blit(title, tr)

        sc = self.font_medium.render(f"Final Score: {score}", True, WHITE)
        sr = sc.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(sc, sr)

        hint = self.font_medium.render("Press SPACE to play again", True, WHITE)
        hr = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 35))
        surface.blit(hint, hr)

    def draw_pause(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        title = self.font_large.render("PAUSED", True, WHITE)
        tr = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        surface.blit(title, tr)

    def draw_menu(self, surface):
        surface.fill(BLACK)
        cx = SCREEN_WIDTH // 2
        cy = SCREEN_HEIGHT // 2

        title = pygame.font.Font(None, 60).render("TANK BATTLE", True, HUD_ACCENT)
        tr = title.get_rect(center=(cx, cy - 80))
        surface.blit(title, tr)

        sub = self.font_large.render("坦克大战", True, WHITE)
        sr = sub.get_rect(center=(cx, cy - 40))
        surface.blit(sub, sr)

        start = self.font_medium.render("Press SPACE to start", True, HUD_TEXT)
        start_r = start.get_rect(center=(cx, cy + 20))
        surface.blit(start, start_r)

        controls = [
            "Arrow Keys: Move",
            "Space: Fire",
            "P: Pause",
            "ESC: Quit",
        ]
        for i, line in enumerate(controls):
            t = self.font_small.render(line, True, (120, 120, 120))
            surface.blit(t, t.get_rect(center=(cx, cy + 70 + i * 20)))
