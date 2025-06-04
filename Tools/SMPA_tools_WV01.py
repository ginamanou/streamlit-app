#------------------------------------------------------------------------------------
# Module: SMPA_tools_V02
# Purpose:  A library of many different functions that are used from several scripts
# Functions:    1    time_calculations
#               2    set_time_for_SPC_to_datetime
#               3    read_all
#               4    df_uc_for_app
#               5    df_spc_for_app
#               6    calculate_strain
#               7    calculate_rate_of_variable
#               8    smoothen_curve
#               9    part_of_curve
#               10   calc_polynomial
#               11   fit_curve_and_local_minimum
#               12   plot_creep_deflecion_curve
#               13   plot_Force_deflecion_curve
#               14   plot_u_rate_over_time
#               15   plot_u_rate_over_u
#               16   plot_smooth_u_rate_over_time
#               17   plot_smooth_u_rate_over_u
#               18   calculate_t0_index
#               19   calculate_tR_index
#               20   plot_u0_and_uR
#           
# External packages:
#           |_____________  pandas
#           |_____________  numpy
#           |_____________  matplotlib
#           |_____________  os
#
# Author:   Georgia Manou, georgia.manou@outlook.com
# Version:  2.0, 15th March 2024
#------------------------------------------------------------------------------------


##################################################################################################################################################################################################
###########################################################               All Imports           ##################################################################################################
##################################################################################################################################################################################################

# Packages related to data manipulation
import pandas as pd
import numpy as np

# Package related to plotting
import matplotlib.pyplot as plt

# Packages related to directory handling
import os
    
##################################################################################################################################################################################################
###########################################################               Function 1                 #############################################################################################
##################################################################################################################################################################################################

def time_calculations(dataframe):
    #------------------------------------------------------------------------------------
    # Function: time_calculations
    # Purpose:  From a pandas datetime object it derives and puts into separate columns the following:
    #             Date
    #             Time
    #             Hour
    #             Minute
    #             Seconds
    #           and calculates and puts into separate columns the following:
    #             Total seconds since the beginning of the experiment
    #             Total minutes since the beginning of the experiment
    #             Total Hours since the beginning of the experiment
    # Input:    dataframe     ... a pandas dataframe
    # Output:   dataframe     ... the samme dataframe that was provided as input but appended with the calculations 
    #           
    # External packages:
    #           |_____________  pandas
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    dataframe['Date'] = pd.to_datetime(dataframe['DateTime']).dt.date
    dataframe['Time'] = pd.to_datetime(dataframe['DateTime']).dt.time
    dataframe['Hour'] = pd.to_datetime(dataframe['DateTime']).dt.hour
    dataframe['Minute'] = pd.to_datetime(dataframe['DateTime']).dt.minute
    dataframe['Second'] = pd.to_datetime(dataframe['DateTime']).dt.second
    dataframe['TotalSeconds'] = dataframe['DateTime'].diff().dt.total_seconds().cumsum()       # Calculate the total amount of seconds since the start of the experimet
    dataframe.loc[0, 'TotalSeconds'] = 0
    dataframe['TotalSeconds'] = dataframe['TotalSeconds'].astype(int, errors='ignore')
    dataframe['TotalMinutes'] = dataframe['TotalSeconds']/60
    dataframe['TotalHours'] = dataframe['TotalSeconds']/3600
    return dataframe

##################################################################################################################################################################################################
###########################################################               Function 2                 #############################################################################################
##################################################################################################################################################################################################

