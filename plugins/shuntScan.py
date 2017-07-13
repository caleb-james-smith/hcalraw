#####################################################################
#  shuntScan.py                                                     #
#                                                                   #           
#  Plugin to be used with hcalraw to create histograms              #
#  from shunt scans	                                            #
#                                                                   #
#  Usage:                                                           #
#  Select with the --plugins option in oneRun.py or look.py         #
#                                                                   #
#  Dependencies:						    #
#  ADC_charge.py  - Build dictionary for ADC linearization	    #
#  data/adc_charges.txt  - Stores ADC linearization values	    #
#                                                                   #
#####################################################################

import collections
from configuration import hw, sw
import printer
from pprint import pprint
from ADC_charge import getADC_charge

# Events from 1-500 correspond to shunt setting 0, 501-1000 to shunt setting 1, etc...
EVT_PER_SHUNT = 500
MAX_SHUNT = 32
shunt_bins = [1 + n * EVT_PER_SHUNT for n in range(MAX_SHUNT + 1)]


# Shunt settings to keep
SHUNT_MASK = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
	      0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]


def shuntScan(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
    for r, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

	nTsMax = raw[None]["firstNTs"]
        #print "nTsMax = ", nTsMax
	for fedId, dct in sorted(raw.iteritems()):
            if fedId is None:
                continue
            
	    h = dct["header"]
	    # Event number 
	    evt = h["EvN"]

            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()

	    # sanity checks for chunks
            for block in blocks:
                if type(block) is not dict:
                    printer.warning("FED %d block is not dict" % fedId)
                    continue
                elif "channelData" not in block:
                    printer.warning("FED %d block has no channelData" % fedId)
                    continue

            for channelData in block["channelData"].values():
		if channelData["QIE"]:
                    # check error flags
                    errf = "ErrFNZ" if channelData["ErrF"] else "ErrF0"

                    # Clean or problematic error flag
                    eq = "!=" if channelData["ErrF"] else "=="

                    nAdcMax = 256
		    		    
		    # i: time slice
                    for (i, adc) in enumerate(channelData["QIE"]):
			if nTsMax <= i:
			    break
			
			fib = channelData["Fiber"]
			fibCh = channelData["FibCh"]
			
			shunt = 0
			
			# Determine the shunt setting by which bin the event falls into
			shunt = -1
			for b, lim in enumerate(shunt_bins):
			    if evt < lim:
				shunt = b - 1
				break


			# Veto Gsel settings not in list
			if shunt not in SHUNT_MASK: continue
			
			book.fill((i, adc), "ADC_vs_TS_2D_%s_%d" % (errf, fedId),
				  (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
				  title="FED %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, eq))
			
			"""
			book.fill((i, adc), "ADC_vs_TS_%s_%d_" % (errf, fedId),
				  nTsMax, -0.5, nTsMax - 0.5,
				  title="ADC vs TS  FED %d (ErrF %s 0) Fib;time slice;ADC;Counts / bin" % (fedId, eq))			
			
			book.fill((i, adc),
				  "ADC_vs_TS_%s_FED_%d_Fib_%d_Ch_%d" % (errf, fedId, fib, fibCh),
				  nTsMax, -0.5, nTsMax - 0.5,
				  title="ADC vs TS  FED %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, fib, fibCh, eq))
			"""

			book.fill((i, adc),
				  "ADC_vs_TS_%s_FED_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, fib, fibCh),
				  (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
				  title="ADC vs TS  FED %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, fib, fibCh, eq))
			
			book.fill((shunt, adc), "ADC_vs_Gsel_%s_FED_%d_Fib_%d_Ch_%d_TS_%d" % (errf, fedId, fib, fibCh, i),
                                  MAX_SHUNT, -0.5, MAX_SHUNT - 0.5, 
				  title="ADC vs Gsel TS %d  FED %d Fib %d Ch %d (ErrF %s 0);Gsel;ADC;Counts / bin" % (i, fedId, fib, fibCh, eq))

			charge = getADC_charge(shunt,adc)
			# Linearized adc (charge vs TS)
			book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Fib_%d_Ch_%d" % (errf, fedId, fib, fibCh),
				  nTsMax, -0.5, nTsMax-0.5,
				  title="Charge vs TS  FED %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, fib, fibCh, eq))

			book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, fib, fibCh),
				  (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
				  title="Charge vs TS  FED %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, fib, fibCh, eq))
			
			book.fill((shunt, charge), "Charge_vs_Gsel_%s_FED_%d_Fib_%d_Ch_%d_TS_%d" % (errf, fedId, fib, fibCh, i),
				  MAX_SHUNT, -0.5, MAX_SHUNT - 0.5,
				  title="Charge vs Gsel TS %d  FED %d Fib %d Ch %d (ErrF %s 0);Gsel;Charge [fC];Counts / bin" % (i, fedId, fib, fibCh, eq))

