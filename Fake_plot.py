import ROOT
import numpy as np
from cmsstyle import CMS_lumi
import math

##########################################################################################
# Argument Parser to manage options
import sys
rootfiles  = sys.argv[1:]

if len(rootfiles)==0:
  print "Usage: Add ntuple root files as arguments"
  exit()

# https://codereview.stackexchange.com/questions/145850/subclassing-int-to-make-colors
class Color(int):
    """Create a new ROOT.TColor object with an associated index"""
    __slots__ = ["object"]

    def __new__(cls, r, g, b, a=1.0):
        """Constructor. r, g, b and a are in [0, 1]"""
        # Explicitly use floats here to disambiguate
        # between the two TColor constructors
        color = ROOT.TColor(float(r), float(g), float(b), float(a))
        self = int.__new__(cls, color.GetNumber())
        self.object = color
        return self

def DrawThis(onetree):
  c2 = ROOT.TCanvas('c2','',700,700)
  c2.cd()
  c2.Draw()
  for effidx, eff in enumerate(iso_efficiencies):
    if 'raw' in var:
      options = 'a'*(effidx!=0) + 'pl' + ' same'*(effidx!=0)
      ROOT.gStyle.SetOptStat(0)
    else:
      options = 'a'*(effidx==0) + 'pl' + ' same'*(effidx!=0)
    eff.Draw(options)
    eff.SetFillColor(0)
    eff.SetTitle('; '+Xtitles[varidx]+'; fake rate')
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    ROOT.gPad.Update()
    ROOT.gPad.SetTicky(1)
    ROOT.gPad.SetLogy('raw' not in var)

    if 'raw' in var:
      eff.GetYaxis().SetTitleOffset(1.35)
      eff.GetYaxis().SetRangeUser(minim-0.5*(maxim*1.05-minim), maxim*1.05)
      eff.GetXaxis().SetRangeUser(Xranges[varidx][0], Xranges[varidx][1])
    else:
      eff.GetPaintedGraph().GetYaxis().SetTitleOffset(1.35)
      # Logscale: Fix if no labels on y axis due to small range:
      #minim/math.sqrt(maxim*1.1/minim), maxim*1.1
      maximdef = maxim*1.1
      minimdef = minim/math.sqrt(maxim/minim)
      onelabel = False
      for loops in [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]:
         onelabel = onelabel or ((maximdef>=loops) and (minimdef<=loops))
      if not onelabel:
        for loops in [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]:
          if maximdef > loops:
            minimdef = minimdef/(loops*11.0/maximdef)
            maximdef = loops * 11.0
            break

      twolabels = False
      for loops in [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]:
         twolabels = twolabels or ((maximdef>=loops) and (minimdef<=loops/10.0))
      if not twolabels:
        for loops in [1.0, 0.1, 0.01, 0.001, 0.0001, 0.00001, 0.000001, 0.0000001, 0.00000001, 0.000000001]:
          if minimdef > loops:
            minimdef = loops * 0.9
            break

      eff.GetPaintedGraph().GetYaxis().SetRangeUser(minimdef, maximdef) # Yranges[varidx][0], Yranges[varidx][1]
      #eff.GetPaintedGraph().GetYaxis().SetRangeUser(0.005, 0.035)
      eff.GetPaintedGraph().GetXaxis().SetRangeUser(Xranges[varidx][0], Xranges[varidx][1])

    CMS_lumi(ROOT.gPad, lumiindex, 0)
    ROOT.gPad.Update()

  if not onetree: leg.SetHeader("Fake #tau_{h} from " + samplename + ", " + num[1], "C")
  leg.Draw('same')
  ROOT.gPad.Update()
  for iformat in ['png']: # , 'pdf'
    savename = 'fake_'+var
    if not onetree: savename = 'fake_'+var+'_'+str(numidx)
    if doJet and (WhatAreFakes.lower() not in savename): savename = savename + '_' + WhatAreFakes.lower()
    ROOT.gPad.SaveAs(savename+'.%s' %iformat)
  del c2

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)

########## SETUP

# Luminosity (hardcoded, because I think it isn't changed much, so it's easier like this)
lumiindex = 4 # 13 TeV
#lumiindex = 5 # 14 TeV
if 'ttbar' in rootfiles[0].lower():
  samplename = "TTbar"
  WhatAreFakes = 'Jet'
elif 'zmm' in rootfiles[0].lower():
  samplename = "ZMM"
  WhatAreFakes = 'Mu'
elif 'zee' in rootfiles[0].lower():
  samplename = "ZEE"
  WhatAreFakes = 'El'
else: #Hardcoded
  samplename = "TTbar"
  WhatAreFakes = 'Jet' # Options: Jet, El, Mu