def set_time_for_SPC_to_datetime(dataframe):
    #------------------------------------------------------------------------------------
    # Function: set_time_for_SPC_to_datetime
    # Purpose:  Transforms the time column into a pandas datetime object
    #           From this it derives and puts into separate columns the following:
    #             Date
    #             Time
    #             Hour
    #             Minute
    #             Seconds
    #           and calculates and puts into separate columns the following:
    #             Total seconds since the beginning of the experiment
    #             Total minutes since the beginning of the experiment
    #             Total Hours since the beginning of the experiment
    # Input:    dataframe     ... a pandas dataframe
    # Output:   dataframe     ... the samme dataframe that was provided as input but with the time column transformed and appended with the calculations 
    # 
    # Internal functions:
    #           |_____________  SMPA_tools_v02.py/time_calculations        
    # External packages:
    #           |_____________  pandas
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    if dataframe.dtypes.iloc[0] != 'object':                                                # Phoenix - Format 2. When the 'Time' column is recorded in seconds, as in 0,1,2...
        dataframe['DateTime'] = pd.to_datetime(dataframe['DateTime'], unit='s')
        #print('The DateTime shown in the respective column is not the actual of the experiment. The time increment is indeed 1s')
        # Create different columns for Date, Time, Hours, Minutes, Seconds, TotalSeconds and TotalHours since the start of each experiment
        time_calculations(dataframe)
    else:                                                                                   # Phoenix - Format 1 or FAST.
        dataframe['DateTime'] = pd.to_datetime(dataframe['DateTime'], format = '%d-0%m-%y %H:%M:%S.%f')            
        # Create different columns for Date, Time, Hours, Minutes, Seconds, TotalSeconds and TotalHours since the start of each experiment
        time_calculations(dataframe)
    return dataframe

##################################################################################################################################################################################################
###########################################################               Function 3                 #############################################################################################
##################################################################################################################################################################################################

def read_all(*args):
    #------------------------------------------------------------------------------------
    # Function: read_all
    # Purpose:  Reads all the data formats of Small punch creep and Uniaxial creep files, including Old_DAQ_Software format BUT NOT .tdms files        
    #           Performs some initial cleaning/preprocessing of the data (e.g. removal of whitespaces), transformation of datatypes (e.g. time to pandas datetime), renaming of columns, calculation of extra columns related to time
    # Input:    *args       ... a number of paths that is not predefined. The paths are full paths including each file's extension
    # Output:   df          ... a pandas dataframe (data tabular form)          
    # Internal functions:
    #           |_____________  SMPA_tools_v02.py/time_calculations
    #           |_____________  SMPA_tools_v02.py/set_time_for_SPC_to_datetime
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    count_uniaxial = 0
    count_old_DAQ = 0
    
    files = []
    count_arg = 0
    for arg in args:
        count_arg += 1
        if ('.csv' not in arg) & ('.txt' not in arg):
            print('The path number', count_arg, ' that you have provided is not a full path. Please provide the full path(s) of the experiment(s) you want to analyse')
            return
        
        files.append(arg)
        
        if 'Log_Data' in arg:
            count_uniaxial += 1
        if 'Old_DAQ_Software' in arg:
            count_old_DAQ += 1
    
    if len(files) == 0:
        print('You have not selected any files')
            
    if ((count_uniaxial != 0) & (count_uniaxial != len(files))) | ((count_old_DAQ != 0) & (count_old_DAQ != len(files))):
        print('You have provided paths that correspond to different experiments or experiment formats. Please check again your inputs to the function.')
        return
    
    # Uniaxial Creep
    if (count_uniaxial != 0) & (count_uniaxial == len(files)):
        df = pd.read_csv(files[0], skiprows=[0,2,3], na_values="NAN")
        df.rename(columns=lambda x: x.strip(), inplace=True)                                                       
        if "OrbitDP10(1)" not in df.columns:
            df.rename(columns={'TIMESTAMP': 'DateTime', 'LVDT(1)': 'lvdt1', 'LVDT(2)': 'lvdt2'}, inplace=True)
        else:
            df.rename(columns={'TIMESTAMP': 'DateTime', 'OrbitDP10(1)': 'lvdt1', 'OrbitDP10(2)': 'lvdt2'}, inplace=True)
        df['DateTime'] = pd.to_datetime(df['DateTime'], format = '%Y-%m-%d %H:%M:%S')
        time_calculations(df)
        if len(files) > 1:
            for i in range(1, len(files)):
                df_additional = pd.read_csv(files[i], skiprows=[0,2,3], na_values="NAN")
                df_additional.rename(columns=lambda x: x.strip(), inplace=True)                                   
                if "OrbitDP10(1)" not in df_additional.columns:
                    df_additional.rename(columns={'TIMESTAMP': 'DateTime', 'LVDT(1)': 'lvdt1', 'LVDT(2)': 'lvdt2'}, inplace=True)
                else:
                    df_additional.rename(columns={'TIMESTAMP': 'DateTime', 'OrbitDP10(1)': 'lvdt1', 'OrbitDP10(2)': 'lvdt2'}, inplace=True)
                df_additional['DateTime'] = pd.to_datetime(df['DateTime'], format = '%Y-%m-%d %H:%M:%S')
                time_calculations(df_additional)                                                                   
                df = pd.concat([df, df_additional])
        df.reset_index(inplace=True)
        df.drop(columns=['index'], inplace=True)
    
    # SPC - Format: "Old DAQ Software" with file extention ".txt"
    if (count_old_DAQ != 0) & (count_old_DAQ == len(files)):
        with open(files[0]) as f:
            lines=f.readlines()
        counter = 0
        for line in lines:
            counter += 1
            if (''.join(line).startswith('index')):
                header_rows = counter
                break
        df = pd.read_csv(files[0], encoding='ansi', sep='\t', skiprows=header_rows, names=['index', 'DateTime', 'Temperature', 'Force', 'u', 'lvdt_AUX', 'flag', 'trigger'])
        df = df.iloc[:len(df)-1 , 1:]
        df['DateTime'] = pd.to_datetime(df['DateTime'], unit='s')
        time_calculations(df)
        if len(files) > 1:
            for i in range(1, len(files)):
                with open(files[i]):
                    lines=i.readlines()
                counter = 0
                for line in lines:
                    counter += 1
                    if (''.join(line).startswith('index')):
                        header_rows = counter
                        break
                df_additional = pd.read_csv(files[i], encoding='ansi', sep='\t', skiprows=header_rows, names=['index', 'DateTime', 'Temperature', 'Force', 'u', 'lvdt_AUX', 'flag', 'trigger'])
                df_additional = df.iloc[:len(df)-1 , 1:]
                df_additional['DateTime'] = pd.to_datetime(df_additional['DateTime'], unit='s')
                time_calculations(df_additional)
                
                df = pd.concat([df, df_additional])
        df.reset_index(inplace=True)
        df.drop(columns=['index'], inplace=True)                
                
    # SPC - Format: with extention ".csv" where the time is either in datetime or in seconds
    if (count_uniaxial == 0) & (count_old_DAQ == 0):
        df = pd.read_csv(files[0])
        df.rename(columns=lambda x: x.strip(), inplace=True)                                                      # It strips whitespaces from the columns' names
        df.rename(columns={'Time': 'DateTime', 'LVDT_main': 'u'}, inplace=True)
        set_time_for_SPC_to_datetime(df)                                                                      # It sets the DateTime to pandas datetime64 format
        if len(files) > 1:
            for i in range(1, len(files)):
                df_additional = pd.read_csv(files[i])
                df_additional.rename(columns=lambda x: x.strip(), inplace=True)                                   # It strips whitespaces from the columns' names
                df_additional.rename(columns={'Time': 'DateTime', 'LVDT_main': 'u'}, inplace=True)
                set_time_for_SPC_to_datetime(df_additional)                                                   # It sets the DateTime to pandas datetime64 format
                df = pd.concat([df, df_additional])
        df.reset_index(inplace=True)
        df.drop(columns=['index'], inplace=True)          
    
    return df

