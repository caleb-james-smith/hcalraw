import collections
from configuration import hw, sw
import printer
from pprint import pprint

INSPECT_FEDID = 1114
MAX_SHUNT = 32
# shunt_bins = [1, 501, 1001, 1501, ...]
# Events from 1-500 correspond to shunt setting 0, 501-1000 to shunt setting 1, etc...
shunt_bins = [1 + n * 500 for n in range(MAX_SHUNT)]

def shunt(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
    # sanity check
    for i, raw in enumerate([raw1, raw2]):
        if not raw:
            continue

        for fedId, dct in sorted(raw.iteritems()):
            if fedId != INSPECT_FEDID:
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

                    for (n, adc) in enumerate(channelData["QIE"]):
			shunt = -1
			# Determine the shunt setting by which bin the event falls into
			for b, lim in enumerate(shunt_bins):
			    if evt < lim:
				shunt = b - 1
				break


			book.fill((shunt, adc), "ADC_vs_Shunt setting_%s_%d" % (errf, fedId),
                                  (MAX_SHUNT, nAdcMax), (-0.5, -0.5), (MAX_SHUNT - 0.5, nAdcMax - 0.5),
                                  title="FED %d (ErrF %s 0);Shunt setting;ADC;Counts / bin" % (fedId, eq))              
