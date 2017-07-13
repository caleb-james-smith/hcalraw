#!/usr/bin/env python
##################################################
#  normQ_vs_Gsel_plot.py                         #
#						 #
#  Runs on an output file from shuntScan plugin  #
#  to produce a histogram of normalized charge   #
#  vs gsel setting.				 #
##################################################

import sys
import optparse
import ROOT
from ROOT import TFile, TCanvas, gROOT

# Sum over these time slices
TS_MASK = [3, 4, 5, 6]

# TS to use for pedestal charge
PED_TS = 1

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')
parser.add_option('-e', '--fedId', dest='fedId', help='fed Id', default=1776, type='int')
parser.add_option('-f', '--fiber', dest='fiber', help='fiber', default=None, type='int')
parser.add_option('-c', '--fibCh', dest='fibCh', help='fiber channel', default=None, type='int')

(opt,args) = parser.parse_args()

f = TFile.Open(opt.inF, 'r')
try:
    if f.IsZombie(): 
	print "File %s is a zombie" % opt.inF
	sys.exit()
except: #Couldn't open file, exit
    sys.exit()

gROOT.SetBatch(True)  # True: Don't display canvas
c = TCanvas("c","c",1700,1200)

charge_ts_h = []

# Pedestal charge
ped_h = f.Get("Charge_vs_Gsel_ErrF0_FED_%d_Fib_%d_Ch_%d_TS_%d" % (opt.fedId, opt.fiber, opt.fibCh, PED_TS))
try:
    ped_h.SetDirectory(0)
except:
    print "FED %d Fib %d Ch %d not found in file %s" % (opt.fedId, opt.fiber, opt.fibCh, opt.inF)
    sys.exit()

for ts in TS_MASK:
    htemp = f.Get("Charge_vs_Gsel_ErrF0_FED_%d_Fib_%d_Ch_%d_TS_%d"%(opt.fedId, opt.fiber, opt.fibCh, ts))
    htemp.SetDirectory(0)
    charge_ts_h.append(htemp)

# Done with TFile
f.Close()


totQ = charge_ts_h[0].Clone()
totQ.BuildOptions(0.8, 1.2, '')
for i in xrange(1, len(TS_MASK)):
    totQ.Add(charge_ts_h[i])


# To ensure TProfile subtracts histograms correctly
tot_ped = ped_h.Clone()
for i in xrange(1, len(TS_MASK)):
    tot_ped.Add(ped_h)

# Pedestal subtraction
totQ.Add(tot_ped, -1)

# Correct number of entries after histogram addition
for b in xrange(1, totQ.GetNbinsX() + 1):
    totQ.SetBinEntries(b, totQ.GetBinEntries(b)/2.0)

# Normalize by Gsel0 value
totQ.Scale(1.0 / totQ.GetBinContent(1))

# Reset stat table
totQ.ResetStats()


totQ.SetAxisRange(0.8, 1.2, "Y")
totQ.GetYaxis().SetTitle("Tot Q / Tot Q (Gsel = 0)")
totQ.SetTitle("Normalized Total Charge vs Gsel   FED %d Fib %d Ch %d" % (opt.fedId, opt.fiber, opt.fibCh))

# Draw to canvas and save to root,jpg file
totQ.Draw()
c.SaveAs("NormQ_vs_Gsel_FED_%d_Fib_%d_Ch_%d.jpg" % (opt.fedId, opt.fiber, opt.fibCh))
outF = TFile.Open("NormQ_vs_Gsel_FED_%d_Fib_%d_Ch_%d.root" % (opt.fedId, opt.fiber, opt.fibCh), 'RECREATE')
outF.cd()
totQ.SetName("NormQ_vs_Gsel_FED_%d_Fib_%d_Ch_%d" % (opt.fedId, opt.fiber, opt.fibCh))
totQ.Write()
outF.Close()
