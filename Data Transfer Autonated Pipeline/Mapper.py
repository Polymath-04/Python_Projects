import Variable_Config as v

class mapit:
    TableName=''
    ColumnNames=[]
    ConvColumnNames=[]
    widthOffset=[]
    formatList=[]
    header=0
    ConvColumnNames=[]
    ColumnDType=[]
    masterColumnNames=[]
    masterConvColumnNames=[]
    masterColumnDType=[]
    masterFormatList=[]

    def __init__(self):
        if v.SEGMENT=='DAM':
            self.TableName='tbl_InternetDAM'
            self.ColumnNames=['Date', 'Hour', 'Time Block', 'Purchase Bid (MW)', 'Sell Bid (MW)', 'MCV (MW)','Final Scheduled Volume (MW)', 'MCP (Rs/MWh) *']
            self.widthOffset=[2,0,2,1,1,1,3,0,3]
            self.header=4
        elif v.SEGMENT=='GDAM':
            self.TableName='tbl_InternetGDAM'
            self.ColumnNames=['Date','Hour','Time Block','Purchase Bid (MW)','Total Sell Bid (MW)','Solar Bid (MW)','Non-Solar Sell Bid (MW)','Hydro Sell Bid (MW)','Total MCV (MW)','Solar MCV (MW)','Non-Solar MCV (MW)','Hydro MCV (MW)','Total FSV (MW)','Solar FSV (MW)','Non-Solar FSV (MW)','Hydro FSV (MW)','MCP (Rs/MWh)']
            self.widthOffset=[2,0,2,1,1,-1,1,-1,0,2,2,2,3,1,1,1,2,3]
            self.header=4
        elif v.SEGMENT=='HPDAM':
            self.TableName='tbl_InternetHPDAM'
            self.ColumnNames=['Date', 'Hour', 'Time Block', 'Purchase Bid (MW)', 'Sell Bid (MW)', 'MCV (MW)','Final Scheduled Volume (MW)', 'MCP (Rs/MWh) *']
            self.widthOffset=[2,0,2,1,1,1,3,0,3]
            self.header=4
        elif v.SEGMENT=='RTM':
            self.TableName='tbl_InternetRTM'
            self.ColumnNames=['Date', 'Hour', 'Session ID', 'Time Block', 'Purchase Bid (MW)', 'Sell Bid (MW)', 'MCV (MW)','Final Scheduled Volume (MW)', 'MCP (Rs/MWh) *']
            self.widthOffset=[2,0,2,1,1,1,1,3,0,3]
            self.header=4
        elif v.SEGMENT=='TAM':
            self.TableName='tbl_InternetTAM'
            self.ColumnNames=['Trade Date','Contract Type','Instrument Name','Highest Price','Lowest Price','Average Price','Weighted Average','Total Traded Volume (MWh)','No of Trades']
            self.widthOffset=[2,1,1,2,0,1,0,1,1,1]
            self.header=3
        elif v.SEGMENT=='GTAM':
            self.TableName='tbl_InternetGTAM'
            self.ColumnNames=['Trade Date','Contract Type','Instrument Name','Highest Price (Rs/Mwh)','Lowest Price (Rs/Mwh)','Average Price (Rs/Mwh)','Weighted Average (Rs/Mwh)','Total Traded Volume (MWh)','No of Trades']
            self.widthOffset=[2,1,1,2,0,0,0,1,1,1]
            self.header=3

        else: exit("Invalid Segment Entered in variables file")

        self.ConvColumnNames=[self.formatName(i) for i in self.ColumnNames]

        self.ColumnDType=self.generateDTypeList(self.ColumnNames)
        self.formatList=['VARCHAR (255)']+self.ColumnDType

        self.masterColumnNames=['Date', 'Hour', 'Time Block', 'Purchase Bid (MW)', 'Sell Bid (MW)', 'MCV (MW)','Final Scheduled Volume (MW)', 'MCP (Rs/MWh) *']
        if v.SEGMENT=='RTM': self.masterConvColumnNames=['Record_Date','Record_Hour','Time_Block','Purchase_Bid_MW','Sell_Bid_MW','MCV_MW','Final_Scheduled_Volume_MW','MCP_Rs_MWh']#[formatName(i) for i in masterColumnNames]
        elif v.SEGMENT=='GDAM': self.masterConvColumnNames=['Record_Date','Record_Hour','Time_Block','Purchase_Bid_MW','Total_Sell_Bid_MW','Total_MCV_MW','Total_FSV_MW','MCP_Rs_MWh']
        else: self.masterConvColumnNames=[self.formatName(i) for i in self.masterColumnNames]

        self.masterColumnDType=self.generateDTypeList(self.masterColumnNames)
        self.masterFormatList=['VARCHAR (255)']+self.masterColumnDType

    def formatName(self,text):
        if text in ['Date','Trade Date']: return 'Record_Date'
        if text=='Hour': return 'Record_Hour'
        if v.SEGMENT=='GTAM': text=text.replace(' (Rs/Mwh)','')
        return text.replace(' *', '').replace('(', '').replace(')', '').replace('/', '_').replace(' ', '_').replace('-','_')

    def generateDTypeList(self,cnames):
        ColumnDType=[]
        for i in cnames:
            if 'MW' in i or 'Price' in i or 'Average' in i: ColumnDType.append('FLOAT')
            elif i in ['Date','Trade Date']: ColumnDType.append('DATE')
            elif i in ['Contract Type','Instrument Name']: ColumnDType.append('VARCHAR (255)')
            else: ColumnDType.append('INT')
        return ColumnDType
