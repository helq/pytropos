from numpy import *
from numpy.fft import *
signal = array([-2., 8., -6., 4., 1., 0., 3., 5.]) # could also be complex
fourier = fft(signal)
fourier
# array([ 13. +0.j , 3.36396103 +4.05025253j,
#          2. +1.j , -9.36396103-13.94974747j,
#        -21. +0.j , -9.36396103+13.94974747j,
#          2. -1.j , 3.36396103 -4.05025253j])

N = len(signal)
fourier = empty(N,complex)
for k in range(N): # equivalent but much slower
    fourier[k] = sum(signal * exp(-1j*2*pi*k*arange(N)/N))
# ...
timestep = 0.1 # if unit=day -> freq unit=cycles/day
fftfreq(N, d=timestep) # freqs corresponding to 'fourier'
# array([ 0. , 1.25, 2.5 , 3.75, -5. , -3.75, -2.5 , -1.25])

