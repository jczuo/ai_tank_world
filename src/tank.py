import os
import pygame
import random
import math
from constants import *
from bullet import Bullet


def _draw_tank_body(surface, body_color, turret_color, size):
    """程序化绘制坦克图形 (朝上)"""
    s = size
    surface.fill((0, 0, 0, 0))
    # 履带
    track_color = (60, 60, 60)
    pygame.draw.rect(surface, track_color, (1, 2, 8, s - 4))
    pygame.draw.rect(surface, track_color, (s - 9, 2, 8, s - 4))
    for i in range(2, s - 4, 5):
        pygame.draw.line(surface, (40, 40, 40), (1, i), (9, i), 1)
        pygame.draw.line(surface, (40, 40, 40), (s - 9, i), (s - 1, i), 1)
    # 车体
    pygame.draw.rect(surface, body_color, (7, 4, s - 14, s - 8))
    lighter = tuple(min(255, c + 30) for c in body_color[:3])
    pygame.draw.rect(surface, lighter, (9, 6, s - 18, s - 12))
    # 炮塔
    tw = s // 3
    th = s // 3
    tx = (s - tw) // 2
    ty = (s - th) // 2
    pygame.draw.rect(surface, turret_color, (tx, ty, tw, th))
    # 炮管
    barrel_w = 4
    barrel_h = s // 2
    bx = (s - barrel_w) // 2
    pygame.draw.rect(surface, turret_color, (bx, 0, barrel_w, ty + 2))
    pygame.draw.rect(surface, (min(255, turret_color[0] + 40),
                                min(255, turret_color[1] + 40),
                                min(255, turret_color[2] + 40)),
                     (bx + 1, 0, barrel_w - 2, ty + 2))


class Tank(pygame.sprite.Sprite):
    """玩家坦克"""

    def __init__(self, grid_x, grid_y):
        super().__init__()
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.direction = "up"

        # 属性
        self.max_health = PLAYER_HEALTH
        self.health = self.max_health
        self.speed = PLAYER_SPEED
        self.fire_cooldown = PLAYER_FIRE_COOLDOWN
        self.last_fire_time = 0
        self.star_level = 0
        self.shielded = False

        # 画坦克
        self._build_image(GREEN, DARK_GREEN)
        self.rect = self.image.get_rect()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE

        # 冰面滑行
        self.sliding = False
        self.slide_dx = 0
        self.slide_dy = 0

    def _build_image(self, body_color, turret_color):
        self.original_image = pygame.Surface((TANK_SIZE, TANK_SIZE), pygame.SRCALPHA)
        # 尝试加载图片，失败则程序化绘制
        try:
            path = os.path.join("assets", "images", "tank_green.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self.original_image = pygame.transform.scale(img, (TANK_SIZE, TANK_SIZE))
            else:
                raise FileNotFoundError
        except Exception:
            _draw_tank_body(self.original_image, body_color, turret_color, TANK_SIZE)
        self.image = self.original_image.copy()

    def _rotate_image(self):
        angles = {"up": 0, "down": 180, "left": 90, "right": 270}
        self.image = pygame.transform.rotate(self.original_image, angles[self.direction])
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)

    @property
    def upgrade(self):
        return PLAYER_UPGRADES[min(self.star_level, 3)]

    def apply_star(self):
        if self.star_level < 3:
            self.star_level += 1

    def can_fire(self):
        now = pygame.time.get_ticks()
        return now - self.last_fire_time >= self.fire_cooldown

    def fire(self):
        if not self.can_fire():
            return None
        self.last_fire_time = pygame.time.get_ticks()
        x, y = self._bullet_start()
        up = self.upgrade
        return Bullet(x, y, self.direction,
                      speed=up["bullet_speed"],
                      damage=up["bullet_damage"],
                      can_break_steel=up["can_break_steel"],
                      owner="player")

    def active_bullet_limit(self):
        return self.upgrade["max_bullets"]

    def _bullet_start(self):
        cx, cy = self.rect.centerx, self.rect.centery
        half = TANK_SIZE // 2
        if self.direction == "up":
            return cx, self.rect.top
        elif self.direction == "down":
            return cx, self.rect.bottom
        elif self.direction == "left":
            return self.rect.left, cy
        else:
            return self.rect.right, cy

    def move(self, dx, dy, terrain_group, tank_group):
        new_dir = self._direction_from(dx, dy)
        if new_dir != self.direction:
            self.direction = new_dir
            self._rotate_image()
            return

        new_gx = self.grid_x + dx
        new_gy = self.grid_y + dy

        if not self._in_bounds(new_gx, new_gy):
            return

        new_rect = pygame.Rect(new_gx * GRID_SIZE, new_gy * GRID_SIZE,
                                TANK_SIZE, TANK_SIZE)

        if self._collides_terrain(new_rect, terrain_group):
            return
        if self._collides_tanks(new_rect, tank_group):
            return

        self.grid_x = new_gx
        self.grid_y = new_gy
        self.rect.x = new_gx * GRID_SIZE
        self.rect.y = new_gy * GRID_SIZE

    def _direction_from(self, dx, dy):
        if dx < 0:
            return "left"
        if dx > 0:
            return "right"
        if dy < 0:
            return "up"
        if dy > 0:
            return "down"
        return self.direction

    def _in_bounds(self, gx, gy):
        return (0 <= gx * GRID_SIZE <= GAME_WIDTH - TANK_SIZE and
                0 <= gy * GRID_SIZE <= GAME_HEIGHT - TANK_SIZE)

    def _collides_terrain(self, new_rect, terrain_group):
        for t in terrain_group:
            if t.is_solid and t.rect.colliderect(new_rect):
                return True
        return False

    def _collides_tanks(self, new_rect, tank_group):
        for tank in tank_group:
            if tank is not self and tank.alive() and tank.rect.colliderect(new_rect):
                return True
        return False

    def hit(self, damage=1):
        if self.shielded:
            return False
        self.health -= damage
        if self.health <= 0:
            self.kill()
            return True
        return False

    def is_on_ice(self, terrain_group):
        for t in terrain_group:
            if t.terrain_type == TERRAIN_ICE and t.rect.colliderect(self.rect):
                return True
        return False

    def update(self, *args):
        pass


