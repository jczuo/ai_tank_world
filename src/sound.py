import pygame
import os

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.muted_sounds = set()  # 用于存储被静音的音效名称

    def load_sounds(self):
        sound_files = {
            'shoot': 'shoot.wav',  # 改回使用 .wav 文件
            'hit_brick': 'hit_brick.wav',
            'hit_tank': 'shoot.wav',  # 暂时使用 shoot.wav 代替
            'tank_explosion': 'hit_brick.wav',  # 暂时使用 hit_brick.wav 代替
            'shot': 'shot.flac'
        }
        for sound_name, file_name in sound_files.items():
            try:
                file_path = os.path.join('assets', 'sounds', file_name)
                self.sounds[sound_name] = pygame.mixer.Sound(file_path)
                print(f"成功加载音效文件：{file_name}")
            except pygame.error as e:
                print(f"警告：无法加载音效文件 '{file_name}'。错误：{str(e)}")
                self.sounds[sound_name] = None

    def play_sound(self, sound_name):
        if sound_name not in self.muted_sounds and self.sounds.get(sound_name):
            self.sounds[sound_name].play()

    def mute_sound(self, sound_name):
        self.muted_sounds.add(sound_name)

    def unmute_sound(self, sound_name):
        self.muted_sounds.discard(sound_name)

    def play_shoot(self):
        self.play_sound('shoot')

    def play_hit_brick(self):
        self.play_sound('hit_brick')

    def play_hit_tank(self):
        self.play_sound('hit_tank')

    def play_tank_explosion(self):
        self.play_sound('tank_explosion')

    def play_shot(self):
        self.play_sound('shot')