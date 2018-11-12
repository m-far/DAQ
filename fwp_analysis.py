# -*- coding: utf-8 -*-
"""
This module contains tools for data analysis.

Some of its most useful tools are:
    
mean : function
    Returns average or weighted average and standard deviation.
linear_fit : function
    Applies linear fit and returns m, b and Rsq. Can also plot it.
nonlinear_fit : function
    Applies nonlinear fit and returns parameters and Rsq. Plots it.
smooth : function
    Smooths data using a window with requested size.

@author: Vall
"""

import fwp_string as fst
import matplotlib.pyplot as plt
from math import sqrt
import numpy as np
from scipy.optimize import curve_fit
from scipy.signal import find_peaks
from collections import namedtuple

#%%

def rms(data):
    """Takes a list or array and returns RMS value.
    
    Parameters
    ---------
    data : array or list
        Data to be analized.
    
    Returns
    -------
    float
        RMS value of analized data.
    
    """
    
    import numpy as np
    
    return np.sqrt(np.mean((np.array(data))**2))

#%%

def main_frequency(data, samplerate=44100):
    """Returns main frequency and its Fourier amplitude.
    
    Parameters
    ----------
    data : np.array
        Data inside a 1D array.
    samplerate : int, float
        The data's sampling rate.
    
    Returns
    -------
    samplerate : int, float
        The data's sampling rate.
    main_frequency : float
        The data's main frequency.
    fourier_peak : float
        The main frequency's fourier amplitude.
    """
    
    fourier = np.abs(np.fft.rfft(data))
    fourier_frequencies = np.fft.rfftfreq(len(data), d=1./samplerate)
    max_frequency = fourier_frequencies[np.argmax(fourier)]
    fourier_peak = max(fourier)
    
    return max_frequency, fourier_peak

#%%

def mean(X, dX=None):
    """Returns average or weighted average and standard deviation.
    
    If dX is given, it returns weighted average (weight=1/dX**2) of 
    data. If not, it returns common average.

    Parameters
    ----------
    X : list, np.array
        Data.
    dX=None : list, np.array
        Data's error.
    
    Returns
    -------
    (mean, std): tuple
        This tuple contains data's mean and standard deviation. If dX is 
        given, it returns weighted values (weight=1/dX**2).
    
    Raises
    ------
    "The X data is not np.array-like" : TypeError
        If X can't be easily converted to numpy array.
    "The dX data is not np.array-like" : TypeError
        If dX can't be easily converted to numpy array.
    "The dX array's length should match X's" : IndexError
        If dX's length doesn't match X's.
    
    """
    
    
    if not isinstance(X, np.ndarray):
        try:
            X = np.array(X)
        except:
            raise TypeError("The X data is not np.array like")

    if dX is not None:
        if not isinstance(dX, np.ndarray):
            try:
                dX = np.array(dX)
            except:
                raise TypeError("The dX data is not np.array like")
        if len(dX) != len(X):
            raise IndexError("The dX array's length should match X's")

        mean = np.average(X, weights=1/dX**2)
        variance = np.average((X-mean)**2, weights=1/dX**2)
        return (mean, sqrt(variance))
    
    else:
        return (np.mean(X), np.std(X))

#%%

