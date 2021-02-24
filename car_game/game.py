
import car
import os
import pygame
from pygame.locals import *
import math
import pdb
import time
import copy
import numpy as np
pygame.init()


class CarGame:
    def __init__(self, resolution):
        self.resolution = resolution
        self.screen = pygame.display.set_mode(resolution)
        self.screen.fill((0, 192, 0))
        self.running = True
        self.track = pygame.image.load('track.png')
        self.visible_track = pygame.image.load('track_textured.png')
        self.visible_track = pygame.transform.scale(self.visible_track,resolution)
        self.track = pygame.transform.scale(self.track,resolution)
        self.start_line = pygame.Rect(844, 1324, 140, 200)
        self.clr_outside_trk = self.track.get_at((0, 0))
        self.total_cars = 10
        self.frames = 0
        self.all_cars = []
        self.dead_cars = []
        self.network_size = [5,10,5]
        self.generation = 0

    def track_setup(self, network = None):
        for i in range(self.total_cars):
            red_car = car.Car(self.network_size, self.screen, self.track, self.clr_outside_trk)
            red_car.load_car_sprite('red', 360)
            self.all_cars.append(red_car)
            if network:
                red_car.network = copy.deepcopy(network)
                red_car.network.mutate_weights()

    
    def game_setup(self):
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

                if event.key == K_ESCAPE:
                    self.running = False

                elif event.key == K_UP:

                    if car.gear_lock > 24:
                        car.gear += 1

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
            #print("outside track")
            return True
        else:
            #print("inside")
            return False

    def check_lap(self,car):

        if(self.start_line.collidepoint(car.xc, car.yc)):

            if(car.timer > 60):
                car.lap += 1
                car.timer = 0

    def game_loop(self):
        while self.running:
            #front, left, right collision sensor
            #current gear
            #self.user_control(self.all_cars[0])
            #time.sleep(0.15)
            self.screen.fill((0, 192, 0))
            self.clock.tick(60)
            self.frames += 1
            self.screen.blit(self.visible_track,(0,0))
            key = pygame.key.get_pressed()
            print("\r Length of cars: {}, generation: {}".format(len(self.all_cars), self.generation),end="\r")

            for car in self.all_cars:
                #____Graphical updates___
                car.update()
                car.draw_car(car.xc, car.yc, self.screen)

                pygame.display.update()
                #____Computing of car___
                self.check_lap(car)
                if(self.collision(car)):
                    self.dead_cars.append([copy.deepcopy(car.network), copy.copy(car.score)])
                    self.all_cars.remove(car)
                    del car
            if(len(self.all_cars)==0):
                #Respawn all cars with brains based on the best performer
                best_network = self.best_score_network(self.dead_cars)
                self.dead_cars.clear()
                self.all_cars.clear()
                self.track_setup(best_network)
                self.generation += 1

           



            for event in pygame.event.get():
                continue
                #print("Gaming bro")


    def best_score_network(self, cars):
        best_score = 0
        best_network = 0
        for car in cars:
            if(best_score < car[1]):
                best_network = car[0]
                best_score = car[1]
        return best_network




game = CarGame((1000, 1000))
game.track_setup()
game.game_setup()

game.game_loop()
