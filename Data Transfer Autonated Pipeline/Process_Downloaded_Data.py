from sqlalchemy import text, inspect
import pandas as pd
from sys import exit
from datetime import datetime
from re import match
import SQLconnection
import Variable_Config as v
import Mapper
m=Mapper.mapit()

engine=SQLconnection.create_connection()
mycursor=engine.connect()
if v.EVALUATION: print("CONNECTION MADE")
#######
#mycursor.execute(text("drop table monthly_raw"))
#mycursor.commit()
#######

# check and create a new table "monthly_raw" if it doesn't exist
# (with column values same as market_snapshot) 
inspector=inspect(engine)
if not m.TableName in inspector.get_table_names(): 
    mycursor.execute(text("CREATE TABLE "+m.TableName+" (Segment VARCHAR(255), "+(', '.join([' '.join(map(str, i)) for i in zip(m.ConvColumnNames, m.ColumnDType)]))+")"))
    mycursor.commit()
    if v.EVALUATION: print("NEW TABLE CREATED")

# read the excel file and insert the data into a pandas dataframe
try:
    df=pd.read_excel(v.INPUT_FILE_LOCATION,header=m.header)
    if v.DELETE_DOWNLOADED_FILE:
        try:
            from pathlib import Path
            Path(v.INPUT_FILE_LOCATION).unlink()
            print(f"File {v.INPUT_FILE_LOCATION} has been deleted successfully.")
        except FileNotFoundError:
            print(f"File {v.INPUT_FILE_LOCATION} not found.")
        except PermissionError:
            print(f"Permission denied to delete {v.INPUT_FILE_LOCATION}.")
        except Exception as e:
            print(f"An error occurred: {e}")
except Exception as e:
    exit("Invalid Input File: \n"+v.INPUT_FILE_LOCATION+"\n"+str(e))

if v.EVALUATION: print("FILE READ SUCCESSFULLY")

# remove aggregate table present directly below daily data in the input file
try:
    df=df.iloc[:df[df['Date']=='Date'].index[0]]
except Exception:
    pass
if v.EVALUATION: print("AGGREGATE TABLE REMOVED")

# check if all the required columns are present in the dataframe and there are no duplicate columns present
colnames=dict.fromkeys(m.ColumnNames,0)
for c in df.columns:
    if c in colnames: colnames[c]+=1
    if '.' in c: exit("Duplicate Columns present for \"{}\" Column".format(c[:c.find('.')]))
for k,c in colnames.items():
    if c==0: exit("Missing \"{}\" Column from Input File \nRequired Columns: ".format(k)+','.join(m.ColumnNames)+"\nInput File Location: "+v.INPUT_FILE_LOCATION)

if v.EVALUATION: print("COLUMNS CHECKED")

# rename the columns to remove special characters
df.columns = [m.formatName(c) for c in df.columns]
if v.EVALUATION: print("COLUMNS RENAMED")

# check for any empty values 
if df.isnull().sum().sum(): exit("Empty Values Present in File. Please check and upload correct file")
if v.EVALUATION: print("NO EMPTY VALUES")
############

