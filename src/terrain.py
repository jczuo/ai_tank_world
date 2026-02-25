import pygame
import math
from constants import *


class Terrain(pygame.sprite.Sprite):
    """所有地形的基类"""

    def __init__(self, grid_x, grid_y, terrain_type):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.terrain_type = terrain_type
        self.is_solid = True
        self.blocks_bullets = True
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE

    def hit(self, damage=1, can_break_steel=False):
        return False

    def is_passable_by_tank(self):
        return not self.is_solid

    def is_passable_by_bullet(self):
        return not self.blocks_bullets


class BrickWall(Terrain):
    """砖墙 - 可被摧毁"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_BRICK)
        self.health = BRICK_HEALTH
        self._draw()

    def _draw(self):
        s = GRID_SIZE
        self.image.fill(BRICK_COLOR)
        lc = BRICK_LINE_COLOR
        pygame.draw.line(self.image, lc, (0, s // 2), (s, s // 2), 1)
        pygame.draw.line(self.image, lc, (s // 2, 0), (s // 2, s // 2), 1)
        pygame.draw.line(self.image, lc, (0, 0), (0, s), 1)
        pygame.draw.line(self.image, lc, (s - 1, 0), (s - 1, s), 1)
        pygame.draw.line(self.image, lc, (s // 4, s // 2), (s // 4, s), 1)
        pygame.draw.line(self.image, lc, (3 * s // 4, s // 2), (3 * s // 4, s), 1)

    def _draw_damaged(self):
        s = GRID_SIZE
        self.image.fill((0, 0, 0, 0))
        self.image.fill((*BRICK_COLOR[:3], 180))
        lc = BRICK_LINE_COLOR
        pygame.draw.line(self.image, lc, (0, s // 2), (s, s // 2), 1)
        pygame.draw.line(self.image, lc, (s // 2, 0), (s // 2, s // 2), 1)
        for cx, cy in [(s // 4, s // 4), (3 * s // 4, 3 * s // 4)]:
            pygame.draw.line(self.image, (50, 50, 50), (cx - 3, cy - 3), (cx + 3, cy + 3), 1)
            pygame.draw.line(self.image, (50, 50, 50), (cx + 3, cy - 3), (cx - 3, cy + 3), 1)

    def hit(self, damage=1, can_break_steel=False):
        self.health -= damage
        if self.health <= 0:
            self.is_solid = False
            self.blocks_bullets = False
            self.kill()
            return True
        self._draw_damaged()
        return True


class SteelWall(Terrain):
    """钢墙 - 通常不可摧毁"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_STEEL)
        self._draw()

    def _draw(self):
        s = GRID_SIZE
        self.image.fill(STEEL_COLOR)
        pygame.draw.rect(self.image, STEEL_SHINE, (1, 1, s // 2 - 1, s // 2 - 1))
        pygame.draw.rect(self.image, STEEL_SHADOW, (s // 2, s // 2, s // 2 - 1, s // 2 - 1))
        pygame.draw.rect(self.image, STEEL_SHADOW, (0, 0, s, s), 1)
        mid = s // 2
        pygame.draw.line(self.image, STEEL_SHADOW, (0, mid), (s, mid), 1)
        pygame.draw.line(self.image, STEEL_SHADOW, (mid, 0), (mid, s), 1)

    def hit(self, damage=1, can_break_steel=False):
        if can_break_steel:
            self.is_solid = False
            self.blocks_bullets = False
            self.kill()
            return True
        return True  # 子弹消失但墙不毁


class Water(Terrain):
    """水面 - 坦克不可通行，子弹可通过"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_WATER)
        self.is_solid = True
        self.blocks_bullets = False
        self.anim_offset = 0
        self._draw()

    def _draw(self):
        s = GRID_SIZE
        self.image.fill(WATER_COLOR_1)
        for i in range(0, s, 4):
            offset = int(2 * math.sin((i + self.anim_offset) * 0.5))
            pygame.draw.line(self.image, WATER_COLOR_2,
                             (0, i + offset), (s, i + offset), 1)

    def update(self):
        self.anim_offset = (self.anim_offset + 0.05) % (2 * math.pi * 20)
        self._draw()


class Forest(Terrain):
    """草丛 - 坦克可通行，提供视觉遮挡（绘制在坦克上方）"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_FOREST)
        self.is_solid = False
        self.blocks_bullets = False
        self._draw()

    def _draw(self):
        s = GRID_SIZE
        self.image.fill((0, 0, 0, 0))
        self.image.fill(FOREST_COLOR)
        for cx, cy, r in [(s // 4, s // 4, 5), (3 * s // 4, s // 4, 4),
                           (s // 2, s // 2, 5), (s // 4, 3 * s // 4, 4),
                           (3 * s // 4, 3 * s // 4, 5)]:
            pygame.draw.circle(self.image, FOREST_DARK, (cx, cy), r)
            pygame.draw.circle(self.image, FOREST_COLOR, (cx - 1, cy - 1), r - 1)


class Ice(Terrain):
    """冰面 - 坦克可通行但会滑行"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_ICE)
        self.is_solid = False
        self.blocks_bullets = False
        self._draw()

    def _draw(self):
        s = GRID_SIZE
        self.image.fill(ICE_COLOR)
        pygame.draw.line(self.image, ICE_SHINE, (2, 2), (s // 2, s // 3), 1)
        pygame.draw.line(self.image, ICE_SHINE, (s // 2, s // 2), (s - 3, s - 4), 1)
        pygame.draw.rect(self.image, WHITE, (s // 4, s // 4, 3, 2))


class Base(Terrain):
    """基地(鹰) - 被摧毁则游戏结束"""

    def __init__(self, grid_x, grid_y):
        super().__init__(grid_x, grid_y, TERRAIN_BASE)
        self.is_solid = True
        self.blocks_bullets = True
        self.destroyed = False
        self.image = pygame.Surface((GRID_SIZE * 2, GRID_SIZE * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE
        self._draw()

    def _draw(self):
        s = GRID_SIZE * 2
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, BASE_BORDER, (0, 0, s, s), 2)
        pygame.draw.rect(self.image, (40, 40, 40), (2, 2, s - 4, s - 4))
        cx, cy = s // 2, s // 2
        pts = []
        for i in range(5):
            angle = math.radians(-90 + i * 72)
            pts.append((cx + int(12 * math.cos(angle)), cy + int(12 * math.sin(angle))))
            angle2 = math.radians(-90 + i * 72 + 36)
            pts.append((cx + int(5 * math.cos(angle2)), cy + int(5 * math.sin(angle2))))
        pygame.draw.polygon(self.image, BASE_COLOR, pts)
        pygame.draw.polygon(self.image, BASE_BORDER, pts, 1)

    def _draw_destroyed(self):
        s = GRID_SIZE * 2
        self.image.fill((0, 0, 0, 0))
        pygame.draw.rect(self.image, (80, 80, 80), (2, 2, s - 4, s - 4))
        pygame.draw.line(self.image, DARK_RED, (4, 4), (s - 4, s - 4), 2)
        pygame.draw.line(self.image, DARK_RED, (s - 4, 4), (4, s - 4), 2)

    def hit(self, damage=1, can_break_steel=False):
        if not self.destroyed:
            self.destroyed = True
            self._draw_destroyed()
            return True
        return False


TERRAIN_CLASSES = {
    TERRAIN_BRICK: BrickWall,
    TERRAIN_STEEL: SteelWall,
    TERRAIN_WATER: Water,
    TERRAIN_FOREST: Forest,
    TERRAIN_ICE: Ice,
    TERRAIN_BASE: Base,
}


def create_terrain(grid_x, grid_y, terrain_char):
    cls = TERRAIN_CLASSES.get(terrain_char)
    if cls:
        return cls(grid_x, grid_y)
    return None
