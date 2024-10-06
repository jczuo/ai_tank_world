import pygame
from game import Game

def main():
    pygame.init()
    pygame.mixer.init()  # 初始化音频系统
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()