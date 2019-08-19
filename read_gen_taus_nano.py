'''
Loops on the events and operates the matching between reconstructed and generated taus
as well as reconstructed tau and seeding jet (geometrically closest to the tau).
It produces a flat ntuple with one with an entry for each reconstructed tau.

Launch with, e.g.
ipython -i -- read_taus_nano.py --qcd --maxevents 1000000 --logfreq 1000

Tau recommendations
https://twiki.cern.ch/twiki/bin/viewauth/CMS/TauIDRecommendation13TeV

NanoAOD
https://twiki.cern.ch/twiki/bin/view/CMSPublic/WorkBookNanoAOD

A description of the NanoAOD branch content is given in branches.txt and
https://cms-nanoaod-integration.web.cern.ch/integration/master-102X/mc102X_doc.html



ipython -i -- read_taus_nano.py --dy --logfreq 1000 --filein


'''
import ROOT
from time import time
from datetime import datetime, timedelta
from array import array
from collections import OrderedDict
from deltar import deltaR, deltaPhi
import glob

# here the ntuple branches, and how to get the quantities stored in such branches, are defined
from treeVariables import branches_event, branches_tau, branches_gen, branches_jet, branches_all, prepareBranches
from files import dy_files, qcd_files

##########################################################################################
# Argument Parser to manage options
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--dy'       , dest='genuine_taus', action='store_true'  , help='Process on DY->LL sample. This option, or --qcd, needs to be always specified')
parser.add_argument('--qcd'      , dest='genuine_taus', action='store_false' , help='Process on QCD multijet sample. This option, or --dy, needs to be always specified')
parser.add_argument('--maxevents', dest='maxevents'   , default=-1 , type=int, help='Events to process. Default = -1 --> process all events')
parser.add_argument('--fileout'  , dest='fileout'     , default=''           , help='Specify the output ntuple name. Default dy_ntuple.root if --dy is chosen, else qcd_tuple.root --qcd is chosen')
parser.add_argument('--filein'   , dest='filein'      , default=''           , help='Specify the input ntuple name. Default none, it will pick up files automatically')
parser.add_argument('--logfreq'  , dest='logfreq'     , default=100, type=int, help='Print processing status every N events. Default N = 100')

args = parser.parse_args() 

genuine_taus = args.genuine_taus
maxevents    = args.maxevents
filein       = args.filein
fileout      = args.fileout
logfreq      = args.logfreq

# files = dy_files if genuine_taus else qcd_files
# files = ['/eos/cms/store/group/phys_tau/ProdNanoAODv5DeepTau/2018/11June19_v1/WW_TuneCP5_13TeV-pythia8/NanoAODv5DeepTau/190612_161100/0000/myNanoProdMc2018_NANO_59.root']
# files = ['dy.root']

# files = glob.glob('/eos/cms/store/group/phys_tau/ProdNanoAODv5DeepTau/2018/13June19_v3/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/Autumn18-from_102X_upgrade2018_realistic_v15_ver1-NanoAODv5DeepTau/190613_102255/0000/*root')
files = glob.glob('/eos/cms/store/group/phys_tau/ProdNanoAODv5DeepTau/2018/13June19_v3/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/Autumn18-from_FlatPU0to70_102X_upgrade2018_realistic_v15_ver1-NanoAODv5DeepTau/190613_102219/0000/*root')

if len(fileout)==0:
    fileout = 'dy_gen_tuple.root' if genuine_taus else 'qcd_gen_tuple.root'

##########################################################################################
# initialise output files to save the flat ntuples
outfile_tau = ROOT.TFile(fileout, 'recreate')
branches_all_names = [br.name() for br in branches_all]
ntuple_tau = ROOT.TNtuple('tree', 'tree', ':'.join(branches_all_names))
tofill_tau = OrderedDict(zip(branches_all_names, [-99.]*len(branches_all_names))) # initialise all branches to unphysical -99       

##########################################################################################
# Get ahold of the events
events = ROOT.TChain('Events')
print 'loading files ...'
for ifile in files:
    events.Add(ifile)
print '... done!'
maxevents = maxevents if maxevents>=0 else events.GetEntries() # total number of events in the files

##########################################################################################
# start looping on the events
start = time()
for i, ev in enumerate(events):
    
    ######################################################################################
    # controls on the events being processed
    if maxevents>0 and i>maxevents:
        break
        
    if i%logfreq==0:
        percentage = float(i)/maxevents*100.
        speed = float(i)/(time()-start)
        eta = datetime.now() + timedelta(seconds=(maxevents-i) / max(0.1, speed))
        print '===> processing %d / %d event \t completed %.1f%s \t %.1f ev/s \t ETA %s s' %(i, maxevents, percentage, '%', speed, eta.strftime('%Y-%m-%d %H:%M:%S'))

    ######################################################################################
    # fill the ntuple: each reco tau makes an entry
    for igen in range(ev.nGenVisTau): 
        
        # initialise before filling
        for k, v in tofill_tau.iteritems(): tofill_tau[k] = -99. 
    
        # per event quantities
        for ibranch in branches_event:
            tofill_tau[ibranch.name()] = ibranch.value(ev)

        # per gen tau quantities
        for ibranch in branches_gen:
            tofill_tau[ibranch.name()] = ibranch.value(ev)[igen]

        # loop on all reco taus and match to gen taus
        best_match_idx_tau = -1
        dRmax = 0.3
        for itau in range(ev.nTau):
            dR = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], ev.GenVisTau_eta[igen], ev.GenVisTau_phi[igen])
            if dR > dRmax: continue
            dRmax = dR
            best_match_idx_tau = itau
    
        # if a match is found fill reco tau quantities
        if best_match_idx_tau>=0:
            for ibranch in branches_tau:
                tofill_tau[ibranch.name()] = ibranch.value(ev)[best_match_idx_tau]
 
            # per jet quantities, find the reco jet that matches best, aka tau seed (if any)
            best_match_idx_jet = ev.Tau_jetIdx[best_match_idx_tau]
            if best_match_idx_jet>=0:
                for ibranch in branches_jet:
                    tofill_tau[ibranch.name()] = ibranch.value(ev)[best_match_idx_jet]
        
        # fill the tree
        ntuple_tau.Fill(array('f', prepareBranches(tofill_tau.values())))

##########################################################################################
# write the ntuples and close the files
outfile_tau.cd()
ntuple_tau .Write()
outfile_tau.Close()