def linear_fit(X, Y, dY=None, showplot=True,
               plot_some_errors=(False, 20), **kwargs):
    """Applies linear fit and returns m, b and Rsq. Can also plot it.
    
    By default, it applies minimum-square linear fit 'y = m*x + b'. If 
    dY is specified, it applies weighted minimum-square linear fit.
    
    Parameters
    ----------
    X : np.array, list
        Independent X data to fit.
    Y : np-array, list
        Dependent Y data to fit.
    dY : np-array, list
        Dependent Y data's associated error.
    shoplot : bool
        Says whether to plot or not.
    plot_some_errors : tuple (bool, int)
        Says wehther to plot only some error bars (bool) and specifies 
        the number of error bars to plot.
    
    Returns
    -------
    rsq : float
        Linear fit's R Square Coefficient.
    (m, dm): tuple (float, float)
        Linear fit's slope: value and associated error, both as float.
    (b, db): tuple (float, float)
        Linear fit's origin: value and associated error, both as float.
        
    Other Parameters
    ----------------
    txt_position : tuple (horizontal, vertical), optional
        Indicates the parameters' text position. Each of its values 
        should be a number (distance in points measured on figure). 
        But vertical value can also be 'up' or 'down'.
    mb_units : tuple (m_units, b_units), optional
        Indicates the parameter's units. Each of its values should be a 
        string.
    mb_error_digits : tuple (m_error_digits, b_error_digits), optional
        Indicates the number of digits to print in the parameters' 
        associated error. Default is 3 for slope 'm' and 2 for intercept 
        'b'.
    mb_string_scale : tuple (m_string_scale, b_string_scale), optional
        Indicates whether to apply string prefix's scale to printed 
        parameters. Each of its values should be a bool; i.e.: 'True' 
        means 'm=1230.03 V' with 'dm = 10.32 V' would be printed as 
        'm = (1.230 + 0.010) V'. Default is '(False, False)'.
    rsq_decimal_digits : int, optional.
        Indicates the number of digits to print in the Rsq. Default: 3.
        
    Warnings
    --------
    The returned Rsq doesn't take dY weights into account.
    
    """

    # ¿Cómo hago Rsq si tengo pesos?
    
    if dY is None:
        W = None
    else:
        W = 1/dY**2
        
    fit_data = np.polyfit(X,Y,1,cov=True,w=W)
    
    m = fit_data[0][0]
    dm = sqrt(fit_data[1][0,0])
    b = fit_data[0][1]
    db = sqrt(fit_data[1][1,1])
    rsq = 1 - sum( (Y - m*X - b)**2 )/sum( (Y - np.mean(Y))**2 )

    try:
        kwargs['text_position']
    except KeyError:
        if m > 1:
            aux = 'up'
        else:
            aux = 'down'
        kwargs['text_position'] = (.02, aux)

    if showplot:

        plt.figure()
        if dY is None:
            plt.plot(X, Y, 'b.', zorder=0)
        else:
            if plot_some_errors[0] == False:
                plt.errorbar(X, Y, yerr=dY, linestyle='b', marker='.',
                             ecolor='b', elinewidth=1.5, zorder=0)
            else:
                plt.errorbar(X, Y, yerr=dY, linestyle='-', marker='.',
                             color='b', ecolor='b', elinewidth=1.5,
                             errorevery=len(Y)/plot_some_errors[1], 
                             zorder=0)
        plt.plot(X, m*X+b, 'r-', zorder=100)
        plt.legend(["Ajuste lineal ponderado","Datos"])
        
        kwargs_list = ['mb_units', 'mb_string_scale', 
                       'mb_error_digits', 'rsq_decimal_digits']
        kwargs_default = [('', ''), (False, False), (3, 2), 3]
        for key, value in zip(kwargs_list, kwargs_default):
            try:
                kwargs[key]
            except KeyError:
                kwargs[key] = value
        
        if kwargs['text_position'][1] == 'up':
            vertical = [.9, .82, .74]
        elif kwargs['text_position'][1] == 'down':
            vertical = [.05, .13, .21]
        else:
            if kwargs['text_position'][1] <= .08:
                fact = .08
            else:
                fact = -.08
            vertical = [kwargs['text_position'][1]+fact*i for i in range(3)]
        
        plt.annotate('m = {}'.format(fst.error_value(
                        m, 
                        dm,
                        error_digits=kwargs['mb_error_digits'][0],
                        units=kwargs['mb_units'][0],
                        string_scale=kwargs['mb_string_scale'][0],
                        one_point_scale=True,
                        legend=True)),
                    (kwargs['text_position'][0], vertical[0]),
                    xycoords='axes fraction')
        plt.annotate('b = {}'.format(fst.error_value(
                        b, 
                        db,
                        error_digits=kwargs['mb_error_digits'][1],
                        units=kwargs['mb_units'][1],
                        string_scale=kwargs['mb_string_scale'][1],
                        one_point_scale=True,
                        legend=True)),
                    (kwargs['text_position'][0], vertical[1]),
                    xycoords='axes fraction')
        rsqft = r'$R^2$ = {:.' + str(kwargs['rsq_decimal_digits']) + 'f}'
        plt.annotate(rsqft.format(rsq),
                    (kwargs['text_position'][0], vertical[2]),
                    xycoords='axes fraction')
        
        plt.show()

    return rsq, (m, dm), (b, db)

