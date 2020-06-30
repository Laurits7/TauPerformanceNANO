import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from itertools import product
from root_numpy import root2array
from sklearn.metrics import roc_curve, roc_auc_score

##########################################################################################
# Argument Parser to manage options
import sys
rootfiles  = sys.argv[1:]

if (len(rootfiles))==0 or (len(rootfiles)%2!=0):
  print "Usage: Add sets of ntuple root files as arguments (In each set: Signal first, Fakes second)"
  exit()

branches = [
    'tau_gen_pt'                , 
    'tau_gen_eta'               ,
    'tau_pt'                    , 
    'tau_eta'                   ,
    'tau_jet_pt'                ,
    'tau_jet_eta'               , 
    'tau_decayMode'             ,
    'tau_rawDeepTau2017v2p1VSjet' ,
    'tau_rawMVAnewDM2017v2'     ,
    'ntrueint'                  ,
]

shapes=[]
selection=[]

selection.append('&'.join(['tau_gen_pt>20', 'abs(tau_gen_eta)<2.3', 'tau_pt>20', 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6'])) # Signal
selection.append('&'.join(['tau_jet_pt>20', 'abs(tau_jet_eta)<2.3', 'tau_gen_pt<0', 'tau_pt>20', 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6'])) # Fake

for i,r in enumerate(rootfiles):
  shapes.append(pd.DataFrame( root2array(r, 'tree', branches = branches, selection = selection[i%2]) ))

  # define targets: genuine taus get 1, fake taus get 0
  if i%2==0:
    shapes[i]['target'] = np.ones (shapes[i].shape[0]).astype(np.int)
  else:
    shapes[i]['target'] = np.zeros(shapes[i].shape[0]).astype(np.int)

# concatenate the datasets, preserving the information
setnr = len(rootfiles)/2
alltaus=[[] for x in range(setnr)]

for i in range(setnr):
  alltaus[i].append(pd.concat(shapes[2*i:2*i+2]))

  alltaus[i].append(alltaus[i][0][alltaus[i][0].ntrueint<25])

  alltaus[i].append(alltaus[i][0][alltaus[i][0].ntrueint>=25])
  alltaus[i][-1] = alltaus[i][-1][alltaus[i][-1].ntrueint<50]

  alltaus[i].append(alltaus[i][0][alltaus[i][0].ntrueint>=50])

  alltaus[i].append(alltaus[i][0][alltaus[i][0].tau_pt<100])

  alltaus[i].append(alltaus[i][0][alltaus[i][0].tau_pt>=100])

PUs = ['', '; PU $<$ 25', '; 25 $\leq$ PU $<$ 50', '; 50 $\leq$ PU']
PUleg = ['_all', '_lowpu', '_midpu', '_highpu']
PUs += ['; $p_T$ $<$ 100 GeV', '; $p_T$ $\geq$ 100 GeV']
PUleg += ['_lowpt', '_highpt']
names=[]
if setnr>1:
  for i in range(setnr):
    names.append('; ' + rootfiles[2*i].replace('.root', '') + '/' + rootfiles[2*i+1].replace('.root', ''))
else:
  names.append('')
colors=[['b','r'], ['g','y'], ['c','m']]

# let sklearn do the heavy lifting and compute the ROC curves for you
list_mva = [[[0 for x in range(3)] for y in alltaus[z]] for z in range(setnr)]
list_deep = [[[0 for x in range(3)] for y in alltaus[z]] for z in range(setnr)]
for j in range(setnr):
  for i,pu in enumerate(alltaus[j]):
    list_mva[j][i][0],  list_mva[j][i][1],  list_mva[j][i][2]  = roc_curve(alltaus[j][i].target, alltaus[j][i].tau_rawMVAnewDM2017v2)
    list_deep[j][i][0], list_deep[j][i][1], list_deep[j][i][2] = roc_curve(alltaus[j][i].target, alltaus[j][i].tau_rawDeepTau2017v2p1VSjet)


for i in range(len(PUs)):

  ax1 = plt.subplot(111)
  # ax1 = plt.subplot(211)

  # plot
  for j in range(setnr):
    ax1.plot(list_mva[j][i][1],  list_mva[j][i][0] , label=r'MVA TauID 2017v2'+PUs[i]+names[j], color=colors[j][0], linestyle='-')
    ax1.plot(list_deep[j][i][1], list_deep[j][i][0], label=r'DeepTau TauID 2017v2p1'+PUs[i]+names[j], color=colors[j][1], linestyle='-')

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
  name = 'roc'+PUleg[i]+'.png'
  print 'Saving',name
  plt.savefig(name)
  plt.clf()

exit()
