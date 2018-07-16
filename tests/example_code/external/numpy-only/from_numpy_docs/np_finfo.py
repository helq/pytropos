from numpy import *
f = finfo(float) # the numbers given are machine dependent
f.nmant, f.nexp # nr of bits in the mantissa and in the exponent
# (52, 11)
f.machep # most negative n so that 1.0 + 2**n != 1.0
# -52
f.eps # floating point precision: 2**machep
# array(2.2204460492503131e-16)
f.precision # nr of precise decimal digits: int(-log10(eps))
# 15
f.resolution # 10**(-precision)
# array(1.0000000000000001e-15)
f.negep # most negative n so that 1.0 - 2**n != 1.0
# -53
f.epsneg # floating point precision: 2**negep
# array(1.1102230246251565e-16)
f.minexp # most negative n so that 2**n gives normal numbers
# -1022
f.tiny # smallest usuable floating point nr: 2**minexp
# array(2.2250738585072014e-308)
f.maxexp # smallest positive n so that 2**n causes overflow
# 1024
f.min, f.max # the most negative and most positive usuable floating number
# (-1.7976931348623157e+308, array(1.7976931348623157e+308))

