import ROOT
from time import time
from datetime import datetime, timedelta
from array import array
from collections import OrderedDict
import math
import subprocess
import glob

from deltar import deltaR, deltaPhi

def MatchTausToRefs(DoubleCountRate, RefObj):

  # For each Ref, get the closest RecoTau
  Match = {}
  for iref in RefObj:
    best_match_idx = -1
    dRmax = 0.5
    for itau in range(ev.nTau):
      #if ev.Tau_jetIdx[itau] >= 0: # Is this needed?
      dR = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], GetRefEta(iref), GetRefPhi(iref))
      if dR > dRmax: continue
      dRmax = dR
      best_match_idx = itau
    if best_match_idx>=0: Match[iref]=best_match_idx

  # Is the same Tau assinged to more than one Ref?
  DoubleCheck = []
  for iref,itau in Match.iteritems():
    for jref,jtau in Match.iteritems():
      if jref >= iref: continue
      if itau==jtau:
        if iref not in DoubleCheck: DoubleCheck.append(iref)
        if jref not in DoubleCheck: DoubleCheck.append(jref)
  if DoubleCheck != []: DoubleCountRate += 1

  # Get all distances between all conflicting Refs and corresponding Taus
  Distances = {}
  for iref in DoubleCheck:
    for jref in DoubleCheck:
      itau = Match[jref]
      Distances[str(iref)+"_"+str(itau)] = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], GetRefEta(iref), GetRefPhi(iref))

  # Remove all conflicting Refs, to re-assign later
  for iref in DoubleCheck:
    del Match[iref]

  # Assign shortest distance between Tau and Ref, then move on ignoring the already assigned Taus/Refs
  while Distances != {}:
    keepthis = min(Distances, key=Distances.get)
    thisref = int(keepthis[:keepthis.find("_")])
    thistau = int(keepthis[keepthis.rfind("_")+1:])
    Match[thisref] = thistau
    deletethis = []
    for element in Distances:
      if element.startswith(str(thisref)) or element.endswith(str(thistau)): deletethis.append(element)
    for element in deletethis: del Distances[element]

  return Match, DoubleCountRate

def GetRefEta(iref):
  if doEff:
    return ev.GenVisTau_eta[iref]
  elif useRecoJets:
    return ev.Jet_eta[iref]
  elif useFakeEle or useFakeMu:
    return ev.GenPart_eta[iref]
  else:
    return ev.GenJet_eta[iref]

def GetRefPhi(iref):
  if doEff:
    return ev.GenVisTau_phi[iref]
  elif useRecoJets:
    return ev.Jet_phi[iref]
  elif useFakeEle or useFakeMu:
    return ev.GenPart_phi[iref]
  else:
    return ev.GenJet_phi[iref]

# here the ntuple branches, and how to get the quantities stored in such branches, are defined
from treeVariables import branches_event, branches_tau, branches_gen, branches_jet, branches_ele, branches_mu, branches_genjet, branches_all, prepareBranches

##########################################################################################
# Argument Parser to manage options
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--maxevents', dest='maxevents'   , default=-1, type=int  , help='Events to process. Default = -1 --> process all events')
parser.add_argument('--output'   , dest='output'      , default=''            , help='Specify the output ntuple name.')
parser.add_argument('--dir'      , dest='dir'         , default='/eos/user/d/dmroy/TauVal' , help='Directory containing sets of nAOD root files.')
parser.add_argument('--file'     , dest='file'        , default=''            , help='Specify the input ntuple name.')
parser.add_argument('--logfreq'  , dest='logfreq'     , default=1000, type=int, help='Print processing status every N events. Default N = 100')
parser.add_argument('--eff'      , dest='doeff'       , action='store_true'   , help='Process samples for efficiency (ZTT, TauGun)')
parser.add_argument('--fake'     , dest='dofake'      , action='store_true'   , help='Process samples for fake rates (TTbar, QCD)')
parser.add_argument('--recojets' , dest='recojets'    , action='store_true'   , help='For fakes, match Taus to Reco jets instead of Gen jets')
parser.add_argument('--fakeele'  , dest='fakeele'     , action='store_true'   , help='For fakes, match Taus to Reco electrons instead of Gen jets')
parser.add_argument('--fakemu'   , dest='fakemu'      , action='store_true'   , help='For fakes, match Taus to Reco muons instead of Gen jets')
parser.add_argument('--tentau  ' , dest='tentau'      , action='store_true'   , help='Specify when using TenTau/TauGun sample!')

args = parser.parse_args()

maxevents    = args.maxevents
file         = args.file
fileout      = args.output
dir_         = args.dir
logfreq      = args.logfreq
doEff        = args.doeff
doFake       = args.dofake
useRecoJets  = args.recojets
useFakeEle   = args.fakeele
useFakeMu    = args.fakemu
TenTau       = args.tentau