class EnemyTank(Tank):
    """敌方坦克基类，支持多种类型"""

    def __init__(self, grid_x, grid_y, enemy_type="basic"):
        self.enemy_type = enemy_type
        cfg = ENEMY_TYPES[enemy_type]
        super().__init__(grid_x, grid_y)

        self.max_health = cfg["health"]
        self.health = self.max_health
        self.speed = cfg["speed"]
        self.fire_cooldown = cfg["fire_cooldown"]
        self.bullet_speed = cfg["bullet_speed"]
        self.bullet_damage = cfg["bullet_damage"]
        self.score_value = cfg["score"]
        self.body_color = cfg["color"]
        self.turret_color = cfg["color_dark"]

        # AI 状态
        self.move_timer = 0
        self.move_interval = random.randint(500, 1500)
        self.current_dx = 0
        self.current_dy = 1  # 默认向下
        self.last_move_time = pygame.time.get_ticks()
        self.frozen = False

        # 重新绘制
        self._build_enemy_image()
        self.rect.x = grid_x * GRID_SIZE
        self.rect.y = grid_y * GRID_SIZE

    def _build_enemy_image(self):
        self.original_image = pygame.Surface((TANK_SIZE, TANK_SIZE), pygame.SRCALPHA)
        _draw_tank_body(self.original_image, self.body_color, self.turret_color, TANK_SIZE)
        self.image = self.original_image.copy()
        self._rotate_image()

    def _update_armor_color(self):
        if self.enemy_type == "armor":
            color = ARMOR_HP_COLORS.get(self.health, RED)
            darker = tuple(max(0, c - 50) for c in color[:3])
            self.body_color = color
            self.turret_color = darker
            self._build_enemy_image()

    def hit(self, damage=1):
        self.health -= damage
        if self.enemy_type == "armor":
            self._update_armor_color()
        if self.health <= 0:
            self.kill()
            return True
        return False

    def can_fire(self):
        if self.frozen:
            return False
        now = pygame.time.get_ticks()
        return now - self.last_fire_time >= self.fire_cooldown

    def fire(self):
        if not self.can_fire():
            return None
        self.last_fire_time = pygame.time.get_ticks()
        x, y = self._bullet_start()
        return Bullet(x, y, self.direction,
                      speed=self.bullet_speed,
                      damage=self.bullet_damage,
                      owner="enemy")

    def ai_update(self, terrain_group, all_tanks, player):
        """AI 逻辑：移动和射击"""
        if self.frozen:
            return None

        now = pygame.time.get_ticks()

        # 移动逻辑
        if now - self.last_move_time >= self.move_interval:
            self.last_move_time = now
            self.move_interval = random.randint(400, 1200)
            self._choose_direction(player)

        if self.current_dx != 0 or self.current_dy != 0:
            old_gx, old_gy = self.grid_x, self.grid_y
            self.move(self.current_dx, self.current_dy, terrain_group, all_tanks)
            if self.grid_x == old_gx and self.grid_y == old_gy:
                if self.direction == self._direction_from(self.current_dx, self.current_dy):
                    self._choose_direction(player)

        # 射击逻辑
        if self.can_fire():
            if self._should_shoot(player):
                return self.fire()
        return None

    def _choose_direction(self, player):
        """选择移动方向 - 有一定概率朝玩家/基地方向移动"""
        r = random.random()
        if r < 0.4:
            # 朝玩家方向
            dx = 0
            dy = 0
            if abs(player.grid_x - self.grid_x) > abs(player.grid_y - self.grid_y):
                dx = 1 if player.grid_x > self.grid_x else -1
            else:
                dy = 1 if player.grid_y > self.grid_y else -1
            self.current_dx = dx
            self.current_dy = dy
        elif r < 0.6:
            # 朝下(基地方向)
            self.current_dx = 0
            self.current_dy = 1
        else:
            # 随机方向
            dirs = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            self.current_dx, self.current_dy = random.choice(dirs)

    def _should_shoot(self, player):
        """判断是否应该射击"""
        if self.direction == "up" and player.grid_y < self.grid_y:
            return abs(player.grid_x - self.grid_x) <= 3
        if self.direction == "down" and player.grid_y > self.grid_y:
            return abs(player.grid_x - self.grid_x) <= 3
        if self.direction == "left" and player.grid_x < self.grid_x:
            return abs(player.grid_y - self.grid_y) <= 3
        if self.direction == "right" and player.grid_x > self.grid_x:
            return abs(player.grid_y - self.grid_y) <= 3
        return random.random() < 0.3
