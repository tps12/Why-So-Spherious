import random

import pygame
from pygame.locals import *

from Planet import Planet

class Display:

    def main_loop(self):

        planet = Planet(200,1,(0,True))
        row = random.randint(1, planet.row_count-2)
        planet.rows[row][random.randint(0,
                                        planet.row_lengths[row]-1)] = (255,True)

        pygame.init()    

        screen = pygame.display.set_mode((planet.max_row,planet.row_count),
                                         HWSURFACE)
        pygame.display.set_caption('Planet')

        screen.fill((128,128,128))

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
                    (value,dirty) = planet.rows[row][column]
                    if value > 10:
                        for (r,c) in planet.adjacent(row,column):
                            adjustments.append((r,c,value-10))

            for (row,column,value) in adjustments:
                planet.rows[row][column] = (value,True)

            screen.lock()
            for y in range(0, screen.get_height()):
                for x in range(0, screen.get_width()):
                    if in_bounds(x,y):
                        (value,dirty) = planet.rows[y][x - planet.row_offsets[y]]
                        if dirty:
                            screen.set_at((x,y),(value,value,value))
                            planet.rows[y][x - planet.row_offsets[y]] = (value,False)
            screen.unlock()
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
