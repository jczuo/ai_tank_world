import pygame
from game import Game


def main():
    pygame.init()
    try:
        pygame.mixer.init()
    except Exception:
        pass

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
