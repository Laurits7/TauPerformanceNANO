import ROOT
import numpy as np
from cmsstyle import CMS_lumi

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

# dy_file_name  = 'dy_gen_tuple.root.bkup'
dy_file_name  = 'dy_gen_tuple.root.big.bkup'

dy_file = ROOT.TFile.Open(dy_file_name, 'read')
dy_file.cd()
dy_tree = dy_file.Get('tree')

c1 = ROOT.TCanvas('c1', '', 700, 700)

# pu_binning = np.array([0., 10.] + range(12, 46, 2) + [50., 55., 60,  65., 70.])
pu_binning = np.array(np.arange(0.5,1.5,0.025), dtype=float)

pt = 20
den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==0'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode>0', 'tau_gen_decayMode<3'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==10'])
# den_selection = '&'.join(['tau_gen_pt>0', 'abs(tau_gen_eta)<2.3', 'tau_gen_decayMode==11'])

# colour palette
# https://gist.github.com/gipert/df72b67c1d02bbb41f1dd406b6397811
# https://personal.sron.nl/~pault/data/colourschemes.pdf
freeID = ROOT.TColor.GetFreeColorIndex()
sunset_palette = [
    Color(  0./255,   0./255,   0./255),
    Color(136./255, 136./255, 136./255),

#     Color( 54./255,  75./255, 154./255),
#     Color( 74./255, 123./255, 183./255),
#     Color(110./255, 166./255, 205./255),
#     Color(152./255, 202./255, 225./255),
# 
#     Color(221./255,  61./255,  45./255),
#     Color(246./255, 126./255,  75./255),
#     Color(253./255, 179./255, 102./255),
#     Color(254./255, 218./255, 139./255),


#     Color(194./255, 228./255, 239./255),
#     Color(234./255, 236./255, 204./255),
#     Color(254./255, 218./255, 139./255),
#     Color(253./255, 179./255, 102./255),
#     Color(246./255, 126./255,  75./255),
#     Color(221./255,  61./255,  45./255),
#     Color(165./255,   0./255,  38./255),

#     Color(221./255,  61./255,  45./255),
#     Color(246./255, 126./255,  75./255),
#     Color(253./255, 179./255, 102./255),
#     Color(254./255, 218./255, 139./255),

    Color( 27./255, 120./255,  55./255),
    Color( 90./255, 174./255,  97./255),
    Color(172./255, 211./255, 158./255),
    Color(217./255, 240./255, 211./255),
]