#%%

def nonlinear_fit(X, Y, fitfunction, initial_guess=None, dY=None, 
                  showplot=True, plot_some_errors=(False, 20), 
                  **kwargs):
    """Applies nonlinear fit and returns parameters and Rsq. Plots it.
    
    By default, it applies minimum-square fit. If dY is specified, it 
    applies weighted minimum-square fit.
    
    Parameters
    ----------
    X : np.array, list
        Independent X data to fit.
    Y : np-array, list
        Dependent Y data to fit.
    fitfunction : function
        The function you want to apply. Its arguments must be 'X' as 
        np.array followed by the other parameters 'a0', 'a1', etc as 
        float. Must return only 'Y' as np.array.
    initial_guess=None : list, optional
        A list containing a initial guess for each parameter.
    dY : np-array, list, optional
        Dependent Y data's associated error.
    shoplot : bool
        Says whether to plot or not.
    plot_some_errors : tuple (bool, int)
        Says wehther to plot only some error bars (bool) and specifies 
        the number of error bars to plot.
    
    Returns
    -------
    rsq : float
        Fit's R Square Coefficient.
    parameters : list of tuples
        Fit's parameters, each as a tuple containing value and error, 
        both as tuples.
    
    Other Parameters
    -----------------
    txt_position : tuple (horizontal, vertical), optional
        Indicates the parameters' text position. Each of its values 
        should be a number (distance in points measured on figure). 
        But vertical value can also be 'up' or 'down'.
    par_units : list, optional
        Indicates the parameters' units. Each of its values should be a 
        string.
    par_error_digits : list, optional
        Indicates the number of digits to print in the parameters' 
        associated error. Default is 3 for all of them.
    par_string_scale : list, optional
        Indicates whether to apply string prefix's scale to printed 
        parameters. Each of its values should be a bool. Default is 
        False for all of them.
    rsq_decimal_digits : int, optional.
        Indicates the number of digits to print in the Rsq. Default: 3.
        
    Warnings
    --------
    The returned Rsq doesn't take dY weights into account.
    
    """
    
    if not isinstance(X, np.ndarray):
        raise TypeError("X should be a np.array")
    if not isinstance(Y, np.ndarray):
        raise TypeError("Y should be a np.array")
    if not isinstance(dY, np.ndarray) and dY is not None:
        raise TypeError("dY shouuld be a np.array")
    if len(X) != len(Y):
        raise IndexError("X and Y must have same lenght")
    if dY is not None and len(dY) != len(Y):
        raise IndexError("dY and Y must have same lenght")
    
    if dY is None:
        W = None
    else:
        W = 1/dY**2
    
    parameters, covariance = curve_fit(fitfunction, X, Y,
                                       p0=initial_guess, sigma=W)  
    rsq = sum( (Y - fitfunction(X, *parameters))**2 )
    rsq = rsq/sum( (Y - np.mean(Y))**2 )
    rsq = 1 - rsq

    if showplot:
        
        plt.figure()
        if dY is None:
            plt.plot(X, Y, 'b.', zorder=0)
        else:
            if plot_some_errors[0] == False:
                plt.errorbar(X, Y, yerr=dY, linestyle='b', marker='.',
                             ecolor='b', elinewidth=1.5, zorder=0)
            else:
                plt.errorbar(X, Y, yerr=dY, linestyle='-', marker='.',
                             color='b', ecolor='b', elinewidth=1.5,
                             errorevery=len(Y)/plot_some_errors[1], 
                             zorder=0)
        plt.plot(X, fitfunction(X, *parameters), 'r-', zorder=100)        
        plt.legend(["Ajuste lineal ponderado","Datos"])
        
        n = len(parameters)
        kwargs_list = ['text_position', 'par_units', 'par_string_scale', 
                       'par_error_digits', 'rsq_decimal_digits']
        kwargs_default = [(.02,'up'), ['' for i in range(n)], 
                          [False for i in range(n)], 
                          [3 for i in range(n)], 3]
        for key, value in zip(kwargs_list, kwargs_default):
            try:
                kwargs[key]
                if key != 'text_position':
                    try:
                        if len(kwargs[key]) != n:
                            print("Wrong number of parameters",
                                  "on '{}'".format(key))
                            kwargs[key] = value
                    except TypeError:
                        kwargs[key] = [kwargs[key] for i in len(n)]
            except KeyError:
                kwargs[key] = value
        
        if kwargs['text_position'][1] == 'up':
            vertical = [.9-i*.08 for i in range(n+1)]
        elif kwargs['text_position'][1] == 'down':
            vertical = [.05+i*.08 for i in range(n+1)]
        else:
            if kwargs['text_position'][1] <= .08:
                fact = .08
            else:
                fact = -.08
            vertical = [
                kwargs['text_position'][1]+fact*i for i in range(n+1)]
        
        for i in range(n):
            plt.annotate(
                    'a{} = {}'.format(
                        i,
                        fst.error_value(
                            parameters[i], 
                            sqrt(covariance[i,i]),
                            error_digits=kwargs['par_error_digits'][i],
                            units=kwargs['par_units'][i],
                            string_scale=kwargs['par_string_scale'][i],
                            one_point_scale=True,
                            legend=True)),
                    (kwargs['text_position'][0], vertical[i]),
                    xycoords='axes fraction')
        rsqft = r'$R^2$ = {:.' + str(kwargs['rsq_decimal_digits'])+'f}'
        plt.annotate(rsqft.format(rsq),
                    (kwargs['text_position'][0], vertical[-i]),
                    xycoords='axes fraction')
        
        plt.show()
    
    parameters_error = np.array(
            [sqrt(covariance[i,i]) for i in range(n)])
    parameters = list(zip(parameters, parameters_error))
    
    return rsq, parameters

