import pygame
pygame.init()
from pygame.locals import *
import math
import pdb
import car
import random
import neural_network
import numpy as np

class Car:
    def __init__(self, model, screen, track, clr_outside_trk): #model = [6,5,3,4]
        #game objects
        self.screen = screen
        self.track = track
        self.clr_outside_trk = clr_outside_trk

        #car setup
        self.xs = 600
        self.ys = 450
        self.xt = self.xs-100
        self.yt = self.ys + 100
        self.dt = 1.0
        self.font = pygame.font.Font(None,24)
        self.msg = ["STOP", "GEAR 1", "GEAR 2", "GEAR 3", "GEAR 4"]
        self.gears = []
        self.gear_lock = 24
        for i in range(len(self.msg)):
            self.gears += [self.font.render(self.msg[i],1,(250,250,250))]
        self.speedo = []
        self.laps = []
        self.dist = []
        self.timer = 0
        self.direction = 0
        for i in range(101):
            self.speedo += [self.font.render("SPEED "+str(i),1,(250,250,250))]
            self.laps += [self.font.render("LAP "+str(i),1,(250,250,250))]

        #Network
        self.score = 0
        self.network = neural_network.Network(model)

    def inherit_and_modify_weights(self, car_obj):
        #self.weights = car_obj.weights*random
        return car_obj

    def load_car_sprite(self,path,NF):
        self.view = 270
        self.images = []
        self.NF = NF
        self.xc = 500
        self.yc = 850
        self.xf = 500
        self.yf = 850
        self.speed = 0
        self.gear = 1
        self.wobble = 0
        self.lap = 0
        for f in range(NF):
            nv = len(str(f+1))
            name = path+'/fr_'
            if nv == 1:
                name += '000'
            if nv == 2:
                name += '00'
            if nv == 3:
                name += '0'
            self.images += [pygame.image.load(name+str(f+1)+'.png')]
    def draw_car(self,x,y,screen):
        view = self.view

        if view < 0 :
            view = view + 360
        view = view%360

        screen.blit(self.images[self.view],(x-32,y-32))
        screen.blit(self.gears[self.gear],(self.xt,self.yt))
        indicated = int(10.0*self.speed)
        screen.blit(self.speedo[indicated],(self.xt+100,self.yt))
        screen.blit(self.laps[self.lap],(self.xt,self.yt+50))

    def update(self):

        self.gear_lock += 1
        self.timer += 1
        self.speed = .95*self.speed + .05*(2.5*self.gear)
        #print (self.gear,'\t',int(10.0*self.speed),'\t',self.lap)
        
        theta = self.view/57.296
        old_xc = self.xc
        old_yc = self.yc
        vx = self.speed*math.sin(theta)
        vy = -self.speed*math.cos(theta)
        self.xf = self.xf + vx*self.dt
        self.yf = self.yf + vy*self.dt
        self.xc = int(self.xf)
        self.yc = int(self.yf)

        direction = math.atan2(vy, vx)
        self.direction = math.degrees(direction)

        #Handle network inputs
        self.dist = self.distance_from_car(self.screen, self.track, self.clr_outside_trk)

        #Feed to network

        self.score += np.sqrt(vx**2 + vy**2)

        #next move
        next_move = self.network.next_move(self) #Returns vector with probability of the next move
        #print("Next move", next_move)
        self.move(next_move)

    def move(self, next_move):
        if(next_move==0):
            #gear up
            if self.gear_lock > 24:
                self.gear += 1
                self.gear_lock = 0
                if self.gear > 4:
                    self.gear = 4

        elif(next_move==1):
            #gear down
            self.gear -= 1
            if self.gear < 1:
                self.gear = 1

        elif(next_move==2):
            #left
            self.view = (self.view+2) % 360

        elif(next_move==3):
            #right
            self.view = (self.view+358) % 360
        elif(next_move==4):
            #Go straight
            return

    def distance_from_car(self, screen, track, clr_outside_trk):
        #convert back to radians = math.radians(direction)
        try:

            direct = math.radians(self.direction)
            theta = self.view/57.296
            c_front = 100
            c_sides = 50
            x_front = int(c_front*math.sin(theta))
            y_front = int(c_front*math.cos(theta))
            x_right = int(c_sides*math.sin(theta + math.pi/2))
            y_right = int(c_sides*math.cos(theta + math.pi/2))
            x_left = int(c_sides*math.sin(theta - math.pi/2))
            y_left = int(c_sides*math.cos(theta - math.pi/2))

            dist_front = c_front
            dist_left = c_sides
            dist_right = c_sides

            pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_front,self.yc - y_front)) 
            pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_left,self.yc - y_left)) 
            pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_right,self.yc - y_right)) 


            surface_infront = track.get_at((self.xc + x_front, self.yc - y_front))
            surface_left = track.get_at((self.xc + x_left, self.yc - y_left))
            surface_right = track.get_at((self.xc + x_right, self.yc - y_right))

            if(surface_infront == clr_outside_trk):
                dist_front = self.calc_distance(c_front, track,x_front,y_front,clr_outside_trk)
            if(surface_left == clr_outside_trk):
                dist_left = self.calc_distance(c_sides, track,x_left,y_left,clr_outside_trk)
            if(surface_right == clr_outside_trk):
                dist_right = self.calc_distance(c_sides, track,x_right,y_right,clr_outside_trk)
            return [dist_front, dist_left, dist_right]
        
        except IndexError:
            return [1,1,1]
        

    def calc_distance(self,size_of_line,track, x_cord, y_cord, clr_outside_trk):
        i = 10
        while i >= 1:
            x = int(self.xc + x_cord/i)
            y = int(self.yc - y_cord/i)

            ground = track.get_at((x,y))
            if(ground == clr_outside_trk):
                #print("distance: ", size_of_line/i, "i is: ", i)
                return size_of_line/i
            i -= 0.5
        return -1