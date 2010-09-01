import pygame
from pygame.locals import *

from Planet import Planet

class Display:

    def main_loop(self):

        planet = Planet(200,1)

        pygame.init()    

        screen = pygame.display.set_mode((planet.max_row,planet.row_count),
                                         HWSURFACE)
        pygame.display.set_caption('Planet')

        background = pygame.Surface(screen.get_size())
        background.fill((128,128,128))

        limit = pygame.time.Clock()

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True

            screen.blit(background, (0,0))
            for y in range(0, screen.get_height()):
                for x in range(0, screen.get_width()):
                    if (x > planet.row_offsets[y] and
                        x <= planet.row_offsets[y] + planet.row_lengths[y]):
                        screen.set_at((x,y),(0,0,0))
            
            pygame.display.flip()

            limit.tick(500)

if __name__ == '__main__':
    Display().main_loop()
