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

# dy_file_name  = 'dy_gen_tuple.root.bkup'
dy_file_name  = 'dy_gen_tuple.root.big.bkup'

dy_file = ROOT.TFile.Open(dy_file_name, 'read')
dy_file.cd()
dy_tree = dy_file.Get('tree')

c1 = ROOT.TCanvas('c1','',700,700)

# pu_binning = np.array([0., 10.] + range(12, 46, 2) + [50., 55., 60,  65., 70.])
pu_binning = np.array(range(18, 30, 2) + range(30, 40, 5) + range(40, 100, 10) + range(100, 200, 50) + [200., 500., 1000., 5000.], dtype=float)

pt = 40
# den_selection = '&'.join(['tau_pt>20', 'abs(tau_eta)<2.3'])
den_selection = '&'.join(['tau_gen_pt>20', 'abs(tau_gen_eta)<2.3'])
# den_selection = '&'.join(['tau_gen_pt>%d'%pt, 'abs(tau_gen_eta)<2.3'])

# colour palette
# https://gist.github.com/gipert/df72b67c1d02bbb41f1dd406b6397811
# https://personal.sron.nl/~pault/data/colourschemes.pdf
freeID = ROOT.TColor.GetFreeColorIndex()
sunset_palette = [
    Color(  0./255,   0./255,   0./255), # black
    Color(136./255, 136./255, 136./255), # gray

    Color( 54./255,  75./255, 154./255),
    Color( 74./255, 123./255, 183./255),
    Color(110./255, 166./255, 205./255),
    Color(152./255, 202./255, 225./255),
#     Color(194./255, 228./255, 239./255),
#     Color(234./255, 236./255, 204./255),
#     Color(254./255, 218./255, 139./255),
#     Color(253./255, 179./255, 102./255),
#     Color(246./255, 126./255,  75./255),
#     Color(221./255,  61./255,  45./255),
#     Color(165./255,   0./255,  38./255),

    Color(221./255,  61./255,  45./255),
    Color(246./255, 126./255,  75./255),
    Color(253./255, 179./255, 102./255),
    Color(254./255, 218./255, 139./255),
]

numerators = [
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3'])                                                                       , 'new Decay Mode with 2-prong'   ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6'])                               , 'new Decay Mode without 2-prong'),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=3'])    , 'MVA TauID 2017v2 Loose'        ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=4'])    , 'MVA TauID 2017v2 Medium'       ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=5'])    , 'MVA TauID 2017v2 Tight'        ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idMVAnewDM2017v2>=6'])    , 'MVA TauID 2017v2 VTight'       ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2VSjet>=3']), 'DeepTau 2017v2 VLoose'         ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2VSjet>=4']), 'DeepTau 2017v2 Loose'          ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2VSjet>=5']), 'DeepTau 2017v2 Medium'         ),
    ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_pt>%d'%pt, 'abs(tau_eta)<2.3', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2VSjet>=6']), 'DeepTau 2017v2 Tight'          ),
#     ('&'.join([den_selection, 'tau_decayMode>=0', 'tau_decayMode!=5', 'tau_decayMode!=6', 'tau_idDeepTau2017v2VSjet>=7']), 'DeepTau 2017v2 VTight'         ),
]

histo_iso_pu_den = ROOT.TH1F('h_tau_pt', '', len(pu_binning)-1, pu_binning)
# dy_tree.Draw('tau_pt >> h_tau_pt', den_selection)
dy_tree.Draw('tau_gen_pt >> h_tau_pt', den_selection)

leg = ROOT.TLegend(.2,.12,.88,.35)
leg.SetHeader("Genuine #tau_{h} from DY#rightarrow#tau#tau", "C")
leg.SetBorderSize(0)
leg.SetFillColor(ROOT.kWhite)
leg.SetFillStyle(1001)
leg.SetNColumns(2)

c1.Draw()
histo_iso_pu_nums = []
iso_efficiencies = []
for ii, inum in enumerate(numerators):
    legend = inum[1].replace(' ', '')
    colour = sunset_palette[ii]
    histo_iso_pu_num = ROOT.TH1F('h_tau_pt%s'%legend, '', len(pu_binning)-1, pu_binning)
    hname = histo_iso_pu_num.GetName()
#     dy_tree.Draw('tau_pt >> %s'%hname, inum[0])
    dy_tree.Draw('tau_gen_pt >> %s'%hname, inum[0])
    histo_iso_pu_nums.append(histo_iso_pu_num)
    iso_efficiency = ROOT.TEfficiency(histo_iso_pu_num, histo_iso_pu_den)
    iso_efficiency.SetLineColor(colour)
    iso_efficiency.SetLineWidth(2)
    iso_efficiency.SetFillColor(ROOT.kWhite)
    iso_efficiency.Draw('apl') 
    iso_efficiencies.append(iso_efficiency)
#     if ii==0: leg.AddEntry(0, '', '')
    leg.AddEntry(iso_efficiency, inum[1])

for ii, ieff in enumerate(iso_efficiencies):
    options = 'a'*(ii==0) + 'pl' + ' same'*(ii!=0)
    ieff.Draw(options)
    ieff.SetFillColor(0)
#     ieff.SetTitle('; #tau_{h} p_{T} (GeV); efficiency')
    ieff.SetTitle('; gen #tau_{h} p_{T} (GeV); efficiency')
    ROOT.gPad.SetGridx()
    ROOT.gPad.SetGridy()
    ROOT.gPad.Update()
    ROOT.gPad.SetTicky(1)
    ieff.GetPaintedGraph().GetYaxis().SetRangeUser(0, 1.05)
#     ieff.GetPaintedGraph().GetYaxis().SetRangeUser(0, 0.95)
#     ieff.GetPaintedGraph().GetXaxis().SetRangeUser(19.9999, 500.0001)
    ieff.GetPaintedGraph().GetXaxis().SetRangeUser(19.9999, 150.0001)
    ROOT.gPad.SetLogx(False)
    CMS_lumi(ROOT.gPad, 4, 0)
    ROOT.gPad.Update()

# be a better person, always add a legend
leg.Draw('same')
ROOT.gPad.Update()
for iformat in ['png', 'pdf']:
#     ROOT.gPad.SaveAs('pu_tau_pt_eff.%s' %iformat)
    ROOT.gPad.SaveAs('pu_gentau_pt_eff.%s' %iformat)

