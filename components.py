import pygame
import math
import numpy as np

class Cell(pygame.Rect):
    def __init__(self, x, y, len_side, is_wall=False):
        pygame.Rect.__init__(self, x, y, len_side, len_side)
        self.is_wall = is_wall

    def set_wall(self, is_wall):
        self.is_wall = is_wall

    def show_hollow(self, display, colour):
        pygame.draw.rect(display, colour, self, 1)

    def show(self, display, colour):
        pygame.draw.rect(display, colour, self)

class Player:
    def __init__(self, x, y, radius):
        self.pos    = [ x, y ]
        self.radius = radius
        self.rays   = []
        self.collisions =[]

    def cast_rays(self, grid, cell_size):
        self.rays.clear()

        self.collisions.clear()

        for a in range(0, 361, 5):
            rads = math.radians(a)
            cos, sin = math.cos(rads), math.sin(rads)
            self.rays.append(Ray(self.pos[0], self.pos[1], cos, sin))
            distance = self.rays[-1].cast(grid, cell_size)
            self.rays[-1].end_pos = (self.pos[0]+distance*cos, self.pos[1]+distance*sin)
            self.collisions.append((math.floor(self.rays[-1].end_pos[0]), math.floor(self.rays[-1].end_pos[1])))
        
    def move(self, direction):
        self.pos[0] += direction[0]
        self.pos[1] += direction[1]

    def show(self, display, colour):
        pygame.draw.circle(display, colour, ((self.pos[0], self.pos[1])), self.radius)

        # for point in self.collisions:
        #     pygame.draw.circle(display, pygame.Color('#FF0000'), point, 1)


class Ray:
    def __init__(self, start_x, start_y, cos, sin):
        self.start_pos = [ start_x, start_y ]
        self.cos       = int(cos) if np.allclose(cos, int(cos), atol=1e-05) else cos
        self.sin       = int(sin) if np.allclose(sin, int(sin), atol=1e-05) else sin
        self.end_pos   = None
        self.intersects = []

    def cast(self, grid, cell_size):
        """
        Raycasting algorithm found online at 'https://lodev.org/cgtutor/raycasting.html'
        """
        current_pos = list(self.start_pos)
        self.intersects.clear()

        tan   = 0 if self.cos == 0 else self.sin / self.cos
        cot   = 0 if self.sin == 0 else self.cos / self.sin
        c_tan = self.start_pos[1] - tan * self.start_pos[0]
        c_cot = cot * self.start_pos[1] - self.start_pos[0]

        vertical = horizontal = False

        if self.cos == 0:
            vertical = True
        if self.cos == 1 or self.cos == -1:
            horizontal = True

        while True:
            stick_x = list(current_pos)
            stick_y = list(current_pos)

            remainder_x = current_pos[0] % 20
            remainder_y = current_pos[1] % 20

            if remainder_x == 0:
                stick_x[0] = stick_x[0]+20 if self.cos > 0 else stick_x[0]-20
            else:
                stick_x[0] = stick_x[0]+20-remainder_x if self.cos > 0 else stick_x[0]-remainder_x

            stick_x[0] = int(stick_x[0]) if abs(round(stick_x[0], 5)-int(round(stick_x[0], 5))) == 0 else stick_x[0]

            stick_x[1] = tan*stick_x[0]+c_tan

            if stick_x[1] < 0:
                stick_x[1] = 0
            else:
                stick_x[1] = int(stick_x[1]) if abs(round(stick_x[1], 5)-int(round(stick_x[1], 5))) == 0 else stick_x[1]


            if remainder_y == 0:
                stick_y[1] = stick_y[1]+20 if self.sin > 0 else stick_y[1]-20
            else:
                stick_y[1] = stick_y[1]+20-remainder_y if self.sin > 0 else stick_y[1]-remainder_y

            stick_y[1] = int(stick_y[1]) if abs(round(stick_y[1], 5)-int(round(stick_y[1], 5))) == 0 else stick_y[1]

            stick_y[0] = cot*stick_y[1]-c_cot 

            if stick_y[0] < 0:
                stick_y[0] = 0
            else:
                stick_y[0] = int(stick_y[0]) if abs(round(stick_y[0], 5)-int(round(stick_y[0], 5))) == 0 else stick_y[0]

            sign_sin = self.sin / abs(self.sin) if self.sin != 0 else 0
            sign_cos = self.cos / abs(self.cos) if self.cos != 0 else 0

            dx0, dx1, dy0, dy1     = stick_x[0]-current_pos[0], stick_x[1]-current_pos[1], stick_y[0]-current_pos[0], stick_y[1]-current_pos[1]
            sdx0, sdx1, sdy0, sdy1 = dx0 / abs(dx0) if dx0 != 0 else 0, dx1 / abs(dx1) if dx1 != 0 else 0, dy0 / abs(dy0) if dy0 != 0 else 0, dy1 / abs(dy1) if dy1 != 0 else 0  

            if vertical:
                remainder = current_pos[1] % 20

                if remainder == 0:
                    current_pos[1] = current_pos[1]+20 if self.sin > 0 else current_pos[1]-20
                else:
                    current_pos[1] = current_pos[1]+20-remainder if self.sin > 0 else current_pos[1]-remainder
            elif horizontal:
                remainder = current_pos[0] % 20

                if remainder == 0:
                    current_pos[0] = current_pos[0]+20 if self.cos > 0 else current_pos[0]-20
                else:
                    current_pos[0] = current_pos[0]+20-remainder if self.cos > 0 else current_pos[0]-remainder
            elif (sign_cos != 0 and sdx0 != 0 and sign_cos != sdx0) or (sign_sin != 0 and sdx1 != 0 and sign_sin != sdx1): 
                current_pos = stick_y
            elif (sign_cos != 0 and sdy0 != 0 and sign_cos != sdy0) or (sign_sin != 0 and sdy1 != 0 and sign_sin != sdy1): 
                current_pos = stick_x
            else:
                current2x = math.hypot(stick_x[0]-current_pos[0], stick_x[1]-current_pos[1])
                current2y = math.hypot(stick_y[0]-current_pos[0], stick_y[1]-current_pos[1])

                current_pos = stick_x if current2x < current2y and current2x > 1 else stick_y

            if current_pos[0] < 0:
                return math.hypot(self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[0] >= grid[0][-1].x+cell_size:
                return math.hypot(grid[0][-1].x+cell_size-self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[1] < 0:
                return math.hypot(current_pos[0]-self.start_pos[0], self.start_pos[1])
            elif current_pos[1] >= grid[-1][0].y+cell_size:
                return math.hypot(current_pos[0]-self.start_pos[0], grid[-1][0].y+cell_size-self.start_pos[1])
            
            column, row = math.floor(current_pos[0]/cell_size), math.floor(current_pos[1]/cell_size)

            if current_pos[0] % 20 == 0 and current_pos[1] % 20 == 0:
                if grid[row][column].is_wall or grid[row][column-1].is_wall or grid[row-1][column].is_wall or grid[row-1][column-1].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[0] % 20 == 0:
                if grid[row][column].is_wall or grid[row][column-1].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[1] % 20 == 0:
                if grid[row][column].is_wall or grid[row-1][column].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])

    def show(self, display, colour):
        pygame.draw.aaline(display, colour, self.start_pos, self.end_pos)

        for point in self.intersects:
            pygame.draw.circle(display, pygame.Color('#0000FF'), point, 1)
