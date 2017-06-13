import collections
from configuration import hw, sw
import printer
from pprint import pprint
from ADC_charge import getADC_charge

# Events from 1-500 correspond to shunt setting 0, 501-1000 to shunt setting 1, etc...
MAX_SHUNT = 32
shunt_bins = [1 + n * 500 for n in range(MAX_SHUNT)]

FIB = 16

# Shunt settings to keep
SHUNT_MASK = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
	      0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]


def shunt(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
    for r, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

	nTsMax = raw[None]["firstNTs"]
        for fedId, dct in sorted(raw.iteritems()):
            if fedId is None:
                continue
            
	    h = dct["header"]
	    # Event number 
	    evt = h["EvN"]

            # get the important chunks of raw data
            blocks = dct["htrBlocks"].values()

	    #pprint(blocks)
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
			"""
			# From histogram.py
			# the 32 fibers of HEP17 carrying SiPM data
			if block["Crate"] != 34:
			    continue

			fib = 0
			if block["Slot"] == 12:
			    fib += 12 + channelData["Fiber"] - 1
			    if 13 <= channelData["Fiber"]:
				fib -= 2
			elif block["Slot"] == 11 and 12 <= channelData["Fiber"]:
			    fib += channelData["Fiber"] - 12
			else:
			    continue
			"""
			fib = channelData["Fiber"]
			fibCh = channelData["FibCh"]
			#if fib != FIB: continue	
			#print "Crate %d Slot %d Fiber %d channel %d" % (block["Crate"], block["Slot"], channelData["Fiber"], channelData["FibCh"])


			if (2 <= channelData["Flavor"]) and (not channelData["ErrF"]):
			    printer.warning("Crate %d Slot %d Fib %d Channel %d has flavor %d" % \
					    (block["Crate"], block["Slot"], channelData["Fiber"], channelData["FibCh"], channelData["Flavor"]))

			
			# Determine the shunt setting by which bin the event falls into
			shunt = -1
			for b, lim in enumerate(shunt_bins):
			    if evt < lim:
				shunt = b - 1
				break


			# Veto Gsel settings not in list
			if shunt not in SHUNT_MASK: continue
			
			book.fill((i, adc), "ADC_vs_TS_%s_%d" % (errf, fedId),
				  (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
				  title="FED %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, eq))

			book.fill((i, adc),
				  "ADC_vs_TS_HEP17_%s_Fib_%d_Ch_%d" % (errf, fib, fibCh),
				  nTsMax, nAdcMax, -0.5, nTsMax - 0.5,
				  title="HEP17 Fib %d Ch %d;time slice;ADC;Counts / bin" % (fib, fibCh))

			book.fill(adc,
				  "HEP17_ADC_TS%d" % i,
				   nAdcMax, -0.5, nAdcMax - 0.5,
				   title="HEP17 TS%d;ADC;Counts / bin" % i)



			book.fill((shunt, adc), "ADC_vs_Gsel_%s_%d Fib %d Ch %d TS %d" % (errf, fedId, fib, fibCh, i),
                                  MAX_SHUNT, -0.5, MAX_SHUNT - 0.5, 
				  title="FED %d (ErrF %s 0);Gsel;ADC;Counts / bin" % (fedId, eq))

			charge = getADC_charge(shunt,adc)
			# Linearized adc (charge vs TS)
			book.fill((i, charge), "Charge_vs_TS_%s_%d_Fib_%d_Ch_%d" % (errf, fedId, fib, fibCh),
				  nTsMax, -0.5, nTsMax-0.5,
				  title="FED %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, eq))

			book.fill((shunt, charge), "Charge_vs_Gsel_%s_%d_Fib_%d_Ch_%d_TS_%d" % (errf, fedId, fib, fibCh, i),
				  MAX_SHUNT, -0.5, MAX_SHUNT - 0.5,
				  title="Charge vs Gsel TS %d FED %d (ErrF %s 0);Gsel;Charge [fC];Counts / bin" % (i, fedId, eq))