##################################################################################################################################################################################################
###########################################################               Function 4                 #############################################################################################
##################################################################################################################################################################################################

def df_uc_for_app(dataframe, time_col, lvdt1_col, lvdt2_col):
    #------------------------------------------------------------------------------------
    # Function: df_uc_for_app
    # Use:      Web application solely
    # Purpose:  Renames columns
    #           Transforms time data to pandas datetime format
    #           Performs calculations related to the time column. It calculates and creates the following extra columns:
    #             Date
    #             Time
    #             Hour
    #             Minute
    #             Seconds
    #             Total seconds since the beginning of the experiment
    #             Total minutes since the beginning of the experiment
    #             Total Hours since the beginning of the experiment
    # Input:    dataframe       ... a pandas dataframe that contains the log data
    #           time_col        ... exact name of the time column of the log data file
    #           lvdt1_col       ... exact name of the LVDT1 column of the log data file
    #           lvdt2_col       ... exact name of the LVDT2 column of the log data file
    # Output:   dataframe       ... a pandas dataframe           
    # Internal functions:
    #           |_____________  SMPA_tools_v02.py/time_calculations
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 

    # --- Start function ---
    dataframe.rename(columns={time_col: 'DateTime', lvdt1_col: 'lvdt1', lvdt2_col: 'lvdt2'}, inplace=True)
    dataframe['DateTime'] = pd.to_datetime(dataframe['DateTime'])#, format='mixed')
    time_calculations(dataframe)
    return dataframe