if (doEff and doFake) or ((not doEff) and (not doFake)):
  print "What do you want? Efficiencies or fake rates?"
  exit()

# Where to read nAODs from
files = glob.glob(dir_+"/"+file+"/*.root")

if len(files)==0:
  print "What files should be used?"
  exit()
if len(fileout)==0:
    fileout = file + ".root"

##########################################################################################
# initialise output files to save the flat ntuples
outfile_tau = ROOT.TFile(fileout, 'recreate')
branches_all_names = [br.name() for br in branches_all]
ntuple_tau = ROOT.TNtuple('tree', 'tree', ':'.join(branches_all_names))
tofill_tau = OrderedDict(zip(branches_all_names, [-999.]*len(branches_all_names))) # initialise all branches to unphysical -999

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
DoubleCountRate = 0
for i, ev in enumerate(events):
    AlreadyMatched = []
    
    ######################################################################################
    # controls on the events being processed
    if maxevents>0 and i>maxevents:
        break
        
    if (i%logfreq==0) and (i>0):
        percentage = float(i)/maxevents*100.
        speed = float(i)/(time()-start)
        eta = datetime.now() + timedelta(seconds=(maxevents-i) / max(0.1, speed))
        print '===> processing %d / %d event \t completed %.1f%s \t %.1f ev/s \t ETA %s s' %(i, maxevents, percentage, '%', speed, eta.strftime('%Y-%m-%d %H:%M:%S'))
        print "DoubleCountRate:",float(DoubleCountRate)/i

    if doEff:
      ######################################################################################
      # fill the ntuple: each reco tau makes an entry
      GoodGenTaus = []
      for igen in range(ev.nGenVisTau):
          if ev.GenVisTau_pt[igen] < 10: continue
          if abs(ev.GenVisTau_eta[igen]) > 2.3: continue
          if TenTau:
            skipthis = 0
            for jgen in range(ev.nGenVisTau):
              if igen==jgen: continue
              if deltaR(ev.GenVisTau_eta[igen], ev.GenVisTau_phi[igen], ev.GenVisTau_eta[jgen], ev.GenVisTau_phi[jgen]) < 0.5:
                skipthis=1
                break
            if skipthis==1: continue
          GoodGenTaus.append(igen)

          ###########################

      Matched, DoubleCountRate = MatchTausToRefs(DoubleCountRate, GoodGenTaus)

      for igen in GoodGenTaus:
          # initialise before filling
          for k, v in tofill_tau.iteritems(): tofill_tau[k] = -999

          # per event quantities
          for ibranch in branches_event:
              tofill_tau[ibranch.name()] = ibranch.value(ev)

          # per gen tau quantities
          for ibranch in branches_gen:
              tofill_tau[ibranch.name()] = ibranch.value(ev)[igen]

          # loop on all reco taus and match to gen taus
          #best_match_idx_tau = -1
          #dRmax = 0.5
          #for itau in range(ev.nTau):
          #    dR = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], ev.GenVisTau_eta[igen], ev.GenVisTau_phi[igen])
          #    if dR > dRmax: continue
          #    dRmax = dR
          #    best_match_idx_tau = itau

          if igen in Matched:
              best_match_idx_tau = Matched[igen]

              # if a match is found fill reco tau quantities
              for ibranch in branches_tau:
                  tofill_tau[ibranch.name()] = ibranch.value(ev)[best_match_idx_tau]

              # per jet quantities, find the reco jet that matches best, aka tau seed (if any)
              best_match_idx_jet = ev.Tau_jetIdx[best_match_idx_tau]
              if best_match_idx_jet>=0:
                  for ibranch in branches_jet:
                      tofill_tau[ibranch.name()] = ibranch.value(ev)[best_match_idx_jet]

          # fill the tree
          ntuple_tau.Fill(array('f', prepareBranches(tofill_tau.values())))

    elif doFake:
      ######################################################################################
      # fill the ntuple: each good jet makes an entry
      GoodJets = []
      if useRecoJets:
        njet = ev.nJet
      elif useFakeEle or useFakeMu:
        njet = ev.nGenPart
      else:
        njet = ev.nGenJet
      for ijet in range(njet):
          if useRecoJets:
            jetpt = ev.Jet_pt[ijet]
            jeteta = ev.Jet_eta[ijet]
            jetphi = ev.Jet_phi[ijet]
            jetgenidx = ev.Jet_genJetIdx[ijet]
          elif useFakeEle or useFakeMu:
            jetpt = ev.GenPart_pt[ijet]
            jeteta = ev.GenPart_eta[ijet]
            jetphi = ev.GenPart_phi[ijet]
            jetgenidx = ijet
          else:
            jetpt = ev.GenJet_pt[ijet]
            jeteta = ev.GenJet_eta[ijet]
            jetphi = ev.GenJet_phi[ijet]
            jetgenidx = ijet

          # save only if jet pt > 20 GeV, in tracker acceptance and true jet (no e, m, t)
          if jetpt < 20: continue
          if abs(jeteta) > 2.3: continue
          if (jetgenidx < 0) or (jetgenidx >= ev.nGenJet): continue # Only for Recojets

          ###########################
          # check pollution from non jets (compare to GenJet regardless of whether Reco or Gen jets are used for Tau matching)
          ###########################
          badjet = 0
          if useFakeEle or useFakeMu:
            if (useFakeEle and abs(ev.GenPart_pdgId[ijet])!=11) or (useFakeMu and abs(ev.GenPart_pdgId[ijet])!=13): continue
            if not ((ev.GenPart_statusFlags[ijet] >> 0 & 1) or ((ev.GenPart_status[ijet] == 1) and (ev.GenPart_statusFlags[ijet] >> 5 & 1))): continue # "isPrompt()" or "isDirectPromptTauDecayProductFinalState()" requirement
          else:
            for igen in xrange(ev.nGenPart):
              if abs(ev.GenPart_pdgId[igen]) not in [11, 13, 15]: continue #, 15
              if ev.GenPart_pt[igen] < 15: continue
              if ev.GenPart_status[igen] != 1: continue

              seleclep = (abs(ev.GenPart_pdgId[igen]) in [11, 13]) and (ev.GenPart_statusFlags[igen] >> 0 & 1) # "isPromptFinalState()" requirement
              selectau = (abs(ev.GenPart_pdgId[igen]) == 15) and (ev.GenPart_statusFlags[igen] >> 1 & 1) and (ev.GenPart_statusFlags[igen] >> 0 & 1) # "isPromptDecayed()" requirement
              if not (seleclep or selectau): continue # 1-to-1 from miniAOD setup

              dR = deltaR(ev.GenPart_eta[igen], ev.GenPart_phi[igen], ev.GenJet_eta[jetgenidx], ev.GenJet_phi[jetgenidx])
              if dR < 0.50:
                badjet = 1
                break
          if badjet == 0: GoodJets.append(ijet)
          ###########################

      Matched, DoubleCountRate = MatchTausToRefs(DoubleCountRate, GoodJets)

      for ijet in GoodJets:
          # initialise before filling
          for k, v in tofill_tau.iteritems(): tofill_tau[k] = -999

          # per event quantities
          for ibranch in branches_event:
              tofill_tau[ibranch.name()] = ibranch.value(ev)

          # per jet quantities, find the reco jet that matches best, aka tau seed (if any)
          if useRecoJets:
            for ibranch in branches_jet:
              tofill_tau[ibranch.name()] = ibranch.value(ev)[ijet]
          elif useFakeEle:
            for ibranch in branches_ele:
              tofill_tau[ibranch.name()] = ibranch.value(ev)[ijet]
          elif useFakeMu:
            for ibranch in branches_mu:
              tofill_tau[ibranch.name()] = ibranch.value(ev)[ijet]
          else:
            for ibranch in branches_genjet:
              tofill_tau[ibranch.name()] = ibranch.value(ev)[ijet]

          # loop on reco taus and save them if they match to -THIS- jet
          #best_match_idx = -1
          #dRmaxJET = 0.5
          #for itau in range(ev.nTau):
          #    if ev.Tau_jetIdx[itau] >= 0: # Is this needed?
          #        dR = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], jeteta, jetphi)
          #        if dR > dRmaxJET: continue
          #        dRmaxJET = dR
          #        best_match_idx = itau
          #if best_match_idx>=0:
          if ijet in Matched:
              itau = Matched[ijet]
              for ibranch in branches_tau:
                   tofill_tau[ibranch.name()] = ibranch.value(ev)[itau]

              # per gen tau quantities, find the gen visible tau that matches best (if any)
              best_match_idx = -1
              dRmax = 0.3
              for igen in range(ev.nGenVisTau): 
                  dR = deltaR(ev.Tau_eta[itau], ev.Tau_phi[itau], ev.GenVisTau_eta[igen], ev.GenVisTau_phi[igen])
                  if dR > dRmax: continue
                  dRmax = dR
                  best_match_idx = igen
              if best_match_idx>=0:
                  for ibranch in branches_gen:
                      tofill_tau[ibranch.name()] = ibranch.value(ev)[best_match_idx]

          # fill the tree
          ntuple_tau.Fill(array('f', prepareBranches(tofill_tau.values())))

##########################################################################################
# write the ntuples and close the files
outfile_tau.cd()
ntuple_tau.Write()
outfile_tau.Close()

