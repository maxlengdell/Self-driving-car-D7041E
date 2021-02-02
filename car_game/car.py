import pygame
pygame.init()
from pygame.locals import *
import math
import pdb
import car
import random
class Car:
    def __init__(self):
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
        for i in range(101):
            self.speedo += [self.font.render("SPEED "+str(i),1,(250,250,250))]
            self.laps += [self.font.render("LAP "+str(i),1,(250,250,250))]
    def load_car_sprite(self,path,NF):
        self.view = 270
        self.images = []
        self.NF = NF
        self.xc = 912
        self.yc = 1410
        self.xf = 912.0
        self.yf = 1410.0
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
        view = self.view + int(random.gauss(0,self.wobble))

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
        self.speed = .95*self.speed + .05*(2.5*self.gear)
        #print (self.gear,'\t',int(10.0*self.speed),'\t',self.lap)
        
        theta = self.view/57.296

        vx = self.speed*math.sin(theta)
        vy = -self.speed*math.cos(theta)
        self.xf = self.xf + vx*self.dt
        self.yf = self.yf + vy*self.dt
        self.xc = int(self.xf)
        self.yc = int(self.yf)