##################################################################################################################################################################################################
###########################################################               Function 5                 #############################################################################################
##################################################################################################################################################################################################

def df_spc_for_app(dataframe, time_col, u_col, force_col, temp_col):
    #------------------------------------------------------------------------------------
    # Function: df_spc_for_app
    # Use:      Web application solely
    # Purpose:  Renames columns
    #           Transforms time data to pandas datetime format
    #           Performs calculations related to the time column. It calculates and creates the following extra columns:
    #             Date
    #             Time
    #             Hour
    #             Minute
    #             Seconds
    #             Total seconds since the beginning of the experiment
    #             Total minutes since the beginning of the experiment
    #             Total Hours since the beginning of the experiment
    # Input:    dataframe       ... a pandas dataframe that contains the log data
    #           time_col        ... exact name of the time column of the log data file
    #           u_col           ... exact name of the deflection (u) column of the log data file
    #           force_col       ... exact name of the LVDT2 column of the log data file
    #           temp_col        ... exact name of the LVDT2 column of the log data file
    # Output:   dataframe       ... a pandas dataframe           
    # Internal functions:
    #           |_____________  SMPA_tools_v02.py/time_calculations
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 

    # --- Start function ---   
    dataframe.rename(columns={time_col: 'DateTime', u_col: 'u', force_col: 'Force', temp_col: 'Temperature'}, inplace=True)
    dataframe['DateTime'] = pd.to_datetime(dataframe['DateTime'], errors = 'coerce')#, format='%d-0%m-%y %H:%M:%S.%f')
    time_calculations(dataframe)
    return dataframe

##################################################################################################################################################################################################
###########################################################               Function 6                 #############################################################################################
##################################################################################################################################################################################################

def calculate_strain(dataframe, gauge_length):
    #------------------------------------------------------------------------------------
    # Function: calculate_strain
    # Purpose:  Calculates strain1, strain2, and average strain based on the values of LVDT1, LVDT2, and the average of the two LVDTs, respectively
    # Input:    datarame           ... a pandas dataframe
    #           gauge_length       ... an integer or a string indicating a number
    # Output:   datarame           ... a pandas dataframe appended with the calculated columns
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    dataframe.loc[0, 'disp1'] = 0
    dataframe.loc[0, 'disp2'] = 0
    dataframe.loc[0, 'strain1'] = 0
    dataframe.loc[0, 'strain2'] = 0
    dataframe.loc[0, 'strain_avg'] = 0

    # # Alternative 1 - much slower
    # for row in range(1, len(dataframe)):
    #     dataframe.loc[row, 'disp1'] = dataframe.loc[0, 'lvdt1'] - dataframe.loc[row, 'lvdt1']
    #     dataframe.loc[row, 'disp2'] = dataframe.loc[0, 'lvdt2'] - dataframe.loc[row, 'lvdt2']

    #     dataframe.loc[row, 'strain1'] = (dataframe.loc[row, 'disp1']/gauge_length)*100                    
    #     dataframe.loc[row, 'strain2'] = (dataframe.loc[row, 'disp2']/gauge_length)*100

    # Alternative 2 - fast!!
    dataframe.loc[1:, 'disp1'] = dataframe.loc[0, 'lvdt1'] - dataframe.loc[1:, 'lvdt1'].astype('float')
    dataframe.loc[1:, 'disp2'] = dataframe.loc[0, 'lvdt2'] - dataframe.loc[1:, 'lvdt2']  

    dataframe.loc[1:, 'strain1'] = (dataframe.loc[1:, 'disp1']/int(gauge_length))*100            # in %                
    dataframe.loc[1:, 'strain2'] = (dataframe.loc[1:, 'disp2']/int(gauge_length))*100            # in %
    
    dataframe.loc[1:, 'strain_avg'] = (dataframe.loc[1:, 'strain1']+dataframe.loc[1:, 'strain2'])/2

    return dataframe 

##################################################################################################################################################################################################
###########################################################               Function 7                 #############################################################################################
##################################################################################################################################################################################################

