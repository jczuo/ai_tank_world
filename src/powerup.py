import pygame
import math
from constants import *


class PowerUp(pygame.sprite.Sprite):
    """道具基类"""

    TYPES = {
        "star":   {"color": YELLOW,  "symbol": "★", "name": "火力升级"},
        "shield": {"color": CYAN,    "symbol": "S",  "name": "护盾"},
        "life":   {"color": RED,     "symbol": "♥",  "name": "额外生命"},
        "bomb":   {"color": ORANGE,  "symbol": "B",  "name": "全屏炸弹"},
        "timer":  {"color": BLUE,    "symbol": "T",  "name": "冰冻敌人"},
    }

    def __init__(self, grid_x, grid_y, powerup_type):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.powerup_type = powerup_type
        self.spawn_time = pygame.time.get_ticks()
        info = self.TYPES[powerup_type]
        self.color = info["color"]
        self.symbol = info["symbol"]
        self.name = info["name"]
        self.visible = True

        self.image = pygame.Surface((POWERUP_SIZE, POWERUP_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE
        self._draw()

    def _draw(self):
        s = POWERUP_SIZE
        self.image.fill((0, 0, 0, 0))
        if not self.visible:
            return
        pygame.draw.rect(self.image, (*self.color[:3], 40), (0, 0, s, s))
        pygame.draw.rect(self.image, self.color, (0, 0, s, s), 2)
        try:
            font = pygame.font.Font(None, 28)
            text = font.render(self.symbol, True, self.color)
            tr = text.get_rect(center=(s // 2, s // 2))
            self.image.blit(text, tr)
        except Exception:
            pygame.draw.circle(self.image, self.color, (s // 2, s // 2), 8)

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.spawn_time
        if elapsed > POWERUP_DURATION:
            self.kill()
            return
        if elapsed > POWERUP_BLINK_START:
            self.visible = (elapsed // 200) % 2 == 0
            self._draw()
