
import car
import os
import pygame
from pygame.locals import *
import math
import pdb
pygame.init()


class carGame:
    def __init__(self, resolution):
        self.resolution = resolution
        self.screen = pygame.display.set_mode(resolution)
        self.screen.fill((0, 192, 0))
        self.running = True
        self.track = pygame.image.load('track.png')
        self.visible_track = pygame.image.load('track_textured.png')
        self.trap = pygame.Rect(844, 1324, 140, 200)
        self.clr_outside_trk = self.track.get_at((0, 0))
        self.lap = 0
        self.frames = 0

        print("init done")

    def track_setup(self):

        self.red_car = car.Car()
        self.red_car.load_car_sprite('red', 360)
        self.red_car.draw_car(self.red_car.xs, self.red_car.ys, self.screen)

    def game_setup(self):
        self.max_laps = 10
        #car.max_laps = self.max_laps
        self.clock = pygame.time.Clock()

    def user_control(self,car):
        key = pygame.key.get_pressed()
        if car.gear > 0:
            if key[K_d]:
                car.view = (car.view+2) % 360
            elif key[K_a]:
                car.view = (car.view+358) % 360
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == KEYDOWN:
                print("Current gear: ", car.gear)

                if event.key == K_ESCAPE:
                    self.running = False

                elif event.key == K_UP:

                    if car.gear_lock > 24:
                        car.gear += 1
                        print(car.gear)
                        car.gear_lock = 0
                        if car.gear > 4:
                            car.gear = 4
                elif event.key == K_DOWN:

                    car.gear -= 1
                    if car.gear < 0:
                        car.gear = 0
    def collision(self, car):
        surface_under_car = self.track.get_at((car.xc, car.yc))
        if(surface_under_car == self.clr_outside_trk):
            print("outside track")
        else:
            print("inside")

    def game_loop(self):
        while self.running:
            car = self.red_car
            
            self.frames += 1
            car.update()
            self.clock.tick(24)
            self.screen.fill((0, 192, 0))
            self.screen.blit(self.visible_track,
                             (car.xs-car.xc, car.ys-car.yc))
            car.draw_car(self.red_car.xs, self.red_car.ys, self.screen)

            pygame.display.flip()
            self.user_control(car)
            self.collision(car)

            


game = carGame((1224, 720))
game.track_setup()
game.game_setup()

game.game_loop()
