# 屏幕设置
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 60

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 通用大小设置
GRID_SIZE = 20  # 每个小格子的大小
UNIT_SIZE = GRID_SIZE * 2  # 坦克和大砖块的统一大小

# 坦克设置
TANK_SPEED = 0.5  # 将速度降低到原来的一半
TANK_SIZE = GRID_SIZE * 2  # 或者根据需要调整这个值

# 子弹设置
BULLET_SPEED = 5  # 你可以根据需要调整这个值
BULLET_SIZE = 4

# 砖块设置
BRICK_SIZE = GRID_SIZE  # 恢复原来的砖块大小
BRICK_COLOR = (255, 128, 0)  # 橙色
BRICK_HEALTH = 1
BRICK_BREAK_TIME = 10

# 地图设置
MAP_ROWS = 30
MAP_COLS = 30

# 音效设置
SOUND_SAMPLE_RATE = 44100
SOUND_DURATION = 0.1  # 音效持续时间（秒）
SHOOT_FREQUENCY = 440  # 发射音效的频率（赫兹）
HIT_FREQUENCY = 220  # 击中音效的频率（赫兹）

# 添加以下两行
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE