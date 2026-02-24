#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 18:43:32 2023

@author: klaudio
"""

import numpy as np
import matplotlib.pyplot as plt


# Defining the logistic map: r - the coefficient ranging from 0 to 4; x01 - starting
# value, a.k.a. seed; steps - number of steps to complete one simulation

def logistic_map(r,x0,steps):
    x = np.zeros(steps + 1)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = r*x[i]*(1 - x[i])
    return x[1:]

# Defining the gaussian map: alpha and beta - the coefficients where the latter
# typically ranges from -1 to 1; x02 - starting value, a.k.a. seed;
# steps - number of steps to complete one simulation
def gaussian_map(alpha,beta,x0,steps):
    x = np.zeros(steps + 1)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = np.exp(-alpha*x[i]**2) + beta#*x[i]**2
    return x[1:]

# Defining the logistic exponential map: r - the coefficient ranging from 0 to 4;
# x03 - starting value, a.k.a. seed; steps - number of steps to complete one simulation
def logistic_exponential_map(r,x0,steps):
    x = np.zeros(steps + 1)
    x[0] = x0
    for i in range(steps):
        x[i + 1] = x[i]*np.exp(r*(1 - x[i]))
    return x[1:]

# Finds the steady state of a given time series pertaining to the logistic map
# last - the last values of the series x that are analyzed
def steady_state(r1,r2,alpha,beta,x01,x02,x03,steps,last,res,mode):
    if mode == 1:
        series = logistic_map(r1,x01,steps)
        temp = np.round(series[len(series)-last:],res)
    elif mode == 2:
        series = gaussian_map(alpha,beta,x02,steps)
        temp = np.round(series[len(series)-last:],res)
    else:
        series = logistic_exponential_map(r2,x03,steps)
        temp = np.round(series[len(series)-last:],res)
    return list(np.unique(np.array(temp)))

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
def lyapunov_exponent(series, threshold, l = 5):
    N = len(series)
    eps = threshold
    dlist = []
    n = 0
    for i in range(N-l-1):
        for j in range(i+1,N-l):
            if d(series,i,j) < eps:
                n += 1
                temp = []
                for k in range(l):
                    if d(series,i+k,j+k) == 0:
                        temp = [-5, -4, -3, -2, -1]
                        dlist.append(temp)
                    else:
                        temp.append(np.log(d(series,i+k,j+k)))
                        dlist.append(temp)
            if n == 100:
                break
    
    lyap = []
    for ser in dlist:
        a, _ = linear_fit(np.arange(len(ser)), ser)
        lyap.append(a)
    return sum(lyap)/len(lyap)


#=============================================================================#
#                               Main Body                                     #
#=============================================================================#

while True:
    x01 = float(input('Provide the initial value for the logistic map: '))
    if x01 < 0 or x01 > 1:
        print('The initial value must be in the range [0, 1]: ')
    else:
        break

while True:
    x02 = float(input('Provide the initial value for the gaussian map: '))
    if x02 < 0 or x02 > 1:
        print('The initial value must be in the range [0, 1]: ')
    else:
        break

while True:
    x03 = float(input('Provide the initial value for the logistic exponential map: '))
    if x03 < 0 or x03 > 1:
        print('The initial value must be in the range [0, 1]: ')
    else:
        break

while True:
    r1_min = float(input('Provide r1_min: '))
    if r1_min < 0 or r1_min >= 4:
        print('r_min should be in the range ]0, 4[: ')
    else:
        break

while True:
    r1_max = float(input('Provide r1_max: '))
    if r1_max < 0 or r1_max >= 4:
        print('r1_min should be in the range ]0, 4]: ')
    elif r1_max < r1_min:
        print('r1_max must be larger than r1_min! Provide r1_max: ')
    else:
        break

while True:
    r2_min = float(input('Provide r2_min: '))
    if r2_min < 0 or r2_min >= 4:
        print('r2_min should be in the range ]0, 4[: ')
    else:
        break

while True:
    r2_max = float(input('Provide r2_max: '))
    if r2_max < 0 or r2_max >= 4:
        print('r2_min should be in the range ]0, 4]: ')
    elif r2_max < r2_min:
        print('r2_max must be larger than r2_min! Provide r2_max: ')
    else:
        break

while True:
    alpha = float(input('Provide \u03B1: '))
    if alpha <= 0:
        print('\u03B1 should be striclty positive: ')
    else:
        break
    
beta_min = float(input('Provide \u03B2_min (Advised -1): '))
beta_max = float(input('Provide \u03B2_max (Advised 1): '))

while True:
    steps = int(input('Provide the duration of one simulation: '))
    if steps <= 0:
        print('The # of steps is a natural number: ')
    else:
        break

while True:
    last = int(input('Provide the last entries of the series to be analyzed: '))
    if last <= 0:
        print('The # of last entries is a natural number: ')
    elif last >= steps/4:
        print('The value provided should be at most steps/4: ')
    else:
        break

while True:
    res = int(input('Provide the rounding: '))
    if last <= 0:
        print('The # of last entries is a natural number: ')
    elif last >= steps/4:
        print('The value provided should be at most steps/4: ')
    else:
        break

# Logistic map
r_val = np.arange(r1_min,r1_max,0.01)
final_list = []
LE_11 = []
for r in r_val:
    lst = steady_state(r,r2_min,alpha,beta_min,x01,x02,x03,steps,last,res,1)
    LE11 = lyapunov_exponent(logistic_map(r,x01,steps), 0.01)
    final_list.append(lst)
    LE_11.append(LE11)

r_val = list(r_val)

LE_1 = [] # List of Lyapunov exponents for each value of r
for r in r_val:
    x = np.array(logistic_map(r, x01, steps))
    LE_temp = np.mean(np.log(abs(r*(1-2*x))))
    LE_1.append(LE_temp)

plt.figure(figsize=(10,6))

ax1 = plt.subplot(211)
for i in range(len(r_val)):
    ax1.plot([r_val[i]]*len(final_list[i]),final_list[i],'m.')
ax1.grid()
ax1.set_xlabel('r',fontsize=14)
ax1.set_ylabel('Steady State values', fontsize=14)

ax2 = plt.subplot(212)
ax2.plot(r_val,LE_1,'b',lw=2,label='Calculation using the ODE formula')
ax2.plot(r_val,LE_11,'k',lw=2,label='Calculation from the series')
ax2.grid()
ax2.set_xlabel('r',fontsize=14)
ax2.set_ylabel('Lyapunov Eksponent', fontsize=14)
ax2.legend(loc='best')
plt.savefig('Lyapunov_logistic_map.pdf')

# Gaussian map
beta_val = np.arange(beta_min,beta_max,0.01)
final_list = []
LE_22 = []
for b in beta_val:
    lst = steady_state(r1_min,r2_min,alpha,b,x01,x02,x03,steps,last,res,2)
    LE22 = lyapunov_exponent(gaussian_map(alpha,b,x02,steps), 0.01)
    final_list.append(lst)
    LE_22.append(LE22)

b_val = list(beta_val)

LE_2 = [] # List of Lyapunov exponents for each value of beta
for b in b_val:
    x = np.array(gaussian_map(alpha, b, x02, steps))
    LE_temp = np.mean(np.log(abs(-alpha*x*np.exp(-alpha*x**2))))# + 2*b*x)))
    LE_2.append(LE_temp)

plt.figure(figsize=(10,6))

ax1 = plt.subplot(211)
for i in range(len(b_val)):
    ax1.plot([b_val[i]]*len(final_list[i]),final_list[i],'m.')
ax1.grid()
ax1.set_xlabel('\u03B2', fontsize=14)
ax1.set_ylabel('Steady State values', fontsize=14)

ax2 = plt.subplot(212)
ax2.plot(b_val,LE_2,'b',lw=2,label='Calculation using the ODE formula')
ax2.plot(b_val,LE_22,'k',lw=2,label='Calculation from the series')
ax2.grid()
ax2.set_xlabel('\u03B2', fontsize=14)
ax2.set_ylabel('Lyapunov Eksponent', fontsize=14)
ax2.legend(loc='best')
plt.savefig('Lyapunov_gaussian_map.pdf')

# Logistic exponential map
r_val = np.arange(r2_min,r2_max,0.01)
final_list = []
LE_33 = []
for r in r_val:
    lst = steady_state(r1_min,r,alpha,beta_min,x01,x02,x03,steps,last,res,3)
    LE33 = lyapunov_exponent(logistic_exponential_map(r,x03,steps), 0.01)
    final_list.append(lst)
    LE_33.append(LE33)

r_val = list(r_val)

LE_3 = [] # List of Lyapunov exponents for each value of r
for r in r_val:
    x = np.array(logistic_exponential_map(r, x03, steps))
    LE_temp = np.mean(np.log(abs(np.exp(r*(1 - x)) - r*x*np.exp(r*(1 - x)))))
    LE_3.append(LE_temp)

plt.figure(figsize=(10,6))

ax1 = plt.subplot(211)
for i in range(len(r_val)):
    ax1.plot([r_val[i]]*len(final_list[i]),final_list[i],'m.')
ax1.grid()
ax1.set_xlabel('r', fontsize=14)
ax1.set_ylabel('Steady State values', fontsize=14)

ax2 = plt.subplot(212)
ax2.plot(r_val,LE_3,'b',lw=2,label='Calculation using the ODE formula')
ax2.plot(r_val,LE_33,'k',lw=2,label='Calculation from the series')
ax2.grid()
ax2.set_xlabel('r',fontsize=14)
ax2.set_ylabel('Lyapunov Eksponent', fontsize=14)
ax2.legend(loc='best')
plt.savefig('Lyapunov_logistic_exponential_map.pdf')