#%%

def smooth(X, window_len=11, window='hanning'):
    """Smooths data using a window with requested size.
    
    This method is based on the convolution of a scaled window with the 
    signal. The signal is prepared by introducing reflected copies of 
    the signal (with the window size) in both ends so that transient 
    parts are minimized in the begining and end part of the output 
    signal.
    
    Parameters
    ----------
    X : np.array
        Input signal 
    window_len : int {1, 3, 5, ...}
        Dimension of the smoothing window; should be an odd integer
    window : str {'flat', 'hanning', 'hamming', 'bartlett', 'blackman'}
        Type of window; i.e. flat window will produce a moving average 
        smoothing. Could be the window itself if an array instead of a 
        string.

    Returns
    -------
    np.array
        Smoothed signal
        
    Examples
    --------
    >>> t = np.linspace(-2,2,0.1)
    >>> x = np.sin(t) + np.randn(len(t))*0.1
    >>> y = smooth(x)
    
    See Also
    --------
    numpy.hanning
    numpy.hamming
    numpy.bartlett
    numpy.blackman
    numpy.convolve
    scipy.signal.lfilter
    
    Warnings
    --------
    Beware! This was taken from: SciPy-CookBook/ipython/SignalSmooth.py
    
    length(output) != length(input). To correct this: return 
    y[(window_len/2-1):-(window_len/2)] instead of just y.
      
    """

    if X.ndim != 1:
        raise ValueError("X should be a 1 dimension array.")

    if X.size < window_len:
        raise ValueError("X needs to be bigger than window_len.")

    if window_len < 3:
        return X

    allowed = ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']
    if not window in allowed:
        raise ValueError("Window should be on {}".format(allowed))

    S = np.r_[X[window_len-1 : 0 : -1], X, X[-2 : -window_len-1 : -1]]

    if window == 'flat': # moving average
        W = np.ones(window_len, 'd')
    else:
        W = eval('np.' + window + '(window_len)')
    
    Y = np.convolve(W/W.sum(), S, mode='valid')
    
    return Y

#%%

