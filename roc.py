import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from itertools import product
from root_numpy import root2array
from sklearn.metrics import roc_curve, roc_auc_score

branches = [
    'tau_gen_pt'                , 
    'tau_gen_eta'               ,
    'tau_pt'                    , 
    'tau_eta'                   ,
    'tau_jet_pt'                ,
    'tau_jet_eta'               , 
    'tau_decayMode'             ,
    'tau_rawDeepTau2017v2VSjet' ,
    'tau_rawMVAnewDM2017v2'     ,
    'ntrueint'                  ,
]

sig_selection = '&'.join(['tau_gen_pt>20', 'abs(tau_gen_eta)<2.3', 'tau_pt>20', 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6'])
bkg_selection = '&'.join(['tau_jet_pt>20', 'abs(tau_jet_eta)<2.3', 'tau_gen_pt<0', 'tau_pt>20', 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6'])

sig = pd.DataFrame( root2array('dy_gen_tuple.root.big.bkup', 'tree', branches = branches, selection = sig_selection) )
bkg = pd.DataFrame( root2array('qcd_jet_tuple.root.bkup'   , 'tree', branches = branches, selection = bkg_selection) )

# define targets: genuine taus get 1, fake taus get 0
sig['target'] = np.ones (sig.shape[0]).astype(np.int)
bkg['target'] = np.zeros(bkg.shape[0]).astype(np.int)

# concatenate the datasets, preserving the information
alltaus = pd.concat([sig, bkg])

alltaus_lowpu = alltaus[alltaus.ntrueint<25]
alltaus_midpu = alltaus[alltaus.ntrueint>=25]
alltaus_midpu = alltaus_midpu[alltaus_midpu.ntrueint<50]
alltaus_higpu = alltaus[alltaus.ntrueint>=50]

# let sklearn do the heavy lifting and compute the ROC curves for you
fpr_mva_lowpu, tpr_mva_lowpu, wps_mva_lowpu = roc_curve(alltaus_lowpu.target, alltaus_lowpu.tau_rawMVAnewDM2017v2) 
fpr_mva_midpu, tpr_mva_midpu, wps_mva_midpu = roc_curve(alltaus_midpu.target, alltaus_midpu.tau_rawMVAnewDM2017v2) 
fpr_mva_higpu, tpr_mva_higpu, wps_mva_higpu = roc_curve(alltaus_higpu.target, alltaus_higpu.tau_rawMVAnewDM2017v2) 

fpr_dt_lowpu , tpr_dt_lowpu , wps_dt_lowpu  = roc_curve(alltaus_lowpu.target, alltaus_lowpu.tau_rawDeepTau2017v2VSjet) 
fpr_dt_midpu , tpr_dt_midpu , wps_dt_midpu  = roc_curve(alltaus_midpu.target, alltaus_midpu.tau_rawDeepTau2017v2VSjet) 
fpr_dt_higpu , tpr_dt_higpu , wps_dt_higpu  = roc_curve(alltaus_higpu.target, alltaus_higpu.tau_rawDeepTau2017v2VSjet) 



ax1 = plt.subplot(111)
# ax1 = plt.subplot(211)

# plot
ax1.plot(tpr_mva_lowpu, fpr_mva_lowpu, label=r'MVA TauID - PU $<$ 25'              , color='b', linestyle='-' )
ax1.plot(tpr_mva_midpu, fpr_mva_midpu, label=r'MVA TauID - 25 $\leq$ PU $<$ 50'    , color='b', linestyle='--')
ax1.plot(tpr_mva_higpu, fpr_mva_higpu, label=r'MVA TauID - 50 $\leq$ PU $<$ 75'    , color='b', linestyle='-.')
ax1.plot(tpr_dt_lowpu , fpr_dt_lowpu , label=r'DeepTau TauID - PU $<$ 25'          , color='r', linestyle='-' )
ax1.plot(tpr_dt_midpu , fpr_dt_midpu , label=r'DeepTau TauID - 25 $\leq$ PU $<$ 50', color='r', linestyle='--')
ax1.plot(tpr_dt_higpu , fpr_dt_higpu , label=r'DeepTau TauID - 50 $\leq$ PU $<$ 75', color='r', linestyle='-.')

############################################################################################

# plot the also the diagonal, that corresponds to no random picks, no discrimination power
# xy = [i*j for i,j in product([10.**i for i in range(-8, 0)], [1,2,4,8])]+[1]
# plt.plot(xy, xy, color='grey', linestyle='--')

# ratio pad
# ax2 = plt.subplot(212, sharex=ax1)
# 
# ax2.plot(tpr_mva_midpu, fpr_mva_midpu, color='b', linestyle='--')
# ax2.plot(tpr_mva_higpu, fpr_mva_higpu, color='b', linestyle='-.')
# ax2.plot(tpr_dt_midpu , fpr_dt_midpu , color='r', linestyle='--')
# ax2.plot(tpr_dt_higpu , fpr_dt_higpu , color='r', linestyle='-.')

# cosmetics
plt.xlabel(r'genuine $\tau_h$ efficiency') # aka 'True Positive Rate' outside hep
plt.ylabel(r'$j\to\tau_h$ fake rate') # aka 'False Positive Rate' outside hep

# axis range
# plt.xlim([0.0, 0.4])
# plt.ylim([0.0, 1.0])

# grid
plt.grid(True)

# legend
plt.legend(loc='lower right')

# log y
plt.yscale('log')

# limits
x1,x2,y1,y2 = plt.axis()
plt.axis((x1,x2,1.e-4,1))

# save plot
plt.savefig('roc.pdf')
