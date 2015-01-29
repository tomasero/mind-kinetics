# import pandas

import numpy as np
import mdp
# import Oger
from sklearn import neighbors, datasets
from sklearn.pipeline import Pipeline
import pylab as plt

from preprocess import *

import pylab as pl

from scipy.stats.stats import pearsonr

remove60 = BandstopFilter(55, 65, sampling_rate=250)
remove120 = BandstopFilter(115, 125, sampling_rate=250)

ica = mdp.nodes.FastICANode()
artifacts = RemoveArtifacts(remove_electricity=False)
bandpass = BandpassFilter(7, 30, sampling_rate=250)

fisher = FisherFeaturesUncorr(output_dim = 20, labelA = -1, labelB = 1)
features = EEGFeatures(wavelets_freqs=(10,))

n_sigs = 70
m = 10
csp1 = CSP(labelA = 0, labelB = 1, m=m, input_dim=n_sigs)
csp2 = CSP(labelA = 0, labelB = -1, m=m, input_dim=n_sigs)
csp3 = CSP(labelA = 1, labelB = -1, m=m, input_dim=n_sigs)

csp_layer = mdp.hinet.Layer([csp1, csp2, csp3])

switchboard = mdp.hinet.Switchboard(input_dim=n_sigs, connections=range(n_sigs) * 3)

var = LogVarianceWindow(box_width=300)
embed = mdp.nodes.TimeDelayNode(time_frames=10, gap=1)
fda = mdp.nodes.FDANode(output_dim=2)
knn = mdp.nodes.KNeighborsClassifierScikitsLearnNode(n_neighbors=10)
# reservoir = Oger.nodes.LeakyReservoirNode(output_dim=300, leak_rate=0.05,
#                                           spectral_radius=1.0,
#                                           bias_scaling=0.2)
# ridge = Oger.nodes.RidgeRegressionNode(ridge_param=10)
# gaussian = mdp.nodes.GaussianClassifier()
gaussian = GaussianClassifierArray()
# gauss_proc = mdp.nodes.GaussianHMMScikitsLearnNode()

medfilt = MedianFilter(3)
# classify = mdp.nodes.KNeighborsRegressorScikitsLearnNode(n_neighbors=1)
# classify = mdp.nodes.SVCScikitsLearnNode()
# classify = mdp.nodes.LibSVMClassifier()
# classify = Oger.nodes.RidgeRegressionNode(ridge_param=0.01)
lowpass = LowpassFilter(4, 0.003)
lowpass2 = LowpassFilter(3, 0.005)
lowpass_ignore = LowpassFilter(4, 0.003, ignore=250)
lowpass2_ignore = LowpassFilter(4, 0.2, ignore=250)


pca = mdp.nodes.PCANode(output_dim = 0.98)

cutoff = mdp.nodes.CutoffNode(lower_bound=-1, upper_bound=1)

flow = mdp.Flow([remove60, remove120, ica, artifacts, bandpass,
                 embed, switchboard, csp_layer, var,
                 knn, lowpass, cutoff])

# flow = mdp.Flow([features, fisher,
#                  knn, lowpass_ignore, cutoff])

##I want labels from you classifiers. Yes, labels.
for c in flow:
    if getattr(c, 'label', None):
        c.execute = c.label

# x = sigs_split
# xy = zip(sigs_split, y_split_newaxis)
# xys = zip(sigs_split, y_split)

def get_inp(x, xy, xys):
    inp = [x, x, x,
           x, x, xys, x,
           xys, x, x]
    
    # inp = [x, xys,
    #        xys, x, xys]

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
