import pygame
import os


class SoundManager:

    def __init__(self):
        self.sounds = {}
        self.muted = False

    def load_sounds(self):
        sound_files = {
            'shoot': 'shoot.wav',
            'hit_brick': 'hit_brick.wav',
            'hit_tank': 'shoot.wav',
            'tank_explosion': 'hit_brick.wav',
            'powerup': 'shoot.wav',
            'life': 'hit_brick.wav',
        }
        for name, filename in sound_files.items():
            try:
                path = os.path.join('assets', 'sounds', filename)
                self.sounds[name] = pygame.mixer.Sound(path)
                self.sounds[name].set_volume(0.4)
            except pygame.error:
                self.sounds[name] = None

    def play(self, name):
        if not self.muted and self.sounds.get(name):
            self.sounds[name].play()

    def play_shoot(self):
        self.play('shoot')

    def play_hit_brick(self):
        self.play('hit_brick')

    def play_hit_tank(self):
        self.play('hit_tank')

    def play_tank_explosion(self):
        self.play('tank_explosion')

    def play_powerup(self):
        self.play('powerup')

    def play_life(self):
        self.play('life')
