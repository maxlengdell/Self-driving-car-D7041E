
import car
import os
import pygame
from pygame.locals import *
import math
import pdb
import time
import copy
import numpy as np
import neural_network
pygame.init()



class CarGame:
    def __init__(self, resolution):
        self.resolution = resolution
        self.screen = pygame.display.set_mode(resolution)
        self.screen.fill((0, 192, 0))
        self.running = True
        self.track = pygame.image.load('track_3.png')
        self.visible_track = pygame.image.load('track_3.png')
        #self.track = pygame.transform.flip(self.track,True,False)
        #self.visible_track = pygame.transform.flip(self.visible_track,True,False)
        self.visible_track = pygame.transform.scale(self.visible_track,resolution)
        self.track = pygame.transform.scale(self.track,resolution)
        self.start_line = pygame.Rect(844, 1324, 140, 200)
        self.clr_outside_trk = self.track.get_at((0, 0))
        self.total_cars = 18
        self.frames = 0
        self.all_cars = []
        self.best_score = 0
        self.best_network = 0
        self.dead_cars = []
        self.network_size = [7,10,6,5]
        self.generation = 0
        self.font = pygame.font.Font(None,24) #pygame.font.SysFont('arial',24)
        self.lr_decay = 500

    def track_setup(self, network = None):
        for i in range(self.total_cars):
            red_car = car.Car(self.network_size, self.screen, self.track, self.clr_outside_trk)
            red_car.load_car_sprite('red', 360)
            self.all_cars.append(red_car)
            if network:
                red_car.network = copy.deepcopy(network)
                if(i>0):
                    red_car.network.mutate_weights(self.best_score, self.lr_decay)

    
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
    def HUD(self):
        #self.screen.blit(self.generation,(400,400))
        msg_gen = "Generation: " + str(self.generation)
        msg_cars = "Current cars: " + str(len(self.all_cars))
        hud_gen = self.font.render(msg_gen,False,(0,0,0))
        hud_cars = self.font.render(msg_cars,False,(0,0,0))
        self.screen.blit(hud_gen,(400,400))
        self.screen.blit(hud_cars,(400,440))

    def game_loop(self):
        while self.running:
            #front, left, right collision sensor
            #current gear
            self.user_control(self.all_cars[0])
            #time.sleep(0.1)
            self.screen.fill((0, 192, 0))
            self.clock.tick(1000)
            self.frames += 1
            self.screen.blit(self.visible_track,(0,0))
            self.HUD()

            key = pygame.key.get_pressed()
            #print("\r Generation: {}, best score: {},Length of cars: {}".format(self.generation,int(self.best_score),len(self.all_cars),),end="\r")

            for car in self.all_cars:
                #____Graphical updates___
                car.update()
                car.draw_car(car.xc, car.yc, self.screen)

                #____Computing of car___
                self.check_lap(car)
                if(self.collision(car)):
                    self.dead_cars.append([copy.deepcopy(car.network), copy.copy(car.score)])
                    self.all_cars.remove(car)
                    del car
            pygame.display.flip()

            if(len(self.all_cars)==0):
                #Respawn all cars with brains based on the best performer
                best_network = self.best_score_mean(self.dead_cars)
                self.dead_cars.clear()
                self.all_cars.clear()
                self.track_setup(best_network)
                self.generation += 1

        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.save_best_car('weights.csv')

    def save_best_car(self, filename):
        best_score = 0
        best_weights = 0
        for car in self.all_cars:
            if(car.score > best_score):
                best_score = car.score
                best_weights = car.network.weights
        for i in range(len(best_weights)):
            best_weights[i] = np.asarray(best_weights[i])
        print(np.asarray(best_weights))
        np.savetxt(filename, np.asarray(best_weights), delimiter=",")

    def best_score_network(self, cars):
        best_car = cars[-1]
        self.best_network = best_car[0]
        self.best_score = best_car[-1]

        return self.best_network

    def best_score_mean(self, cars):
        #Get 3 best cars
        best_car = cars[-2:]

        new_car_brain = neural_network.Network(self.network_size)
        mean_weights = np.mean([best_car[0][0].weights,best_car[1][0].weights], axis=0)
        new_car_brain.weights = mean_weights

        self.best_network = new_car_brain
        self.best_score = cars[-1][1]
        return self.best_network


game = CarGame((2000, 1200))
game.track_setup()
game.game_setup()

game.game_loop()
