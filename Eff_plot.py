import ROOT
import numpy as np
from cmsstyle import CMS_lumi

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
    eff.SetTitle('; '+Xtitles[varidx]+'; efficiency')
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    ROOT.gPad.Update()
    ROOT.gPad.SetTicky(1)
    ROOT.gPad.SetLogx(False)
    if 'raw' in var:
      eff.GetYaxis().SetRangeUser(minim-0.5*(maxim*1.05-minim), maxim*1.05)
      eff.GetXaxis().SetRangeUser(Xranges[varidx][0], Xranges[varidx][1])
    else:
      eff.GetPaintedGraph().GetYaxis().SetRangeUser(minim-0.5*(maxim*1.05-minim), maxim*1.05)
      eff.GetPaintedGraph().GetXaxis().SetRangeUser(Xranges[varidx][0], Xranges[varidx][1])

    CMS_lumi(ROOT.gPad, lumiindex, 0)
    ROOT.gPad.Update()

  if not onetree: leg.SetHeader("Genuine #tau_{h} from " + samplename + ", " + num[1], "C")
  leg.Draw('same')
  ROOT.gPad.Update()
  for iformat in ['png']: # , 'pdf'
    savename = 'eff_'+var
    if not onetree: savename = 'eff_'+var+'_'+str(numidx)
    if doGen and ('gen' not in savename): savename = savename + '_gen'
    ROOT.gPad.SaveAs(savename+'.%s' %iformat)
  del c2

ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True)

########## SETUP

# Luminosity (hardcoded, because I think it isn't changed much, so it's easier like this)
lumiindex = 4 # 13 TeV
#lumiindex = 5 # 14 TeV
samplename = "DY#rightarrow#tau#tau"

# pT, eta, phi, PU
variables = ['tau_pt', 'tau_eta', 'tau_phi', 'ntrueint']
binnings = [np.array(range(18, 30, 2) + range(30, 40, 5) + range(40, 100, 10) + range(100, 200, 50) + [200., 500., 1000., 5000.], dtype=float), np.array([x/10.0 for x in range(-24, 25, 2)], dtype=float), np.array([x/10.0 for x in range(-32, 33, 4)], dtype=float), np.array(range(0, 100, 1), dtype=float)]
Xtitles = ['#tau_{h} p_{T} (GeV)', '#tau_{h} #eta', '#tau_{h} #phi', 'number of true interactions']
Xranges = [[19.9999, 150.0001], [-2.6001, 2.6001], [-3.2001, 3.2001], [0, 75.0001]]
# Raw discriminators
variables += ['tau_rawIso', 'tau_rawMVAnewDM2017v2', 'tau_rawDeepTau2017v2p1VSe', 'tau_rawDeepTau2017v2p1VSmu', 'tau_rawDeepTau2017v2p1VSjet', 'tau_rawAntiEle']
Xtitles += ['raw Isolation', 'raw MVA TauID 2017v2', 'raw DeepTau 2017v2p1 against electrons', 'raw DeepTau 2017v2p1 against muons', 'raw DeepTau 2017v2p1 against jets', 'raw Anti-electron']
binnings += [np.array([x/2.0 for x in range(0, 21, 1)], dtype=float)]
Xranges += [[0, 10.0001]]
for i in range(5):
  binnings += [np.array([x/20.0 for x in range(0, 21, 1)], dtype=float)]
  Xranges += [[0, 1.0001]]
# Reco pT, Gen pT
pt_cut = 20
denominators = ['1', '1'] #['tau_gen_pt < 150', 'tau_gen_pt < 150']
#denominators = ['&'.join(['tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3']), '&'.join(['tau_gen_pt>%d'%pt_cut, 'abs(tau_gen_eta)<2.3'])]
numerators = []
for i in range(len(denominators)):
  numerators.append([
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3']), 'new Decay Mode with 2-prong'   ),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6']), 'new Decay Mode without 2-prong'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=3'])    , 'MVA TauID 2017v2 Loose'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=4'])    , 'MVA TauID 2017v2 Medium'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=5'])    , 'MVA TauID 2017v2 Tight'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=6'])    , 'MVA TauID 2017v2 VTight'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2p1VSjet>=3']), 'DeepTau 2017v2 VLoose'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2p1VSjet>=4']), 'DeepTau 2017v2 Loose'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2p1VSjet>=5']), 'DeepTau 2017v2 Medium'),
    ('&'.join([denominators[i], 'tau_idDecayModeNewDMs>=0', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2p1VSjet>=6']), 'DeepTau 2017v2 Tight'),
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
  for doGen in range(2): # len(denominators)
    if not doGen: continue # Not too interessting

    if doGen:
      if var == 'tau_pt': var = 'tau_gen_pt'
      if var == 'tau_eta': var = 'tau_gen_eta'
      if 'gen' in var: Xtitles[varidx] = 'Gen ' + Xtitles[varidx] # Okay to overwrite because it does Reco first anyway

    histo_dens = []
    histnames = []

    c1 = ROOT.TCanvas('c1','',700,700)
    c1.Draw()

    for i,tree in enumerate(trees):
      histnames.append('h_'+var+'_'+str(i))
      histo_dens.append(ROOT.TH1F(histnames[-1], '', len(binnings[varidx])-1, binnings[varidx]))
      tree.Draw(var+' >> '+histnames[-1], denominators[doGen])

    leg = ROOT.TLegend(.11,.12,.89,.35)
    leg.SetHeader("Genuine #tau_{h} from " + samplename, "C")
    leg.SetBorderSize(0)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    leg.SetNColumns(2)

    histo_iso_pu_nums = []
    iso_efficiencies = []
    maxim = 0.01
    minim = 1.00
    for numidx, num in enumerate(numerators[doGen]):
      for i,tree in enumerate(trees):
        if 'raw' not in var:
          histo_iso_pu_num = ROOT.TH1F(histnames[i]+'_%s'%num[1].replace(' ', ''), '', len(binnings[varidx])-1, binnings[varidx])
          tree.Draw(var+' >> %s'%histo_iso_pu_num.GetName(), num[0])
          histo_iso_pu_nums.append(histo_iso_pu_num)
          iso_efficiency = ROOT.TEfficiency(histo_iso_pu_num, histo_dens[i])
          for bin in range(1,len(binnings[varidx])):
            thisef = iso_efficiency.GetEfficiency(bin)
            thiser = max(iso_efficiency.GetEfficiencyErrorLow(bin), iso_efficiency.GetEfficiencyErrorUp(bin))
            if thiser < 0.05:
              if thisef > maxim: maxim = thisef
              if thisef < minim: minim = thisef
        elif numidx==1:
          iso_efficiency = ROOT.TH1F(histnames[i]+'_%s'%num[1].replace(' ', ''), '', len(binnings[varidx])-1, binnings[varidx])
          tree.Draw(var+' >> %s'%iso_efficiency.GetName(), num[0])
          #tree.Project(iso_efficiency.GetName(), var, num[0])
          if iso_efficiency.Integral(0, iso_efficiency.GetNbinsX() + 1) > 0:
            iso_efficiency.Scale(1. / iso_efficiency.Integral(0, iso_efficiency.GetNbinsX() + 1))
          for bin in range(1,len(binnings[varidx])):
            thisef = iso_efficiency.GetBinContent(bin)
            thiser = max(iso_efficiency.GetBinErrorLow(bin), iso_efficiency.GetBinErrorUp(bin))
            if thiser < 0.05:
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
        leg.SetHeader("Genuine #tau_{h} from " + samplename, "C") # QCD flat #hat{p}_{T} 15-7000 GeV
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
