import pygame
import random
import math
from constants import *


class Explosion(pygame.sprite.Sprite):
    """爆炸特效 - 扩散的火焰粒子"""

    def __init__(self, x, y, size="small"):
        super().__init__()
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = EXPLOSION_DURATION if size == "small" else EXPLOSION_DURATION * 2
        radius = GRID_SIZE if size == "small" else GRID_SIZE * 2
        self.max_radius = radius
        self.particles = []
        count = 8 if size == "small" else 16
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2.0)
            self.particles.append({
                "dx": math.cos(angle) * speed,
                "dy": math.sin(angle) * speed,
                "radius": random.randint(2, 5),
                "color": random.choice([RED, ORANGE, YELLOW, WHITE]),
            })
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            self.kill()
            return
        progress = elapsed / self.duration
        self.image.fill((0, 0, 0, 0))
        cx, cy = self.image.get_width() // 2, self.image.get_height() // 2
        alpha = max(0, int(255 * (1 - progress)))
        spread = progress * self.max_radius
        for p in self.particles:
            px = cx + int(p["dx"] * spread)
            py = cy + int(p["dy"] * spread)
            r = max(1, int(p["radius"] * (1 - progress * 0.5)))
            c = (*p["color"][:3], alpha)
            surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, c, (r, r), r)
            self.image.blit(surf, (px - r, py - r))
        center_r = max(1, int(self.max_radius * 0.4 * (1 - progress)))
        center_alpha = max(0, int(200 * (1 - progress)))
        surf = pygame.Surface((center_r * 2, center_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*YELLOW[:3], center_alpha), (center_r, center_r), center_r)
        self.image.blit(surf, (cx - center_r, cy - center_r))


class SpawnEffect(pygame.sprite.Sprite):
    """坦克出生闪烁特效"""

    def __init__(self, x, y, callback, callback_args=()):
        super().__init__()
        self.x = x
        self.y = y
        self.callback = callback
        self.callback_args = callback_args
        self.start_time = pygame.time.get_ticks()
        self.duration = SPAWN_ANIM_DURATION
        self.image = pygame.Surface((TANK_SIZE, TANK_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            if self.callback:
                self.callback(*self.callback_args)
            self.kill()
            return
        progress = elapsed / self.duration
        self.image.fill((0, 0, 0, 0))
        flash = int((elapsed // 100) % 2 == 0)
        if flash:
            s = TANK_SIZE
            alpha = int(180 * (1 - progress * 0.5))
            color = (*WHITE[:3], alpha)
            for i in range(3):
                shrink = int(i * 4 * (1 - progress))
                r = pygame.Rect(shrink, shrink, s - shrink * 2, s - shrink * 2)
                if r.width > 0 and r.height > 0:
                    surf = pygame.Surface((r.width, r.height), pygame.SRCALPHA)
                    pygame.draw.rect(surf, color, (0, 0, r.width, r.height), 2)
                    self.image.blit(surf, r.topleft)


class ShieldEffect(pygame.sprite.Sprite):
    """护盾环绕特效"""

    def __init__(self, tank):
        super().__init__()
        self.tank = tank
        self.start_time = pygame.time.get_ticks()
        self.duration = SHIELD_DURATION
        s = TANK_SIZE + 8
        self.image = pygame.Surface((s, s), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.angle = 0

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.start_time >= self.duration or not self.tank.alive():
            if self.tank.alive():
                self.tank.shielded = False
            self.kill()
            return
        self.angle = (self.angle + 5) % 360
        self.rect.center = self.tank.rect.center
        s = self.image.get_width()
        self.image.fill((0, 0, 0, 0))
        cx, cy = s // 2, s // 2
        r = s // 2 - 1
        remaining = (self.duration - (now - self.start_time)) / self.duration
        alpha = int(200 * remaining) if remaining < 0.3 else 200
        for i in range(8):
            a = math.radians(self.angle + i * 45)
            x = cx + int(r * math.cos(a))
            y = cy + int(r * math.sin(a))
            surf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*CYAN[:3], alpha), (3, 3), 3)
            self.image.blit(surf, (x - 3, y - 3))
        pygame.draw.circle(self.image, (*BLUE[:3], alpha // 3), (cx, cy), r, 1)