ignore_dates=set()
minErrorRelaxation=2
match v.SEGMENT:
    case w if w in ['DAM','RTM']:#,'HPDAM' not active market yet
        def nullBidCheck(t,d,purchase,sell,mcv,fsv):
            purchase,sell,mcv,fsv=float(purchase),float(sell),float(mcv),float(fsv)
            # check if either purchase bid or sell bid is zero, MCV and FSV should also be zero
            if (not purchase or not sell) and (mcv or fsv): 
                if v.EVALUATION: print(f'case1 {d} {v.timeToBlock(t)} {purchase} {sell} {mcv} {fsv}')
                ignore_dates.add(d)
            # check if MCV is less than min(purchase bid, sell bid)
            else:
                m=min(purchase,sell)
                if not (m>=mcv or mcv-m<minErrorRelaxation): 
                    if v.EVALUATION: print(f'case2 {d} {v.timeToBlock(t)} {min(purchase,sell)} {mcv} {fsv}')
                    ignore_dates.add(d)
        df.apply(lambda row: nullBidCheck(row['Time_Block'],row['Record_Date'],row['Purchase_Bid_MW'],row['Sell_Bid_MW'],row['MCV_MW'],row['Final_Scheduled_Volume_MW']), axis=1)
    case 'GDAM':
        def nullBidCheckGDAM(t,d,purchase,sell,solarSell,nonSolarSell,hydroSell,mcv,solarMCV,nonSolarMCV,hydroMCV,fsv,solarFSV,nonSolarFSV,hydroFSV):
            purchase,sell,solarSell,nonSolarSell,hydroSell,mcv,solarMCV,nonSolarMCV,hydroMCV,fsv,solarFSV,nonSolarFSV,hydroFSV=float(purchase),float(sell),float(solarSell),float(nonSolarSell),float(hydroSell),float(mcv),float(solarMCV),float(nonSolarMCV),float(hydroMCV),float(fsv),float(solarFSV),float(nonSolarFSV),float(hydroFSV)
            # check if either purchase bid or sell bid is zero, MCV and FSV should also be zero
            if (not purchase or not sell) and (mcv or fsv): 
                if v.EVALUATION: print(f'case1 {d} {v.timeToBlock(t)} {purchase} {sell} {mcv} {fsv}')
                ignore_dates.add(d)
            elif not solarSell and (solarMCV or solarFSV): 
                if v.EVALUATION: print(f'case1solar {d} {v.timeToBlock(t)} {purchase} {solarSell} {solarMCV} {solarFSV}')
                ignore_dates.add(d)
            elif not nonSolarSell and (nonSolarMCV or nonSolarFSV): 
                if v.EVALUATION: print(f'case1nonsolar {d} {v.timeToBlock(t)} {purchase} {nonSolarSell} {nonSolarMCV} {nonSolarFSV}')
                ignore_dates.add(d)
            elif not hydroSell and (hydroMCV or hydroFSV): 
                if v.EVALUATION: print(f'case1hydro {d} {v.timeToBlock(t)} {purchase} {hydroSell} {hydroMCV} {hydroFSV}')
                ignore_dates.add(d)
            
            # check if MCV is less than min(purchase bid, sell bid)
            else:
                # assumption that solarsell + nonsolarsell + hydrosell = sell
                if not (min(purchase,sell)>=mcv or mcv-min(purchase,sell)<minErrorRelaxation): 
                    if v.EVALUATION: print(f'case2 {d} {v.timeToBlock(t)} {purchase} {sell} {min(purchase,sell)} {mcv} {fsv}')
                    ignore_dates.add(d)
                elif not (min(purchase,solarSell)>=solarMCV or solarMCV-min(purchase,solarSell)<minErrorRelaxation): 
                    if v.EVALUATION: print(f'case2solar {d} {v.timeToBlock(t)} {purchase} {solarSell} {min(purchase,solarSell)} {solarMCV} {solarFSV}')
                    ignore_dates.add(d)
                elif not (min(purchase,nonSolarSell)>=nonSolarMCV or nonSolarMCV-min(purchase,nonSolarSell)<minErrorRelaxation):
                    if v.EVALUATION: print(f'case2nonsolar {d} {v.timeToBlock(t)} {purchase} {nonSolarSell} {min(purchase,nonSolarSell)} {nonSolarMCV} {nonSolarFSV}')
                    ignore_dates.add(d)
                elif not (min(purchase,hydroSell)>=hydroMCV or hydroMCV-min(purchase,hydroSell)<minErrorRelaxation):
                    if v.EVALUATION: print(f'case2hydro {d} {v.timeToBlock(t)} {purchase} {hydroSell} {min(purchase,hydroSell)} {hydroMCV} {hydroFSV}')
                    ignore_dates.add(d)
        df.apply(lambda row: nullBidCheckGDAM(row['Time_Block'],row['Record_Date'],row['Purchase_Bid_MW'],row['Total_Sell_Bid_MW'],row['Solar_Bid_MW'],row['Non_Solar_Sell_Bid_MW'],row['Hydro_Sell_Bid_MW'],row['Total_MCV_MW'],row['Solar_MCV_MW'],row['Non_Solar_MCV_MW'],row['Hydro_MCV_MW'],row['Total_FSV_MW'],row['Solar_FSV_MW'],row['Non_Solar_FSV_MW'],row['Hydro_FSV_MW']), axis=1)
    # case w if w in ['TAM','GTAM']:
    #     def nullBidCheckiTAM(t,d,high,low,avg,weightavg,vol):
    #         purchase,sell,mcv=float(purchase),float(sell),float(mcv)
    #         # check if either purchase bid or sell bid is zero, MCV and FSV should also be zero
    #         if (not purchase or not sell) and (mcv or fsv): 
    #             if v.EVALUATION: print(f'case1 {d} {v.timeToBlock(t)} {not purchase} {not sell} {mcv} {fsv}')
    #             ignore_dates.add(d)
    #         # check if MCV is less than min(purchase bid, sell bid)
    #         else:
    #             m=min(purchase,sell)
    #             if not (m>=mcv or mcv-m<minErrorRelaxation): 
    #                 if v.EVALUATION: print(f'case2 {d} {v.timeToBlock(t)} {min(purchase,sell)} {mcv} {fsv}')
    #                 ignore_dates.add(d)
    #     df.apply(lambda row: nullBidCheckiTAM(v.SEGMENT,row['Highest_Price'],row['Lowest_Price'],row['Average_Price'],row['Weighted_Average'],row['Total_Traded_Volume_MWh']), axis=1)
    case _: pass

