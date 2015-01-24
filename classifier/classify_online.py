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
        self.trial = np.array([-1])
        
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

        self.trial_interval = 4
        self.pause_interval = 2

        self.good_times = 0
        self.total_times = 0
        
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
        # print(val, dirr)
        
    def classify(self):
        out = self.flow(self.data[-300:])
        s = out[-1]
        if abs(s) > self.threshold:
            s = np.sign(s)
        else:
            s = 0

        # print(out[-1])

        if s == self.current_class:
            self.good_times += 1
        self.total_times += 1
        
        self.send_it(out[-1][0], None)

    def background_classify(self):
        while self.classify_loop:
            if len(self.data) > 50 and (not self.pause_now) and self.flow:
                self.classify()
            time.sleep(0.05)

    def train_classifier(self):

        # last 9 trials (3 trials per class)
        min_trial = max(0, self.current_trial - 8)
        
        good = np.logical_and(self.y != 2, self.trial >= min_trial)
        sigs_train = self.data[good]
        y_train = self.y[good].astype('float32')

        # print(self.data.shape, self.y.shape, self.trial.shape)
        
        # inp = classifier.get_inp_xy(sigs_train, y_train)
        f = self.flow
        try:
            print('training classifier...')
            self.flow = classifier.get_flow(sigs_train, y_train)
            self.should_classify = True
            print('updated classifier!')
        except FlowException as e:
            self.flow = f
            print "FlowException error:\n{0}".format(e)
            

    def receive_sample(self, sample):
        t = time.time()
        sample = sample.channels
        #print(sample)
        if not np.any(np.isnan(sample)):
            trial = np.append(self.trial, self.current_trial)
            y = np.append(self.y, self.current_class)
            data = np.vstack( (self.data, sample) )

            self.trial, self.y, self.data = trial, y, data

    def manage_trials(self):
        self.send_it(0, 'pause')
        self.pause_now = True
        self.current_class = 2
        time.sleep(self.pause_interval)
        
        for i in range(len(self.trials)):
            x, t = self.trials[i]
            
            self.current_trial = i
            self.current_class = t
            self.pause_now = False

            print('{0} - {1}'.format(i, x))
            
            if self.flow:
                self.send_it(0, x) # will classify
            else:
                self.send_it(t, x)
            
            time.sleep(self.trial_interval)

            if self.total_times > 0:
                print(float(self.good_times) / self.total_times,
                      self.good_times, self.total_times)
            
            self.send_it(0, 'pause')
            self.pause_now = True
            self.current_class = 2
            # print('pause')

            
            if (i+1) % 3 == 0:
                self.train_classifier()
            else:
                time.sleep(self.pause_interval)
       

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