def calculate_rate_of_variable(dataframe, variable, interval, t0, tR):
    #------------------------------------------------------------------------------------
    # Function: calculate_rate_of_variable
    # Purpose:  Calculates the rate/first derivative of a curve by splitting the dataset into a certain number of sections
    #           and in each section calculating the slope
    # Input:    dataframe        ... a pandas dataframe
    #           variable         ... a string indicating deflection or strain, that can take the following values:
    #                                   'u'
    #                                   'strain1'
    #                                   'strain2'
    #                                   'strain_avg'
    #           interval         ... a number indicating the amount of points that fall into each section
    #           t0               ... time in seconds when the experiment started
    #           tR               ... time to rupture in seconds
    # Output:   rate_points      ... a vector of all the calculated rates
    #           t_points         ... a vector of time records that correspond to the middle of each section (calculated so that we can realistically plot rates over time)
    #                                The times correspond to the middle of each section
    #           var_points       ... a vector of deflections/strains that correspong to the middle of each section (calculated to match deflections/strains to their rates in the same point in time)
    #           
    # External packages:
    #           |_____________  pandas
    #           |_____________  numpy
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    rate_points = []
    t_points = []
    var_points = []

    i = t0
    low = t0
    while i < tR - interval:
        for j in dataframe.TotalSeconds[dataframe.TotalSeconds >= i]:   
            if j >= i+(interval/2):
                middle = j
            if j >= i+interval:
                high = j  
                x = dataframe.TotalHours[(dataframe.TotalSeconds >= low) & (dataframe.TotalSeconds <= high)].values   # choose hours or seconds!!!      
                y = dataframe[variable][(dataframe.TotalSeconds >= low) & (dataframe.TotalSeconds <= high)].values                                         
                low = high 
                break

        model = np.polyfit(x, y, 1)          
        rate_points.append(model[0])
        t_points.append(dataframe.TotalHours[dataframe.TotalSeconds == middle].values[0])      # choose hours or seconds!!!
        var_points.append(dataframe[variable][dataframe.TotalSeconds == middle].values[0])
        i+=interval
        
    return rate_points, t_points, var_points
   
##################################################################################################################################################################################################
###########################################################               Function 8                 #############################################################################################
##################################################################################################################################################################################################

def smoothen_curve(rate_points, t_points, var_points, window_size):
    #------------------------------------------------------------------------------------
    # Function: smoothen_curve
    # Purpose:  Calculates a moving average
    # Input:    rate_points         ... a vector of either deflection rate or strain rate values
    #           t_points            ... a vector of time
    #           var_points          ... a vector of deflection or strain values 
    #           window_size         ... a number indicating the size of the window over which to calculate the moving average
    # Output:   moving_averages     ... a vector of the calculated moving average
    #           tt                  ... a vector of time records that correspond to the middle of each window (calculated so that we can realistically plot rates over time)
    #                                   The times correspond to the middle of each section
    #           rate                ... a vector of deflections/strains that correspong to the middle of each window (calculated to match deflections/strains to their rates in the same point in time)
    #           
    # External packages:
    #           |_____________  pandas
    #           |_____________  numpy
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    arr = rate_points
    i = 0
    # Initialize an empty list to store moving averages
    moving_averages = []
    # Initialize an empty list to store the "timestamps" to which we will assign each moving average
    tt = []
    rate = []

    # Loop through the array to consider every window of size 25
    while i < len(arr) - window_size + 1:

        # Calculate the average of current window
        window_average = round(np.sum(arr[i:i+window_size]) / window_size, 2)

        # Store the average of current window in moving average list
        moving_averages.append(window_average)
        # Store the middle point of time in the window in the tt list
        tt.append(t_points[int(i+(window_size/2))])
        rate.append(var_points[int(i+(window_size/2))])

        # Shift window to right by one position
        i += 1

    return moving_averages, tt, rate

##################################################################################################################################################################################################
###########################################################               Function 9                 #############################################################################################
##################################################################################################################################################################################################

def part_of_curve(moving_averages, tt):
    #------------------------------------------------------------------------------------
    # Function: part_of_curve
    # Purpose:  Isolates part of a curve by removing data either from the beginning or the end
    # Input:    moving_averages      ... a vector of either deflection or strain
    #           tt                   ... a vector of time
    # Output:   middle_part          ... a vector containing values only from the specified part of the curve
    #           tt_middle            ... a vector of time containing values only from the specified part of the curve
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    lower_limit = int(input("Define the lower limit based on the deflection rate plot and press enter: "))
    upper_limit = int(input("Define the upper limit based on the deflection rate plot and press enter: "))
    tt_middle = []
    middle_part = []
    for i in range(len(tt)):
        if (tt[i]>=lower_limit) & (tt[i]<=upper_limit):
            tt_middle.append(tt[i])
            middle_part.append(moving_averages[i])

    return middle_part, tt_middle

