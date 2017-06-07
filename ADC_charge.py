import re

# Shunt settings to keep
SHUNT_MASK = [0b00000, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b10010, \
              0b10100, 0b11000, 0b11010, 0b11100, 0b11110, 0b11111]

# (?<!_)    NOT preceeded by _
# \d+       at least one decimal number (0-9)
# \.        includes a .
r = re.compile(r"(?<!_)\d+\.\d+")

ADC_charges = {}
with open("data/adc_charges.tx", 'r') as f:
    for i,line in enumerate(f):
        if line == '\n': continue

        # re.findall returns a list of strings
        # Convert to list of floats before saving
        ADC_charges.update( {SHUNT_MASK[len(ADC_charges)] : [float(val) for val in r.findall(line)] } )

# To find the corresponding conversion factor
# adc_to_charge[shunt][adc]


def getADC_charge(shunt, adc):
    return ADC_charges[shunt][adc]
    
