import os
import numpy as np
import pandas as pd
import datetime as dt
from os import listdir
from os.path import isfile, join
os.chdir('/home/met/Documents/Scripts')
from Master import circ_mean_np 
###############################################################################   
def line_prepender(filename, line):
    with open(filename, 'r+',encoding = 'latin1') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n' + content)
##############################################################################
# time now
now = dt.datetime.now()
# list with the name of the sites
sites = ['altz','cham','erno','jqro','ltux','unam']
sites = ['jqro']
# where the rain.dat are stored
rain = '/home/met/Documents/Datos_1_min_RUOA_lluvia'
# onlyfiles is a list of the files of each site folder
onlyfiles = [f for f in listdir(rain) if isfile(join(rain, f))]
##############################################################################
# here we take just the 'site' files
for site in sites:
    M = os.path.join('/home/met/data/' ,site,'L1',site+'_Rain_correction.txt')
    if not os.path.exists(M):
        sub = site
    ##############################################################################
        # the loop for reading each 'site' files:
        for s in onlyfiles:
            if sub.lower() in s.lower():
                # generate the route
                route = os.path.join(rain,s)
                # read the data, file_name is the name of the file to be read
                data = pd.read_csv(route,sep=',',skiprows=[0],encoding='latin1',na_values=['null','NaN','nan',' '])
                # indicate the date format
                data['timestamp'] = pd.to_datetime(data['timestamp'], dayfirst = True, format = '%d/%m/%Y %H:%M:%S')
                # set the date as the index                
                data = data.set_index([('timestamp')]) 
                # group by month            
                grouped = data.groupby([lambda x: x.year, lambda x: x.month])  
    ##############################################################################            
                # replace the rain_corregido column
                for d, G in grouped:
                    # year & month of the bin
                    (Y,M) = d
                    # where the L1 are stored
                    # 2 cases
                    if M < 10:
                        L1 = '/home/met/data/'+site+'/L1/Minuto/'+str(Y)+'-0'+str(M)+'-'+site+'_minuto_L1.csv'
                    else:
                        L1 = '/home/met/data/'+site+'/L1/Minuto/'+str(Y)+'-'+str(M)+'-'+site+'_minuto_L1.csv'
                    print(L1)
                    # read the data, file_name is the name of the file to be read
                    data_L1 = pd.read_csv(L1,sep=',',skiprows=[0,1,2,3,4,5,7],encoding='latin1',na_values=['null']) 
                    # indicate the date format
                    data_L1['TIMESTAMP'] = pd.to_datetime(data_L1['TIMESTAMP'], dayfirst = True)
                    # set the date as the index                
                    data_L1 = data_L1.set_index([('TIMESTAMP')]) 
                    # concat the data2['Pres_Avg']
                    data_L1 = pd.concat([data_L1, G], axis=1)
                    # delete RECORD 
                    del data_L1['Rain_Tot']
                    # rename the corrected column
                    data_L1 = data_L1.rename(columns = {'Rain_corregido':'Rain_Tot'}) 
                    # define the columns order
                    cols=['Temp_Avg','RH_Avg','WSpeed_Avg','WSpeed_Max','WDir_Avg','WDir_SD','Rain_Tot','Press_Avg','Rad_Avg','Visibility']
                    # re-arrange the columns order
                    data_L1 = data_L1[cols]  
    ##############################################################################  
                    ### MEAN THE L1 DATA ###
                    # resample the data  
                    # (mean every 60 min)
                    min60 = data_L1.resample('60Min').agg({'Temp_Avg': np.mean, 'RH_Avg': np.mean, 
                            'WSpeed_Avg': np.mean, 'WSpeed_Max': np.max, 'WDir_Avg': circ_mean_np,
                            'WDir_SD':np.mean, 'Rain_Tot': np.nansum, 'Press_Avg': np.mean, 
                            'Rad_Avg': np.mean, 'Visibility': np.mean})
                    # define the columns order
                    del min60['WDir_SD']
                    cols=['Temp_Avg','RH_Avg','WSpeed_Avg','WSpeed_Max','WDir_Avg','Rain_Tot',
                          'Press_Avg','Rad_Avg','Visibility']
                    # re-arrange the columns order
                    min60 = min60[cols]
    ##############################################################################  
                    ### REMOVE AVERAGES THAT ARE NOT VALID ###
                    # count the number of observations per hour
                    C = data_L1.resample('H').count()
                    # remove not valid data
                    ################ Temperature
                    # 50% of data required
                    iT = C[C['Temp_Avg'] < 30].index
                    min60.set_value(iT,u'Temp_Avg', np.NaN )
                    ################ Relative Humidity
                    # 50% of data required
                    iRH = C[C['RH_Avg'] < 30].index
                    min60.set_value(iRH,'RH_Avg', np.NaN )
                    ################ Wind Speed
                    # 50% of data required
                    iWS = C[C['WSpeed_Avg'] < 30].index
                    min60.set_value(iWS,'WSpeed_Avg', np.NaN )
                    ################ WSpeed_Max
                    # 1.66% of data required
                    iWSM = C[C['WSpeed_Max'] < 0].index
                    min60.set_value(iWSM,'WSpeed_Max', np.NaN )
                    ################ Wind Direction
                    # 50% of data required        
                    iWD = C[C['WDir_Avg'] < 30].index
                    min60.set_value(iWD,'WDir_Avg', np.NaN )
                    ################ Total Rain
                    # 90% of data required
                    iTRain = C[C['Rain_Tot'] < 53].index
                    min60.set_value(iTRain,'Rain_Tot', np.NaN )
                    ################ Pressure
                    # 1.66% of data required
                    iPre = C[C['Press_Avg'] < 0].index
                    min60.set_value(iPre,'Press_Avg', np.NaN )
                    ################ Radiation
                    # 50% of data required
                    iRad = C[C['Rad_Avg'] < 30].index
                    min60.set_value(iRad,'Rad_Avg', np.NaN )
                    ################ Visibility 
                    # 50% of data required
                    iVis = C[C['Visibility'] < 30].index
                    min60.set_value(iVis,'Visibility', np.NaN )
    ##############################################################################
    ##############################################################################     
                    ### SAVE THE L1 DATA ###
                    # define the coordenates & ... of each site
                    if site ==   'AGSC':
                        name = 'Atmospheric Observatory Aguascalientes'; name2 = 'Aguascalientes'            
                        N = 21.9157; W = 102.3190; masl = 1868;  UT = 6
                    elif site == 'altz':
                        name = 'Atmospheric Observatory Altzomoni'; name2 = 'State of Mexico'            
                        N = 19.1187; W = 98.6552;  masl = 3985;  UT = 6
                    elif site == 'cham':
                        name = 'Atmospheric Observatory Chamela'; name2 = 'Jalisco'            
                        N = 19.4983; W = 105.0446; masl = 91;  UT = 6
                    elif site == 'erno':
                        name = 'Atmospheric Observatory Hermosillo'; name2 = 'Sonora'            
                        N = 29.0814; W = 110.9706; masl = 154;  UT = 7
                    elif site == 'jqro':
                        name = 'Atmospheric Observatory Juriquilla'; name2 = 'Queretaro'            
                        N = 20.7030; W = 100.4473; masl = 1945;  UT = 6
                    elif site == 'ltux':
                        name = 'Atmospheric Observatory Los Tuxtlas'; name2 = 'Veracruz'            
                        N = 18.5853; W = 95.0752; masl = 180;  UT = 6
                    elif site == 'MAZT':
                        name = 'Meteorological Station Mazatlan'; name2 = 'Sinaloa'            
                        N = 23.1836; W = 106.425;  masl = 20;  UT = 7
                    elif site == 'MEDA':
                        name = 'Atmospheric Observatory Merida'; name2 = 'Yucatan'            
                        N = 20.9838; W = 89.6452;  masl = 25;  UT = 6
                    elif site == 'MORE':
                        name = 'Atmospheric Observatory Morelia'; name2 = 'Michoacan'            
                        N = 19.6493; W = 101.2221; masl = 1786;  UT = 6
                    elif site == 'SLLO':
                        name = 'Atmospheric Observatory Saltillo'; name2 = 'Coahuila'            
                        N = 25.3532; W = 101.0332; masl = 1786;  UT = 6
                    elif site == 'TMIX':
                        name = 'Meteorological Station Temixco'; name2 = 'Morelos'
                        N = 18.8405; W = 99.2362;  masl = 1253;  UT = 6
                    elif site == 'unam':
                        name = 'Atmpspheric Observatory UNAM'; name2 = 'Mexico City'
                        N = 19.3262; W = 99.1761;  masl = 2280;  UT = 6
                    ### reset the index ###
                    # minute table    
                    data_L1  = data_L1.reset_index()
                    # hour table            
                    min60 = min60.reset_index()
                    # define the index column name
                    # minute table
                    header_min = [['TIMESTAMP','Temp_Avg','RH_Avg','WSpeed_Avg','WSpeed_Max','WDir_Avg','WDir_SD','Rain_Tot','Press_Avg','Rad_Avg','Visibility'],
                              ['yyyy-mm-dd HH:MM:SS',u'\xb0C','%','m/s','m/s','deg','deg','mm','hPa','W/m^2','m']]
                    # hour table
                    header_min60 = [['TIMESTAMP','Temp_Avg','RH_Avg','WSpeed_Avg','WSpeed_Max','WDir_Avg','Rain_Tot','Press_Avg','Rad_Avg','Visibility'],
                              ['yyyy-mm-dd HH:MM:SS',u'\xb0C','%','m/s','m/s','deg','mm','hPa','W/m^2','m']]
                    ### insert the header ###
                    # minute table    
                    data_L1.columns  = pd.MultiIndex.from_tuples(list(zip(*header_min)))
                    # hour table            
                    min60.columns = pd.MultiIndex.from_tuples(list(zip(*header_min60)))
                    ### indicate the file name ###
                    # minute table
                    pathM = L1
                    # hour table
                    pathH = '/home/met/data/'+site+'/L1/Hora/'+pathM[30:43]+'hora_L1.csv'
                    ### save the data ###
                    # minute table
                    data_L1.round(2).to_csv(pathM, na_rep='null', index=False, encoding = 'latin1')
                    # hour table  
                    min60.round(2).to_csv(pathH, na_rep='null', index=False, encoding = 'latin1')     
                    #######################################################################
                    # header
                    for path in [pathM,pathH]:
                        # Add some data
                        line_prepender(path, 'Red Universitaria de Observatorios Atmosfericos (RUOA)\n'+name+' ('+site+'), '+name2+'\nLat '+str(N)+' N, Lon '+str(W)+' W, Alt '+str(masl)+' masl\nTime UTC-'+str(UT)+'h\nMeteorological data\n ') 
                        # delete the 9th line        
                        #lines = []
                        #with open(path, 'r') as f:
                        #    lines = f.readlines()
                        #with open(path, 'w') as f:
                        #    f.writelines(lines[:8] + lines[9:]) 
        # Create the file that indicate that the correction has been made
        R = {'The multipliers corrections were made on:' : [now]}        
    # convert it to Dataframe
        R = pd.DataFrame(R)
        # save the record file
        R.to_csv(os.path.join('/home/met/data/' ,site,'L1',site+'_Rain_correction.txt'),index=False)                            
    else:
            print ('')
            print ('The rain correction has already been made for '+site)
            print ('')