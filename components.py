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

    def cast_rays(self, grid, cell_size):
        self.rays.clear()

        for a in range(0, 361, 5):
            rads = math.radians(a)
            cos, sin = math.cos(rads), math.sin(rads)
            self.rays.append(Ray(self.pos[0], self.pos[1], cos, sin))
            distance = self.rays[-1].cast(grid, cell_size)
            self.rays[-1].end_pos = (self.pos[0]+distance*cos, self.pos[1]+distance*sin)
        
    def move(self, direction):
        self.pos[0] += direction[0]
        self.pos[1] += direction[1]

    def show(self, display, colour):
        pygame.draw.circle(display, colour, ((self.pos[0], self.pos[1])), self.radius)

class Ray:
    def __init__(self, start_x, start_y, cos, sin):
        self.start_pos = [ start_x, start_y ]
        self.cos       = int(cos) if np.allclose(cos, int(cos), atol=1e-05) else cos
        self.sin       = int(sin) if np.allclose(sin, int(sin), atol=1e-05) else sin
        self.end_pos   = None

    def cast(self, grid, cell_size):
        """
        Raycasting algorithm found online at 'https://lodev.org/cgtutor/raycasting.html'
        """
        current_pos = list(self.start_pos)

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
            next_hor = list(current_pos)
            next_ver = list(current_pos)
            
            rem_x = current_pos[0] % 20
            rem_y = current_pos[1] % 20

            if horizontal:
                if rem_x == 0:
                    current_pos[0] = current_pos[0]+20 if self.cos > 0 else current_pos[0]-20
                else:
                    current_pos[0] = current_pos[0]+20-rem_x if self.cos > 0 else current_pos[0]-rem_x
            elif vertical:
                if rem_y == 0:
                    current_pos[1] = current_pos[1]+20 if self.sin > 0 else current_pos[1]-20
                else:
                    current_pos[1] = current_pos[1]+20-rem_y if self.sin > 0 else current_pos[1]-rem_y
            else:
                if rem_x == 0:
                    next_hor[0] = next_hor[0]+20 if self.cos > 0 else next_hor[0]-20
                else:
                    next_hor[0] = next_hor[0]+20-rem_x if self.cos > 0 else next_hor[0]-rem_x

                next_hor[0] = int(next_hor[0]) if abs(round(next_hor[0], 5)-int(round(next_hor[0], 5))) == 0 else next_hor[0]

                next_hor[1] = tan*next_hor[0]+c_tan

                if next_hor[1] < 0:
                    next_hor[1] = 0
                else:
                    next_hor[1] = int(next_hor[1]) if abs(round(next_hor[1], 5)-int(round(next_hor[1], 5))) == 0 else next_hor[1]

                if rem_y == 0:
                    next_ver[1] = next_ver[1]+20 if self.sin > 0 else next_ver[1]-20
                else:
                    next_ver[1] = next_ver[1]+20-rem_y if self.sin > 0 else next_ver[1]-rem_y

                next_ver[1] = int(next_ver[1]) if abs(round(next_ver[1], 5)-int(round(next_ver[1], 5))) == 0 else next_ver[1]

                next_ver[0] = cot*next_ver[1]-c_cot

                if next_ver[0] < 0:
                    next_ver[0] = 0
                else:
                    next_ver[0] = int(next_ver[0]) if abs(round(next_ver[0], 5)-int(round(next_ver[0], 5))) == 0 else next_ver[0]

                dx0, dx1, dy0, dy1     = next_hor[0]-current_pos[0], next_hor[1]-current_pos[1], next_ver[0]-current_pos[0], next_ver[1]-current_pos[1]
                sdx0, sdx1, sdy0, sdy1 = dx0 / abs(dx0) if dx0 != 0 else 0, dx1 / abs(dx1) if dx1 != 0 else 0, dy0 / abs(dy0) if dy0 != 0 else 0, dy1 / abs(dy1) if dy1 != 0 else 0  

                sign_cos = self.cos / abs(self.cos)
                sign_sin = self.sin / abs(self.sin)
                
                if (sdx0 != 0 and sign_cos != sdx0) or (sdx1 != 0 and sign_sin != sdx1): 
                    current_pos = next_ver
                elif (sdy0 != 0 and sign_cos != sdy0) or (sdy1 != 0 and sign_sin != sdy1): 
                    current_pos = next_hor
                else:
                    current2hor = math.hypot(next_hor[0]-current_pos[0], next_hor[1]-current_pos[1])
                    current2ver = math.hypot(next_ver[0]-current_pos[0], next_ver[1]-current_pos[1])

                    current_pos = next_hor if current2hor < current2ver and current2hor > 0.5 else next_ver

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
