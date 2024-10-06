import pygame
from constants import *
from tank import Tank, EnemyTank
from bullet import Bullet
from brick import Brick, SmallBrick
from sound import SoundManager
import os

class Game:
    def __init__(self):
        # 初始化 Pygame 和混音器
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(8)  # 设置8个音频通道
        pygame.mixer.music.set_volume(1.0)  # 设置音量为最大
        
        print(f"当前工作目录：{os.getcwd()}")  # 打印当前工作目录，用于调试
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战")
        self.clock = pygame.time.Clock()  # 用于控制游戏帧率
        
        # 创建精灵组，用于管理游戏对象
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bricks = pygame.sprite.Group()
        self.enemy_tanks = pygame.sprite.GroupSingle()  # 单一精灵组，确保只有一个敌人坦克
        
        self.max_enemies = 1  # 设置最大敌人数量
        self.create_enemy_tank()  # 创建初始敌人坦克
        
        # 创建玩家坦克并添加到精灵组
        self.player = Tank(14 * GRID_SIZE, 28 * GRID_SIZE, GREEN)
        self.all_sprites.add(self.player)
        
        # 初始化游戏状态
        self.running = True
        self.direction = "up"
        self.game_over = False
        
        self.create_map()  # 创建游戏地图
        
        self.grid_color = (50, 50, 50)  # 设置网格线颜色
        
        # 初始化音效管理器
        self.sound_manager = SoundManager()
        self.sound_manager.load_sounds()
        print("音效加载状态：")
        for sound_name, sound in self.sound_manager.sounds.items():
            print(f"{sound_name}: {'已加载' if sound else '未加载'}")
        print("静音状态：", self.sound_manager.muted_sounds)
        
        # 创建玩家和敌人子弹组
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
    
    def create_map(self):
        # 地图布局，0表示空白，1表示砖块
        layout = [
            "000000000000000000000000000000",
            "000000000000000000000000000000",
            "001100110011000011001100110011",
            "001100110011000011001100110011",
            "001100110011000011001100110011",
            "001100110011000011001100110011",
            "000000000000000000000000000000",
            "000000000000000000000000000000",
            "001111000011111100001111000011",
            "001111000011111100001111000011",
            "000011000000110000000011000000",
            "000011000000110000000011000000",
            "000011000000110000000011000000",
            "000011000000110000000011000000",
            "000011000011001100000011000000",
            "000011000011001100000011000000",
            "000011000011001100000011000011",
            "000011000011001100000011000011",
            "000000000011001100000000000011",
            "000000000011001100000000000011",
            "001100000011001100000000000011",
            "001100000011001100000000000011",
            "001100000000000000000011000011",
            "001100000000000000000011000011",
            "001100110000000000110011000011",
            "001100110000000000110011000011",
            "000000000000000000000000000000",
            "000000000000000000000000000000",
            "000000000000000000000000000000",
            "000000000000000000000000000000"
        ]
        
        # 根据布局创建砖块
        for row, line in enumerate(layout):
            for col, char in enumerate(line):
                if char == '1':
                    brick = Brick(col * BRICK_SIZE, row * BRICK_SIZE)  # 修正这里的拼写错误
                    self.bricks.add(brick)
                    self.all_sprites.add(brick)
                    for small_brick in brick.small_bricks:
                        self.all_sprites.add(small_brick)

    def create_enemy_tank(self):
        # 如果没有敌人坦克，则创建一个
        if len(self.enemy_tanks) == 0:
            print("尝试创建敌人坦克")
            try:
                new_enemy_tank = EnemyTank(self.bricks)
                self.enemy_tanks.add(new_enemy_tank)
                self.all_sprites.add(new_enemy_tank)
                print(f"敌人坦克创建成功，位置：({new_enemy_tank.grid_x}, {new_enemy_tank.grid_y})")
            except Exception as e:
                print(f"创建敌人坦克时出错：{e}")

    def handle_events(self):
        # 处理游戏事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.shoot()

    def handle_keys(self):
        # 处理键盘输入
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -1
        elif keys[pygame.K_RIGHT]:
            dx = 1
        elif keys[pygame.K_UP]:
            dy = -1
        elif keys[pygame.K_DOWN]:
            dy = 1
        
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, self.bricks, self.enemy_tanks)

    def shoot(self):
        # 玩家发射子弹
        x, y = self.player.get_bullet_start_position()
        bullet = Bullet(x, y, self.player.direction)
        self.all_sprites.add(bullet)
        self.player_bullets.add(bullet)
        self.sound_manager.play_shoot()
    
    def update(self):
        if self.game_over:
            return

        # 更新玩家坦克和子弹
        self.player.update(self.bricks, self.enemy_tanks)
        self.player_bullets.update(self.bricks)
        self.enemy_bullets.update(self.bricks)

        # 更新敌人坦克
        enemy_tank = self.enemy_tanks.sprite
        if enemy_tank:
            bullet = enemy_tank.update(self.bricks, self.player)
            if bullet:
                self.all_sprites.add(bullet)
                self.enemy_bullets.add(bullet)
                self.sound_manager.play_shoot()

        # 如果没有敌人坦克，创建一个新的
        if len(self.enemy_tanks) == 0:
            self.create_enemy_tank()

        # 检测子弹与砖块的碰撞
        for bullet in self.player_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.bricks, False)
            if hits:
                for brick in hits:
                    if isinstance(brick, Brick):
                        if brick.hit(bullet.rect.centerx, bullet.rect.centery):
                            bullet.kill()
                            self.sound_manager.play_hit_brick()
                            break
                    elif isinstance(brick, SmallBrick):
                        brick.hit()
                        bullet.kill()
                        self.sound_manager.play_hit_brick()
                        break

        # 对敌人子弹的处理
        for bullet in self.enemy_bullets:
            hits = pygame.sprite.spritecollide(bullet, self.bricks, False)
            if hits:
                for brick in hits:
                    if isinstance(brick, Brick):
                        if brick.hit(bullet.rect.centerx, bullet.rect.centery):
                            bullet.kill()
                            self.sound_manager.play_hit_brick()
                            break
                    elif isinstance(brick, SmallBrick):
                        brick.hit()
                        bullet.kill()
                        self.sound_manager.play_hit_brick()
                        break

        # 检测玩家子弹与敌人坦克的碰撞
        enemy_hit = pygame.sprite.spritecollide(self.enemy_tanks.sprite, self.player_bullets, True) if self.enemy_tanks.sprite else []
        if enemy_hit:
            if self.enemy_tanks.sprite.hit():  # 如果敌人坦克被摧毁
                self.sound_manager.play_tank_explosion()
                print("敌人坦克被消灭！")
                self.create_enemy_tank()  # 立即创建新的敌人坦克
            else:
                self.sound_manager.play_hit_tank()

        # 检测敌人子弹与玩家的碰撞
        player_hit = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if player_hit:
            if self.player.hit():  # 如果玩家坦克被摧毁
                self.game_over = True
                self.sound_manager.play_tank_explosion()
                print("游戏结束！玩家被击中！")
            else:
                self.sound_manager.play_hit_tank()

        # 更新其他精灵（如砖块）
        for sprite in self.all_sprites:
            if not isinstance(sprite, (Tank, EnemyTank, Bullet)):
                sprite.update()

        # 移除已经消失的砖块
        for brick in self.bricks.copy():
            if isinstance(brick, Brick):
                if brick.is_destroyed():
                    self.bricks.remove(brick)
                    self.all_sprites.remove(brick)
            elif isinstance(brick, SmallBrick):
                if not brick.alive():
                    self.bricks.remove(brick)
                    self.all_sprites.remove(brick)

        # 更新玩家坦克的位置
        self.player.rect.x = int(self.player.grid_x * GRID_SIZE)
        self.player.rect.y = int(self.player.grid_y * GRID_SIZE)

        # 更新敌人坦克的位置
        enemy_tank = self.enemy_tanks.sprite
        if enemy_tank:
            enemy_tank.rect.x = int(enemy_tank.grid_x * GRID_SIZE)
            enemy_tank.rect.y = int(enemy_tank.grid_y * GRID_SIZE)

        # 移除不再需要的精灵
        for sprite in list(self.all_sprites):
            if not sprite.alive():
                sprite.kill()  # 从所有精灵组中移除

        # 限制子弹数量
        if len(self.player_bullets) > 5:
            oldest_bullet = min(self.player_bullets, key=lambda b: b.created_time)
            oldest_bullet.kill()

        if len(self.enemy_bullets) > 15:
            oldest_bullet = min(self.enemy_bullets, key=lambda b: b.created_time)
            oldest_bullet.kill()

    def draw_grid(self):
        # 绘制网格线
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, self.grid_color, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, self.grid_color, (0, y), (SCREEN_WIDTH, y))

    def draw(self):
        # 绘制游戏画面
        self.screen.fill(BLACK)
        self.draw_grid()  # 在绘制精灵之前绘制网格
        
        # 绘制所有精灵
        self.all_sprites.draw(self.screen)
        
        if self.game_over:
            # 显示游戏结束画面
            font = pygame.font.Font(None, 74)
            text = font.render('GAME OVER', True, RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
            self.screen.blit(text, text_rect)
            
            restart_font = pygame.font.Font(None, 36)
            restart_text = restart_font.render('Press SPACE to restart', True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
            self.screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()  # 更新整个显示屏
    
    def run(self):
        # 游戏主循环
        try:
            while self.running:
                self.handle_events()
                if not self.game_over:
                    self.handle_keys()
                self.update()
                self.draw()
                self.clock.tick(FPS)  # 控制游戏帧率
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pygame.quit()

    def reset_game(self):
        # 重置游戏状态
        self.game_over = False
        self.all_sprites.empty()
        self.bullets.empty()
        self.enemy_tanks.empty()
        self.player_bullets.empty()
        self.enemy_bullets.empty()
        
        # 重新创建玩家和敌人坦克
        self.player = Tank(14 * GRID_SIZE, 28 * GRID_SIZE, GREEN)
        self.all_sprites.add(self.player)
        self.create_enemy_tank()
        
        # 重新创建地图
        self.create_map()