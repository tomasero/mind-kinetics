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

# from open_bci import *
from open_bci_v3 import *

import classifier

def generate_trials(N):
    L = [("left", -1), ("right", 1), ('baseline', 0)]

    d = list()

    for i in range(N):
        LL = list(L)
        random.shuffle(LL)
        d.extend(LL)

    return d

def initialize_board(port, baud):
    board = OpenBCIBoard(port, baud)
    # for i in range(100):
    #     print(board.ser.read())
    board.disconnect()

    board = OpenBCIBoard(port, baud)
    return board

def find_port():
    import platform, glob

    s = platform.system()
    if s == 'Linux':
        p = glob.glob('/dev/ttyACM*')
        
    elif s == 'Darwin':
        p = glob.glob('/dev/tty.usbmodemfd*')

    if len(p) >= 1:
        return p[0]
    else:
        return None

class MIOnline():

    def __init__(self, port='/dev/ttyUSB0', baud=115200):
        self.board = initialize_board(port, baud)
        # self.board = OpenBCIBoard(port, baud)
        self.bg_thread = None
        self.bg_classify = None

        self.data = np.array([0.0]*8)
        self.y = np.array([0])
        self.trial = np.array([-1])

        self.should_classify = False
        self.classify_loop = True
        self.out_sig = np.array([0])
        # self.controls = np.array([[0]*4])

        self.sock_send = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = '127.0.0.1'
        self.port_send = 33333

        self.sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port_receive = 10000
        self.sock_receive.bind((self.ip, self.port_receive))

        self.threshold = 0.1

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

        self.curr_event = None

        self.arm_port = find_port()
        if self.arm_port:
            print('found arm on port {0}'.format(self.arm_port))
            self.arm = serial.Serial(self.arm_port, 115200);
        else:
            print('did not find arm')
            self.arm = None

        self.running_arm = False

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

    def send_it(self, event, val=0, dir=None, accuracy=None):
        d = {
            'threshold': self.threshold,
            'val': val,
            'event': event,
            'dir': dir,
            'accuracy': accuracy
        }
        self.sock_send.sendto(json.dumps(d), (self.ip, self.port_send))
        # print(val, dirr)

    def classify(self):
        out = self.flow(self.data[-350:])
        s = out[-1]
        if abs(s) > self.threshold:
            s = np.sign(s)
        else:
            s = 0

        if time.time() > self.start_trial + 1 and (not self.pause_now) and (not self.running_arm):
            if s == self.current_class:
                self.good_times += 1
            self.total_times += 1

        if not self.pause_now:
            self.send_it('state', out[-1][0])

        if self.running_arm and self.arm:
            if s == 1:
                self.arm.write('a')
            elif s == -1:
                self.arm.write('A')
            

    def background_classify(self):
        while self.classify_loop:
            if len(self.data) > 50 and (not self.pause_now) and self.flow:
                self.classify()
            else:
                time.sleep(0.05)

    def train_classifier(self):

        trial = y = data = None
        test = False
        while not test:
            trial, y, data = self.trial, self.y, self.data
            test = trial.shape[0] == y.shape[0] and y.shape[0] == data.shape[0]

        # last 6 trials (3 trials per class)
        n_back = 6
        min_trial = max(0, self.current_trial - (n_back - 1))

        good = np.logical_and(y != 2, trial >= min_trial)
        sigs_train = data[good]
        y_train = y[good].astype('float32')

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
        # sample = sample.channels
        sample = sample.channel_data
        if not np.any(np.isnan(sample)):
            trial = np.append(self.trial, self.current_trial)
            y = np.append(self.y, self.current_class)
            data = np.vstack( (self.data, sample) )

            self.trial, self.y, self.data = trial, y, data

    def check_wait(self, wait_time):
        t0 = time.time()
        t = t0
        while t - t0 < wait_time:
            if self.curr_event != 'start':
                return True
            time.sleep(0.05)
            t = time.time()
        return False
    
    def run_trials(self):
        self.pause_now = True
        self.send_it('pause', dir=self.trials[0][0])
        self.current_class = 2
        
        if self.check_wait(self.pause_interval):
            return


        for i in range(len(self.trials)):
            x, t = self.trials[i]

            self.current_trial = i
            self.current_class = t


            print('{0} - {1}\t({2})'.format(i, x, self.data.shape))

            if self.flow:
                self.send_it('state', dir=x, val=0) # will classify
            else:
                self.send_it('state', dir=x, val=t)

            self.pause_now = False

            self.start_trial = time.time()
            
            # time.sleep(self.trial_interval)
            if self.check_wait(self.trial_interval):
                break

            accuracy = None
            
            if self.total_times > 0:
                accuracy = float(self.good_times) / self.total_times
                print(accuracy, self.good_times, self.total_times)

            self.pause_now = True
            self.current_class = 2
            
            if i == len(self.trials) - 1:
                self.send_it('done', accuracy=accuracy)
                break
            

            if (i+1) % 6 == 0:
                self.send_it('classifying', dir=self.trials[i+1][0],
                             accuracy=accuracy)
                self.train_classifier()
                self.good_times = 0
                self.total_times = 0
            else:
                self.send_it('pause', dir=self.trials[i+1][0])

                # time.sleep(self.pause_interval)
                if self.check_wait(self.pause_interval):
                    break

        self.pause_now = True

    def play_trials(self):
        self.pause_now = False
        self.running_arm = True
        while self.curr_event == 'play':
            time.sleep(0.1)
        self.running_arm = False
        self.pause_now = True
                
    def update_commands(self):
        print('updating commands...')
        while True:
            data = self.sock_receive.recv(4096)
            print(data)
            data = json.loads(data)
            event = data.get('event', None)
            self.curr_event = event
            
    def manage_commands(self):
        while True:
            if self.curr_event == 'start':
                self.run_trials()
            elif self.curr_event == 'play':
                self.play_trials()
            time.sleep(0.5)

    def start(self):

        if self.bg_thread:
            self.stop()


        #create a new thread in which the OpenBCIBoard object will stream data
        self.bg_thread = threading.Thread(target=self.board.startStreaming,
                                        args=(self.receive_sample, ))
        self.bg_thread.start()

        self.classify_loop = True

        #create a new thread in which the OpenBCIBoard object will stream data
        self.bg_classify = threading.Thread(target=self.background_classify, args=())
        self.bg_classify.start()

        self.bg_commands = threading.Thread(target=self.update_commands, args=())
        self.bg_commands.start()
        
        self.manage_commands()


if __name__ == '__main__':
    online = MIOnline()
    online.start()
