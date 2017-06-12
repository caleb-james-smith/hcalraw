#!/usr/bin/env python
import optparse
import ROOT
from ROOT import TFile, TCanvas, gROOT

# Sum over these time slices
TS_MASK = [3, 4, 5, 6]

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')

(opt,args) = parser.parse_args()

f = TFile.Open(opt.inF, 'r')

gROOT.SetBatch(True)  # True: Don't display canvas
c = TCanvas("c","c",1700,1200)

charge_ts_h = []

# Pedestal charge
ped_h = f.Get("Charge_vs_Gsel_ErrF0_1114_Fib_16_TS_1")
ped_h.SetDirectory(0)

for ts in TS_MASK:
    htemp = f.Get("Charge_vs_Gsel_ErrF0_1114_Fib_16_TS_%d"%ts)
    htemp.SetDirectory(0)
    charge_ts_h.append(htemp)

# Done with TFile
f.Close()

# Total number of entries considered after charge addition
binEntries = ped_h.GetBinEntries(1) * len(TS_MASK)
print "binEntries = %d" % binEntries

totQ = charge_ts_h[0].Clone()
for i in xrange(1, len(TS_MASK)):
    totQ.Add(charge_ts_h[i])


# To ensure TProfile subtracts histograms correctly
tot_ped = ped_h.Clone()
for i in xrange(1, len(TS_MASK)):
    tot_ped.Add(ped_h)

# Pedestal subtraction
totQ.Add(tot_ped, -1)

# Correct number of entries after histogram addition
for b in xrange(1, totQ.GetNbinsX()):
    totQ.SetBinEntries(b, totQ.GetBinEntries(b)/2.0)

# Normalize by Gsel0 value
totQ.Scale(1.0 / totQ.GetBinContent(1))

# Reset stat table
totQ.ResetStats()


totQ.SetAxisRange(0.8, 1.2, "Y")
totQ.GetYaxis().SetTitle("Tot Q / Tot Q (Gsel = 0)")
totQ.SetTitle("Normalized Total Charge vs Gsel   FED 1114 Fib 16")

# Draw to canvas and save to jpg file
totQ.Draw()
c.SaveAs("Norm_Q_vs_Gsel.jpg")


