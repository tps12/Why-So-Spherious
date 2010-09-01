import random

import pygame
from pygame.locals import *

from Planet import Planet

class Display:

    def main_loop(self):

        planet = Planet(200,1)
        row = random.randint(1, planet.row_count-2)
        planet.rows[row][random.randint(0, planet.row_lengths[row]-1)] = 255

        pygame.init()    

        screen = pygame.display.set_mode((planet.max_row,planet.row_count),
                                         HWSURFACE)
        pygame.display.set_caption('Planet')

        background = pygame.Surface(screen.get_size())
        background.fill((128,128,128))

        limit = pygame.time.Clock()

        done = False

        def in_bounds(x,y):
            return (x > planet.row_offsets[y] and
                    x < planet.row_offsets[y] + planet.row_lengths[y])

        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True

            adjustments = []
            for row in range(planet.row_count):
                for column in range(planet.row_lengths[row]):
                    value = planet.rows[row][column]
                    if value > 10:
                        if column > 1:
                            adjustments.append((row,column-1,value-10))
                        if column < planet.row_lengths[row] - 1:
                            adjustments.append((row,column+1,value-10))

            for (row,column,value) in adjustments:
                planet.rows[row][column] = value

            screen.blit(background, (0,0))
            screen.lock()
            for y in range(0, screen.get_height()):
                for x in range(0, screen.get_width()):
                    if in_bounds(x,y):
                        value = planet.rows[y][x - planet.row_offsets[y]]                                
                        screen.set_at((x,y),(value,value,value))
            screen.unlock()
            
            pygame.display.flip()

            limit.tick(500)

if __name__ == '__main__':
    Display().main_loop()
