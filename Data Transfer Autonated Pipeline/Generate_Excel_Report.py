import pandas as pd
from sqlalchemy import create_engine, text
import datetime
import SQLconnection
import Variable_Config as v
import Mapper
import numpy as np

m=Mapper.mapit()

MAX_SHEET_ROWS=1048576

OUTPUT_FILE_LOCATION=v.OUTPUT_FILE_LOCATION+'\\'+v.SEGMENT+'_Internet_Data_'+v.START_DATE+'_'+v.END_DATE+'.xlsx'
s,e=datetime.datetime.strptime(v.START_DATE,v.INPUT_FILE_DATE_FORMAT).strftime(v.SQL_DATE_FORMAT),datetime.datetime.strptime(v.END_DATE,v.INPUT_FILE_DATE_FORMAT).strftime(v.SQL_DATE_FORMAT)#'2024-12-01','2024-12-31'

def dateToExcelSerial(current):
    #print(current)
    return current.toordinal() - 693594

# create a connection to the database
engine=SQLconnection.create_connection()
cnxn=engine.connect()

result=cnxn.execute(text("select count(*) from "+m.TableName))
mc=0
for r in result:
    mc=r[0]
if not s or not e:
    print("{} entries present in "+m.TableName+" table. \nGenerate Complete Report or Date Range? (C/R): ".format(mc),end='')
    ans=input().strip()
else: ans='R'
if ans=='C' and mc<MAX_SHEET_ROWS: 
    script = "SELECT * FROM "+m.TableName+" order by Record_Date"

else: 
    if not s or not e:
        s=e=False
        while not s:
            print("Enter Start Date (format: dd-mm-yyyy): ",end='')
            try:
                s=datetime.datetime.strptime(input().strip(),v.INPUT_FILE_DATE_FORMAT).strftime(v.SQL_DATE_FORMAT)
            except Exception as e:
                s=False
                print("Invalid Date Entered. Please Check and Try Again")
                print(e)
        while not e:
            print("Enter End Date (format: dd-mm-yyyy): ",end='')
            try:
                e=datetime.datetime.strptime(input().strip(),v.INPUT_FILE_DATE_FORMAT).strftime(v.SQL_DATE_FORMAT)
            except Exception as e:
                e=False
                print("Invalid Date Entered. Please Check and Try Again")
    if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']: script="select * from "+m.TableName+" where segment=\'"+v.SEGMENT+"\' and Record_Date between \'"+s+"\' and \'"+e+"\' order by Record_Date,Time_Block"
    elif v.SEGMENT in ['TAM','GTAM']: script="SELECT * FROM "+m.TableName+" where Segment=\'"+v.SEGMENT+"\' and Record_Date between \'"+s+"\' and \'"+e+"\' order by Record_Date,Contract_Type,Instrument_Name"

# parse string to data type
parse={'FLOAT':float,'INT':int, 'VARCHAR (255)':str}
df = pd.read_sql_query(text(script), cnxn,dtype=dict([(m.ConvColumnNames[i],parse[m.ColumnDType[i]]) for i in range(len(m.ConvColumnNames)) if m.ColumnDType[i]!='DATE']))
df.columns=['Segment']+m.ColumnNames

from dateutil import parser
# function to get financial year
def finYear(date_str):
    date = parser.parse(str(date_str))
    if date.month < 4: return f"FY{date.year-1}-{date.strftime("%y")}"
    else: return f"FY{date.year}-{(date+pd.DateOffset(years=1)).strftime("%y")}"
def quarter(date_str):
    date=parser.parse(str(date_str))
    res='ERROR '
    if date.month<4: res='Q1 '
    elif date.month<7: res='Q2 '
    elif date.month<10: res='Q3 '
    else: res='Q4 '
    return res + str(date.year)
def tradingDate(date):
    if v.SEGMENT in ['DAM','GDAM','HPDAM']: return date-1#dateToExcelSerial(date-pd.DateOffset(days=1))
    if v.SEGMENT=='RTM': return date#dateToExcelSerial(date)
    print("tradingDate function in Extract.py is not complete, add trading date for TAM and GTAM")
    #if v.SEGMENT in ['TAM','GTAM']: return date-1#dateToExcelSerial(date-pd.DateOffset(days=1)) # don't know their trading dates this is just a placeholder
    exit("Unhandled Segment in tradingDate function")

extra_columnNames=[]
extra_widthOffset=[]
extra_formatList=[]

if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    # add extra formulas columns
    extra_columnNames=['Financial Year','Quarter','Trading Date']
    extra_widthOffset=[0,2,1]
    extra_formatList=['VARCHAR (255)','VARCHAR (255)','DATE']

if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']:
    for i in extra_columnNames:
        if i=='Financial Year': df[i]=df['Date'].apply(finYear)
        elif i=='Quarter': df[i]=df['Date'].apply(quarter)
        elif i=='Trading Date': 
            df['Date']=df['Date'].apply(dateToExcelSerial)
            df[i]=df['Date'].apply(tradingDate)
        else: exit("Unhandled extra column while extracting")
    if type(df['Date'][0])!=np.int64: df['Date']=df['Date'].apply(dateToExcelSerial)
elif v.SEGMENT in ['TAM','GTAM']:
    for i in extra_columnNames:
        if i=='Financial Year': df[i]=df['Trade Date'].apply(finYear)
        elif i=='Quarter': df[i]=df['Trade Date'].apply(quarter)
        else: exit("Unhandled extra column while extracting")

# rearrange columns if required
df=df.loc[:,['Segment']+extra_columnNames+m.ColumnNames]
if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM']: df.rename(columns={'Date': 'Delivery Date'}, inplace=True)
elif v.SEGMENT not in ['TAM','GTAM']: exit("Unhandled Segment")

# Create a Pandas Excel writer using XlsxWriter as the engine.
writer = pd.ExcelWriter(OUTPUT_FILE_LOCATION, engine="xlsxwriter")

# Convert the dataframe to an XlsxWriter Excel object.
df.to_excel(writer, sheet_name="Sheet1",index=False)

# Get the xlsxwriter workbook and worksheet objects.
workbook = writer.book
worksheet = writer.sheets["Sheet1"]

# Add some cell formats.
general = workbook.add_format()
fformat = workbook.add_format({"num_format": "0.00"})
dformat = workbook.add_format({"num_format": "dd-mm-yyyy"})
iformat = workbook.add_format({"num_format": "0"})

# Note: It isn't possible to format any cells that already have a format such
# as the index or headers or any cells that contain dates or datetimes.
def mapFormat(value):
    if value=='VARCHAR (255)': return general
    elif value=='FLOAT': return fformat
    elif value=='DATE': return dformat
    elif value=='INT': return iformat
    else: 
        exit("Unhandled Data Type ({}) while mapping formats to columns".format(value))
formatlist=[mapFormat(i) for i in [m.formatList[0]]+extra_formatList+m.formatList[1:]]
widthoffset=[m.widthOffset[0]]+extra_widthOffset+m.widthOffset[1:]

# adjust the column widths based on the content
for i, col in enumerate(df.columns):
    width = max(df[col].apply(lambda x: len(str(x))).max(), len(col))
    worksheet.set_column(i, i, width+widthoffset[i],formatlist[i])

# Get the dimensions of the dataframe.
(max_row, max_col) = df.shape

# Create a list of column headers, to use in add_table().
column_settings = []
for header in df.columns:
    column_settings.append({'header': header})


# Add the table.
worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

# Close the Pandas Excel writer and output the Excel file.
writer.close()



