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
        
ROOT.TH1.SetDefaultSumw2()

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(False)

########## SETUP

# Luminosity (hardcoded, because I think it isn't changed much, so it's easier like this)
lumiindex = 4 # 13 TeV
#lumiindex = 5 # 14 TeV

# pT, eta, PU
variables = ['tau_pt/tau_gen_pt'] #, 'tau_eta/tau_gen_eta', 'ntrueint'
binnings = [np.array(np.arange(0.5,1.5,0.025), dtype=float), np.array(np.arange(0.95,1.05,0.005), dtype=float), np.array(range(0, 80, 1), dtype=float)]
Xtitles = ['#tau^{RECO} p_{T}/#tau^{GEN} p_{T}'] #, '#tau^{RECO} #eta/#tau^{GEN} #eta', 'Number of true interactions'
#Xranges = [[19.9999, 150.0001], [-2.6001, 2.7001], [0, 75.0001]]
# Reco pT, Gen pT
pt_cut = 20
den_selection = '1'
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==0'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode>0', 'tau_gen_decayMode<3'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==10'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==11'])
numerators = [
   ('&'.join([den_selection                              , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong'   , 0, 1),
  ('&'.join([den_selection, 'ntrueint<25'                , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong; PU < 25'   , 0, 1),
  ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong; 25 < PU < 50'   , 0, 2),
  ('&'.join([den_selection, 'ntrueint>50'                , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong; 50 < PU'   , 0, 1),

   ('&'.join([den_selection                              , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong', 1, 1),
  ('&'.join([den_selection, 'ntrueint<25'                , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong; PU < 25', 1, 1),
  ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong; 25 < PU < 50', 1, 2),
  ('&'.join([den_selection, 'ntrueint>50'                , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong; 50 < PU', 1, 1),

   ('&'.join([den_selection                               , 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==0'])                      , 'new Decay Mode 1-prong'           , 2, 1),
   ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong; PU < 25'           , 2, 1),
   ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong; 25 < PU < 50'           , 2, 2),
   ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong; 50 < PU'           , 2, 3),

   ('&'.join([den_selection                               , 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])   , 'new Decay Mode 1-prong + n#pi^{0}', 3, 1),
   ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0}; PU < 25', 3, 1),
   ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0}; 25 < PU < 50', 3, 2),
   ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0}; 50 < PU', 3, 3),

   ('&'.join([den_selection                               , 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==10'])                     , 'new Decay Mode 3-prong'           , 4, 1),
   ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong; PU < 25'           , 4, 1),
   ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong; 25 < PU < 50'           , 4, 2),
   ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong; 50 < PU'           , 4, 3),

   ('&'.join([den_selection                               , 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==11'])                     , 'new Decay Mode 3-prong + #pi^{0}' , 5, 1),
   ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0}; PU < 25' , 5, 1),
   ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0}; 25 < PU < 50' , 5, 2),
   ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt_cut, 'abs(tau_eta)<2.3', 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0}; 50 < PU' , 5, 3),
  ]

#numerators_split = [ [numerators[0],numerators[4],numerators[8],numerators[12],numerators[16],numerators[20]], [numerators[1],numerators[5],numerators[9],numerators[13],numerators[17],numerators[21]], [numerators[2],numerators[6],numerators[10],numerators[14],numerators[18],numerators[22]], [numerators[3],numerators[7],numerators[11],numerators[15],numerators[19],numerators[23]] ]
numerators_split = [ [0, 4, 8, 12, 16, 20], [1, 5, 9, 13, 17, 21], [2, 6, 10, 14, 18, 22], [3, 7, 11, 15, 19, 23] ]

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
    Color(238./255, 102./255, 119./255), # red
    Color( 68./255, 119./255, 170./255), # blue
    Color( 34./255, 136./255,  51./255), # green
    Color(204./255, 187./255,  68./255), # yellow
    Color(170./255,  51./255, 119./255), # purple
    Color(102./255, 204./255, 238./255), # cyan
    Color(187./255, 187./255, 187./255), # grey

]]


file = ROOT.TFile.Open(rootfiles[0], 'read')
file.cd()
tree = file.Get('tree')

for varidx,var in enumerate(variables):
  for jnum,beta in enumerate(numerators_split):

    c1 = ROOT.TCanvas('c1', '', 700, 700)

    #histname = 'h_'+var
    #histo_den = ROOT.TH1F(histname, '', len(binnings[varidx])-1, binnings[varidx])
    #tree.Draw(var+' >> '+histname, den_selection)

    # leg = ROOT.TLegend(.12,.12,.88,.35)
    leg = ROOT.TLegend(.12,.7,.88,.88)
    # leg.SetHeader("Genuine #tau_{h} from DY#rightarrow#tau#tau, #tau_{h} p_{T}>%d GeV" %pt, "C")
    leg.SetBorderSize(0)
    leg.SetFillColor(ROOT.kWhite)
    leg.SetFillStyle(1001)
    # leg.SetNColumns(2)

    histo_iso_pu_nums = []

    for inum,alpha in enumerate(beta):
      num = numerators[alpha]
      histo_iso_pu_num = ROOT.TH1F('h_'+var[:6]+'_'+str(inum)+'_'+str(jnum), '', len(binnings[varidx])-1, binnings[varidx])
      tree.Draw(var+' >> %s'%histo_iso_pu_num.GetName(), num[0])
      histo_iso_pu_nums.append(histo_iso_pu_num)
      histo_iso_pu_num.SetLineColor(sunset_palette[1][inum])
      histo_iso_pu_num.SetLineWidth(2)
      #histo_iso_pu_num.SetLineStyle(num[-1])
      histo_iso_pu_num.SetFillColor(ROOT.kWhite)
      ROOT.gPad.SetTicky(1)
      # if ii==0: leg.AddEntry(0, '', '')
      leg.AddEntry(histo_iso_pu_num, num[1])

    maximum = 0.
    for ii, ieff in enumerate(histo_iso_pu_nums):
      if ieff.Integral()!= 0: ieff.Scale(1./ieff.Integral())
      maximum = max(maximum, ieff.GetMaximum())
    for ii, ieff in enumerate(histo_iso_pu_nums):
      options = 'hist' + ' same'*(ii!=0)
      #if ieff.Integral()!= 0: ieff.Scale(1./ieff.Integral())
      ieff.Draw(options)
      ieff.SetFillColor(0)
      #maximum = max(maximum, ieff.GetMaximum())
      ROOT.gPad.SetGridx()
      ROOT.gPad.SetGridy()
      ROOT.gPad.Update()
      ROOT.gPad.SetTicky(1)
      ieff.GetYaxis().SetRangeUser(0., 1.6*maximum)
      ieff.GetXaxis().SetTitle(Xtitles[varidx])
      ieff.GetYaxis().SetTitle('a.u.')
      ieff.GetXaxis().SetTitleOffset(1.3)
      ieff.GetYaxis().SetTitleOffset(1.3)
      # ROOT.gPad.SetLogy(True)
      CMS_lumi(ROOT.gPad, lumiindex, 0)
      ROOT.gPad.Update()

    # be a better person, always add a legend
    leg.Draw('same')
    ROOT.gPad.Update()

    if 'pt' in var: savename='pt'
    if 'eta' in var: savename='eta'
    if 'ntrueint' in var: savename='pu'
    if jnum==0: savename2 = ''
    elif jnum==1: savename2 = '_lowpu'
    elif jnum==2: savename2 = '_midpu'
    elif jnum==3: savename2 = '_highpu'
    
    for iformat in ['png']: #, 'pdf'
      c1.SaveAs('response_%s%s.%s' %(savename, savename2, iformat))

    del c1
    del leg

exit()
