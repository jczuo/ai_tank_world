import pygame
from constants import *


class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, direction, speed=PLAYER_BULLET_SPEED,
                 damage=1, can_break_steel=False, owner="player"):
        super().__init__()
        self.direction = direction
        self.speed = speed
        self.damage = damage
        self.can_break_steel = can_break_steel
        self.owner = owner
        self.created_time = pygame.time.get_ticks()

        size = BULLET_SIZE
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        color = YELLOW if owner == "player" else RED
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x, y))
        self._align_to_grid()

    def _align_to_grid(self):
        if self.direction in ("up", "down"):
            self.rect.centerx = round(self.rect.centerx / GRID_SIZE) * GRID_SIZE
        else:
            self.rect.centery = round(self.rect.centery / GRID_SIZE) * GRID_SIZE

    def update(self):
        dx = {"left": -1, "right": 1}.get(self.direction, 0)
        dy = {"up": -1, "down": 1}.get(self.direction, 0)
        self.rect.x += dx * self.speed
        self.rect.y += dy * self.speed

        if (self.rect.right < 0 or self.rect.left > GAME_WIDTH or
                self.rect.bottom < 0 or self.rect.top > GAME_HEIGHT):
            self.kill()
