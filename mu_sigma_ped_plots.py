#!/usr/bin/env python
###################################################
#  mu_sigma_ped_plots.py                          #
#                                                 #
#  Runs on an output file from pulseRun plugin    #
#  to produce a histograms of mean/stddev ADC and #
#  charge from all channels.			  #
###################################################
import sys
import optparse
import ROOT
from ROOT import TFile, TCanvas, TH1D, gROOT


# Sum over these time slices
TS_MASK = [3, 4, 5, 6]

# Number of fibers
FIBER = 24
# Number of channels per fiber
FIBCH = 8

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--inF', dest='inF', help='input file', default=None, type='string')
parser.add_option('-e', '--fedId', dest='fedId', help='fed Id', default=1776, type='int')
parser.add_option('-w', '--warn', dest='warn', help='warn on errors (0 or 1)', default=0, type='int')
parser.add_option('-f', '--fiberMask', dest='fiberMask', help='fiber to inspect', default=-1, type='int')
(opt,args) = parser.parse_args()

f = TFile.Open(opt.inF, 'r')
try:
    if f.IsZombie():
        print "File %s is a zombie" % opt.inF
        sys.exit()
except: # Couldn't open file, exit
    sys.exit()

gROOT.SetBatch(True)  # True: Don't display canvas
c = TCanvas("c","c",1700,1200)

adc_ts_h = {}
charge_ts_h = {}
for fib in xrange(0, FIBER):
    if opt.fiberMask != -1:
	if fib != opt.fiberMask: continue
    adc_ts_h_perfiber = {}
    charge_ts_h_perfiber = {}
    for fibch in xrange(0, FIBCH):
	htemp = None
	htemp = f.Get("ADC_vs_TS_ErrF0_FED_%d_Fib_%d_Ch_%d" %(opt.fedId, fib, fibch))
	try:	
	    htemp.SetDirectory(0)
	    #htemp.SetBinContent(1, 0)
	    #htemp.SetBinEntries(1, 0)
	    adc_ts_h_perfiber.update( {fibch:htemp} )
	except:
	    if opt.warn: print "ADC vs TS in Fib %d Ch %d has no good data" % (fib, fibch)
	
	htemp = None
	htemp = f.Get("Charge_vs_TS_ErrF0_FED_%d_Fib_%d_Ch_%d" % (opt.fedId, fib, fibch))
	try:
	    htemp.SetDirectory(0)
	    #htemp.SetBinContent(1, 0)
	    #htemp.SetBinEntries(1, 0)
	    charge_ts_h_perfiber.update( {fibch:htemp} )
	except:
	    if opt.warn: print "Charge vs TS in Fib %d Ch %d has no good data" % (fib, fibch)
	

    adc_ts_h.update( {fib:adc_ts_h_perfiber} )
    charge_ts_h.update( {fib:charge_ts_h_perfiber} )


# Done with TFile
f.Close()

# TProfile h
# h.GetMean(2) Y axis mean
# h.GetRMS(2)  Y axis rms

mean = TH1D("mean", "Mean ADC", 100, 0,10)
mean.GetXaxis().SetTitle("Mean [ADC]")
mean.GetYaxis().SetTitle("Events/bin")

rms = TH1D("rms", "RMS ADC", 100, 0, 10)
rms.GetXaxis().SetTitle("\sigma [ADC]")
rms.GetYaxis().SetTitle("Events/bin")

charge = TH1D("charge", "Total Charge", 100, 0, 200.0)
charge.GetXaxis().SetTitle("Charge [fC]")
charge.GetYaxis().SetTitle("Events/bin")

for fib in xrange(0, FIBER):
    for fibch in xrange(0, FIBCH):
	try:
	    mean.Fill(adc_ts_h[fib][fibch].GetMean(2))
	    rms.Fill(adc_ts_h[fib][fibch].GetRMS(2))
	   
	    totQ = 0.0
	    for i in TS_MASK:
	    	totQ += charge_ts_h[fib][fibch].GetBinContent(i+1)

	    charge.Fill(totQ)

	except:
	    None

mean.Draw()
c.SaveAs("mean_ADC.jpg")
rms.Draw()
c.SaveAs("rms_ADC.jpg")
charge.Draw()
c.SaveAs("charge.jpg")

outF = TFile.Open("mean_rms_totQ_FED_%d.root" % opt.fedId, 'RECREATE')
outF.cd()
mean.SetName("mean_ADC_FED_%d" % opt.fedId)
rms.SetName("rms_ADC_FED_%d" % opt.fedId)
charge.SetName("charge_FED_%d" % opt.fedId)
mean.Write()
rms.Write()
charge.Write()
outF.Close()