# pT, eta, phi, PU
variables = ['tau_pt', 'tau_eta', 'tau_phi', 'ntrueint']
binnings = [np.array(range(18, 30, 2) + range(30, 40, 5) + range(40, 100, 10) + range(100, 200, 50) + [200., 500., 1000., 5000.], dtype=float), np.array([x/10.0 for x in range(-24, 25, 2)], dtype=float), np.array([x/10.0 for x in range(-32, 33, 4)], dtype=float), np.array(range(0, 100, 1), dtype=float)]
Xtitles = ['#tau_{h} p_{T} (GeV)', '#tau_{h} #eta', '#tau_{h} #phi', 'number of true interactions']
Xranges = [[19.9999, 150.0001], [-2.6001, 2.6001], [-3.2001, 3.2001], [0, 75.0001]]
Yranges = [[1e-5, 0.3], [1e-5, 0.3], [1e-5, 0.3], [5e-4, 0.3]]
# Raw discriminators
variables += ['tau_rawIso', 'tau_rawMVAnewDM2017v2', 'tau_rawDeepTau2017v2p1VSe', 'tau_rawDeepTau2017v2p1VSmu', 'tau_rawDeepTau2017v2p1VSjet', 'tau_rawAntiEle']
Xtitles += ['raw Isolation', 'raw MVA TauID 2017v2', 'raw DeepTau 2017v2p1 against electrons', 'raw DeepTau 2017v2p1 against muons', 'raw DeepTau 2017v2p1 against jets', 'raw Anti-electron']
binnings += [np.array([x/2.0 for x in range(0, 21, 1)], dtype=float)]
Xranges += [[0, 10.0001]]
for i in range(5):
  binnings += [np.array([x/20.0 for x in range(0, 21, 1)], dtype=float)]
  Xranges += [[0, 1.0001]]
