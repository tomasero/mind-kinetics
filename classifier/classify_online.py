#!/usr/bin/env python2

import random
import time
import threading
import csv
import numpy as np
from multiprocessing import Process
import sys
import serial

import socket
import json
from mdp import FlowException

# sys.path.append('..')
from open_bci import *

import classifier

def generate_trials(N):
    L = [("left", -1), ("right", 1), ('baseline', 0)]

    d = list()
    
    for i in range(N):
        LL = list(L)
        random.shuffle(LL)
        d.extend(LL)

    return d

#TODO: update the classifier every few trials

class MIOnline():

    def __init__(self, port=None, baud=115200):
        self.board = OpenBCIBoard(port, baud)
        self.bg_thread = None
        self.bg_classify = None
        self.data = np.array([0.0]*8)
        self.y = np.array([0])
        self.should_classify = False
        self.classify_loop = True
        self.out_sig = np.array([0])
        # self.controls = np.array([[0]*4])

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = '127.0.0.1'
        self.port = 33333
        
        self.threshold = 0.2
        
        # 0 for baseline, -1 for left hand, 1 for right hand
        # 2 for pause
        self.current_class = 0

        self.current_trial = 0
        self.trials = generate_trials(10)

        self.pause_now = True

        self.flow = None
        
    def stop(self):
        # resolve files and stuff
        self.board.should_stream = False
        self.should_classify = False
        self.classify_loop = False
        #self.bg_thread.join()
        self.bg_thread = None
        self.bg_classify = None
        self.data = np.array([0]*8)

    def disconnect(self):
        self.board.disconnect()

    def send_it(self, val, dirr):
        d = {
            'threshold': self.threshold,
            'val': val,
            'dir': dirr
        }
        self.sock.sendto(json.dumps(d), (self.ip, self.port))
        print(val, dirr)
        
    def classify(self):
        out = self.flow(self.data[-300:])
        s = out[-1]
        if abs(s) > self.threshold:
            s = np.sign(s)
        else:
            s = 0

        print(out[-1])

        if not self.pause_now:
            self.send_it(out[-1], None)

    def background_classify(self):
        while self.classify_loop:
            if len(self.data) > 50 and self.should_classify and self.flow:
                self.classify()
            time.sleep(0.05)

    def train_classifier(self):

        good = self.y != 2
        sigs_train = self.data[good]
        y_train = self.y[good]
        
        # inp = classifier.get_inp_xy(sigs_train, y_train)
        f = self.flow
        try:
            self.flow = classifier.get_flow(sigs_train, y_train)
        except FlowException:
            self.flow = f
            

    def receive_sample(self, sample):
        t = time.time()
        sample = sample.channels
        #print(sample)
        if not np.any(np.isnan(sample)):
            self.data = np.vstack( (self.data, sample) )
            self.y = np.append(self.y, self.current_class)

    def manage_trials(self):
        self.send_it(0, 'pause')
        self.current_class = 2
        time.sleep(2)
        
        for i in range(len(self.trials)):
            x, t = self.trials[i]
            
            self.current_trial = i
            self.current_class = t

            self.send_it(t, x)
            time.sleep(2)

            self.send_it(0, 'pause')
            self.current_class = 2

            
            if (i+1) % 3 == 0:
                self.train_classifier()
            else:
                time.sleep(2)
       

    def start(self):

        if self.bg_thread:
            self.stop()


        #create a new thread in which the OpenBCIBoard object will stream data
        self.bg_thread = threading.Thread(target=self.board.start,
                                        args=(self.receive_sample, ))
        self.bg_thread.start()

        self.classify_loop = True

        #create a new thread in which the OpenBCIBoard object will stream data
        self.bg_classify = threading.Thread(target=self.background_classify, args=())
        self.bg_classify.start()
        
        self.manage_trials()


if __name__ == '__main__':
    online = MIOnline()
    online.start()




