import ROOT
import numpy as np
from cmsstyle import CMS_lumi

        
ROOT.TH1.SetDefaultSumw2()
ROOT.gROOT.SetBatch(True) 
ROOT.gStyle.SetOptStat(False) 

# dy_file_name  = 'dy_gen_tuple.root.bkup'
dy_file_name  = 'dy_gen_tuple.root.big.bkup'

dy_file = ROOT.TFile.Open(dy_file_name, 'read')
dy_file.cd()
dy_tree = dy_file.Get('tree')

c1 = ROOT.TCanvas('c1', '', 700, 700)

# define the histogram
h2_dm = ROOT.TH2F('dm', '', 12, 0, 12, 12, 0, 12)
# dy_tree.Draw('tau_decayMode : tau_gen_decayMode >> dm', 'tau_pt>0 & ntrueint<25', 'colz text')
# dy_tree.Draw('tau_decayMode : tau_gen_decayMode >> dm', 'tau_pt>0 & ntrueint>=25 & ntrueint<50', 'colz text')
dy_tree.Draw('tau_decayMode : tau_gen_decayMode >> dm', 'tau_pt>0 & ntrueint>=50', 'colz text')
h2_dm.GetYaxis().SetTitle('reco decay mode')
h2_dm.GetXaxis().SetTitle('gen decay mode')

# run only on interesting, i.e. not empty, bins
xbins = np.array([0, 1, 2, 10, 11]) + 1 # notice the +1 offset: ROOT's bin counting starts from 1 rather than 0
ybins = np.array([0, 1, 5, 6, 10, 11]) + 1

# show only 1 digit
ROOT.gStyle.SetPaintTextFormat('4.1f')

# clone the table, so that you don't mess up with it
h2_dm_clone = h2_dm.Clone()

# cosmetics
h2_dm_clone.GetZaxis().SetRangeUser(0., 100.)

# column normalisation
for xbin in xbins:
    tot_taus = 0.
    # run once to get the total number of entries in a given column
    for ybin in ybins:
        tot_taus += h2_dm_clone.GetBinContent(xbin, ybin)
    # run again to normalise the bin content
    for ybin in ybins:
        h2_dm_clone.SetBinContent(xbin, ybin, 100.*h2_dm_clone.GetBinContent(xbin, ybin)/tot_taus) # multiply by 100 to display percentages
# redraw the table
c1.Draw()
h2_dm_clone.Draw('col text')
CMS_lumi(ROOT.gPad, 4, 0)
ROOT.gPad.Update()


# ROOT.gPad.SaveAs('migration_matrix_lowpu.pdf')
# ROOT.gPad.SaveAs('migration_matrix_midpu.pdf')
ROOT.gPad.SaveAs('migration_matrix_highpu.pdf')

