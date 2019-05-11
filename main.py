#!/home/antoine/dev/personal/shenanigans/raycasting/venv/bin/python

import pygame
import json

from components import Cell, Player, Ray

pygame.init()

width, heigth, columns, rows = 400, 400, 20, 20
cell_size = width // columns

display = pygame.display.set_mode((width, heigth))
pygame.display.set_caption('Raycasting')
clock = pygame.time.Clock()

palette = {
        'white': pygame.Color('#FFFFFF'),
        'black': pygame.Color('#000000'),
        'red': pygame.Color('#FF0000'),
        'blue': pygame.Color('#0000FF'),
        'green': pygame.Color('#00FF00'),
}

kill_switch = False

grid = [ [ Cell(x*cell_size, y*cell_size, cell_size) for x in range(columns) ] for y in range(rows) ] 

player = Player(10*cell_size, 10*cell_size, cell_size//2)

with open('map.json', 'r') as f:
    arena = json.load(f)

while not kill_switch:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            kill_switch = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                player.move((0, -1*cell_size))
            if event.key == pygame.K_RIGHT:
                player.move((1*cell_size, 0))
            if event.key == pygame.K_DOWN:
                player.move((0, 1*cell_size))
            if event.key == pygame.K_LEFT:
                player.move((-1*cell_size, 0))

    for wall in arena["walls"]:
        for cell in wall["cells"]:
            grid[cell["row"]][cell["column"]].set_wall(True)

    display.fill(palette['black'])

    player.cast_rays(grid, cell_size)

    # Drawing goes under this comment
    
    # for row in grid:
    #     for cell in row:
    #         cell.show_hollow(display, palette['red'])

    for wall in arena["walls"]:
        for cell in wall["cells"]:
            grid[cell["row"]][cell["column"]].show(display, palette['green'])

    for ray in player.rays:
        ray.show(display, palette['white'])

    player.show(display, palette['white'])

    pygame.display.update()

    clock.tick(60)

pygame.quit()
quit()
