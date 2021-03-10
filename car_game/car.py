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
        # for i in range(len(self.msg)):
        #     self.gears += [self.font.render(self.msg[i],1,(250,250,250))]
        self.speedo = []
        self.laps = []
        self.dist = []
        self.timer = 0
        self.direction = 0
        self.wobble = 15
        # for i in range(101):
        #     self.speedo += [self.font.render("SPEED "+str(i),1,(250,250,250))]
        #     self.laps += [self.font.render("LAP "+str(i),1,(250,250,250))]

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
        self.xc = 0.49*1920
        self.yc = 0.67*1080
        self.xf = 0.49*1920
        self.yf = 0.67*1080
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
        #screen.blit(self.gears[self.gear],(self.xt,self.yt))
        indicated = int(10.0*self.speed)
        #screen.blit(self.speedo[indicated],(self.xt+100,self.yt))
        #screen.blit(self.laps[self.lap],(self.xt,self.yt+50))

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
        next_move = self.network.next_move(self, 300) #Returns vector with probability of the next move
        #print("Next move", next_move)
        self.move(next_move)

    def move(self, next_move):
        if(next_move==0):
            #gear up
            if self.gear_lock > 24:
                self.gear=1
                # self.gear += 1
                # self.gear_lock = 0
                if self.gear > 4:
                    self.gear = 4

        elif(next_move==1):
            #gear down
            #self.gear -= 1
            self.gear = 1
            if self.gear < 1:
                self.gear = 1

        elif(next_move==2):
            #left
            self.view = (self.view+3) % 360

        elif(next_move==3):
            #right
            self.view = (self.view+357) % 360
        elif(next_move==4):
            #Go straight
            return

    def distance_from_car(self, screen, track, clr_outside_trk):
        #convert back to radians = math.radians(direction)
        try:

            direct = math.radians(self.direction)
            theta = self.view/57.296
            c = 300
            x_front = int(c*math.sin(theta))
            y_front = int(c*math.cos(theta))
            x_right = int(c*math.sin(theta + math.pi/2))
            y_right = int(c*math.cos(theta + math.pi/2))
            x_left = int(c*math.sin(theta - math.pi/2))
            y_left = int(c*math.cos(theta - math.pi/2))

            x_60_r = int(c*math.sin(theta + math.pi/3))
            y_60_r = int(c*math.cos(theta + math.pi/3))
            x_60_l = int(c*math.sin(theta - math.pi/3))
            y_60_l = int(c*math.cos(theta - math.pi/3))

            x_30_r = int(c*math.sin(theta + math.pi/6))
            y_30_r = int(c*math.cos(theta + math.pi/6))
            x_30_l = int(c*math.sin(theta - math.pi/6))
            y_30_l = int(c*math.cos(theta - math.pi/6))

            x_10_r = int(c*math.sin(theta + math.pi/18))
            y_10_r = int(c*math.cos(theta + math.pi/18))
            x_10_l = int(c*math.sin(theta - math.pi/18))
            y_10_l = int(c*math.cos(theta - math.pi/18))

            dist = c

            #pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_left,self.yc - y_left)) 
            #pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_right,self.yc - y_right)) 
            
            #pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_60_r,self.yc - y_60_r)) 
            #pygame.draw.line(screen, (0,0,0), (self.xc,self.yc), (self.xc + x_60_l,self.yc - y_60_l)) 

            # surface_infront = track.get_at((self.xc + x_front, self.yc - y_front))
            # surface_left = track.get_at((self.xc + x_left, self.yc - y_left))
            # surface_right = track.get_at((self.xc + x_right, self.yc - y_right))
            # surface_diag_left = track.get_at((self.xc + x_60_l, self.yc - y_60_l))
            # surface_diag_right = track.get_at((self.xc + x_60_r, self.yc - y_60_r))

            dist_front = self.calc_distance(c, track, x_front, y_front, clr_outside_trk, screen)



            dist_left = self.calc_distance(c, track,x_left,y_left,clr_outside_trk, screen)
            dist_right = self.calc_distance(c, track,x_right,y_right,clr_outside_trk, screen)

            dist_60_left = self.calc_distance(c, track, x_60_l,y_60_l,clr_outside_trk, screen)
            dist_60_right = self.calc_distance(c, track, x_60_r,y_60_r,clr_outside_trk, screen)
            
            dist_30_left = self.calc_distance(c, track, x_30_l,y_30_l,clr_outside_trk, screen)
            dist_30_right = self.calc_distance(c, track, x_30_r,y_30_r,clr_outside_trk, screen)

            dist_10_left = self.calc_distance(c, track, x_10_l,y_10_l,clr_outside_trk, screen)
            dist_10_right = self.calc_distance(c, track, x_10_r,y_10_r,clr_outside_trk, screen)


            return [dist_front, dist_left, dist_right, dist_10_left, dist_10_right, dist_30_left, dist_30_right, dist_60_left, dist_60_right]
        
        except IndexError:
            print("INDEX FUCKERS")
            return [1,1,1,1,1]
        

    def calc_distance(self,size_of_line,track, x_cord, y_cord, clr_outside_trk, screen):
        i = 100
        while i >= 1:
            x = int(self.xc + x_cord/i)
            y = int(self.yc - y_cord/i)

            ground = track.get_at((x,y))

            if(ground == clr_outside_trk):
            
                #pygame.draw.circle(screen, (0,0,0), (x,y), 5)

                return size_of_line/i
            i -= 0.1
        return size_of_line