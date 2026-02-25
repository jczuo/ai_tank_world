import pygame
import random
from constants import *
from tank import Tank, EnemyTank
from bullet import Bullet
from terrain import create_terrain, Forest, Base, Water, Ice, BrickWall, SteelWall
from powerup import PowerUp
from effects import Explosion, SpawnEffect, ShieldEffect
from level import get_level, get_enemy_list, LEVELS
from hud import HUD
from sound import SoundManager


class Game:

    # 游戏状态
    STATE_MENU = "menu"
    STATE_PLAYING = "playing"
    STATE_LEVEL_TRANSITION = "level_transition"
    STATE_PAUSED = "paused"
    STATE_GAME_OVER = "game_over"
    STATE_VICTORY = "victory"

    def __init__(self):
        pygame.init()
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
        except Exception:
            pass

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("坦克大战 - Tank Battle")
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        self.sound = SoundManager()
        self.sound.load_sounds()

        self.state = self.STATE_MENU
        self.running = True
        self.score = 0
        self.lives = PLAYER_LIVES
        self.current_level = 0
        self.transition_start = 0

        self._init_groups()

    def _init_groups(self):
        self.terrain_solid = pygame.sprite.Group()    # 坦克不可通行的地形
        self.terrain_overlay = pygame.sprite.Group()   # 草丛（绘制在坦克上层）
        self.terrain_under = pygame.sprite.Group()     # 水面/冰面（绘制在坦克下层）
        self.all_terrain = pygame.sprite.Group()

        self.player_group = pygame.sprite.GroupSingle()
        self.enemy_group = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        self.base_group = pygame.sprite.GroupSingle()

        self.player = None
        self.enemy_queue = []
        self.next_spawn_time = 0
        self.spawn_point_index = 0
        self.freeze_end_time = 0

    def _clear_groups(self):
        for g in [self.terrain_solid, self.terrain_overlay, self.terrain_under,
                   self.all_terrain, self.player_group, self.enemy_group,
                   self.player_bullets, self.enemy_bullets, self.effects,
                   self.powerups, self.base_group]:
            g.empty()

    def start_level(self, level_idx):
        self._clear_groups()
        self.current_level = level_idx
        level_data = get_level(level_idx)
        self._build_map(level_data["layout"])
        self.enemy_queue = get_enemy_list(level_data)
        self.next_spawn_time = pygame.time.get_ticks() + 2000
        self.spawn_point_index = 0
        self.freeze_end_time = 0

        # 创建玩家
        px, py = PLAYER_SPAWN
        self.player = Tank(px, py)
        self.player_group.add(self.player)

        # 初始护盾
        self.player.shielded = True
        shield = ShieldEffect(self.player)
        shield.duration = 3000
        shield.start_time = pygame.time.get_ticks()
        self.effects.add(shield)

    def _build_map(self, layout):
        base_placed = False
        for row, line in enumerate(layout):
            col = 0
            while col < len(line):
                ch = line[col]
                if ch == 'E':
                    if not base_placed:
                        base = Base(col, row)
                        self.base_group.add(base)
                        self.terrain_solid.add(base)
                        self.all_terrain.add(base)
                        base_placed = True
                    col += 1
                    continue
                if ch == '0':
                    col += 1
                    continue

                t = create_terrain(col, row, ch)
                if t is None:
                    col += 1
                    continue

                self.all_terrain.add(t)
                if isinstance(t, Forest):
                    self.terrain_overlay.add(t)
                elif isinstance(t, (Water, Ice)):
                    self.terrain_under.add(t)
                    if isinstance(t, Water):
                        self.terrain_solid.add(t)
                else:
                    self.terrain_solid.add(t)
                col += 1

    def _spawn_enemy(self):
        if not self.enemy_queue:
            return
        if len(self.enemy_group) >= MAX_ACTIVE_ENEMIES:
            return
        now = pygame.time.get_ticks()
        if now < self.next_spawn_time:
            return

        etype = self.enemy_queue[0]
        sp = ENEMY_SPAWN_POINTS[self.spawn_point_index % len(ENEMY_SPAWN_POINTS)]
        self.spawn_point_index += 1

        # 检查出生点是否被占据
        spawn_rect = pygame.Rect(sp[0] * GRID_SIZE, sp[1] * GRID_SIZE,
                                  TANK_SIZE, TANK_SIZE)
        blocked = False
        for tank in self.enemy_group:
            if tank.rect.colliderect(spawn_rect):
                blocked = True
                break
        if self.player and self.player.rect.colliderect(spawn_rect):
            blocked = True

        if blocked:
            self.next_spawn_time = now + 500
            return

        self.enemy_queue.pop(0)
        self.next_spawn_time = now + ENEMY_SPAWN_DELAY

        def do_spawn(gx, gy, et):
            enemy = EnemyTank(gx, gy, et)
            self.enemy_group.add(enemy)

        effect = SpawnEffect(sp[0] * GRID_SIZE, sp[1] * GRID_SIZE,
                             do_spawn, (sp[0], sp[1], etype))
        self.effects.add(effect)

    def _spawn_powerup(self):
        """随机在空地生成道具"""
        ptypes = list(PowerUp.TYPES.keys())
        ptype = random.choice(ptypes)
        for _ in range(50):
            gx = random.randint(2, GAME_COLS - 4)
            gy = random.randint(2, GAME_ROWS - 4)
            test_rect = pygame.Rect(gx * GRID_SIZE, gy * GRID_SIZE,
                                     POWERUP_SIZE, POWERUP_SIZE)
            if any(t.rect.colliderect(test_rect) for t in self.terrain_solid):
                continue
            pu = PowerUp(gx, gy, ptype)
            self.powerups.add(pu)
            return

    # ==================== 事件处理 ====================

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if self.state == self.STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        self._start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state == self.STATE_PLAYING:
                    if event.key == pygame.K_SPACE:
                        self._player_shoot()
                    elif event.key == pygame.K_p:
                        self.state = self.STATE_PAUSED
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state == self.STATE_PAUSED:
                    if event.key in (pygame.K_p, pygame.K_SPACE):
                        self.state = self.STATE_PLAYING
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
                    if event.key == pygame.K_SPACE:
                        self._start_new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

    def _start_new_game(self):
        self.score = 0
        self.lives = PLAYER_LIVES
        self.current_level = 0
        self._begin_level_transition()

    def _begin_level_transition(self):
        self.state = self.STATE_LEVEL_TRANSITION
        self.transition_start = pygame.time.get_ticks()

    def _player_shoot(self):
        if not self.player or not self.player.alive():
            return
        if len(self.player_bullets) >= self.player.active_bullet_limit():
            return
        bullet = self.player.fire()
        if bullet:
            self.player_bullets.add(bullet)
            self.sound.play_shoot()

    # ==================== 更新逻辑 ====================

    def update(self):
        if self.state == self.STATE_MENU:
            return

        if self.state == self.STATE_LEVEL_TRANSITION:
            now = pygame.time.get_ticks()
            if now - self.transition_start > 2000:
                self.start_level(self.current_level)
                self.state = self.STATE_PLAYING
            return

        if self.state == self.STATE_PAUSED:
            return

        if self.state in (self.STATE_GAME_OVER, self.STATE_VICTORY):
            return

        # ---- STATE_PLAYING ----
        self._spawn_enemy()

        # 玩家移动
        if self.player and self.player.alive():
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
                all_tanks = pygame.sprite.Group()
                all_tanks.add(*self.enemy_group)
                self.player.move(dx, dy, self.terrain_solid, all_tanks)

        # 冰面滑行处理
        if self.player and self.player.alive() and self.player.is_on_ice(self.terrain_under):
            pass  # 视觉效果预留

        # 敌方 AI
        now = pygame.time.get_ticks()
        frozen = now < self.freeze_end_time
        for enemy in self.enemy_group:
            enemy.frozen = frozen
            if self.player and self.player.alive():
                all_tanks = pygame.sprite.Group()
                all_tanks.add(self.player)
                all_tanks.add(*[e for e in self.enemy_group if e is not enemy])
                bullet = enemy.ai_update(self.terrain_solid, all_tanks, self.player)
                if bullet:
                    self.enemy_bullets.add(bullet)
                    self.sound.play_shoot()

        # 更新子弹
        self.player_bullets.update()
        self.enemy_bullets.update()

        # 碰撞检测
        self._check_bullet_terrain_collision(self.player_bullets)
        self._check_bullet_terrain_collision(self.enemy_bullets)
        self._check_player_bullet_vs_enemies()
        self._check_enemy_bullet_vs_player()
        self._check_bullet_vs_base()
        self._check_bullet_vs_bullet()
        self._check_powerup_pickup()

        # 更新特效和道具
        self.effects.update()
        self.powerups.update()

        # 更新水面动画
        for t in self.terrain_under:
            if isinstance(t, Water):
                t.update()

        # 检查关卡完成
        if not self.enemy_queue and len(self.enemy_group) == 0:
            if self.current_level >= len(LEVELS) - 1:
                self.state = self.STATE_VICTORY
            else:
                self.current_level += 1
                self._begin_level_transition()

    def _check_bullet_terrain_collision(self, bullet_group):
        for bullet in list(bullet_group):
            if not bullet.alive():
                continue
            for t in list(self.all_terrain):
                if not t.alive():
                    continue
                if t.rect.colliderect(bullet.rect):
                    if isinstance(t, Forest):
                        continue
                    if isinstance(t, (Water, Ice)):
                        continue
                    if isinstance(t, Base):
                        if t.hit(bullet.damage, bullet.can_break_steel):
                            self.sound.play_tank_explosion()
                            self.effects.add(Explosion(t.rect.centerx, t.rect.centery, "big"))
                            self.state = self.STATE_GAME_OVER
                        bullet.kill()
                        return
                    hit_result = t.hit(bullet.damage, bullet.can_break_steel)
                    if hit_result:
                        bullet.kill()
                        self.sound.play_hit_brick()
                        if not t.alive():
                            self.effects.add(Explosion(t.rect.centerx, t.rect.centery, "small"))
                        break

    def _check_player_bullet_vs_enemies(self):
        for bullet in list(self.player_bullets):
            if not bullet.alive():
                continue
            for enemy in list(self.enemy_group):
                if not enemy.alive():
                    continue
                if bullet.rect.colliderect(enemy.rect):
                    bullet.kill()
                    destroyed = enemy.hit(bullet.damage)
                    if destroyed:
                        self.score += enemy.score_value
                        self.sound.play_tank_explosion()
                        self.effects.add(Explosion(enemy.rect.centerx, enemy.rect.centery, "big"))
                        if random.random() < 0.3:
                            self._spawn_powerup()
                    else:
                        self.sound.play_hit_tank()
                    break

    def _check_enemy_bullet_vs_player(self):
        if not self.player or not self.player.alive():
            return
        for bullet in list(self.enemy_bullets):
            if not bullet.alive():
                continue
            if bullet.rect.colliderect(self.player.rect):
                bullet.kill()
                destroyed = self.player.hit(bullet.damage)
                if destroyed:
                    self.sound.play_tank_explosion()
                    self.effects.add(Explosion(self.player.rect.centerx,
                                               self.player.rect.centery, "big"))
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = self.STATE_GAME_OVER
                    else:
                        self._respawn_player()
                else:
                    self.sound.play_hit_tank()
                break

    def _check_bullet_vs_base(self):
        base = self.base_group.sprite
        if not base or base.destroyed:
            return
        for bullet in list(self.player_bullets):
            if bullet.rect.colliderect(base.rect):
                bullet.kill()
                break
        for bullet in list(self.enemy_bullets):
            if bullet.rect.colliderect(base.rect):
                bullet.kill()
                base.hit(bullet.damage)
                self.sound.play_tank_explosion()
                self.effects.add(Explosion(base.rect.centerx, base.rect.centery, "big"))
                self.state = self.STATE_GAME_OVER
                break

    def _check_bullet_vs_bullet(self):
        for pb in list(self.player_bullets):
            for eb in list(self.enemy_bullets):
                if pb.alive() and eb.alive() and pb.rect.colliderect(eb.rect):
                    pb.kill()
                    eb.kill()

    def _check_powerup_pickup(self):
        if not self.player or not self.player.alive():
            return
        for pu in list(self.powerups):
            if self.player.rect.colliderect(pu.rect):
                self._apply_powerup(pu.powerup_type)
                self.score += SCORE_POWERUP
                pu.kill()
                self.sound.play_powerup()

    def _apply_powerup(self, ptype):
        if ptype == "star":
            self.player.apply_star()
        elif ptype == "shield":
            self.player.shielded = True
            shield = ShieldEffect(self.player)
            self.effects.add(shield)
        elif ptype == "life":
            self.lives += 1
            self.player.health = self.player.max_health
        elif ptype == "bomb":
            for enemy in list(self.enemy_group):
                self.score += enemy.score_value
                self.effects.add(Explosion(enemy.rect.centerx, enemy.rect.centery, "big"))
                enemy.kill()
            self.sound.play_tank_explosion()
        elif ptype == "timer":
            self.freeze_end_time = pygame.time.get_ticks() + FREEZE_DURATION

    def _respawn_player(self):
        px, py = PLAYER_SPAWN
        self.player = Tank(px, py)
        self.player_group.add(self.player)
        self.player.shielded = True
        shield = ShieldEffect(self.player)
        shield.duration = 3000
        shield.start_time = pygame.time.get_ticks()
        self.effects.add(shield)

    # ==================== 绘制 ====================

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == self.STATE_MENU:
            self.hud.draw_menu(self.screen)
            pygame.display.flip()
            return

        # 绘制游戏区域背景
        game_area = pygame.Rect(0, 0, GAME_WIDTH, GAME_HEIGHT)
        pygame.draw.rect(self.screen, (15, 15, 15), game_area)

        # 网格
        grid_color = (28, 28, 28)
        for x in range(0, GAME_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, GAME_HEIGHT))
        for y in range(0, GAME_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, grid_color, (0, y), (GAME_WIDTH, y))

        # 底层地形 (水面、冰面)
        self.terrain_under.draw(self.screen)

        # 实心地形 (砖墙、钢墙)
        for t in self.terrain_solid:
            if t.alive():
                self.screen.blit(t.image, t.rect)

        # 基地
        base = self.base_group.sprite
        if base:
            self.screen.blit(base.image, base.rect)

        # 道具
        self.powerups.draw(self.screen)

        # 坦克
        if self.player and self.player.alive():
            self.screen.blit(self.player.image, self.player.rect)
        for enemy in self.enemy_group:
            self.screen.blit(enemy.image, enemy.rect)

        # 子弹
        self.player_bullets.draw(self.screen)
        self.enemy_bullets.draw(self.screen)

        # 顶层地形 (草丛遮挡)
        self.terrain_overlay.draw(self.screen)

        # 特效
        self.effects.draw(self.screen)

        # HUD
        gs = self._build_game_state()
        self.hud.draw(self.screen, gs)

        # 覆盖层
        if self.state == self.STATE_LEVEL_TRANSITION:
            level_data = get_level(self.current_level)
            self.hud.draw_level_transition(
                self.screen, self.current_level + 1, level_data["name"])
        elif self.state == self.STATE_GAME_OVER:
            self.hud.draw_game_over(self.screen, self.score)
        elif self.state == self.STATE_VICTORY:
            self.hud.draw_victory(self.screen, self.score)
        elif self.state == self.STATE_PAUSED:
            self.hud.draw_pause(self.screen)

        pygame.display.flip()

    def _build_game_state(self):
        queue_types = {}
        for et in self.enemy_queue:
            queue_types[et] = queue_types.get(et, 0) + 1
        return {
            "level": self.current_level + 1,
            "level_name": get_level(self.current_level)["name"] if self.state != self.STATE_MENU else "",
            "lives": self.lives,
            "health": self.player.health if self.player and self.player.alive() else 0,
            "max_health": PLAYER_HEALTH,
            "star_level": self.player.star_level if self.player else 0,
            "score": self.score,
            "enemies_remaining": len(self.enemy_queue) + len(self.enemy_group),
            "enemies_active": len(self.enemy_group),
            "enemy_queue_types": queue_types,
        }

    # ==================== 主循环 ====================

    def run(self):
        try:
            while self.running:
                self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            pygame.quit()
