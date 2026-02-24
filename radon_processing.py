#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 25 20:03:09 2023

@author: klaudio
"""

import numpy as np
import pandas as pd
# import matplotlib.pyplot as plt
import MFDFA as mf
import nolds

#=============================================================================#
#                             Preparing Data                                  #
#=============================================================================#

with open('Data/radon_data.txt', 'r') as fp:
    count = len(fp.readlines())
    # print('Total lines:', count) # 8


with open('Data/radon_data.txt', 'r') as fp:
    for i in range(7):
        fp.readline()
    
    day = []
    time_day = []
    radonval = []
    temp = []
    rh = []
    for i in range(7,count):
        a = fp.readline().split('\t')
        day.append(a[1])
        # time_day.append(a[1][11:19])
        radonval.append(float(a[2][:3]))
        temp.append(float(a[3][:4]))
        rh.append(float(a[4][:2]))

day = np.array(day,dtype=np.datetime64)
time_day = np.array(time_day)
radonval = np.array(radonval)
temp = np.array(temp)
rh = np.array(rh)

# plt.plot(day,radonval)

# The values in the range (of measurements' times) 1879 - 2040 pertain to the
# period when every window of the flat (except one) were closed and the device
# was active. Values 2696 to 2697 represent measurements that pertain to the
# period during which the dedector was turned off
radonval_effective = np.concatenate((radonval[:1880],radonval[2041:2696],radonval[2698:]))
day_effective = np.concatenate((day[:1880], day[2041:2696],day[2698:]))

# Import rainfall data
# Uploading data
rainfall = pd.read_excel('Data/SHKODRA_Daily_Rain.xlsx',sheet_name = 'Daily Rainfall DATA')
daily_R = pd.read_excel('Data/Daily_R_Shkodra_DATE.xlsx',sheet_name='All_Days')
historic_rainfall = pd.read_excel('Data/SHKODRA_ANNUAL_RAIN_DATA_EMS2023.xlsx',sheet_name = 'Sheet1')

# Data hygiene (converting to numpy array)
Date_short = rainfall['DATA'].to_numpy()
R24 = rainfall['R24'].to_numpy()
Date_long = daily_R['DATE'].to_numpy()
R_long = daily_R['Reshje'].to_numpy()
His_DATA = historic_rainfall['DATA'].to_numpy()
His_Year_R = historic_rainfall['AN_TOT_R'].to_numpy()
His_R_D = historic_rainfall['No_R_D'].to_numpy()


#=============================================================================#
#                               Functions                                     #
#=============================================================================#

# Calculating the Lyapunov Exponent (LE) for a given time series
# The function of difference between two values of the series
def d(series,i,j):
    return abs(series[i]-series[j])

# The function calculates the coefficients of linear fit by least squares
def linear_fit(series1,series2):
    X = series1 - np.mean(series1)
    Y = series2 - np.mean(series2)
    A = np.dot(X,Y)/np.dot(X,X)
    B = np.mean(series2 - A*series1)
    return A, B

# The function calculates the Lyapuov exponent of a given series
def lyapunov_exponent(series, threshold = 0.01, l = 5):
    N = len(series)
    eps = threshold
    dlist = []
    n = 0
    for i in range(N-l-1):
        for j in range(i+1,N-l):
            if d(series,i,j) < eps:
                if n == 1000:
                    break
                else:
                    n += 1
                    temp = []
                    for k in range(l):
                        if d(series,i+k,j+k) == 0:
                            temp = [-5, -4, -3, -2, -1]
                            dlist.append(temp)
                        else:
                            temp.append(np.log(d(series,i+k,j+k)))
                            dlist.append(temp)
                # if n == 100:
                #     break
    
    lyap = []
    for ser in dlist:
        a, _ = linear_fit(np.arange(len(ser)), ser)
        lyap.append(a)
    lyap_final = [x for x in lyap if ~np.isnan(x)]
    return sum(lyap_final)/len(lyap_final)


#=============================================================================#
#                          Benchmarking the methods                           #
#=============================================================================#

# import scipy.io
# mat = scipy.io.loadmat('Dip_Mom_4_Myr.mat')
# dipmom = mat['Dip_Mom_4_Myr']

# lag = np.unique(np.logspace(0.5, 3, 100, dtype=int))
# q = 2 # Order pf the Hurst exponent
# order = 1 # order of the polynomial
# lag, dfa = mf.MFDFA(dipmom[:,1], lag = lag, q = q, order = order)
# H_hat = np.polyfit(np.log(lag)[4:20],np.log(dfa[4:20]),1)[0]

# print('Estimated H = '+'{:.3f}'.format(H_hat[0]))


# # Cacluation with nolds
# h = nolds.hurst_rs(dipmom[:,1])
# H = nolds.dfa(dipmom[:,1])

# print('Estimated H = '+'{:.3f}'.format(h))
# print('Estimated H = '+'{:.3f}'.format(H))

# # Calculation with the defined functions above
# le = lyapunov_exponent(dipmom[:,3])

# # Calculation with nolds
# le_1 = nolds.lyap_r(dipmom[:,3])
# le_2 = nolds.lyap_e(dipmom[:,3])

# print(np.round(le,4), np.round(le_1,4), np.round(np.max(le_2),4))


#=============================================================================#
#                               Main Body                                     #
#=============================================================================#

# CALCULATION OF LYAPUNOV'S EXPONENT OF THE SERIES IN VARIOUS WAYS
# Calculation with the defined functions above
le = lyapunov_exponent(radonval)
le_effective = lyapunov_exponent(radonval_effective)

le_R_short = lyapunov_exponent(R24)
le_R_long = lyapunov_exponent(R_long)

# # Calculation with nolds
# le_1 = nolds.lyap_r(radonval)
# le_effective_1 = nolds.lyap_r(radonval_effective)
# le_2 = nolds.lyap_e(radonval)
# le_effective_2 = nolds.lyap_e(radonval_effective)

# print(np.round(le,4), np.round(le_effective,4), np.round(le_1,4), np.round(le_effective_1,4), np.round(np.max(le_2),4), np.round(np.max(le_effective_2),4))
print(np.round(le,4), np.round(le_effective,4), np.round(le_R_short,4), np.round(le_R_long,4))

# # CALCULATION OF HURST EXPONENT
# # Calculation with MFDFA
# lag = np.unique(np.logspace(0.5, 3, 100, dtype=int))
# q = 2 # Order pf the Hurst exponent
# order = 1 # order of the polynomial
# lag1, dfa1 = mf.MFDFA(radonval, lag = lag, q = q, order = order)
# lag2, dfa2 = mf.MFDFA(radonval_effective, lag = lag, q = q, order = order)

# H_hat_1 = np.polyfit(np.log(lag1)[4:20],np.log(dfa1[4:20]),1)[0]
# H_hat_2 = np.polyfit(np.log(lag2)[4:20],np.log(dfa2[4:20]),1)[0]

# print('Estimated H = '+'{:.3f}'.format(H_hat_1[0]))
# print('Estimated H_eff = '+'{:.3f}'.format(H_hat_2[0]))


# # Cacluation with nolds
# h1 = nolds.hurst_rs(radonval)
# h2 = nolds.hurst_rs(radonval_effective)
# H1 = nolds.dfa(radonval)
# H2 = nolds.dfa(radonval_effective)

# print('Estimated H = '+'{:.3f}'.format(h1))
# print('Estimated H_eff = '+'{:.3f}'.format(h2))
# print('Estimated H(dfa) = '+'{:.3f}'.format(H1))
# print('Estimated H_eff(dfa) = '+'{:.3f}'.format(H2))
