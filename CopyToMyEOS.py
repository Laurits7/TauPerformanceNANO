import subprocess
import os

result = subprocess.check_output("dasgoclient --query='file dataset=/RelValTTbar_13/CMSSW_11_0_0_pre13-PU25ns_110X_mcRun2_asymptotic_v5-v1/NANOAODSIM'", shell=True) # instance=prod/phys03 system=dbs3

# dataset=/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIIAutumn18NanoAODv5_v1-DeepTauv2_TauPOG-v1/USER

files = ["root://cms-xrd-global.cern.ch/" + s.strip() for s in result.splitlines()]

#files = files[:104] # Take subset

# Have to make folder manually??
for f in files:
  os.system('xrdcp -f '+f+' /eos/user/d/dmroy/TauVal/Final_mininano_TTbar/')
