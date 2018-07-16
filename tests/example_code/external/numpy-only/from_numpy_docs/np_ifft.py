from numpy import *
from numpy.fft import *
signal = array([-2., 8., -6., 4., 1., 0., 3., 5.])
fourier = fft(signal)
ifft(fourier) # Inverse fourier transform
# array([-2. +0.00000000e+00j, 8. +1.51410866e-15j, -6. +3.77475828e-15j,
#         4. +2.06737026e-16j, 1. +0.00000000e+00j, 0. -1.92758271e-15j,
#         3. -3.77475828e-15j, 5. +2.06737026e-16j])

allclose(signal.astype(complex), ifft(fft(signal))) # ifft(fft()) = original signal
# True

N = len(fourier)
signal = empty(N,complex)
for k in range(N): # equivalent but much slower
    signal[k] = sum(fourier * exp(+1j*2*pi*k*arange(N)/N)) / N

