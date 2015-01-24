# import pandas

import numpy as np
import mdp
import Oger
from sklearn import neighbors, datasets
from sklearn.pipeline import Pipeline
import pylab as plt

from preprocess import *

import pylab as pl

from scipy.stats.stats import pearsonr

ica = mdp.nodes.FastICANode()
artifacts = RemoveArtifacts(remove_electricity=False)
bandpass = BandpassFilter(7, 30, sampling_rate=250)

n_sigs = 70

csp1 = CSP(labelA = 0, labelB = 1, m=10, input_dim=n_sigs)
csp2 = CSP(labelA = 0, labelB = -1, m=10, input_dim=n_sigs)

csp_layer = mdp.hinet.Layer([csp1, csp2])

switchboard = mdp.hinet.Switchboard(input_dim=n_sigs, connections=range(n_sigs) * 2)

var = LogVarianceWindow(box_width=150)
embed = mdp.nodes.TimeDelayNode(time_frames=10, gap=1)
fda = mdp.nodes.FDANode(output_dim=2)
knn = mdp.nodes.KNeighborsClassifierScikitsLearnNode(n_neighbors=10)
reservoir = Oger.nodes.LeakyReservoirNode(output_dim=300, leak_rate=0.01,
                                          spectral_radius=1.0,
                                          input_scaling=0.1, bias_scaling=0.2)
ridge = Oger.nodes.RidgeRegressionNode(ridge_param=10)
# gaussian = mdp.nodes.GaussianClassifier()
gaussian = GaussianClassifierArray()
# gauss_proc = mdp.nodes.GaussianHMMScikitsLearnNode()

medfilt = MedianFilter(3)
# classify = mdp.nodes.KNeighborsRegressorScikitsLearnNode(n_neighbors=1)
# classify = mdp.nodes.SVCScikitsLearnNode()
# classify = mdp.nodes.LibSVMClassifier()
# classify = Oger.nodes.RidgeRegressionNode(ridge_param=0.01)
lowpass = LowpassFilter(4, 0.005)
lowpass2 = LowpassFilter(3, 0.005)

cutoff = mdp.nodes.CutoffNode(lower_bound=-1, upper_bound=1)

flow = mdp.Flow([medfilt, ica, artifacts, bandpass,
                 embed, switchboard, csp_layer, var, fda,
                 knn, lowpass, cutoff])

##I want labels from you classifiers. Yes, labels.
for c in flow:
    if getattr(c, 'label', None):
        c.execute = c.label

# x = sigs_split
# xy = zip(sigs_split, y_split_newaxis)
# xys = zip(sigs_split, y_split)

def get_inp(x, xy, xys):
    inp = [x, x, x, x,
           x, x, xys, x, xys,
           xys, xy, xy]
    return inp

def get_inp_xy(X, y):
    yy = y[:, np.newaxis].astype('float32')
    x = [X]
    xy = [(X, yy)]
    xys = [(X, y)]
    return get_inp(x, xy, xys)

def get_flow(X, y):
    f = flow.copy()
    inp = get_inp_xy(X, y)
    f.train(inp)
    return f