##################################################################################################################################################################################################
###########################################################               Function 10                 #############################################################################################
##################################################################################################################################################################################################

def calc_polynomial(middle_part, tt_middle):
    #------------------------------------------------------------------------------------
    # Function: calc_polynomial
    # Purpose:  Calculates a polynomial of second degree
    # Input:    middle_part      ... a vector of either deflection or strain rates
    #           tt_middle        ... a vector of time
    # Output:   poly             ... the exuation of the calculates polynomial
    #
    # External packages:
    #           |_____________  numpy
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------   
  
    # --- Start function ---
    curve = np.polyfit(tt_middle, middle_part, 2, full=True)
    poly = np.poly1d(curve[0])

    return poly

##################################################################################################################################################################################################
###########################################################               Function 11                 #############################################################################################
##################################################################################################################################################################################################

def fit_curve_and_local_minimum(poly, middle_part, tt_middle):
    #------------------------------------------------------------------------------------
    # Function: fit_curve_and_local_minimum
    # Purpose:  Calculates the minimum of a fitted polynomial and plots it, together with the original and the fitted curve
    # Input:    poly             ... the equation of a fitted polynomial to either the deflection or the strain rate curve
    #           middle_part      ... a vector of either deflection or strain rates
    #           tt_middle        ... a vector of time
    # Output:   plot             ... a plot showcasing the actual curve, the fitted curve, and the calculated minimum of the fit
    #
    # External packages:
    #           |_____________  matplotlib
    #           |_____________  numpy
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------
    
    # --- Start function ---
    # Calculations
    crit = poly.deriv().r
    r_crit = crit[crit.imag==0].real
    test = poly.deriv(2)(r_crit)

    # Plot
    # PLot the actual data points
    plt.plot(tt_middle, middle_part, 'o--', label='u\'(t)')
    plt.title("Creep deflection rate and local minima", color='grey')
    plt.xlabel('Time [h]', color='grey')
    plt.ylabel('Deflection rate $\dot{u}$ [μm/h]', color='grey')
    plt.tick_params(colors='grey', which='both')

    # Compute local minima excluding range boundaries
    x_min = r_crit[test>0]
    y_min = poly(x_min)
    # Plot the minimum point
    plt.plot(x_min, y_min, '*', color='purple', label='local minimum', markersize=12)

    # Compute a curve based on the fitted poly
    xc = np.arange(int(tt_middle[0]), int(tt_middle[len(tt_middle)-1]), 0.02)
    yc = poly(xc)
    # Plot the curve
    plt.plot(xc, yc, color='red', label='fitted curve')
    plt.legend()
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 12                #############################################################################################
##################################################################################################################################################################################################