if v.EVALUATION:
    if ignore_dates:
        print("Invalid Dates with issues in Purchase Bid, Sell Bid and MCV: ")
        for i in ignore_dates:
            print(i)
    else: print("NO INVALID DATES DUE TO PURCHASE, SELL, MCV, FSV ISSUES PRESENT")

# iterate through the dataframe to check for missing entries in between the range of dates given in input file
bc=0
# check if first date in input file is in correct format, if yes then convert to datetime format
try:
    currDate=datetime.strptime(df.iloc[0]['Record_Date'], v.INPUT_FILE_DATE_FORMAT)
except Exception as e:
    exit("Invalid Date at row {} in input file: \nDate Value: {}, \nEntry: {}, \nError: {}".format(6,df.iloc[0]['Record_Date'],df.iloc[0],e))
for i in df.itertuples():
    idate=None
    for c in range(len(m.ConvColumnNames)):
        dt=m.ColumnDType[c]
        if dt=='DATE':
            # check if the date value of the current row is in correct format
            try:
                if type(getattr(i,m.ConvColumnNames[c])) is datetime: 
                    idate=getattr(i,m.ConvColumnNames[c])
                    df.at[i.Index,c]=idate.strftime(v.INPUT_FILE_DATE_FORMAT)
                else: idate=datetime.strptime(getattr(i,m.ConvColumnNames[c]), v.INPUT_FILE_DATE_FORMAT)
            except Exception as e: 
                exit("Invalid Date at row {} in input file: \nDate Value: {}, \nError: {}".format(i.Index+6,getattr(i,m.ConvColumnNames[c]),e))

        elif dt=='INT':
            if m.ConvColumnNames[c]=='Record_Hour':
                # check if hour value is in correct format
                try:
                    if int(i.Record_Hour)!=float(i.Record_Hour) or int(i.Record_Hour) not in range(1,25): exit("Invalid Hour at row {} in input file: \nHour Value: {}, \nEntry: {}".format(i.Index+6,i.Record_Hour,i))
                except:
                    exit("Invalid Hour Format at row {} in input file: \nHour Value: {}, \nEntry: {}".format(i.Index+6,i.Record_Hour,i))
            elif m.ConvColumnNames[c]=='Time_Block':
                # check if the time block value is in correct format
                if not match(v.INPUT_FILE_TIME_BLOCK_FORMAT, i.Time_Block): exit("Invalid Time_Block at row {} in input file: \nTime_Block Value: {}, \nEntry: {}".format(i.Index+6,i.Time_Block,i))
            else:
                # check if generic int value in in correct format
                try:
                    if int(getattr(i,m.ConvColumnNames[c]))!=float(getattr(i,m.ConvColumnNames[c])): exit("Invalid value (should be int) at row {} in input file: \nValue: {}, \nEntry: {}".format(i.Index+6,getattr(i,m.ConvColumnNames[c]),i))
                except:
                    exit("Invalid Format (should be int) at row {} in input file: \nValue: {}, \nEntry: {}".format(i.Index+6,getattr(i,m.ConvColumnNames[c]),i))

        elif dt=='FLOAT':
            # check if float values in the row are positive floats
            try:
                if not float(getattr(i,m.ConvColumnNames[c])) >=0: 
                    exit("Invalid Negative Value at row {} in input file: \nEntry: {}".format(i.Index+6,i))
            except Exception as e:
                exit("Invalid Format for Value at row {} in input file: \nEntry: {}".format(i.Index+6,i))
        elif dt!='VARCHAR (255)': exit("Unhandled Data Type while testing formats")
    if not idate: exit("Row does not have a date entry present\nEntry:{}".format(i))

    # check if the dates are in order and each date has 96 entries
    if idate!=currDate:
        #if days_between(currDate,idate)==1: 
        if (idate-currDate).days==1:
            if v.SEGMENT not in ['TAM','GTAM']:
                if bc==96: bc,currDate=0,idate
                elif bc<96: exit("Incomplete entries for Date: {} (only {} entries present)".format(currDate,bc))
                else: exit("Duplicate entries for Date: {} ({} entries present)".format(currDate,bc))
            else: bc,currDate=0,idate
        elif v.SEGMENT in ['TAM','GTAM']: bc,currDate=0,idate
        else: 
            exit("Inconsistent Dates (Make sure all the dates are in order and data for all the dates is present in the range)")
    bc+=1

    if "Time Block" in m.ColumnNames:
        # check for any extra / duplicate entries for the date
        time_block=v.timeToBlock(i.Time_Block)
        if time_block<bc: exit("Duplicate entries for Date: {} (Time_Block: {})".format(i.Record_Date,i.Time_Block))
        elif time_block>bc: exit("Missing Block for Date {}: Check before Time Block {}".format(i.Record_Date,i.Time_Block))
