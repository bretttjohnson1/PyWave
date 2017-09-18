from particle import Particle
import pygame
import numpy
from multiprocessing.dummy import Pool as ThreadPool
from math import cos
from math import sin
from math import pow
from math import sqrt
from random import randint
from random import seed
from time import time
from pygame.locals import DOUBLEBUF
from pygame.locals import OPENGL


from OpenGL.GL import *
from OpenGL.GL import glTranslatef
from OpenGL.GL import glClear

from OpenGL.GL import GL_COLOR_BUFFER_BIT
from OpenGL.GL import GL_DEPTH_BUFFER_BIT
from OpenGL.GLU import gluPerspective

# scale render by factor
renderscale = .1
# number of points in x and y direction
xsize = 50
ysize = 50


spring_const = .001
tension_const = .01
spring_range = 2

# grid that stores points
points_grid = numpy.array([[Particle(j, 0, i) for i in range(ysize)]
                           for j in range(xsize)], dtype=Particle)

time0 = 0
time1 = 0


def time_start():
    global time0
    time0 = time()


def time_stop():
    global time1
    time1 = time()
    print("Time:" + str(1000000*(time1 - time0)))


def compute_physics():
    pool = ThreadPool(4)
    pool.map(calculate_physics, range(spring_range, ysize-spring_range))
    pool.map(tick_physics, range(spring_range, ysize-spring_range))
    pool.close()
    pool.join()


def tick_physics(i):
    for j in range(spring_range, ysize-spring_range):
        points_grid[i][j].tick()


def calculate_physics(i):
    for j in range(spring_range, ysize-spring_range):
        current_particle = points_grid[i][j]

        current_particle.vy -= current_particle.y*spring_const
        current_particle.vx -= (current_particle.x-i)*spring_const
        current_particle.vz -= (current_particle.z-j)*spring_const
        for a in range(i-spring_range, i+spring_range+1):
            for b in range(j-spring_range, j+spring_range+1):
                if(a >= 0 and a < xsize and b >= 0 and b < xsize and a != i and b != j):

                    deltax = points_grid[a][b].x - current_particle.x
                    deltay = points_grid[a][b].y - current_particle.y
                    deltaz = points_grid[a][b].z - current_particle.z
                    dist = sqrt(deltax**2 +
                                deltay**2 +
                                deltaz**2)

                    correct_dist = sqrt((a-i)*(a-i)+(b-j)*(b-j))

                    force = dist - correct_dist

                    precal = tension_const/dist
                    precal_force = force*precal

                    current_particle.vx += deltax*precal_force
                    current_particle.vy += deltay*precal
                    current_particle.vz += deltaz*precal_force


def updaterotation(theta, phi):

    keys_down = pygame.key.get_pressed()

    if keys_down[pygame.K_LEFT]:
        theta = theta + 1

    if keys_down[pygame.K_RIGHT]:
        theta = theta - 1

    if keys_down[pygame.K_UP]:
        phi = phi + 1

    if keys_down[pygame.K_DOWN]:
        phi = phi - 1

    return theta, phi


def updateposition(xpos, ypos, zpos):
    keys_down = pygame.key.get_pressed()

    if keys_down[pygame.K_w]:
        zpos = zpos + .1

    if keys_down[pygame.K_s]:
        zpos = zpos - .1

    if keys_down[pygame.K_a]:
        xpos = xpos + .1

    if keys_down[pygame.K_d]:
        xpos = xpos - .1

    if keys_down[pygame.K_SPACE]:
        ypos = ypos - .1

    if keys_down[pygame.K_c]:
        ypos = ypos + .1

    return xpos, ypos, zpos


def main():
    pygame.init()
    resolution = (1200, 960)
    pygame.display.set_mode(resolution, DOUBLEBUF | OPENGL)

    gluPerspective(45, (resolution[0]/resolution[1]), 0.1, 50.0)
    glTranslatef(0.0, 0.0, -4)
    # glRotatef(10, 1, 0, 0)
    glPolygonMode(GL_FRONT, GL_LINE)
    glPolygonMode(GL_BACK, GL_LINE)

    # rotation values
    phi = 0.0
    theta = 0.0

    # position values
    xpos = 0.0
    ypos = 0.0
    zpos = 0.0

    seed()
    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        if pygame.key.get_pressed()[pygame.K_ESCAPE]:
            pygame.quit()
            quit()

        theta, phi = updaterotation(theta, phi)

        xpos, ypos, zpos = updateposition(xpos, ypos, zpos)

        #print("physics")
        #time_start()
        compute_physics()
        #time_stop()

        if pygame.key.get_pressed()[pygame.K_o]:
            xrand = randint(spring_range+1, xsize-spring_range)
            yrand = randint(spring_range+1, ysize-spring_range)
            for i in range(xrand-1, xrand+2):
                for j in range(yrand-1, yrand+2):
                    points_grid[i][j].vy += 1

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        # translate grid
        glTranslatef(xpos, ypos, zpos)

        # rotate grid
        glRotatef(theta, 0, 1, 0)
        glRotatef(phi, cos(theta/360*6.2831), 0, sin(theta/360*6.283))

        # scale down and translate to center of grid
        glScalef(renderscale, renderscale, renderscale)
        glTranslatef(-xsize/2, 0, -ysize/2)

        for i in range(spring_range, xsize-spring_range-1):
            for j in range(spring_range, ysize-spring_range-1):
                glBegin(GL_QUADS)
                glVertex3f(points_grid[i][j].x, points_grid[i][j].y, points_grid[i][j].z)
                glVertex3f(points_grid[i][j+1].x, points_grid[i][j+1].y, points_grid[i][j+1].z)
                glVertex3f(points_grid[i+1][j+1].x, points_grid[i+1][j+1].y, points_grid[i+1][j+1].z)
                glVertex3f(points_grid[i+1][j].x, points_grid[i+1][j].y, points_grid[i+1][j].z)
                glEnd()
        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)


main()
