import pandas as pd 
import time
import os
os.chdir('/home/met/Documents/Scripts')
import Master
start = time.time()
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# define the path where the sites folders are stored
path = '/home/met/data/'
# define the path where the month data folders are going to be stored
path1 = '/home/met/data/'
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*         
# list with the name of the sites
sites = ['cham','erno','jqro','ltux','meda','mine','more','sllo','ptom','sisl','tmix','unam','mazt','altz','texo']
#sites = ['cham','erno','jqro','ltux','meda','mine','more','sllo','ptom','sisl','tmix','unam']
#sites = ['meda']
# loop for each site
for site in sites:
    print ('*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#')
    print (site)
    counter = 1; success = False
    while success == False:
        # create the folder where the month site data are going to be stored
        L0 = os.path.join(path1,site,'L0') 
        if not os.path.exists(L0):
            os.makedirs(L0)
            os.makedirs(L0 + '/stat')
        # the route of each site folder
        route0 = os.path.join(path,site,'raw')
        # merge the data
        appended_data = Master.merge_files(route0, skip_rows = [0,2,3], include = ['Minuto'])
        # name of the columns to be extracted
        cols, _ = Master.col_name(site, appended_data, Timestamp = True, Record = True)
        # re-arrange the columns order
        appended_data = appended_data[cols]    
        # convert the first data column into datetime64
        appended_data['TIMESTAMP'] = pd.to_datetime(appended_data['TIMESTAMP'], dayfirst=False)
        #appended_data['TIMESTAMP'] = pd.to_datetime(appended_data['TIMESTAMP'], dayfirst = False, errors = 'coerce')
        #idx = appended_data[appended_data['TIMESTAMP'].isnull()].index 
        appended_data, oldest, youngest = Master.fill_missing_measurements(appended_data)   
        # get the last data month uploaded 
        # 'site+_RECORD.dat' is file with the record of the upload dates
        Rrd = os.path.join('/home/met/data/',site,'L0',site+'_record.txt')
        # check the record    
        F, R1, FileDate = Master.record(site, Rrd, oldest, youngest)    
        # 'date2' is the string of the first  date to be taken         
        # 'date2' is the string of the last  date to be taken 
        date1 = str(FileDate.strftime('%Y')) + '-' + str(FileDate.strftime('%m'))
        date2 = youngest.strftime('%Y') + '-' + youngest.strftime('%m') + '-' + youngest.strftime('%d')
        # the new 'appended_data' is the range of days contained between data1 & data2
        appended_data = appended_data[date1:date2] 
        # split & save the data by month
        Master.save_month(L0, site, appended_data, extension = '.dat', Record = True)
        # write the record
        Master.write_record(site, youngest, Rrd, F, R1)
        success, counter = Master.master_of_none(site, counter)
end = time.time()
print ('*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#')
print ('___ Elipsed Time: ' + '%d' % (end - start) + ' s ___')
