#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 10 12:14:11 2018

@author: met
"""
import pandas as pd 
import numpy as np
from os import listdir
from os.path import exists, isfile, join
import os
os.chdir('/home/met/Documents/Scripts')
import Master

# 'Site_variables.xlsx' file path
variables_file = '/home/met/Documents/XLSX/Site_variables.xlsx' 
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# define the path where the sites folders are stored
path = '/home/met/data/'
# define the path where the month data folders are going to be stored
path1 = '/home/met/data/'
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*         
# list with the name of the sites
sites = ['agsc','altz','cham','erno','jqro','ltux','mazt','meda','mine','more','sllo','ptom','sisl','tmix','unam']
M = []
# loop for each site
for site in sites:
    # the route of each site folder
    folder_path = os.path.join(path,site,'raw')
    # onlyfiles is a list of the files of each site folder
    onlyfiles = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    # the loop for reading each 'minuto' files:
    DF = []
    for s in onlyfiles:
        if any(i.lower() in s.lower() for i in ['minuto']):
            route = join(folder_path,s)
            data = pd.read_csv(route,sep=',',encoding='latin1', skiprows = [0,2,3], nrows = 1)
            columns = data.columns
            # read the 'site_variables.xlsx' file
            site_variables = pd.read_excel(variables_file, header = [0,1])
            # extract the variable & unit names
            V, _ = zip(*site_variables.columns.tolist())
            missing = []
            for element in columns:
                if not element in V and not element in ['TIMESTAMP', 'RECORD']:
                    missing.append(element)
            if missing:
                df = pd.DataFrame(data = np.full((1,len(missing)), 'X'), index = [np.array([site]), np.array([s])],columns = missing)
                df.index.names =['Site','File']
                DF.append(df)
    if DF:
        DF = pd.concat(DF) 
        M.append(DF)
M = pd.concat(M)
save = '/home/met/Documents/Raw_Extra_Columns.csv'
M.to_csv(save, na_rep = ' ', index = True, encoding = 'latin1')                   
                
                
                
                
                