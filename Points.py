import random

import pygame
from pygame.locals import *

from Planet import Planet

class Display:

    def main_loop(self):

        planet = Planet(100,1,0)

        pygame.init()    

        screen = pygame.display.set_mode((planet.max_row,planet.row_count),
                                         HWSURFACE)
        pygame.display.set_caption('Planet')

        screen.fill((128,128,128))

        def in_bounds(x,y):
            return (x > planet.row_offsets[y] and
                    x < planet.row_offsets[y] + planet.row_lengths[y])

        screen.lock()
        for y in range(0, screen.get_height()):
            for x in range(0, screen.get_width()):
                if in_bounds(x,y):
                    value = planet.rows[y][x - planet.row_offsets[y]]
                    screen.set_at((x,y),(value,value,value))
        screen.unlock()

        points = pygame.sprite.Group()

        for n in range(10):
            point = pygame.sprite.Sprite()
            point.image = pygame.Surface((10,10))
            pygame.draw.circle(point.image, (255,0,0), (5,5), 5)
            row = random.randint(1, planet.row_count-1)
            column = random.randint(0, planet.row_lengths[row]-1)
            point.rect = pygame.Rect(
                (column + planet.row_offsets[row] - point.image.get_width()/2,
                 row - point.image.get_height()/2),
                point.image.get_size())
            points.add(point)

        limit = pygame.time.Clock()

        done = False

        while not done:
            for event in pygame.event.get():
                if event.type == QUIT:
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        done = True
                        
            for point in points:
                row = point.rect.top + point.image.get_height()/2
                column = point.rect.left - planet.row_offsets[row] + point.image.get_width()/2
                adjacent = [a for a in planet.adjacent(row, column)]
                i = random.randint(0, len(adjacent))-1
                if i >= 0:
                    nrow, ncolumn = adjacent[i]
                    point.rect.left = ncolumn + planet.row_offsets[nrow] - point.image.get_width()/2
                    point.rect.top = nrow - point.image.get_height()/2

            points.draw(screen)
            
            pygame.display.flip()

            limit.tick()

if __name__ == '__main__':
    Display().main_loop()
