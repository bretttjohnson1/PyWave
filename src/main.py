from particle import Particle
import pygame
import threading
from multiprocessing.dummy import Pool as ThreadPool
from math import cos
from math import sin
from math import pow
from math import sqrt
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


spring_const = .01
tension_const = .1
spring_range = 2

# grid that stores points
points_grid = [[Particle(j, 0, i) for i in range(ysize)]
               for j in range(xsize)]


def compute_physics():
    while True:
        pool = ThreadPool(4)
        pool.map(calculate_physics, range(spring_range+1, ysize-spring_range))
        pool.map(tick_physics, range(spring_range+1, ysize-spring_range))
        pool.close()
        pool.join()


def tick_physics(i):
    for j in range(spring_range+1, ysize-spring_range):
        points_grid[i][j].tick()


def calculate_physics(i):
    for j in range(spring_range+1, ysize-spring_range):
        points_grid[i][j].vy -= points_grid[i][j].y*spring_const
        points_grid[i][j].vx -= (points_grid[i][j].x-i)*spring_const
        points_grid[i][j].vz -= (points_grid[i][j].z-j)*spring_const
        for a in range(i-spring_range, i+spring_range+1):
            for b in range(j-spring_range, j+spring_range+1):
                if(a >= 0 and a < xsize and b >= 0 and b < xsize and a != i and b != j):

                    deltax = points_grid[a][b].x - points_grid[i][j].x
                    deltay = points_grid[a][b].y - points_grid[i][j].y
                    deltaz = points_grid[a][b].z - points_grid[i][j].z
                    dist = sqrt(pow(deltax, 2) +
                                pow(deltay, 2) +
                                pow(deltaz, 2))
                    forcex = 0
                    forcey = 0
                    forcez = 0
                    if deltax != 0:
                        forcex = pow(deltax, 2)*abs(deltax)/deltax
                    if deltay != 0:
                        forcey = pow(deltay, 2)*abs(deltay)/deltay
                    if deltaz != 0:
                        forcez = pow(deltaz, 2)*abs(deltaz)/deltaz

                    points_grid[i][j].vx += forcex*tension_const/dist
                    points_grid[i][j].vy += forcey*tension_const/dist
                    points_grid[i][j].vz += forcez*tension_const/dist


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

    compute_thread = threading.Thread(target=compute_physics)
    compute_thread.start()

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

        if pygame.key.get_pressed()[pygame.K_o]:
            for i in range(int(xsize/2)-1, int(xsize/2)+2):
                for j in range(int(ysize/2)-1, int(ysize/2)+2):
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

        for i in range(xsize-1):
            for j in range(ysize-1):
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