def find(L, L0):
    """Takes an array of data and searches the index(es) of value L0.
    
    Parameters
    ----------
    L : list, np.array
        Array where I search
    L0 : int, float
        Value I search
    
    Returns
    -------
    ind : list
        Indexes of L that match L0.
    
    Raises
    ------
    "L must be a list or similar" : TypeError
        If L is not of an allowed type.
    
    """

    if not isinstance(L, list):
        try:
            L = list(L)
        except TypeError:
            L = [].append(L)
        else:
            return TypeError("L must be a list or similar")
            
    ind = []
    N = -1
    while N < len(L):
        val = L[N+1 : len(L)]
        try:
            # Write the index on L and not on val
            N = val.index(L0) + len(L) - len(val)
        except ValueError:
            break
        ind.append(N)
        
    return ind

#%%

def compare_error_value(X1, dX1, X2, dX2):
    """Comparison of two measuremntes X1+-dX1 and X2+-dX2.
    
    Parameters
    ----------
    X1 : int, float
        First value.
    dX1 : int, float.
        First value's error.
    X2 : int, float
        Second value.
    dX2 : int, float
        Second value's error.
    
    Returns
    -------
    string : str
        Written answer.
        
    """
    
    from numpy import array
        
    A1 = (X1-dX1, X1+dX1)
    A2 = (X2-dX2, X2+dX2)
    
    answer = array([0,0])
    if A2[0] <= X1[0] <= A2[1]:
        answer[0] = answer[0]+1
    if A1[0]<=X2[0]<=A1[1]:
        answer[0] = answer[0]+1
    if A1[0]<=A2[0]<=A1[1]:
        answer[1] = answer[1]+1
    if A2[0]<=A1[0]<=A2[1]:
        answer[1] = answer[1]+1
    if A1[0]<=A2[1]<=A1[1]:
        answer[1] = answer[1]+1
    if A2[0]<=A1[1]<=A2[1]:
        answer[1] = answer[1]+1    
        
    if X1 == X2:
        string = "Coincidencia absoluta "
    elif answer[0] == 0:
        string = "No coincidencia "
    elif answer[0] == 1:
        string = "Coincidencia parcial "
    else:
        string = "Coincidencia total "
    if answer[1] < 2:
        string = string + "sin intersección de incertezas"
    elif answer[1] == 2:
        string = string + "con intersección parcial de incertezas"
    elif answer[1] == 3:
        string = string + "con intersección total de incertezas"
    else:
        string = string + "con intersección absoluta de incertezas"
        
    return string

#%%

def single_extreme(X, mode='min'):    
    """Returns an absolute extreme of a multidimensional array.
    
    Parameters
    ----------
    X : list, array
        Multidimensional array-like of numbers.
    mode : str {'min', 'max'}
        Indicates which extreme to find (if a minimum or maximum).
    
    Returns
    -------
    float, int
        Value of the extreme.
    
    """
    
    if mode not in ['min', 'max']:
        raise ValueError("mode must be 'min' or 'max'")
    
    if mode == 'min':
        while True:
            try:
                X = list(X)
                X[0]
                X = min(X[i] for i in range(len(X)))
            except:
                return X

    else:
        while True:
            try:
                X = list(X)
                X[0]
                X = max(X[i] for i in range(len(X)))
            except:
                return X
            
#%% Distance between peaks
                
def peak_separation(signal, time=1, *args, **kwargs):
    '''Calculates mean peak separation.
    
    Parameters
    ----------
    signal : array-like
        Signal to evaluates peaks on
    time : scalar or array-like
        If scalar, it should indicate time step. If array-like, 
        should be same lenght as signal and correspond to time 
        of measurements.

    Other parameters
    ----------------
    Parameters passed to scipy.signal.find_peaks.
        height
        threshold
        distance
        prominence
        width
        wlen
        rel_height
    
    Returns
    -------
    string : str
        Written answer.
    
    See also: scipy.signal.find_peaks
    
    '''
        
    peaks = find_peaks(signal, *args, **kwargs)[0]
    
    if isinstance(time, (list, tuple, np.ndarray)):
        if not len(signal)==len(time):
            raise ValueError('Time and signal must be same lenght.')
            
        peak_times = time[peaks]
    else:
        peak_times = peaks * time
        
    return np.mean(peak_times)

#%% PID class