# Kinds of fakes
KindOfFake = {
'Jet' : ['tau_idDeepTau2017v2p1VSjet', 'tau_jet_pt', 'tau_jet_eta'],
'El' : ['tau_idDeepTau2017v2p1VSe', 'tau_ele_pt', 'tau_ele_eta'],
'Mu' : ['tau_idDeepTau2017v2p1VSmu', 'tau_mu_pt', 'tau_mu_eta'],
}
# Reco Tau pT, Jet pT
pt_cut = 20
denominators = ['1', '1'] #['tau_gen_pt<0', 'tau_gen_pt<0']
#if WhatAreFakes == 'El': ['tau_gen_pt<0 && tau_idAntiEle>0.5', 'tau_gen_pt<0 && tau_idAntiEle>0.5']
#if WhatAreFakes == 'Mu': ['tau_gen_pt<0 && tau_idAntiMu>0.5', 'tau_gen_pt<0 && tau_idAntiMu>0.5']
#denominators = ['&'.join(['tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_gen_pt<0']), '&'.join(['tau_jet_pt>%d' %pt_cut, 'abs(tau_jet_eta)<2.3', 'tau_gen_pt<0'])]
leptondiscr = '1'#'tau_idDeepTau2017v2p1VSjet>0.5 && tau_idDeepTau2017v2p1VSmu>0.5 && tau_idDeepTau2017v2p1VSe>0.5'
numerators = []
for i in range(len(denominators)):
  numerators.append([
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3']), 'new Decay Mode with 2-prong'   ),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6']), 'new Decay Mode without 2-prong'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=3'])    , 'MVA TauID 2017v2 Loose'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=4'])    , 'MVA TauID 2017v2 Medium'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=5'])    , 'MVA TauID 2017v2 Tight'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=6'])    , 'MVA TauID 2017v2 VTight'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', KindOfFake[WhatAreFakes][0]+'>=3']), 'DeepTau 2017v2 VLoose'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', KindOfFake[WhatAreFakes][0]+'>=4']), 'DeepTau 2017v2 Loose'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', KindOfFake[WhatAreFakes][0]+'>=5']), 'DeepTau 2017v2 Medium'),
    ('&'.join([denominators[i], leptondiscr, 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', KindOfFake[WhatAreFakes][0]+'>=6']), 'DeepTau 2017v2 Tight'),
    #('&'.join([denominators[i], 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2p1VSjet>=7']), 'DeepTau 2017v2 VTight'),
    ])

# colour palette
# https://gist.github.com/gipert/df72b67c1d02bbb41f1dd406b6397811
# https://personal.sron.nl/~pault/data/colourschemes.pdf
freeID = ROOT.TColor.GetFreeColorIndex()
sunset_palette = [[ # For plotting all WPs in one plot
    Color(  0./255,   0./255,   0./255), # black
    Color(136./255, 136./255, 136./255), # gray

    Color( 54./255,  75./255, 154./255), # blue
    Color( 74./255, 123./255, 183./255),
    Color(110./255, 166./255, 205./255),
    Color(152./255, 202./255, 225./255), # ...lighter

    Color(221./255,  61./255,  45./255), # red
    Color(246./255, 126./255,  75./255),
    Color(253./255, 179./255, 102./255),
    Color(254./255, 218./255, 139./255), # ...lighter
],[ # For plotting different years in one plot
    Color(  0./255,   0./255,   0./255), # black
    Color( 54./255,  75./255, 154./255), # blue
    Color(221./255,  61./255,  45./255), # red
    Color( 27./255, 120./255,  55./255), # green
    Color(118./255,  42./255, 131./255), # purple

]]


files = []
trees = []
for file in rootfiles:
  files.append(ROOT.TFile.Open(file, 'read'))
  files[-1].cd()
  trees.append(files[-1].Get('tree'))

for varidx,var in enumerate(variables):
  for doJet in range(2): # len(denominators)
    if not doJet: continue # These plots aren't that interesting, and also require different Y range lists

    if doJet:
      if var == 'tau_pt': var = KindOfFake[WhatAreFakes][1]
      if var == 'tau_eta': var = KindOfFake[WhatAreFakes][2]
      if WhatAreFakes.lower() in var: Xtitles[varidx] = WhatAreFakes + ' ' + Xtitles[varidx] # Okay to overwrite because it does Reco first anyway

    histo_dens = []
    histnames = []

    c1 = ROOT.TCanvas('c1','',700,700)
    c1.Draw()

    for i,tree in enumerate(trees):
      histnames.append('h_'+var+'_'+str(i))
      histo_dens.append(ROOT.TH1F(histnames[-1], '', len(binnings[varidx])-1, binnings[varidx]))
      tree.Draw(var+' >> '+histnames[-1], denominators[doJet])

    leg = ROOT.TLegend(.11,.12,.89,.35)
    leg.SetHeader("Fake #tau_{h} from " + samplename, "C") # QCD flat #hat{p}_{T} 15-7000 GeV
    leg.SetBorderSize(0)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetNColumns(2)

    histo_iso_pu_nums = []
    iso_efficiencies = []
    maxim = 0.001
    minim = 1.0
    for numidx, num in enumerate(numerators[doJet]):
      for i,tree in enumerate(trees):
        if 'raw' not in var:
          histo_iso_pu_num = ROOT.TH1F(histnames[i]+'_%s'%num[1].replace(' ', ''), '', len(binnings[varidx])-1, binnings[varidx])
          tree.Draw(var+' >> %s'%histo_iso_pu_num.GetName(), num[0])
          histo_iso_pu_nums.append(histo_iso_pu_num)
          iso_efficiency = ROOT.TEfficiency(histo_iso_pu_num, histo_dens[i])
          for bin in range(1,len(binnings[varidx])):
            thisef = iso_efficiency.GetEfficiency(bin)
            thiser = max(iso_efficiency.GetEfficiencyErrorLow(bin), iso_efficiency.GetEfficiencyErrorUp(bin))
            if thiser < 0.5:
              if thisef > maxim: maxim = thisef
              if thisef < minim and thisef != 0: minim = thisef
        elif numidx==1:
          iso_efficiency = ROOT.TH1F(histnames[i]+'_%s'%num[1].replace(' ', ''), '', len(binnings[varidx])-1, binnings[varidx])
          tree.Draw(var+' >> %s'%iso_efficiency.GetName(), num[0])
          #tree.Project(iso_efficiency.GetName(), var, num[0])
          if iso_efficiency.Integral(0, iso_efficiency.GetNbinsX() + 1) > 0:
            iso_efficiency.Scale(1. / iso_efficiency.Integral(0, iso_efficiency.GetNbinsX() + 1))
          for bin in range(1,len(binnings[varidx])):
            thisef = iso_efficiency.GetBinContent(bin)
            thiser = max(iso_efficiency.GetBinErrorLow(bin), iso_efficiency.GetBinErrorUp(bin))
            if thiser < 0.5:
              if thisef > maxim: maxim = thisef
              if thisef < minim: minim = thisef
        else: continue # No point plotting MVA/DeepTau WPs over raw variables

        if len(trees)==1:
          iso_efficiency.SetLineColor(sunset_palette[0][numidx])
          leg.AddEntry(iso_efficiency, num[1])
        else:
          iso_efficiency.SetLineColor(sunset_palette[1][i])
          leg.AddEntry(iso_efficiency, rootfiles[i].replace('.root', ''))
        iso_efficiency.SetLineWidth(2)
        iso_efficiency.SetFillColor(ROOT.kWhite)
        iso_efficiency.Draw('apl')
        iso_efficiencies.append(iso_efficiency)

      if len(trees)>1: # For plotting different years in one plot
        if numidx!=1 and 'raw' in var: continue
        DrawThis(False)
        del leg
        leg = ROOT.TLegend(.11,.12,.89,.35)
        leg.SetHeader("Fake #tau_{h} from " + samplename, "C") # QCD flat #hat{p}_{T} 15-7000 GeV
        leg.SetBorderSize(0)
        leg.SetFillColor(ROOT.kWhite)
        leg.SetFillStyle(1001)
        leg.SetNColumns(2)
        histo_iso_pu_nums = []
        iso_efficiencies = []
        maxim = 0.01
        minim = 1.0


    if len(trees)==1: # For plotting all WPs in one plot
      DrawThis(True)

    del c1
    del leg

exit()
