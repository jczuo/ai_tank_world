import os
import pygame
import random
from constants import *
from bullet import Bullet
from brick import SmallBrick, Brick

class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.load_image(color)
        self.rect = self.image.get_rect()
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.rect.x = self.grid_x * GRID_SIZE
        self.rect.y = self.grid_y * GRID_SIZE
        self.direction = "up"
        self.color = color
        self.health = 5  # 玩家坦克生命值为5

    def load_image(self, color):
        try:
            if color == GREEN:
                image_path = os.path.join("assets", "images", "tank_green.png")
            else:
                image_path = os.path.join("assets", "images", "tank_red.png")
            
            print(f"尝试加载图片：{image_path}")
            if os.path.exists(image_path):
                self.original_image = pygame.image.load(image_path).convert_alpha()
                self.original_image = pygame.transform.scale(self.original_image, (TANK_SIZE, TANK_SIZE))
                print(f"成功加载图片：{image_path}")
            else:
                print(f"图片文件不存在：{image_path}")
                raise FileNotFoundError(f"找不到图片文件：{image_path}")
        except Exception as e:
            print(f"加载图片时出错：{e}")
            print("使用纯色方块代替贴图")
            self.original_image = pygame.Surface((TANK_SIZE, TANK_SIZE))
            self.original_image.fill(color)
        
        self.image = self.original_image.copy()

    def move(self, dx, dy, bricks, enemy_tanks):
        new_direction = self.get_new_direction(dx, dy)
        
        # 如果方向改变，先更新方向和图像
        if new_direction != self.direction:
            self.direction = new_direction
            self.update_image()
            return  # 方向改变时，不移动位置
        
        new_grid_x = self.grid_x + dx
        new_grid_y = self.grid_y + dy

        # 检查是否超出屏幕边界
        if 0 <= new_grid_x * GRID_SIZE < SCREEN_WIDTH - TANK_SIZE + 1 and 0 <= new_grid_y * GRID_SIZE < SCREEN_HEIGHT - TANK_SIZE + 1:
            # 创建新位置的矩形，考虑坦克的实际大小
            new_rect = pygame.Rect(new_grid_x * GRID_SIZE, new_grid_y * GRID_SIZE, TANK_SIZE, TANK_SIZE)
            
            # 检查与砖块的碰撞
            brick_collision = any(brick.rect.colliderect(new_rect) for brick in bricks 
                                  if isinstance(brick, (Brick, SmallBrick)) and brick.is_solid)
            
            # 检查与敌方坦克的碰撞
            enemy_collision = any(enemy_tank.rect.colliderect(new_rect) for enemy_tank in enemy_tanks if enemy_tank != self)
            
            if not brick_collision and not enemy_collision:
                self.grid_x = new_grid_x
                self.grid_y = new_grid_y
                self.rect.x = self.grid_x * GRID_SIZE
                self.rect.y = self.grid_y * GRID_SIZE

    def get_new_direction(self, dx, dy):
        if dx < 0:
            return "left"
        elif dx > 0:
            return "right"
        elif dy < 0:
            return "up"
        elif dy > 0:
            return "down"
        return self.direction  # 如果没有移动，保持当前方向

    def check_collision(self, new_x, new_y, bricks, enemy_tanks):
        # 检查是否超出屏幕边界
        if new_x < 0 or new_x >= GRID_WIDTH or new_y < 0 or new_y >= GRID_HEIGHT:
            return True

        # 检查是否与砖块碰撞
        for brick in bricks:
            if brick.grid_x == new_x and brick.grid_y == new_y:
                return True

        # 检查是否与敌人坦克碰撞
        for enemy in enemy_tanks:
            if enemy.grid_x == new_x and enemy.grid_y == new_y:
                return True

        return False

    def get_bullet_start_position(self):
        if self.direction == "up":
            return self.rect.centerx, self.rect.top
        elif self.direction == "down":
            return self.rect.centerx, self.rect.bottom
        elif self.direction == "left":
            return self.rect.left, self.rect.centery
        elif self.direction == "right":
            return self.rect.right, self.rect.centery

    def update_image(self):
        if self.direction == "up":
            self.image = self.original_image
        elif self.direction == "down":
            self.image = pygame.transform.rotate(self.original_image, 180)
        elif self.direction == "left":
            self.image = pygame.transform.rotate(self.original_image, 90)
        elif self.direction == "right":
            self.image = pygame.transform.rotate(self.original_image, 270)

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        return self.health <= 0

class EnemyTank(Tank):
    def __init__(self, bricks):
        print("开始初始化敌人坦克")
        # 找到一个不与砖块重叠的位置
        attempts = 0
        while attempts < 100:  # 限制尝试次数，防止无限循环
            x = random.randint(0, (SCREEN_WIDTH - TANK_SIZE) // GRID_SIZE) * GRID_SIZE
            y = random.randint(0, (SCREEN_HEIGHT - TANK_SIZE) // GRID_SIZE) * GRID_SIZE
            temp_rect = pygame.Rect(x, y, TANK_SIZE, TANK_SIZE)
            if not any(brick.rect.colliderect(temp_rect) for brick in bricks if isinstance(brick, (Brick, SmallBrick)) and brick.is_solid):
                print(f"找到合适的位置：({x}, {y})")
                break
            attempts += 1
        
        if attempts == 100:
            print("无法找到合适的位置，使用默认位置")
            x, y = 0, 0

        super().__init__(x, y, RED)
        self.move_cooldown = 0
        self.fire_cooldown = 0
        self.health = 3  # 敌人坦克生命值为3
        print("敌人坦克初始化完成")

    def find_empty_position(self, start_x, start_y, bricks):
        for y in range(start_y, start_y + 3):
            for x in range(start_x, start_x + 3):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, TANK_SIZE, TANK_SIZE)
                if not self.check_collision(rect, bricks):
                    return x, y
        return start_x, start_y  # 如果没有找到空位,返回起始位置

    def update(self, bricks, player):
        # 实现敌人坦克的移动逻辑
        dx, dy = self.get_movement_direction(player)
        self.move(dx, dy, bricks, pygame.sprite.GroupSingle(player))

        # 更新坦克位置
        self.rect.x = int(self.grid_x * GRID_SIZE)
        self.rect.y = int(self.grid_y * GRID_SIZE)

        # 实现射击逻辑
        # ...（射击逻辑保持不变）

    def get_movement_direction(self, player):
        # 实现简单的追踪逻辑
        dx = 1 if player.grid_x > self.grid_x else -1 if player.grid_x < self.grid_x else 0
        dy = 1 if player.grid_y > self.grid_y else -1 if player.grid_y < self.grid_y else 0
        return dx, dy

    def hit(self):
        self.health -= 1
        if self.health <= 0:
            self.kill()
        return self.health <= 0