def plot_creep_deflecion_curve(dataframe):
    #------------------------------------------------------------------------------------
    # Function: plot_creep_deflecion_curve
    # Purpose:  Plot a creep deflection curve
    # Input:    dataframe        ... a pandas dataframe
    # Output:   plot             ... a plot of a creep deflection curve
    #
    # External packages:
    #           |_____________  matplotlib
    #           |_____________  pandas
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------
    
    # --- Start function ---
    plt.plot(dataframe.TotalHours, dataframe.u, 'o--')
    plt.title('Creep deflection curve', color='grey', pad=15)
    plt.xlabel('Time [h]', color='grey')
    plt.ylabel('Deflection $u$ [µm]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 13                #############################################################################################
##################################################################################################################################################################################################
    
def plot_Force_deflecion_curve(dataframe):
    #------------------------------------------------------------------------------------
    # Function: plot_Force_deflecion_curve
    # Purpose:  Plot a Force-deflection curve
    # Input:    dataframe        ... a pandas dataframe
    # Output:   plot             ... a plot of Force-deflection 
    #
    # External packages:
    #           |_____________  matplotlib
    #           |_____________  pandas
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------

    # --- Start function ---
    plt.figure(figsize=(8, 8))
    plt.plot(dataframe.u, dataframe.Force, 'o--')
    plt.title('Force-deflection curve', color='grey', pad=15)
    plt.xlabel('Deflection $u$ [µm]', color='grey')
    plt.ylabel('Force [N]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.xticks(rotation=45)
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 14                #############################################################################################
##################################################################################################################################################################################################

def plot_u_rate_over_time(dudt, t_points):
    #------------------------------------------------------------------------------------
    # Function: plot_u_rate_over_time
    # Purpose:  Plot deflection rate vs. time
    # Input:    dudt        ... a vector of deflection rate
    #           t_points    ... a vector of time
    # Output:   plot        ... a plot of deflection rate vs. time
    #
    # External packages:
    #           |_____________  matplotlib
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------
    
    # --- Start function ---
    #plt.figure(figsize=(7, 7.7))
    plt.plot(t_points, dudt, '--o')
    plt.title("Deflection rate vs. time", color='grey', pad=15)
    plt.xlabel('Time [h]', color='grey')     # choose hours or seconds!!!
    plt.ylabel('Deflection rate $\dot{u}$ [μm/h]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.ticklabel_format(style='plain')
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 15                #############################################################################################
##################################################################################################################################################################################################

def plot_u_rate_over_u(dudt, u_points):
    #------------------------------------------------------------------------------------
    # Function: plot_u_rate_over_u
    # Purpose:  Plot deflection rate vs. deflection 
    # Input:    dudt         ... a vector of deflection rate
    #           u_points     ... a vector of deflection 
    # Output:   plot         ... a plot of deflection rate vs. deflection
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    #plt.figure(figsize=(7, 7.7))
    plt.plot(u_points, dudt, '--o')
    plt.title("Deflection rate vs. deflection", color='grey', pad=15)
    plt.xlabel('Deflection $u$ [μm]', color='grey')     # choose hours or seconds!!!
    plt.ylabel('Deflection rate $\dot{u}$ [μm/h]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.ticklabel_format(style='plain')
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 16                #############################################################################################
##################################################################################################################################################################################################

def plot_smooth_u_rate_over_time(moving_averages, tt):
    #------------------------------------------------------------------------------------
    # Function: plot_smooth_u_rate_over_time
    # Purpose:  Plot deflection rate vs. time
    #           The only difference with Function 14 is the styling of the graph
    # Input:    moving_averages     ... a vector of deflection rate
    #           tt                  ... a time
    # Output:   plot                ... a plot deflection rate vs. time
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    #plt.plot(tt, moving_averages, 'o--')
    plt.scatter(tt, moving_averages, facecolors='none', edgecolors='b', linestyle='--')
    plt.title("Smoothened deflection rate", color='grey', pad=15)
    plt.xlabel('Time [h]', color='grey')                          # choose hours or seconds!!!
    plt.ylabel('Deflection rate $\dot{u}$ [μm/h]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.title('Smoothing with moving average')
    plt.yscale('log')
    plt.show()
    
##################################################################################################################################################################################################
###########################################################               Function 17                #############################################################################################
##################################################################################################################################################################################################

def plot_smooth_u_rate_over_u(moving_averages, uu):
    #------------------------------------------------------------------------------------
    # Function: plot_smooth_u_rate_over_u
    # Purpose:  Plot deflection rate vs. deflection 
    # Input:    moving_averages     ... a vector of deflection rate
    #           uu                  ... a vector of deflection 
    # Output:   plot                ... a plot of deflection rate vs deflection 
    #
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    #plt.plot(tt, moving_averages, 'o--')
    plt.scatter(uu, moving_averages, facecolors='none', edgecolors='b', linestyle='--')
    plt.title("Smoothened deflection rate", color='grey', pad=15)
    plt.xlabel('Deflection [μm]', color='grey')                          # choose hours or seconds!!!
    plt.ylabel('Deflection rate $\dot{u}$ [μm/h]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.title('Smoothing with moving average')
    plt.yscale('log')
    plt.show()

##################################################################################################################################################################################################
###########################################################               Function 18                #############################################################################################
##################################################################################################################################################################################################

def calculate_t0_index(dataframe, first_magn_check, second_magn_check):
    #------------------------------------------------------------------------------------
    # Function: calculate_t0_index
    # Purpose:  Calculates the index at the start of the experiment (when the full load starts being applied)
    #           First, the difference of the deflection column of the input dataframe is calculated
    #           Then, starting from the first data point the algorithm checks the differences.
    #           Once it finds one bigger than the first_magn_check, it checks the rest of the values (until the half point of the dataframe for more efficiency) to see if there is a difference bigger than the second_magn_check
    #           If there is, then the stop_end takes the index value of the last difference bigger than second_magn_check, otherwise of the first difference bigger than first_magn_check
    #
    # Input:    dataframe              ... a pandas dataframe
    #           first_magn_check       ... a number indiacting a magnitude of difference that is the first check 
    #           second_magn_check      ... a number indiacting a magnitude of difference that is the second check (after a difference bigger than the first_magn_check has been identified)
    # Output:   stop_start             ... the index of the input dataframe at the moment when the full load started being applied
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    dataframe['du'] = dataframe.u.diff().abs()
    
    for i in range(int(len(dataframe)/2)):
        if dataframe.loc[i, 'du'] > first_magn_check:
            key = i
            break

    stop_ini = key - 1

    return stop_ini

##################################################################################################################################################################################################
###########################################################               Function 19                #############################################################################################
##################################################################################################################################################################################################

def calculate_tR_index(dataframe, first_magn_check, second_magn_check, variable):
    #------------------------------------------------------------------------------------
    # Function: calculate_tR_index
    # Purpose:  Calculates the index at time to rupture
    #           First, the difference of the specified variable of the input dataframe is calculated
    #           Then, starting from the last data point the algorithm checks the differences.
    #           Once it finds one bigger than the first_magn_check, it checks the rest of the values (until the half point of the dataframe for more efficiency) to see if there is a difference bigger than the second_magn_check
    #           If there is, then the stop_end takes the index value of the latter, otherwise of the former
    #
    # Input:    dataframe              ... a pandas dataframe
    #           first_magn_check       ... a number indiacting a magnitude of difference that is the first check 
    #           second_magn_check      ... a number indiacting a magnitude of difference that is the second check (after a difference bigger than the first_magn_check has been identified)
    #           variable               ... a specific variable/column of the input dataframe (either deflection 'u' or 'strain1', 'strain2', 'strain_avg')
    # Output:   stop_end               ... the index of the input dataframe at the moment of rupture 
    # External packages:
    #           |_____________  pandas
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    dataframe['dvar'] = dataframe[variable].diff().abs()
    
    for i in range(int(len(dataframe))-1, int(len(dataframe)/2), -1):
        if dataframe.loc[i, 'dvar'] > first_magn_check:
            key = i
            for j in range(i-1, int(len(dataframe)/5), -1):
                if dataframe.loc[j, 'dvar'] > second_magn_check:
                    key = j
            break
    
    stop_end = key-1
    return stop_end

##################################################################################################################################################################################################
###########################################################               Function 20                #############################################################################################
##################################################################################################################################################################################################

def plot_u0_and_uR(dataframe, i0, iR):
    #------------------------------------------------------------------------------------
    # Function: plot_u0_and_uR
    # Purpose:  Plots a creep deflection curve but without the invalid points at the beginning (before the full load was applied) and at the end (after rupture)
    # Input:    dataframe        ... a pandas dataframe
    #           i0               ... an index number (related to the dataframe index) indiacting the moment that the load started to be loaded
    #           iR               ... an index number (related to the dataframe index) indicating the moment of rupture
    # Output:   plot             ... a plot of creep-deflection curve
    # External packages:
    #           |_____________  pandas
    #           |_____________  matplotlib
    # Author:   Georgia Manou, georgia.manou@outlook.com
    # Version:  1.0, 15th March 2024
    #------------------------------------------------------------------------------------ 
    
    # --- Start function ---
    plt.plot(dataframe.TotalHours, dataframe.u, 'o--')
    plt.plot(dataframe.TotalHours[i0], dataframe.u[i0], '*', color='purple', label='local minimum', markersize=12)
    plt.plot(dataframe.TotalHours[iR], dataframe.u[iR], '*', color='purple', label='local minimum', markersize=12)
    plt.title('Creep deflection curve with u0 and uR', color='grey', pad=15)
    plt.xlabel('Time [h]', color='grey')
    plt.ylabel('Deflection $u$ [µm]', color='grey')
    plt.tick_params(colors='grey', which='both')
    plt.show()