if v.EVALUATION: print("DATA VALIDATED")

def toSQLentry(value,column,dtype):
    if column=="Time_Block": return str(v.timeToBlock(value))
    if dtype in ['INT','FLOAT']: return str(value)
    if dtype in ['VARCHAR (255)']: return "\'"+str(value)+"\'"
    # change 105 to something if date format is changed in the input file in the future
    elif dtype=='DATE': return "convert(datetime,\'"+str(value)+"\',105)"

def insertIntoSQL(df,tableName,convColumnNames,columnDType):
    # insert the data from the dataframe into the sql table
    ec=sc=0
    rep=set()
    for i in df.itertuples():    
        # check if the data already exists, skip the entry if its already present 
        result=None
        if v.SEGMENT not in ['TAM','GTAM']:
            result=mycursor.execute(text("select * from "+tableName+" where Segment=\'"+v.SEGMENT+"\' and Record_Date=convert(datetime,\'"+str(i.Record_Date)+"\',105) and Time_Block="+str(v.timeToBlock(i.Time_Block))+" and Record_Hour="+str(i.Record_Hour)))
        else:
            result=mycursor.execute(text("select * from "+tableName+" where Segment=\'"+v.SEGMENT+"\' and Record_Date=convert(datetime,\'"+str(i.Record_Date)+"\',105) and Instrument_Name=\'"+str(i.Instrument_Name)+"\'"))

        # if data is already present in table, discrepency is present, store date of the discrepency
        if result and result.rowcount: rep.add(i.Record_Date)
        elif i.Record_Date not in ignore_dates and i.Record_Date not in rep:
        # if the data does not already exist in table, add the entry to the table
            try:
                mycursor.execute(text("insert into "+tableName+" values(\'"+v.SEGMENT+"\', "+str(', '.join([toSQLentry(getattr(i,convColumnNames[j]),convColumnNames[j],columnDType[j]) for j in range(len(convColumnNames))]))+")"))
                mycursor.commit()
                sc+=1
            except Exception as e:
                # if the insert fails, print the error and the query that failed
                print("Error while inserting {}: {}".format(i,e))
                ec+=1
    if v.EVALUATION: print("DATA INSERTED")
    # print the number of entries that failed to insert, if any
    if ec: 
        print("Number of failed insert entries: {}/{}".format(ec,ec+sc))
        ec=0

    # update the data if the data already exists in the table (with user's permission)
    updateFlag='N'
    uc=0
    if rep: 
        # display dates for which entries are already present in database
        print("Following Dates have entries already present")
        for i in sorted(rep): print(i)
        # ask user if they want to update the data for the dates with discrepencies
        print("Re-Upload data with new values? (Y/N): ".format(len(rep)),end="")
        updateFlag='Y'#input().strip().upper()
        if updateFlag=='Y':
            # iterate through dates with discrepancies
            for d in rep:
                # delete previous data present in database for the date
                mycursor.execute(text("delete from "+tableName+" where Segment=\'"+v.SEGMENT+"\' and Record_Date=convert(datetime,\'"+str(d)+"\',105)"))
                mycursor.commit()
                # insert the new data for the date
                for i in df.loc[df['Record_Date']==d].itertuples():
                    try:
                        mycursor.execute(text("insert into "+tableName+" values(\'"+v.SEGMENT+"\', "+str(', '.join([toSQLentry(getattr(i,convColumnNames[j]),m.ConvColumnNames[j],columnDType[j]) for j in range(len(convColumnNames))]))+")"))
                        mycursor.commit()
                        uc+=1
                    except Exception as e:
                        print("Error while inserting {}: {}".format(i,e))
                        ec+=1
            # print no of entries that failed to insert, if any ELSE print no of entries that were inserted
            if ec: print("Number of Failed update entries: {}/{}".format(ec,ec+uc+sc))
            else: print("Data Updated Successfully ({} new entries, {} updated entries)".format(sc,uc))
        else: print("Data Inserted Successfully ({} entries)".format(sc))
        if v.EVALUATION: print("DATA UPDATED")
    elif not ec:
        # print the number of entries that were successfully inserted
        print("Data Inserted Successfully ({} unique entries)".format(sc))

if v.EVALUATION: print("INSERTING DATA INTO ORG TABLE")
insertIntoSQL(df,m.TableName,m.ConvColumnNames,m.ColumnDType)
if v.EVALUATION: print("DATA INSERTED INTO ORG TABLE")

# if v.SEGMENT in ['DAM','GDAM','HPDAM','RTM'] and m.TableName!='tbl_InternetData':
#     print("Uploading again in tbl_InternetData")
#     df=df.loc[:,m.masterConvColumnNames]
#     if v.EVALUATION: print("INSERTING DATA INTO MASTER TABLE")
#     insertIntoSQL(df,'tbl_InternetData',m.masterConvColumnNames,m.masterColumnDType)
#     if v.EVALUATION: print("DATA INSERTED INTO MASTER TABLE")

# close the connection
mycursor.close()
engine.dispose()
if v.EVALUATION: print("CONNECTION CLOSED")

