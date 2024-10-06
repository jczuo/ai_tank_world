import pygame
from constants import *
from brick import Brick, SmallBrick  # 添加这行来导入 Brick 和 SmallBrick 类

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction
        self.speed = BULLET_SPEED  # 添加这行，定义子弹速度
        self.created_time = pygame.time.get_ticks()  # 添加这行，记录子弹创建时间
        self.align_to_grid()  # 在初始化时就对齐网格

    def align_to_grid(self):
        if self.direction in ["up", "down"]:
            self.rect.centerx = round(self.rect.centerx / GRID_SIZE) * GRID_SIZE
        else:
            self.rect.centery = round(self.rect.centery / GRID_SIZE) * GRID_SIZE

    def update(self, bricks):
        # 保存旧位置
        old_pos = self.rect.center

        # 更新子弹位置
        if self.direction == "up":
            self.rect.y -= self.speed
        elif self.direction == "down":
            self.rect.y += self.speed
        elif self.direction == "left":
            self.rect.x -= self.speed
        elif self.direction == "right":
            self.rect.x += self.speed

        # 检查是否超出屏幕范围
        if (self.rect.right < 0 or self.rect.left > SCREEN_WIDTH or
            self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT):
            self.kill()
            return

        # 检查是否击中砖块
        hit = self.check_brick_collision(bricks)
        if hit:
            self.kill()

    def check_brick_collision(self, bricks):
        hit_bricks = []
        for brick in bricks:
            if isinstance(brick, Brick):
                for small_brick in brick.small_bricks:
                    if small_brick.alive() and small_brick.is_solid:
                        if self.rect.colliderect(small_brick.rect):
                            hit_bricks.append((brick, small_brick))
            elif isinstance(brick, SmallBrick) and brick.is_solid:
                if self.rect.colliderect(brick.rect):
                    hit_bricks.append((brick, brick))

        if hit_bricks:
            # 对所有被击中的砖块进行处理
            for brick, small_brick in hit_bricks:
                if isinstance(brick, Brick):
                    brick.hit(small_brick.rect.centerx, small_brick.rect.centery)
                else:
                    small_brick.hit()
            return True
        return False