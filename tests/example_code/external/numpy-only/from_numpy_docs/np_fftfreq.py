from numpy import *
from numpy.fft import *
signal = array([-2., 8., -6., 4., 1., 0., 3., 5.])
fourier = fft(signal)
N = len(signal)
timestep = 0.1 # if unit=day -> freq unit=cycles/day
freq = fftfreq(N, d=timestep) # freqs corresponding to 'fourier'
freq
# array([ 0. , 1.25, 2.5 , 3.75, -5. , -3.75, -2.5 , -1.25])

fftshift(freq) # freqs in ascending order
# array([-5. , -3.75, -2.5 , -1.25, 0. , 1.25, 2.5 , 3.75])

