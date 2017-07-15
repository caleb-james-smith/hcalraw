#####################################################################
#  pulseRun.py							    #
#								    #		
#  Plugin to be used with hcalraw to create histograms		    #
#  of iQi and LED run pulses.					    #
#								    #
#  Usage:							    #
#  Select with the --plugins option in oneRun.py or look.py	    #
#								    #
#####################################################################

import collections
from configuration import hw, sw
import printer
from pprint import pprint

# Corresponding charge in fC for a given ADC value (represented by the position in the list)
adcCharges=['1.62', '4.86', '8.11', '11.35', '14.59', '17.84', '21.08', '24.32', '27.57', '30.81', '34.05', '37.30', '40.54', '43.78', '47.03', '50.27', '56.75', '63.24', '69.73', '76.21', '82.70', '89.19', '95.67', '102.2', '108.6', '115.1', '121.6', '128.1', '134.6', '141.1', '147.6', '154.0', '160.5', '167.0', '173.5', '180.0', '193.0', '205.9', '218.9', '231.9', '244.9', '257.8', '270.8', '283.8', '296.7', '309.7', '322.7', '335.7', '348.6', '361.6', '374.6', '387.6', '400.5', '413.5', '426.5', '439.4', '452.4', '478.4', '504.3', '530.3', '556.2', '582.1', '608.1', '634.0', '577.6', '603.0', '628.5', '654.0', '679.5', '705.0', '730.5', '756.0', '781.5', '806.9', '832.4', '857.9', '883.4', '908.9', '934.4', '959.9', '1010.9', '1061.8', '1112.8', '1163.8', '1214.8', '1265.7', '1316.7', '1367.7', '1418.7', '1469.6', '1520.6', '1571.6', '1622.6', '1673.5', '1724.5', '1775.5', '1826.5', '1877.5', '1928.4', '1979.4', '2081.4', '2183.3', '2285.3', '2387.2', '2489.2', '2591.1', '2693.1', '2795.0', '2897.0', '2998.9', '3100.9', '3202.8', '3304.8', '3406.8', '3508.7', '3610.7', '3712.6', '3814.6', '3916.5', '4018.5', '4120.4', '4324.3', '4528.2', '4732.1', '4936.1', '5140.0', '5343.9', '5547.8', '5331.9', '5542.5', '5753.1', '5963.7', '6174.3', '6384.9', '6595.5', '6806.1', '7016.7', '7227.3', '7437.9', '7648.4', '7859.0', '8069.6', '8280.2', '8490.8', '8912.0', '9333.2', '9754.3', '10175.5', '10596.7', '11017.9', '11439.1', '11860.3', '12281.4', '12702.6', '13123.8', '13545.0', '13966.2', '14387.3', '14808.5', '15229.7', '15650.9', '16072.1', '16493.2', '16914.4', '17756.8', '18599.1', '19441.5', '20283.9', '21126.2', '21968.6', '22811.0', '23653.3', '24495.7', '25338.0', '26180.4', '27022.8', '27865.1', '28707.5', '29549.9', '30392.2', '31234.6', '32076.9', '32919.3', '33761.7', '34604.0', '36288.8', '37973.5', '39658.2', '41342.9', '43027.6', '44712.4', '46397.1', '43321.6', '44990.1', '46658.6', '48327.1', '49995.7', '51664.2', '53332.7', '55001.2', '56669.7', '58338.2', '60006.7', '61675.2', '63343.7', '65012.3', '66680.8', '68349.3', '71686.3', '75023.3', '78360.3', '81697.4', '85034.4', '88371.4', '91708.4', '95045.4', '98382.5', '101719.5', '105056.5', '108393.5', '111730.6', '115067.6', '118404.6', '121741.6', '125078.6', '128415.7', '131752.7', '135089.7', '141763.8', '148437.8', '155111.8', '161785.9', '168459.9', '175134.0', '181808.0', '188482.1', '195156.1', '201830.1', '208504.2', '215178.2', '221852.3', '228526.3', '235200.4', '241874.4', '248548.4', '255222.5', '261896.5', '268570.6', '275244.6', '288592.7', '301940.8', '315288.9', '328637.0', '341985.1', '355333.1', '368681.2']

def pulseRun(raw1={}, raw2={}, book=None, warnQuality=True, fewerHistos=False, **other):
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
	    #pprint(blocks)
	    # sanity checks for chunks
	    
            #for block in blocks:
            for i, block in enumerate(blocks):
                if type(block) is not dict:
                    printer.warning("FED %d block is not dict" % fedId)
                    continue
                elif "channelData" not in block:
                    printer.warning("FED %d block has no channelData" % fedId)
                    continue
	
		crate = block["Crate"]
		slot = block["Slot"]

		#with open("block%d.log"%i, "a+") as f:
		#    pprint(block, stream=f)

		for channelData in block["channelData"].values():
		    #pprint(channelData)
		    #print "Fiber %d Ch %d  errf = %s"%(channelData["Fiber"], channelData["FibCh"], channelData["ErrF"])
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

			    # Default shunt setting
			    shunt = 0

			    book.fill((i, adc), "ADC_vs_TS_2D_%s_%d" % (errf, fedId),
				      (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
				      title="ADC vs TS  FED %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, fib, fibCh, eq))
			    
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
				      "ADC_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
				      (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
				      title="ADC vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
			    
			    charge = float(adcCharges[adc])
			    # Linearized adc (charge vs TS)
			    book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
				      nTsMax, -0.5, nTsMax-0.5,
				      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, fib, crate, slot, fibCh, eq))

			    book.fill((i, charge), "Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
				      (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
				      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))
			   
			    if i > 0:
				book.fill((i, adc), 
                                      "NoTS0_ADC_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh), (nTsMax, nAdcMax), (-0.5, -0.5), (nTsMax - 0.5, nAdcMax - 0.5),
                                      title="ADC vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;ADC;Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))

				book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d" % (errf, fedId, crate, slot, fib, fibCh),
				      nTsMax, -0.5, nTsMax-0.5,
				      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, crate, slot, fib, fibCh, eq))

				book.fill((i, charge), "NoTS0_Charge_vs_TS_%s_FED_%d_Crate_%d_Slot_%d_Fib_%d_Ch_%d_2D" % (errf, fedId, crate, slot, fib, fibCh),
				      (nTsMax, 100), (-0.5, -0.5), (nTsMax-0.5, 20000),
				      title="Charge vs TS  FED %d Crate %d Slot %d Fib %d Ch %d (ErrF %s 0);time slice;Charge [fC];Counts / bin" % (fedId, fib, crate, slot, fibCh, eq))
