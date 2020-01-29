#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May  8 12:10:05 2018

@author: met
"""
from os import listdir
from os.path import  isfile, join
import pandas as pd
import datetime as dt
import os
os.chdir('/home/met/Documents/Scripts')
import Master
  
print('Running Rainfall Correction...')
folder_path = '/home/met/Documents/Datos_1_min_RUOA_lluvia'
onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
for f in sorted(onlyfiles):
    print(f)
    site = f[:4].lower()
    route1 = join(folder_path, f)
    df = pd.read_csv(route1, skiprows=[0], na_values=['null','NAN',' '])    
    df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst = True, format = '%d/%m/%Y %H:%M:%S')
    df = df.set_index([('timestamp')]) 
    grouped = df.groupby([lambda x: x.year, lambda x: x.month])  
    for (Y, M), G in grouped:
        route2 = '/home/met/data/' + site + '/L1/Minuto/' + str(Y) + '-' + str(M).zfill(2) + '-' + site + '_minuto_L1.csv'
        data = pd.read_csv(route2, sep=',',skiprows=[0,1,2,3,4,5,7],encoding='latin1',na_values=['null','NAN']) 
        data['TIMESTAMP'] = pd.to_datetime(data['TIMESTAMP'], dayfirst = True)
        data = data.set_index([('TIMESTAMP')]) 
        col = data.columns.values
        data = pd.concat([data, G], axis=1)
        del data['Rain_Tot']
        data = data.rename(columns = {'Rain_corregido':'Rain_Tot'})
        data = data[col]
        min60 = Master.df_mean(data, site)        
        Master.save_month('/home/met/data/' + site + '/L1/Minuto/', site, data, version = 'minuto_L1', MDR = False)
        Master.save_month('/home/met/data/' + site + '/L1/Hora/', site, min60, version = 'hora_L1', MDR = False)
R = {'The rainfall corrections were made on:' : [dt.datetime.now()]}        
R = pd.DataFrame(R)
sites = ['altz','cham','erno','jqro','ltux','unam']
for site in sites:
    R.to_csv(join('/home/met/data/' ,site,'L1',site+'_rain_correction.txt'),index=False)    
    