Objective: Download Internet Data of different Market Segments from iexindia.com and store it in SQL Server, Also create a method to generate report of the data from sql in excel 

# further ideas
- skip any day with error and log them to show in the end
- - create custom errors to keep track of general issues while uploading, processing or generating report
- - update all exit statements with raise keywords and custom errors
- - update Download_And_Extract_Excel.py to handle months with incorrect data and process those months day-by-day
- - output all days with invalid data segment-wise
- create .env file 
- create generic db upload file (just add table to mapper and run based on that)
- create detailed evaluation and general log modes
- export logs to txt file
- streamline single file execution process
- prepare process to delete internet file after uploading to sql
- prepare documentation