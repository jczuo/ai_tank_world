import pygame  # 导入pygame模块，类似于C++中的 #include
import random
from constants import *  # 从constants模块导入所有内容，类似于C++中的 using namespace

# 定义SmallBrick类，继承自pygame.sprite.Sprite
class SmallBrick(pygame.sprite.Sprite):
    def __init__(self, x, y):  # 构造函数，相当于C++的 SmallBrick(int x, int y)
        super().__init__()  # 调用父类构造函数，相当于C++的 Sprite::Sprite()
        # 创建Surface对象作为砖块图像
        self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
        self.image.fill(BRICK_COLOR)  # 填充颜色
        self.rect = self.image.get_rect()  # 获取图像的矩形边界
        self.rect.x = x  # 设置x坐标
        self.rect.y = y  # 设置y坐标
        # 整数除法，计算网格坐标
        self.grid_x = x // GRID_SIZE  # // 表示整数除法，相当于C++中的 int除法
        self.grid_y = y // GRID_SIZE
        self.is_solid = True  # 布尔值，表示砖块是否为实心
        self.health = BRICK_HEALTH  # 设置砖块生命值

    def hit(self):  # 砖块被击中时调用的方法
        self.health -= 1
        if self.health <= 0:
            self.is_solid = False
            self.kill()  # 销毁精灵对象，从所有精灵组中移除
        return True  # 总是返回 True 表示击中

    def update(self):  # 更新方法，通常每帧调用
        if not self.is_solid:
            self.image.set_alpha(128)  # 设置透明度，使非实心砖块半透明

# 定义Brick类，由多个SmallBrick组成
class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((BRICK_SIZE, BRICK_SIZE))
        self.image.fill(BRICK_COLOR)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.small_bricks = [SmallBrick(x + i * GRID_SIZE, y + j * GRID_SIZE) 
                             for i in range(BRICK_SIZE // GRID_SIZE) for j in range(BRICK_SIZE // GRID_SIZE)]
        self.is_solid = True

    def hit(self, x, y):
        grid_x = (x - self.rect.x) // GRID_SIZE
        grid_y = (y - self.rect.y) // GRID_SIZE
        index = grid_y * (BRICK_SIZE // GRID_SIZE) + grid_x
        if 0 <= index < len(self.small_bricks):
            small_brick = self.small_bricks[index]
            if small_brick.alive() and small_brick.is_solid:
                small_brick.hit()
                if self.is_destroyed():
                    self.kill()
                return True
        return False

    def is_destroyed(self):
        return not any(small_brick.alive() for small_brick in self.small_bricks)

    def update(self):
        for small_brick in self.small_bricks:
            small_brick.update()
        if self.is_destroyed():
            self.kill()

    def draw(self, surface):
        for small_brick in self.small_bricks:
            if small_brick.alive():
                surface.blit(small_brick.image, small_brick.rect)