numerators = [
#     ('&'.join([den_selection, 'tau_pt>%d'%pt, 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong'   , 0, 1),
#     ('&'.join([den_selection, 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong', 1, 1),

    ('&'.join([den_selection, 'ntrueint<25', 'tau_pt>%d'%pt, 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong - PU < 25'   , 0, 1),
    ('&'.join([den_selection, 'ntrueint<25', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong - PU < 25', 1, 1),

    ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_pt>%d'%pt, 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong - 25 <PU < 50'   , 0, 2),
    ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong - 25 <PU < 50', 1, 2),

    ('&'.join([den_selection, 'ntrueint>50', 'tau_pt>%d'%pt, 'tau_decayMode>=0'])                                          , 'new Decay Mode with 2-prong - 50 < PU < 70'   , 0, 3),
    ('&'.join([den_selection, 'ntrueint>50', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode!=5' , 'tau_decayMode!=6']) , 'new Decay Mode without 2-prong - 50 < PU < 70', 1, 3),



#     ('&'.join([den_selection                               ,'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==0'])                      , 'new Decay Mode 1-prong'           , 2, 1),
#     ('&'.join([den_selection                               ,'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])   , 'new Decay Mode 1-prong + n#pi^{0}', 3, 1),
#     ('&'.join([den_selection                               ,'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==10'])                     , 'new Decay Mode 3-prong'           , 4, 1),
#     ('&'.join([den_selection                               ,'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==11'])                     , 'new Decay Mode 3-prong + #pi^{0}' , 5, 1),

#     ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong - PU < 25'           , 2, 1),
#     ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0} - PU < 25', 3, 1),
#     ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong - PU < 25'           , 4, 1),
#     ('&'.join([den_selection, 'ntrueint<25'                , 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0} - PU < 25' , 5, 1),

#     ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong - 25 <PU < 50'           , 2, 2),
#     ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0} - 25 <PU < 50', 3, 2),
#     ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong - 25 <PU < 50'           , 4, 2),
#     ('&'.join([den_selection, 'ntrueint>=25', 'ntrueint<50', 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0} - 25 <PU < 50' , 5, 2),

#     ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==0'                      , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==0'])                     , 'new Decay Mode 1-prong - 50 < PU < 70'           , 2, 3),
#     ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode>0', 'tau_gen_decayMode<3', 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode>0', 'tau_decayMode<3' ])  , 'new Decay Mode 1-prong + n#pi^{0} - 50 < PU < 70', 3, 3),
#     ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==10'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==10'])                    , 'new Decay Mode 3-prong - 50 < PU < 70'           , 4, 3),
#     ('&'.join([den_selection, 'ntrueint>50'                , 'tau_gen_decayMode==11'                     , 'tau_pt>%d'%pt, 'tau_decayMode>=0', 'tau_decayMode==11'])                    , 'new Decay Mode 3-prong + #pi^{0} - 50 < PU < 70' , 5, 3),



]

histo_iso_pu_den = ROOT.TH1F('iso_pu_den', '', len(pu_binning)-1, pu_binning)
dy_tree.Draw('tau_pt/tau_gen_pt >> iso_pu_den', den_selection)

# leg = ROOT.TLegend(.12,.12,.88,.35)
leg = ROOT.TLegend(.12,.7,.88,.88)
# leg.SetHeader("Genuine #tau_{h} from DY#rightarrow#tau#tau, #tau_{h} p_{T}>%d GeV" %pt, "C")
leg.SetBorderSize(0)
leg.SetFillColor(ROOT.kWhite)
leg.SetFillStyle(1001)
# leg.SetNColumns(2)

histo_iso_pu_nums = []
iso_efficiencies = []
for ii, inum in enumerate(numerators):
    legend = inum[1].replace(' ', '')
    colour = sunset_palette[inum[-2]]
    histo_iso_pu_num = ROOT.TH1F('iso_pu_num_%s'%legend, '', len(pu_binning)-1, pu_binning)
    hname = histo_iso_pu_num.GetName()
    dy_tree.Draw('tau_pt/tau_gen_pt >> %s'%hname, inum[0])
    histo_iso_pu_nums.append(histo_iso_pu_num)
    histo_iso_pu_num.SetLineColor(colour)
    histo_iso_pu_num.SetLineWidth(2)
    histo_iso_pu_num.SetLineStyle(inum[-1])
    histo_iso_pu_num.SetFillColor(ROOT.kWhite)
    ROOT.gPad.SetTicky(1)
#     if ii==0: leg.AddEntry(0, '', '')
    leg.AddEntry(histo_iso_pu_num, inum[1])

maximum = 0.
for ii, ieff in enumerate(histo_iso_pu_nums):
    options = 'hist' + ' same'*(ii!=0)
    ieff.Scale(1./ieff.Integral())
    ieff.Draw(options)
    ieff.SetFillColor(0)
    maximum = max(0., ieff.GetMaximum())
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    ROOT.gPad.Update()
    ROOT.gPad.SetTicky(1)
    ieff.GetYaxis().SetRangeUser(0., 1.6*maximum)
    ieff.GetXaxis().SetTitle('#tau^{RECO} p_{T}/#tau^{GEN} p_{T}')
    ieff.GetYaxis().SetTitle('a.u.')
    ieff.GetXaxis().SetTitleOffset(1.3)
    ieff.GetYaxis().SetTitleOffset(1.3)
#     ROOT.gPad.SetLogy(True)
    CMS_lumi(ROOT.gPad, 4, 0)
    ROOT.gPad.Update()

# be a better person, always add a legend
leg.Draw('same')
ROOT.gPad.Update()

for iformat in ['png', 'pdf']:
    c1.SaveAs('pu_ntrueint_eff_pt%d_pt_response.%s' %(pt, iformat))

