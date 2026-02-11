import pygame as pg
import sys
from os import path
from main import *
from settings import *
from sprites import *

#creates countdown timer for a cooldown
class Cooldown:
    def __init__(self, time):
        self.start_time = 0
        #allows us to set property for time until cooldown
        self.time = time
        #self.current_time = self.time

    def start(self):
        self.start_time = pg.time.get_ticks()

    def ready(self):
        # sets current time to 
        current_time = pg.time.get_ticks()
        # if the difference between current and start time are greater than self.time
        # return True
        if current_time - self.start_time >= self.time:
            return True
        return False