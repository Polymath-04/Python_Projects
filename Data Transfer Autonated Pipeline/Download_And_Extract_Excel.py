# Description: This script will run all the scripts in the project
# input start and end dates here

import Variable_Config as v
from datetime import datetime, timedelta
import datetime as dt

segments=['HPDAM']# 'DAM','GDAM','HPDAM','RTM','TAM','GTAM',['TAM','GTAM']
    
# both inclusive
Start_Date = '01-01-2023'# DD_MM_YYYY
End_Date = '31-12-2024'# DD_MM_YYYY
filenames = [r'Task1_Internet\Task1_Internet\Download_Internet.py',r'Task1_Internet\Task1_Internet\Process_Downloaded_Data.py']#,'Generate_Excel_Report.py']
        
def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)

def monthlist(begin,end):
    begin = datetime.strptime(begin, v.INPUT_FILE_DATE_FORMAT)
    end = datetime.strptime(end, v.INPUT_FILE_DATE_FORMAT)

    result = []
    while True:
        if begin.month == 12:
            next_month = begin.replace(year=begin.year+1,month=1, day=1)
        else:
            next_month = begin.replace(month=begin.month+1, day=1)
        if next_month > end:
            break
        result.append ([begin.strftime(v.INPUT_FILE_DATE_FORMAT),last_day_of_month(begin).strftime(v.INPUT_FILE_DATE_FORMAT)])
        begin = next_month
    result.append ([begin.strftime(v.INPUT_FILE_DATE_FORMAT),end.strftime(v.INPUT_FILE_DATE_FORMAT)])
    return result


date_list = monthlist(Start_Date,End_Date)
# print(monthlist(Start_Date,End_Date))
#s,e=datetime.strptime(START_DATE, v.INPUT_FILE_DATE_FORMAT),datetime.strptime(END_DATE, v.INPUT_FILE_DATE_FORMAT)


for s,e in date_list:
    for seg in segments:
        v.SEGMENT,v.START_DATE,v.END_DATE,v.INPUT_FILE_TIME_BLOCK_FORMAT=v.calibrate(seg,s,e)
        if v.EVALUATION: print('Starting Process for {} {} - {}'.format(v.SEGMENT,s,e))
        for filename in filenames:
            with open(filename) as file:
                exec(file.read())
                if v.EVALUATION: print(filename+' Ran Successfully')
        if v.EVALUATION: print(v.SEGMENT+' Process Ran Successfully')
    if v.EVALUATION: print('{} to {} all data uploaded successfully'.format(s,e))
if v.EVALUATION: print("Everything Ran Successfully")