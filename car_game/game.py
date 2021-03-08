
import car
import os
import sys
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
        self.track = None
        self.screen = None
        self.running = True
        self.default_numberOfCars = 18
        self.frames = 0
        self.all_cars = []
        self.best_score = 0
        self.best_network = 0
        self.dead_cars = []
        self.network_size = [9,6,5]
        self.generation = 0
        self.lr_decay = 500
        self.inMenu = True
        self.currentMap = 'T1.png'

    def load_map(self, trackPic):
        #print(self.resolution)
        self.screen = pygame.display.set_mode(self.resolution)
        self.screen.fill((0, 192, 0))

        self.track = pygame.image.load(trackPic)
        self.visible_track = pygame.image.load(trackPic)
        self.visible_track = pygame.transform.scale(self.visible_track, self.resolution)
        self.track = pygame.transform.scale(self.track,self.resolution)
        self.start_line = pygame.Rect(844, 1324, 140, 200)
        self.clr_outside_trk = self.track.get_at((0, 0))

        self.font = pygame.font.Font(None,24) #pygame.font.SysFont('arial',24)

    def track_setup(self, network = None, numberOfCars = 18):
        print("Track_setup", numberOfCars)
        for i in range(numberOfCars):
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
        self.screen.blit(self.font.render('Press ESC to save and quit',False,(0,0,0)), (400,480))

    def train_loop(self, numberOfCars, filename, showmode):
        self.all_cars.clear()
        print('Starting a training session with',numberOfCars,'number of cars')
        self.load_map(self.currentMap)
        self.track_setup(numberOfCars=int(numberOfCars))
        self.running = True
        while self.running:
            #front, left, right collision sensor
            #time.sleep(0.1)
            if(showmode):
                self.screen.fill((0, 192, 0))
                self.clock.tick(60)
                self.frames += 1
                self.screen.blit(self.visible_track,(0,0))
                self.HUD()

            key = pygame.key.get_pressed()
            #print("\r Generation: {}, best score: {},Length of cars: {}".format(self.generation,int(self.best_score),len(self.all_cars),),end="\r")

            for car in self.all_cars:
                #____Graphical updates___
                car.update()
                if(showmode):
                    car.draw_car(car.xc, car.yc, self.screen)

                #____Computing of car___
                #self.check_lap(car)
                if(self.collision(car)):
                    self.dead_cars.append([copy.deepcopy(car.network), copy.copy(car.score)])
                    self.all_cars.remove(car)
                    del car
            if(showmode):
                pygame.display.flip()
            else:
                best_score = self.dead_cars[-1][1] if len(self.dead_cars) > 0 else 0
                print("\rGeneration: {}, best score {},  number of cars alive {}".format(self.generation,best_score, len(self.all_cars)),end="\r")

            if(len(self.all_cars)==0):
                #Respawn all cars with brains based on the best performer
                best_network = self.best_score_network(self.dead_cars)
                self.dead_cars.clear()
                self.all_cars.clear()
                self.track_setup(best_network, numberOfCars=numberOfCars)
                self.generation += 1
        

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.save_best_car(filename)
                        self.main_menu()
                        

    def show_network(self, filename):
        self.all_cars.clear()
        self.load_map(self.currentMap)
        network = self.load_best_car(filename)
        self.track_setup(network=network,numberOfCars=1)
        self.running = True
        while self.running:
            self.screen.fill((0, 192, 0))
            self.clock.tick(1000)
            self.frames += 1
            self.screen.blit(self.visible_track,(0,0))

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
                self.track_setup(network=network,numberOfCars=1)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.main_menu()

    def save_best_car(self, filename):
        best_score = 0
        best_weights = 0
        for car in self.all_cars:
            if(car.score > best_score):
                best_score = car.score
                best_weights = car.network.weights

        f = open(filename,'w') # * delimiter for every matrix, % delimiter for every row in matrix
        storing_weights = []
        for weight_matrix in best_weights:
            for weight_vector in weight_matrix:
                for integer in weight_vector:
                    f.write(str(integer))
                    f.write(' ')
                f.write(',\n')
            f.write('###\n\n')
        f.close()

    def load_best_car(self,filename):
        model = []
        f = open(filename, 'r')
        data = f.read()
        data = data.split('###\n\n')
        for i in range(len(data)):
            if(data[i] != ''):
                model.append([])
                vector = data[i].split(',\n')
                for j in range(len(vector)):
                    if(vector[j] != ''):
                        model[i].append([])
                        integers = vector[j].split(' ')
                        for k in range(len(integers)):
                            if(integers[k] != ''):
                                model[i][j].append(float(integers[k]))
        network = neural_network.Network(self.network_size)
        network.store_weights(np.array(model))
        return network
    

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

    def main_menu(self):
        self.inMenu = True
        while(self.inMenu):
            inp = input('1 train a new network [filename] [number of cars] [showmode 0/1]\n2 show network [filename] \n3 Choose map [...] \nq for quits \n')
            inp = inp.split(' ')
            if(inp[0] == '1'):
                self.train_loop(filename=inp[1], numberOfCars=int(inp[2]), showmode=int(inp[3]))
                self.inMenu = False
            elif(inp[0] == '2'):
                self.show_network(inp[1])
                self.inMenu = False
            elif(inp[0] == '3'):
                self.currentMap = inp[1]
            elif(inp[0] == 'q'):
                pygame.quit()
                sys.exit()
            else:
                print('Could not interpret your input :(')

game = CarGame((1920, 1080))
game.game_setup()

game.main_menu()
