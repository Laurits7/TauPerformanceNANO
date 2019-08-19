import os
from glob import glob

hostName = os.environ['HOSTNAME']

# Fetch the files stored on EOS at CERN
if 'lxplus' in hostName:
    dy_files  = glob('/store/group/phys_tau/ProdNanoAODv4Priv/16dec18/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ver1/181216_125011/0000/myNanoRunMc2018_NANO_*.root')
    qcd_files = glob('/store/group/phys_tau/ProdNanoAODv4Priv/16dec18/QCD_Pt-15to7000_TuneCP5_Flat2018_13TeV_pythia8/RunIIAutumn18NanoAODv4Priv-from_102X_upgrade2018_realistic_v15_ext1_ver1/190125_113318/0000/myNanoRunMc2018_NANO_*.root')


# Fetch the files stored in Pisa
if 'faiwn' in hostName or 'gridui':

    ntuple_dir = '/gpfs/ddn/cms/user/cmsdas/2019/TauExercise/'

    dy_files  = glob('/'.join([ntuple_dir, 'dy' , 'myNanoRunMc2018_NANO_*.root']))
    qcd_files = glob('/'.join([ntuple_dir, 'qcd', 'myNanoRunMc2018_NANO_*.root']))
