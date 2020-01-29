import pandas as pd
from dateutil.relativedelta import relativedelta
import time
import os
os.chdir('/home/met/Documents/Scripts')
import Master
start_time = time.time()
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*
# define the path where the site folders are stored
path = '/home/met/data/'
#-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*         
# list with the name of the sites
sites = ['altz','cham','erno','jqro','ltux','mazt','meda','mine','more','sllo','ptom','sisl','tmix','unam','texo']
#sites = ['cham','erno','jqro','ltux','mazt','meda','mine','more','sllo','ptom','sisl','texo','tmix','unam']
#sites = ['meda']
# loop for each site
for site in sites:
    print('*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#')
    print(site)
    # find where the L0 data is stored
    L0 = os.path.join(path,site,'L0') 
    # specifie where the L1 data is going to be stored
    # create the folder where the L1 data are going to be stored
    L1 = os.path.join(path,site,'L1') 
    if not os.path.exists(L1):
        os.makedirs(L1)
        os.makedirs(os.path.join(L1,'Minuto'))
        os.makedirs(os.path.join(L1,'Hora'))        
        os.makedirs(os.path.join(L1,'stat')) 
    # Rrd_L0 is the path of the file that indicates what was the last L0 date generated
    Rrd_L0 = os.path.join(L0,site+'_record.txt')
    # Rrd_L1 is the path of the file that indicates what was the last L1 date generated
    Rrd_L1 = os.path.join(L1,site+'_record_L1.txt')
    # obtain the youngest date of the site
    start_year, start_month = Master.youngest_date(site)
    start = pd.to_datetime(start_year+'-'+start_month)
    # obtain the last date 
    _, _, end = Master.record(site, Rrd_L0, None, None)
    # obtain the first date 
    F, R1, start = Master.record(site, Rrd_L1, start, end)
    # create an array with dates to work (start - end)
    dates_array = pd.date_range(start = start, end = end.date() + relativedelta(months = 1), freq = 'M', closed = 'left').strftime('%Y-%m')  
    # print(dates_array, start, end)
    # loop for each month in 'dates_array'
    for date in dates_array:
        print(date)
        # 'file_name' is the name of the file (L0 file) to be read           
        file_name = os.path.join(L0, date + '-' + site + '_L0.dat')
        print(file_name)
        # read the data
        df = pd.read_csv(file_name, sep=',',skiprows=[0,1,2,3,4,5,7],encoding='latin1',na_values=['null','NAN']) 
        # indicate the date format        
        df['TIMESTAMP'] = pd.to_datetime(df['TIMESTAMP'], dayfirst = False)
        # set the date as the index                
        df = df.set_index([('TIMESTAMP')]) 
        # delete RECORD 
        del df['RECORD']
        # correction for the column's name if needed (rain & visibility)
        df, Visibility_name = Master.columns_correction(df)      
        # count the number of observations per day
        CC_min_i = df.resample('D').count() 
        # apply the L1 filters
        df = Master.L1_filter(site, df, extra_filters = True)
        # recount the number of observations per day
        CC_min_f = df.resample('D').count() 
        # obtain the number of observations filtered
        CC_min = CC_min_i - CC_min_f
        # define where the filtered data report is going to be stored        
        CC_min_route = os.path.join(L1, 'stat', date + '-' + site + '_STAT_L1.csv');  
        # save the filtered data report   
        CC_min.to_csv(CC_min_route, na_rep='NaN', line_terminator = '\r\n')
        # add the header to the filtered data report  
        Master.add_header(site, CC_min_route, area = 'Filtered Data')
        # calculation of the hourly averages
        min60 = Master.df_mean(df, site)
        # save the L1 data (minute & hour files)
        Master.save_month(os.path.join(L1, 'Minuto'), site, df, version = 'minuto_L1', MDR = False)
        Master.save_month(os.path.join(L1, 'Hora'), site, min60, version = 'hora_L1', MDR = False)
    Master.master_of_none(site, _, version = 'L1')
    # write the record
    Master.write_record(site, end, Rrd_L1, F, R1)
Master.rainfall_check()
end = time.time()
print('*#*#*#*#*#*#*#*#*#*#*#*#*#*#*#')
print('___ Elipsed Time: ' + '%d' % (end - start_time) + ' s ___')