class PIDController:
    '''A simple class implementing a PID contoller.
    
    Copied from...
    
    Parameters
    ----------
    setpoint : int, float
        Value the PID is suposed to achieve and keep constant.
    kp : int, float, optional
        Value of the PID proportional term's constant.
    ki : int, float, optional
        Value of the PID integral term's constant.
    kd : int, float, optional
        Value of the PID derivative term's constant.
    dt : int, float, optional
        Value of the time interval.
    
    Example
    -------
    >>> pid = PIDController(42, 3, 2, 1)
    >>> while True:
    >>>     signal = read()
            actuator = pid.calculate(signal)
            write(actuator)
    
    '''

    def __init__(self, setpoint, kp=1.0, ki=0.0, kd=0.0, dt=1):

        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt

        self.last_error = 0
        self.p_term = 0
        self.i_term = 0
        self.d_term = 0

    def calculate(self, feedback_value):
        
        error = self.setpoint - feedback_value

        delta_error = error - self.last_error

        self.p_term = error
        self.i_term += error * self.dt
        self.d_term = delta_error / self.dt

        self.last_error = error

        new_value = self.kp * self.p_term
        new_value += self.ki * self.i_term
        new_value += self.kd * self.d_term

        return new_value

stuff_to_log = ('feedback_value',
                'new_value',
                'last_error',
                'p_term',
                'i_term',
                'd_term')

# Create a named tuple with default value for all fields an empty list
PIDlog = namedtuple('PIDLog', stuff_to_log, defaults=[[]]*len(stuff_to_log))

class PIDControllerWithLog:
    """A simple class implementing a PID contoller that keeps a log.
    
    Copied from...
    
    Parameters
    ----------
    setpoint : int, float
        Value the PID is suposed to achieve and keep constant.
    kp : int, float, optional
        Value of the PID proportional term's constant.
    ki : int, float, optional
        Value of the PID integral term's constant.
    kd : int, float, optional
        Value of the PID derivative term's constant.
    dt : int, float, optional
        Value of the time interval.
    
    Example
    -------
    >>> pid = PIDControllerWithLog(42, 3, 2, 1)
    >>> while True:
    >>>     signal = read()
            actuator = pid.calculate(signal)
            write(actuator)
    """
    def __init__(self, setpoint, kp=1.0, ki=0.0, kd=0.0, dt=1, log_data=False):

        self.setpoint = setpoint
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.dt = dt

        self.last_error = 0
        self.p_term = 0
        self.i_term = 0
        self.d_term = 0
        
        # start with a fresh log
        self.log_data = log_data
        self.clearlog()
        
    def __repr__(self):
        string = 'PID with parameters: kp={}, ki={}, kd={}'
        return string.format(self.kp, self.ki, self.kd)

    def calculate(self, feedback_value):
        
        error = self.setpoint - feedback_value

        delta_error = error - self.last_error

        self.p_term = error
        self.i_term += error * self.dt
        self.d_term = delta_error / self.dt

        self.last_error = error

        new_value = self.kp * self.p_term
        new_value += self.ki * self.i_term
        new_value += self.kd * self.d_term
        
        if self.log_data:
            self.last_log = PIDlog._make([feedback_value, new_value, self.last_error,
                                          self.p_term, self.i_term, self.d_term])
            self.__log.append(self.last_log)

        return new_value

    def clearlog(self):
        self.__log = []
        self.last_log = PIDlog()

    @property
    def log(self):
        #read-only
        if self.__log:
            return self.__makelog__()
        else:
            raise ValueError('No logged data.')
            
    def __makelog__(self):
        '''Make a PIDlog nuamedtuple containing the list of each
        value in each field.'''
        log = []
        for i in range(len(self.last_log)):
            log.append([prop[i] for prop in self.__log])
        return PIDlog._make(log)
#%%
pid = PIDControllerWithLog(10, log_data=True)
for k in range(30): pid.calculate(k)
print(pid.log)

#%%
        
def clip_bewtween(value, lower=0, upper=100):
    
    value = max(lower, value)
    value = min(upper, value)
    return value

def append_data_to_string(*args):
    out = ''
    for value in args:
        out += '\t' + str(value)
    return out + '\n'