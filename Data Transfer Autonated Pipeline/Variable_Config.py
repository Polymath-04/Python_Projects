from sys import exit
# import os
# from dotenv import load_dotenv, dotenv_values 
# load_dotenv() 

EVALUATION=True
DELETE_DOWNLOADED_FILE=True
DOWNLOADS_PATH = r"C:\Users\Ext-Parth\Downloads" # downloads path, change as per your requirement
OUTPUT_FILE_LOCATION=r"C:\Users\Ext-Parth\Desktop\testing internet output" #output file location, change as per your requirement
# EVALUATION=os.getenv("EVALUATION")
# DELETE_DOWNLOADED_FILE=os.getenv("DELETE_DOWNLOADED_FILE")
# DOWNLOADS_PATH = r"{}".format(str(os.getenv("DOWNLOADS_PATH")))
# #print(os.getenv("OUTPUT_FILE_LOCATION"))
# OUTPUT_FILE_LOCATION=os.getenv("OUTPUT_FILE_LOCATION")

Server='PARTH_LOCAL' # KAPIL_LAPTOP, KAPIL_DESKTOP, BHAVESH_LOCAL, IEX_Server

# Define below only if running a single file and not Download_And_Extract_Excel.py also set EMPTY_VALUES=False in .env file
EMPTY_VALUES = True # empty values for use in Download_And_Extract_Excel.py
SEGMENT='RTM' if not EMPTY_VALUES else '' # valid options: 'DAM', 'GDAM', 'HPDAM', 'RTM', 'TAM', 'GTAM'
START_DATE='2025-01-01' if not EMPTY_VALUES else ''
END_DATE='2025-01-31' if not EMPTY_VALUES else ''
INPUT_FILE_TIME_BLOCK_FORMAT=r"^\d{2}:\d{2}-\d{2}:\d{2}$" if not EMPTY_VALUES else ''
INPUT_FILE_LOCATION=r"C:\Users\Bhaveu00498\Downloads\RTM_Market Snapshot (1).xlsx" if not EMPTY_VALUES else ''

# server config options
if Server=='server name': # replace with details of your server.
    DB_SERVER='database_server_name'
    DB_NAME='database_name'
    DB_USER='database_user'
    DB_PASSWORD='database_password'
else: exit("Unknown Server")

# Helper Functions
def calibrate(seg,start,end):
    SEGMENT=seg#'DAM' 
    START_DATE=start#'01-12-2024'
    END_DATE=end#'31-12-2024'
    INPUT_FILE_TIME_BLOCK_FORMAT=r"^\d{2}:\d{2} - \d{2}:\d{2}$"
    if SEGMENT=="RTM": INPUT_FILE_TIME_BLOCK_FORMAT=r"^\d{2}:\d{2}-\d{2}:\d{2}$"
    if SEGMENT not in ['DAM','GDAM','HPDAM','RTM','TAM','GTAM']: exit("Invalid Segment Entered")

    return SEGMENT,START_DATE,END_DATE,INPUT_FILE_TIME_BLOCK_FORMAT
def timeToBlock(time):
    return (int(time[-5:-3])*60+int(time[-2:]))//15

# CONSTANTS
SQL_DATE_FORMAT=r"%Y-%m-%d"
INPUT_FILE_DATE_FORMAT=r"%d-%m-%Y" # general format variables, don't change unless format of IEX market snapshots has been changed


################ MISCELLANEOUS STUFF ######################
#TEST=False
#TEST_INPUT_FOLDER_LOCATION=''
#if TEST:
#    if not TEST_INPUT_FOLDER_LOCATION: exit("Testing Mode is ON but Test Input Folder Location is not specified")
#elif not INPUT_FILE_LOCATION: exit("Input File Location Not Specified")

