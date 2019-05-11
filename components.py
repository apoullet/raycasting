import pygame
import math

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
            dir_x, dir_y = math.cos(rads), math.sin(rads)
            self.rays.append(Ray(self.pos[0], self.pos[1], (dir_x, dir_y)))
            distance = self.rays[-1].cast(grid, cell_size)
            self.rays[-1].end_pos = (self.pos[0]+distance*dir_x, self.pos[1]+distance*dir_y)

    def move(self, direction):
        self.pos[0] += direction[0]
        self.pos[1] += direction[1]

    def show(self, display, colour):
        pygame.draw.circle(display, colour, ((self.pos[0], self.pos[1])), self.radius)

class Ray:
    def __init__(self, start_x, start_y, direction):
        self.start_pos  = [ start_x, start_y ]
        self.direction  = direction
        self.end_pos    = None
        self.intersects = []

    def cast(self, grid, cell_size):
        current_pos = list(self.start_pos)
        self.intersects.clear()

        tan   = 0 if self.direction[0] == 0 else self.direction[1] / self.direction[0]
        cot   = 0 if self.direction[1] == 0  else self.direction[0] / self.direction[1]
        c_tan = self.start_pos[1] - tan * self.start_pos[0]
        c_cot = cot * self.start_pos[1] - self.start_pos[0]


        vertical = horizontal = False

        if self.direction[0] == 0:
            vertical = True
        if self.direction[0] == 1:
            horizontal = True

        while True:
            stick_x = list(current_pos)
            stick_y = list(current_pos)

            remainder_x = current_pos[0] % 20
            remainder_y = current_pos[1] % 20

            if remainder_x == 0:
                stick_x[0] = stick_x[0]+20 if self.direction[0] > 0 else stick_x[0]-20
            else:
                stick_x[0] = stick_x[0]+20-remainder_x if self.direction[0] > 0 else stick_x[0]-remainder_x

            stick_x[1] = tan*stick_x[0]+c_tan

            if remainder_y == 0:
                stick_y[1] = stick_y[1]+20 if self.direction[1] > 0 else stick_y[1]-20
            else:
                stick_y[1] = stick_y[1]+20-remainder_y if self.direction[1] > 0 else stick_y[1]-remainder_y

            stick_y[0] = cot*stick_y[1]-c_cot

            current2x = math.hypot(stick_x[0]-current_pos[0], stick_x[1]-current_pos[1])
            current2y = math.hypot(stick_y[0]-current_pos[0], stick_y[1]-current_pos[1])

            if vertical:
                remainder = current_pos[1] % 20

                if remainder == 0:
                    current_pos[1] = current_pos[1]+20 if self.direction[1] > 0 else current_pos[1]-20
                else:
                    current_pos[1] = current_pos[1]+20-remainder if self.direction[1] > 0 else current_pos[1]-remainder
            elif horizontal:
                remainder = current_pos[0] % 20

                if remainder == 0:
                    current_pos[0] = current_pos[0]+20 if self.direction[0] > 0 else current_pos[0]-20
                else:
                    current_pos[0] = current_pos[0]+20-remainder if self.direction[0] > 0 else current_pos[0]-remainder
            else:
                current_pos = stick_x if current2x < current2y and current2x > 0.5 else stick_y


            self.intersects.append((math.floor(current_pos[0]), math.floor(current_pos[1])))

            if current_pos[0] < 0:
                return math.hypot(self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[0] >= grid[0][-1].x+cell_size:
                return math.hypot(grid[0][-1].x+cell_size-self.start_pos[0], current_pos[1]-self.start_pos[1])
            elif current_pos[1] < 0:
                return math.hypot(current_pos[0]-self.start_pos[0], self.start_pos[1])
            elif current_pos[1] >= grid[-1][0].y+cell_size:
                return math.hypot(current_pos[0]-self.start_pos[0], grid[-1][0].y+cell_size-self.start_pos[1])

            if current_pos[0] % 20 == 0:
                if grid[math.floor(current_pos[1])//cell_size][math.floor(current_pos[0])//cell_size-1].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])
                if grid[math.floor(current_pos[1])//cell_size][math.floor(current_pos[0])//cell_size].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])
            else:
                if grid[math.floor(current_pos[1])//cell_size-1][math.floor(current_pos[0])//cell_size].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])
                if grid[math.floor(current_pos[1])//cell_size][math.floor(current_pos[0])//cell_size].is_wall:
                    return math.hypot(current_pos[0]-self.start_pos[0], current_pos[1]-self.start_pos[1])

    def show(self, display, colour):
        pygame.draw.aaline(display, colour, self.start_pos, self.end_pos)

        # for point in self.intersects:
        #     pygame.draw.circle(display, pygame.Color('#0000FF'), point, 1) 
