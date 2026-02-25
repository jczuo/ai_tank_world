# ==================== 屏幕与网格 ====================
GRID_SIZE = 20
GAME_COLS = 30
GAME_ROWS = 30
GAME_WIDTH = GAME_COLS * GRID_SIZE   # 600
GAME_HEIGHT = GAME_ROWS * GRID_SIZE  # 600
SIDEBAR_WIDTH = 180
SCREEN_WIDTH = GAME_WIDTH + SIDEBAR_WIDTH  # 780
SCREEN_HEIGHT = GAME_HEIGHT                # 600
FPS = 60

# 向后兼容
GRID_WIDTH = GAME_COLS
GRID_HEIGHT = GAME_ROWS

# ==================== 颜色 ====================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

GREEN = (76, 175, 80)
DARK_GREEN = (46, 125, 50)
RED = (244, 67, 54)
DARK_RED = (183, 28, 28)
BLUE = (33, 150, 243)
DARK_BLUE = (21, 101, 192)
YELLOW = (255, 235, 59)
ORANGE = (255, 152, 0)
CYAN = (0, 188, 212)
PURPLE = (156, 39, 176)
BROWN = (121, 85, 72)
DARK_BROWN = (78, 52, 46)

# 地形颜色
BRICK_COLOR = (181, 101, 29)
BRICK_LINE_COLOR = (110, 60, 15)
STEEL_COLOR = (189, 189, 189)
STEEL_SHINE = (224, 224, 224)
STEEL_SHADOW = (117, 117, 117)
WATER_COLOR_1 = (30, 136, 229)
WATER_COLOR_2 = (21, 101, 192)
FOREST_COLOR = (56, 142, 60)
FOREST_DARK = (27, 94, 32)
ICE_COLOR = (179, 229, 252)
ICE_SHINE = (227, 242, 253)

# 基地颜色
BASE_COLOR = (255, 215, 0)
BASE_BORDER = (183, 149, 11)

# HUD 颜色
HUD_BG = (30, 30, 30)
HUD_TEXT = (220, 220, 220)
HUD_ACCENT = (255, 193, 7)

# ==================== 坦克配置 ====================
TANK_SIZE = GRID_SIZE * 2  # 40x40
MOVE_COOLDOWN_BASE = 150   # 移动冷却基准(ms)，实际=BASE/speed

# 玩家坦克
PLAYER_HEALTH = 3
PLAYER_LIVES = 3
PLAYER_SPEED = 1.0           # 移动冷却 = 150ms → 约6.7格/秒
PLAYER_FIRE_COOLDOWN = 300   # 毫秒
PLAYER_BULLET_SPEED = 6
PLAYER_BULLET_DAMAGE = 1

# 坦克升级 (星星道具)
PLAYER_UPGRADES = {
    0: {"bullet_speed": 6,  "max_bullets": 1, "bullet_damage": 1, "can_break_steel": False},
    1: {"bullet_speed": 8,  "max_bullets": 1, "bullet_damage": 1, "can_break_steel": False},
    2: {"bullet_speed": 8,  "max_bullets": 2, "bullet_damage": 1, "can_break_steel": False},
    3: {"bullet_speed": 10, "max_bullets": 2, "bullet_damage": 2, "can_break_steel": True},
}

# 敌方坦克类型配置
ENEMY_TYPES = {
    "basic": {
        "health": 1,
        "speed": 0.5,            # 冷却300ms → 约3.3格/秒，较慢
        "fire_cooldown": 2500,
        "bullet_speed": 4,
        "bullet_damage": 1,
        "score": 100,
        "color": GRAY,
        "color_dark": DARK_GRAY,
        "name": "普通坦克",
    },
    "fast": {
        "health": 1,
        "speed": 0.85,           # 冷却176ms → 约5.7格/秒，接近玩家
        "fire_cooldown": 1800,
        "bullet_speed": 5,
        "bullet_damage": 1,
        "score": 200,
        "color": CYAN,
        "color_dark": (0, 131, 143),
        "name": "快速坦克",
    },
    "power": {
        "health": 2,
        "speed": 0.45,           # 冷却333ms → 约3格/秒
        "fire_cooldown": 1200,
        "bullet_speed": 7,
        "bullet_damage": 2,
        "score": 300,
        "color": PURPLE,
        "color_dark": (106, 27, 154),
        "name": "强力坦克",
    },
    "armor": {
        "health": 4,
        "speed": 0.35,           # 冷却428ms → 约2.3格/秒，很慢但很硬
        "fire_cooldown": 2000,
        "bullet_speed": 5,
        "bullet_damage": 1,
        "score": 400,
        "color": YELLOW,
        "color_dark": (245, 127, 23),
        "name": "装甲坦克",
    },
}

# 装甲坦克 HP 对应颜色
ARMOR_HP_COLORS = {
    4: (76, 175, 80),    # 绿色 (满血)
    3: (255, 235, 59),   # 黄色
    2: (255, 152, 0),    # 橙色
    1: (244, 67, 54),    # 红色
}

# ==================== 子弹 ====================
BULLET_SIZE = 6

# ==================== 地形 ====================
BRICK_HEALTH = 2
TERRAIN_EMPTY = '0'
TERRAIN_BRICK = '1'
TERRAIN_STEEL = '2'
TERRAIN_WATER = '3'
TERRAIN_FOREST = '4'
TERRAIN_ICE = '5'
TERRAIN_BASE = 'E'

# ==================== 道具 ====================
POWERUP_SIZE = GRID_SIZE * 2  # 40x40
POWERUP_DURATION = 8000       # 道具在地图上持续毫秒
POWERUP_BLINK_START = 5000    # 开始闪烁的时间

# 道具效果持续时间
SHIELD_DURATION = 10000       # 护盾 10 秒
FREEZE_DURATION = 8000        # 冰冻 8 秒

# ==================== 关卡 ====================
ENEMY_SPAWN_DELAY = 3000      # 敌方坦克出生间隔
MAX_ACTIVE_ENEMIES = 4        # 同时在场最大敌人数

# 敌方出生点 (grid坐标)
ENEMY_SPAWN_POINTS = [
    (0, 0),
    (14, 0),
    (28, 0),
]

# 玩家出生点
PLAYER_SPAWN = (8, 28)

# 基地位置 (左上角grid坐标, 占2x2)
BASE_POS = (14, 27)

# ==================== 特效 ====================
EXPLOSION_DURATION = 400      # 爆炸持续毫秒
SPAWN_ANIM_DURATION = 1500    # 出生动画持续毫秒

# ==================== 分数 ====================
SCORE_POWERUP = 500
