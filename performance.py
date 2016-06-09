#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from StringIO import StringIO

def helper(x):
    plt.plot(x)
    plt.show()

def helper_db(x):
    plt.plot(20*np.log10(x))
    plt.show()

def rgbtotuple(r, g, b):
    return [r/255., g/255., b/255.]

# Source: https://github.com/MTG/sms-tools/blob/master/software/models/dftModel.py

from scipy.fftpack import fft, ifft
import math

tol = 1e-14 # threshold used to compute phase

def dftAnal(x, w, N):
    """
    Analysis of a signal using the discrete Fourier transform
    x: input signal, w: analysis window, N: FFT size
    returns mX, pX: magnitude and phase spectrum
    """

    if np.log2(N) % 2 > tol:                                 # raise error if N not a power of two
        raise ValueError("FFT size (N) is not a power of 2")

    if (w.size > N):                                        # raise error if window size bigger than fft size
        raise ValueError("Window size (M) is bigger than FFT size")

    hN = (N/2)+1                                            # size of positive spectrum, it includes sample 0
    hM1 = int(math.floor((w.size+1)/2))                     # half analysis window size by rounding
    hM2 = int(math.floor(w.size/2))                         # half analysis window size by floor
    fftbuffer = np.zeros(N)                                 # initialize buffer for FFT
    w = w / sum(w)                                          # normalize analysis window
    xw = x*w                                                # window the input sound
    fftbuffer[:hM1] = xw[hM2:]                              # zero-phase window in fftbuffer
    fftbuffer[-hM2:] = xw[:hM2]
    fftbuffer = xw
    X = fft(fftbuffer)                                      # compute FFT
    absX = abs(X[:hN])                                      # compute ansolute value of positive side
    absX[1:] = absX[1:]*2.                                  # normalize frequencies above DC
    absX[absX<np.finfo(float).eps] = np.finfo(float).eps    # if zeros add epsilon to handle log
    mX = 20 * np.log10(absX)                                # magnitude spectrum of positive frequencies in dB
    X[:hN].real[np.abs(X[:hN].real) < tol] = 0.0            # for phase calculation set to 0 the small values
    X[:hN].imag[np.abs(X[:hN].imag) < tol] = 0.0            # for phase calculation set to 0 the small values
    pX = np.unwrap(np.angle(X[:hN]))                        # unwrapped phase spectrum of positive frequencies
    return mX, pX

with open('adc_raw_output.csv', 'r') as f:
    adc_raw_output_csv = f.readlines()

firstPole, inputFreq, clkPeriod, tRiseFall = adc_raw_output_header = np.genfromtxt(StringIO(adc_raw_output_csv[0]), delimiter=',', usecols=(1, 3, 5, 7), unpack=True)
adc_raw_output = np.genfromtxt(StringIO(''.join(adc_raw_output_csv[1:])), delimiter=',', skip_header=1, dtype=np.int32)

print "First Pole:\t\t%d" % firstPole
print "Input Frequency:\t%d Hz" % inputFreq
print "Sample Frequency:\t%d Hz" % (1./clkPeriod)

sampleFreq = 1/clkPeriod
nPeriods = int(5/(clkPeriod*inputFreq))

N = 4096
x = (adc_raw_output[-N:])
#w = np.hamming(N)
#w = np.hanning(N)
w = np.ones(N)
#w = np.blackman(N)
mX, pX = dftAnal(x, w, N)

fftFrequencies = np.round(np.arange(mX.size)*(sampleFreq/N))
freqResolution = sampleFreq/N
indexComponents = np.arange(1, np.int(sampleFreq/2/inputFreq)+1)*int(inputFreq/freqResolution)

indexPresentComp = indexComponents[mX[indexComponents]>-89.]

n_harmonics = 3 # same as Cadence's "Harmonics" less one

thd = np.sqrt(sum((10**((mX[indexComponents[1:1+n_harmonics]]-mX[indexComponents[0]])/20))**2))
thd_db = 20*np.log10(thd)
print "Total Harmonic Distortion:\t%.3f%%" % (thd*100.)
print "\t\t\t\t%.2f dB" % thd_db

bin_spread = 0

noise =10**(mX/20)
noise[np.arange(bin_spread+1)] = np.finfo(float).eps # no DC content
# remove signal content
for component in indexComponents:
    noise[component+bin_spread-np.arange(2*bin_spread+1)] = np.finfo(float).eps
#helper_db(noise)
noise = np.sqrt(sum(noise**2))
noise = 20*np.log10(noise)
print "Noise Floor:\t\t%.2f dB" % noise
snr = mX[indexComponents[0]] - noise
print "Signal to Noise Ratio:\t%.2f dB" % snr

residual = 10**(mX/20)
residual[np.arange(bin_spread+1)] = np.finfo(float).eps # no DC content
residual[indexComponents[0]+bin_spread-np.arange(2*bin_spread+1)] = np.finfo(float).eps # no fundamental
#helper_db(residual)
residual = np.sqrt(sum(residual**2))
residual = 20*np.log10(residual)
print "Noise and Distortion:\t\t%.2f dB" % residual
sinad = mX[indexComponents[0]] - residual
print "SINAD:\t\t\t\t%.2f dB" % sinad
enob = (sinad-1.76)/6.02
print "Effective Number of Bits:\t%.3f" % enob

plt.style.use('ggplot')

plt.subplot(211)
plt.plot(np.arange(nPeriods)*clkPeriod, adc_raw_output[-nPeriods:],
marker='.')
plt.xlim(0, nPeriods*clkPeriod)
plt.ylim(-1, 16)
plt.title('Sampled signal')
plt.xlabel('Time / s')
plt.ylabel('Amplitude / 1')

plt.subplot(212)
plt.plot(fftFrequencies, mX, '-', fftFrequencies[indexPresentComp[0]], mX[indexPresentComp[0]], 'o',
fftFrequencies[indexPresentComp[1:]], mX[indexPresentComp[1:]], 'o')
plt.xlim(min(fftFrequencies), max(fftFrequencies))
plt.ylim(-80, 30)
plt.title('Frequency spectrum of sampled signal')
plt.xlabel('Frequency / Hz')
plt.ylabel('Amplitude / dB')

plt.tight_layout()
plt.show()
