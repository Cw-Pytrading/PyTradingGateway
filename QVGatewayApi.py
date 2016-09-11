import json
import logging
from datetime import datetime, timedelta
import threading
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import zmq
from QVDataType import *

EMPTY_STRING = ''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0

class QVTradingGateway(object):

    def __init__(self):
        self.SettingFileName = 'CTA_Setting.json'
        self.UserID = EMPTY_STRING
        self.Password = EMPTY_STRING
        self.ReqAddress = EMPTY_STRING
        self.MdAddress = EMPTY_STRING
        self.TdAddress = EMPTY_STRING
        self.HbAddress = EMPTY_STRING

        self.CTP_InvestorID = EMPTY_STRING
        self.SGIT_F_InvestorID = EMPTY_STRING
        self.SGIT_S_InvestorID = EMPTY_STRING
        self.ApiType = EMPTY_INT


        self.ReqLogName = EMPTY_STRING
        self.MdLogName  = EMPTY_STRING
        self.TdLogName = EMPTY_STRING
        self.HbLogName = EMPTY_STRING
        self.GatewayLogName = EMPTY_STRING
        self.TickDbName = EMPTY_STRING
        self.OrderDbName = EMPTY_STRING
        self.ErrorDbName = EMPTY_STRING
        self.TradeDbName = EMPTY_STRING
        self.MsgDbName = EMPTY_STRING

        self.DbClient = None
        self.logger = None
        self.MdConnectionStatus = False  # 连接状态
        self.TdConnectionStatus = False  # 连接状态
        self.LoginStatus = False  # 登录状态

        self.UserOrderRef = EMPTY_INT
        self.TraderApi = QVTaderApi(self)
        self.MdApi = QVMdApi(self)
        self.TraderRtnApi = QVTraderRtnApi(self)
        self.HbApi = QVHeartBeatingApi(self)

    # ----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.loadSetting()
        self.LoggerSetup(self.GatewayLogName)
        self.DbConnect()


    # ----------------------------------------------------------------------
    def LoggerSetup(self, LoggerName):  # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        self.logger = logging.getLogger(LoggerName)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(LoggerName + '.log')
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s - [line:%(lineno)d] - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.debug('Logging Config')

    # ----------------------------------------------------------------------
    def loadSetting(self):
        """读取策略配置"""
        with open(self.SettingFileName) as f:
            l = json.load(f)
            for setting in l:
                if setting:
                    d = self.__dict__
                    for key in setting.keys():
                        if key in setting:
                            d[key] = setting[key]
    # ----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.Connect()
        self.Login()
        self.SubscribeTD()
        self.SubscribeHB()
        self.SubscribeMD()


    # ----------------------------------------------------------------------
    def Connect(self):
        self.TraderApi.Connect(self.UserID, self.Password, self.ReqAddress, self.ReqLogName)
        self.MdApi.Connect(self.UserID, self.Password, self.MdAddress, self.MdLogName)
        self.TraderRtnApi.Connect(self.UserID, self.Password, self.TdAddress, self.TdLogName)
        self.HbApi.Connect(self.UserID, self.Password, self.HbAddress, self.HbLogName)

    # ----------------------------------------------------------------------
    def SubscribeTD(self):
        self.TraderRtnApi.ThreadingSetup()

    # ----------------------------------------------------------------------
    def SubscribeMD(self):
        self.MdApi.ThreadingSetup()

    # ----------------------------------------------------------------------
    def SubscribeHB(self):
        self.HbApi.ThreadingSetup()

    # ----------------------------------------------------------------------
    def Login(self):
        self.TraderApi.Login()

    # ----------------------------------------------------------------------
    def LoadMongoSetting(self):
        """载入MongoDB数据库的配置"""
        try:
            f = open("Mongo_setting.json")
            setting = json.load(f)
            host = setting['MongoHost']
            port = setting['MongoPort']
        except:
            host = 'localhost'
            port = 27017

        return host, port

    # ----------------------------------------------------------------------
    def DbConnect(self):
        """连接MongoDB数据库"""
        if not self.DbClient:
            # 读取MongoDB的设置
            host, port = self.LoadMongoSetting()
            self.logger.debug('1')
            try:
                # 设置MongoDB操作的超时时间为0.5秒
                self.DbClient = MongoClient(host, port, serverSelectionTimeoutMS=500)

                # 调用server_info查询服务器状态，防止服务器异常并未连接成功
                self.DbClient.server_info()

                self.logger.info('MongoDB Connect Success')
            except ConnectionFailure:
                self.logger.info('MongoDB Connect Fail')

    #----------------------------------------------------------------------
    def dbInsert(self, dbName, collectionName, d):
        """向MongoDB中插入数据，d是具体数据"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection = db[collectionName]
            collection.insert(d)

    # ----------------------------------------------------------------------
    def insertTick(self, tick):
        """向数据库中插入tick数据"""
        self.dbInsert(self.TickDbName, tick.InstrumentID, tick)

    # ----------------------------------------------------------------------
    def insertOrder(self, order, OrderDate):
        """向数据库中插入order数据"""
        self.dbInsert(self.OrderDbName, OrderDate+order.InstrumentID, order)

    # ----------------------------------------------------------------------
    def insertTrade(self, trade, TradeDate):
        """向数据库中插入trade数据"""
        self.dbInsert(self.TradeDbName, TradeDate+trade.InstrumentID, trade)

    # ----------------------------------------------------------------------
    def insertError(self, error, ErrorDate):
        """向数据库中插入error数据"""
        self.dbInsert(self.ErrorDbName, str(ErrorDate)+ ' @ '+ str(error.errorID), error)

    # ----------------------------------------------------------------------
    def insertMsg(self, msg, MsgDate, MsgName):
        """向数据库中插入msg数据"""
        self.dbInsert(self.MsgDbName, str(MsgDate)+MsgName, msg)

    # ----------------------------------------------------------------------
    def onTick(self, tick):
        """市场行情推送"""
        # 通用事件
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onTrade(self, trade):
        """成交信息推送"""
        # 通用事件
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onOrder(self, order):
        """订单变化推送"""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onPosition(self, position):
        """持仓信息推送"""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onAccount(self, account):
        """账户信息推送"""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onError(self, error):
        """错误信息推送"""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def onContract(self, contract):
        """合约基础信息推送"""
        raise NotImplementedError

    # ----------------------------------------------------------------------
    def SendOrder(self, InstrumentID, Price, Volume, Direction, OffsetFlag, UserOrderRef, ExchangeID, ApiType):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID

        self.TraderApi.SendOrder(InstrumentID, Price, Volume, Direction, OffsetFlag, UserOrderRef, ExchangeID, ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def CancelOrder(self,InstrumentID, UserOrderRef,ApiType, ExchangeID):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID
        self.TraderApi.CancelOrder(InstrumentID, UserOrderRef,ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def ReqPosition(self, InstrumentID, UserOrderRef, ApiType, ExchangeID):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID
        self.TraderApi.ReqPosition(InstrumentID, UserOrderRef, ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def ReqTradingAccount(self, UserOrderRef, ApiType, ExchangeID):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID
        self.TraderApi.ReqTradingAccount(UserOrderRef, ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def ReqOrderInfo(self, UserOrderRef, ApiType, ExchangeID):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID
        self.TraderApi.ReqOrderInfo(UserOrderRef, ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def ReqTradeInfo(self, UserOrderRef,ApiType, ExchangeID):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID
        self.TraderApi.ReqTradeInfo(UserOrderRef, ApiType, InvestorID)

    # ----------------------------------------------------------------------
    def ReqContractInfo(self, InstrumentID, ExchangeID, UserOrderRef, ApiType):
        if ApiType == 1:
            InvestorID = self.CTP_InvestorID
        elif ApiType == 2:
            if ExchangeID == 'SGE':
                InvestorID = self.SGIT_S_InvestorID
            elif ExchangeID in ['SHFE','DCE','CZCE']:
                InvestorID = self.SGIT_F_InvestorID

        self.TraderApi.ReqContractInfo(InstrumentID, ExchangeID, UserOrderRef, ApiType, InvestorID)


class QVTaderApi(object):
    """QV交易API实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """API对象的初始化函数"""
        super(QVTaderApi, self).__init__()

        self.UserID = EMPTY_STRING
        self.Password = EMPTY_STRING
        self.Address = EMPTY_STRING

        self.gateway = gateway

        self.logger = None
        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态

        self.UserOrderRef = EMPTY_INT
        self.socketReq = None


    def LoggerSetup(self, LoggerName):  # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        self.logger = logging.getLogger(LoggerName)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(LoggerName + '.log')
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s - [line:%(lineno)d] - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.debug('Logging Config')

    def Login(self):
        # 请求端口
        contextReq = zmq.Context()
        self.socketReq = contextReq.socket(zmq.REQ)
        self.socketReq.setsockopt_string(zmq.IDENTITY, self.UserID)
        self.socketReq.connect(self.Address)
        self.UserOrderRef = self.ReqLogin()
        self.gateway.UserOrderRef = self.UserOrderRef
        self.gateway.LoginStatus = True

    def Connect(self, UserID, Password, Address, LoggerName):

        self.UserID = UserID
        self.Password = Password
        self.Address = Address
        self.LoggerSetup(LoggerName)

    def SendOrder(self, InstrumentID, Price, Volume, Direction, OffsetFlag, UserOrderRef, ExchangeID, ApiType, InvestorID):
        # 订单报入函数

        data = dict()

        data["BizCode"] = 2
        data["ApiType"] = ApiType
        data["InvestorID"] = InvestorID
        data["UserID"] = self.UserID
        data["InstrumentID"] = InstrumentID
        data["Price"] = Price
        data["Volume"] = Volume
        data["Direction"] = Direction
        data["OffsetFlag"] = OffsetFlag
        data["UserOrderRef"] = UserOrderRef
        data["ExchangeID"] = ExchangeID
        data_string = json.dumps(data)
        self.logger.info(str(data_string))
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('SendOrder ' + str(recvdata))

    def CancelOrder(self,InstrumentID, UserOrderRef, ApiType, InvestorID):
        # 订单撤销函数

        data = dict()

        data["BizCode"] = 3
        data["ApiType"] = ApiType
        data["UserID"] = self.UserID
        data["InvestorID"] = InvestorID
        data["InstrumentID"] = InstrumentID
        data["UserOrderRef"] = UserOrderRef
        data_string = json.dumps(data)
        self.logger.info(str(data_string))
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('CancelOrder ' + str(recvdata))

    def ReqLogin(self):

        data = dict()
        data["BizCode"] = 1
        data["UserID"] = self.UserID
        data["Password"] = self.Password
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        self.logger.debug('request')
        recvdata = self.socketReq.recv_json()
        if int(recvdata['BizCode']) == 1:
            self.loginStatus = True
            OrderRef = int(recvdata['UserRef'])
            self.logger.info('ReqLogin')
        return OrderRef

    def ReqPosition(self, InstrumentID, UserOrderRef, ApiType, InvestorID):

        data = dict()
        data["ApiType"] = ApiType
        data["BizCode"] = 4
        data["UserID"] = self.UserID
        data["InvestorID"] = InvestorID
        data["InstrumentID"] = InstrumentID
        data["UserOrderRef"] = UserOrderRef
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('ReqPosition ' + str(recvdata))

    def ReqTradingAccount(self, UserOrderRef, ApiType, InvestorID):

        data = dict()

        data["BizCode"] = 5
        data["ApiType"] = ApiType
        data["UserID"] = self.UserID
        data["InvestorID"] = InvestorID
        data["UserOrderRef"] = UserOrderRef
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('ReqTradingAccount ' + str(recvdata))

    def ReqOrderInfo(self, UserOrderRef, ApiType, InvestorID):

        data = dict()

        data["BizCode"] = 6
        data["ApiType"] = ApiType
        data["UserID"] = self.UserID
        data["InvestorID"] = InvestorID
        data["UserOrderRef"] = UserOrderRef
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('ReqOrderInfo ' + str(recvdata))

    def ReqTradeInfo(self, UserOrderRef, ApiType, InvestorID):

        data = dict()
        data["BizCode"] = 8
        data["ApiType"] = ApiType
        data["UserID"] = self.UserID
        data["InvestorID"] = InvestorID
        data["UserOrderRef"] = UserOrderRef
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('ReqTradeInfo ' + str(recvdata))

    def ReqContractInfo(self, InstrumentID, ExchangeID, UserOrderRef, ApiType, InvestorID):
        data = dict()

        data["BizCode"] = 10
        data["ApiType"] = ApiType
        data["UserID"] = self.UserID
        data["UserOrderRef"] = UserOrderRef
        data["InvestorID"] = InvestorID
        data["InstrumentID"] = InstrumentID
        data["ExchangeID"] = ExchangeID
        data["ProductID"] = "".join([a for a in InstrumentID if a.isalpha()])
        data["ExchangeInstID"] = InstrumentID
        self.logger.info(data)
        data_string = json.dumps(data)
        self.socketReq.send_string(data_string + '\0')
        recvdata = self.socketReq.recv_json()
        self.logger.info('ReqContractInfo ' + str(recvdata))

class QVMdApi(object):
    """QV交易API实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """API对象的初始化函数"""
        super(QVMdApi, self).__init__()

        self.UserID = EMPTY_STRING
        self.Password = EMPTY_STRING
        self.Address = EMPTY_STRING
        self.logger = QVLogData()
        self.gateway = gateway

        self.logger = None
        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态

        self.socketMdSub = None
        self.tMd = None


    def LoggerSetup(self, LoggerName):  # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        self.logger = logging.getLogger(LoggerName)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(LoggerName + '.log')
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s - [line:%(lineno)d] - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.debug('Logging Config')

    def Connect(self, UserID, Password, Address, LoggerName):
        self.UserID = UserID
        self.Password = Password
        self.Address = Address
        self.LoggerSetup(LoggerName)

    def ThreadingSetup(self):
        # 行情订阅端口
        contextMdSub = zmq.Context()
        self.socketMdSub = contextMdSub.socket(zmq.SUB)
        self.socketMdSub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.tMd = threading.Thread(target=self.MdSub, args=())
        self.tMd.start()


    def MdSub(self):

        self.socketMdSub.connect(self.Address)
        while True:

            MdTickData = self.socketMdSub.recv_json()
            # self.logger.debug(MdTickData)
            tick = QVTickData()
            tick.ApiType = int(MdTickData['ApiType'])
            tick.TradingDay = MdTickData['TradingDay']
            tick.InstrumentID = MdTickData['InstrumentID']
            tick.ExchangeID = MdTickData['ExchangeID']

            tick.LastPrice = float(MdTickData['LastPrice'])
            tick.Volume = int(MdTickData['Volume'])
            tick.BidPrice1 = float(MdTickData['BidPrice1'])
            tick.BidVolume1 = int(MdTickData['BidVolume1'])
            tick.AskPrice1 = float(MdTickData['AskPrice1'])
            tick.AskVolume1 = int(MdTickData['AskVolume1'])
            tick.UpdateTime = MdTickData['UpdateTime']
            tick.UpdateMillisec = int(MdTickData['UpdateMillisec'])

            self.gateway.onTick(tick)


class QVTraderRtnApi(object):
    """QV交易API实现"""

    #----------------------------------------------------------------------
    def __init__(self,gateway):
        """API对象的初始化函数"""
        super(QVTraderRtnApi, self).__init__()

        self.UserID = EMPTY_STRING
        self.Password = EMPTY_STRING
        self.Address = EMPTY_STRING

        self.gateway = gateway

        self.logger = None
        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态

        self.socketTdSub = None
        self.tTd = None

    def LoggerSetup(self, LoggerName):  # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        self.logger = logging.getLogger(LoggerName)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(LoggerName + '.log')
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s - [line:%(lineno)d] - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.debug('Logging Config')


    def Bytes2String(self, bt):
        return bt.decode("GBK")

    def Connect(self, UserID, Password, Address, LoggerName):
        self.UserID = UserID
        self.Password = Password
        self.Address = Address
        self.LoggerSetup(LoggerName)

    def ThreadingSetup(self):
        # 交易订阅端口
        contextTdSub = zmq.Context()
        self.socketTdSub = contextTdSub.socket(zmq.SUB)
        self.socketTdSub.setsockopt_string(zmq.SUBSCRIBE, self.UserID)
        self.tTd = threading.Thread(target=self.TdSub, args=())
        self.tTd.start()


    def TdSub(self):

        self.socketTdSub.connect(self.Address)

        while True:
            tempdata = self.Bytes2String(self.socketTdSub.recv())
            # self.logger.debug(tempdata)
            if tempdata == self.UserID:
                pass
            else:
                recvdata = json.loads(tempdata)
                self.logger.debug(recvdata)

                # 错误信息返回
                if int(recvdata['BizCode']) in [20, 21, 22, 26, 29]:
                    err = QVErrorData()
                    err.ApiType = int(recvdata['ApiType'])
                    err.UserRef = int(recvdata['UserRef'])
                    err.ErrorID = recvdata['ErrorId']
                    err.ErrorMsg = recvdata['ErrorMsg']
                    self.gateway.onError(err)

                # 报单信息返回
                elif int(recvdata['BizCode']) == 23:
                    order = QVOrderData()
                    order.ApiType = int(recvdata['ApiType'])
                    order.InstrumentID = recvdata['InstrumentID']
                    order.BizCode = int(recvdata['BizCode'])
                    order.UserRef = int(recvdata['UserRef'])
                    order.ExchangeID = recvdata['ExchangeID']  # 交易所代码

                    # 报单相关
                    order.LimitPrice = recvdata['LimitPrice']  # 报单价格
                    order.TradedVolume = int(recvdata['VolumeTraded'])  # 报单成交数量
                    order.TotalVolume = int(recvdata['VolumeTotalOriginal'])  # 报单总数量
                    order.OrderTime = recvdata['InsertTime']  # 撤单时间
                    order.CancelTime = recvdata['CancelTime']  # 撤单时间
                    order.SubmitStatus = recvdata['SubmitStatus']  # 报单提交状态
                    order.Status = recvdata['Status']   # 报单状态
                    self.gateway.onOrder(order)

                # 成交回报返回
                elif int(recvdata['BizCode']) in [24, 30]:
                    trade = QVTradeData()
                    if int(recvdata['BizCode']) == 24:
                        trade.RtnSeqNo = recvdata['RtnSeqNo']

                    trade.ApiType = int(recvdata['ApiType'])
                    trade.InstrumentID = recvdata['InstrumentID']
                    trade.BizCode = int(recvdata['BizCode'])
                    trade.UserRef = int(recvdata['UserRef'])
                    trade.TradeID = recvdata['TradeID']
                    trade.Direction = int(chr(recvdata['Direction']))
                    trade.OffsetFlag = int(chr(recvdata['OffsetFlag']))
                    trade.Price = recvdata['Price']
                    trade.Volume = int(recvdata['Volume'])
                    trade.TradeTime = recvdata['TradeTime']

                    self.gateway.onTrade(trade)

                # 合约信息查询返回
                elif int(recvdata['BizCode']) == 16:
                    contract = QVContractData()
                    contract.ApiType = int(recvdata['ApiType'])
                    contract.BizCode = int(recvdata['BizCode'])
                    contract.UserRef = int(recvdata['UserRef'])

                    contract.InstrumentID = recvdata['InstrumentID']
                    # contract.Size = recvdata['VolumeMultiple']
                    # contract.PriceTick = recvdata['PriceTick']
                    # contract.ProductID = recvdata['ProductID']
                    contract.DeliveryMonth = recvdata['DeliveryMonth']
                    contract.DeliveryYear = recvdata['DeliveryYear']
                    self.logger.debug(recvdata)
                    self.gateway.onContract(contract)

                # 持仓查询返回
                elif int(recvdata['BizCode']) == 27:
                    position = QVPositionData()
                    position.ApiType = int(recvdata['ApiType'])
                    position.BizCode = int(recvdata['BizCode'])
                    position.UserRef = int(recvdata['UserRef'])

                    # 持仓相关
                    position.InstrumentID = recvdata['InstrumentID']
                    position.PosiDirection = int(chr(recvdata['PosiDirection']))  # 持仓方向
                    position.Position = int(recvdata['Position'])  # 持仓量
                    position.PositionDate = int(chr(recvdata['PositionDate']))
                    position.HedgeFlag = int(recvdata['HedgeFlag'])
                    self.gateway.onPosition(position)

                # 报单查询返回
                elif int(recvdata['BizCode']) == 28:
                    order = QVOrderData()
                    order.InstrumentID = recvdata['InstrumentID']
                    order.ApiType = int(recvdata['ApiType'])
                    order.BizCode = int(recvdata['BizCode'])
                    order.UserRef = int(recvdata['UserRef'])
                    order.ExchangeID = recvdata['ExchangeID']  # 交易所代码

                    # 报单相关
                    order.LimitPrice = recvdata['LimitPrice']  # 报单价格
                    order.TradedVolume = int(recvdata['VolumeTraded'])  # 报单成交数量
                    order.TotalVolume = int(recvdata['VolumeTotalOriginal'])  # 报单总数量
                    order.OrderTime = recvdata['InsertTime']  # 撤单时间
                    order.CancelTime = recvdata['CancelTime']  # 撤单时间
                    order.SubmitStatus = int(chr(recvdata['SubmitStatus']))  # 报单提交状态
                    order.Status = int(chr(recvdata['Status']))  # 报单状态

                    self.gateway.onOrder(order)

                # 账户资金查询返回
                elif int(recvdata['BizCode']) == 15:
                    account = QVAccountData()
                    account.ApiType = int(recvdata['ApiType'])

                    account.BrokerID = recvdata['BrokerID']  # 账户代码
                    account.AccountID = recvdata['AccountID']  # 账户代码

                    # 数值相关
                    account.PreBalance = recvdata['PreBalance']  # 昨日账户结算净值
                    account.Balance = recvdata['Balance']  # 账户净值
                    account.Available = recvdata['Available']  # 可用资金
                    account.Commission = recvdata['Commission']  # 今日手续费
                    account.CurrMargin = recvdata['CurrMargin']  # 保证金占用
                    account.PreMargin = recvdata['PreMargin']  # 保证金占用
                    account.CloseProfit = recvdata['CloseProfit']  # 平仓盈亏
                    account.PositionProfit = recvdata['PositionProfit']  # 持仓盈亏
                    self.gateway.onAccount(account)



class QVHeartBeatingApi(object):
    """QV交易API实现"""

    #----------------------------------------------------------------------
    def __init__(self, gateway):
        """API对象的初始化函数"""
        super(QVHeartBeatingApi, self).__init__()

        self.UserID = EMPTY_STRING
        self.Password = EMPTY_STRING
        self.Address = EMPTY_STRING
        self.logger = QVLogData()
        self.gateway = gateway

        self.logger = None
        self.connectionStatus = False  # 连接状态
        self.loginStatus = False  # 登录状态

        self.socketHbSub = None
        self.tHb = None


    def LoggerSetup(self, LoggerName):  # CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
        self.logger = logging.getLogger(LoggerName)
        self.logger.setLevel(logging.DEBUG)
        # 创建一个handler，用于写入日志文件
        fh = logging.FileHandler(LoggerName + '.log')
        fh.setLevel(logging.INFO)
        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        formatter = logging.Formatter(
            '%(asctime)s - %(filename)s - %(name)s - [line:%(lineno)d] - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        # 给logger添加handler
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

        self.logger.debug('Logging Config')

    def Connect(self, UserID, Password, Address, LoggerName):
        self.UserID = UserID
        self.Password = Password
        self.Address = Address
        self.LoggerSetup(LoggerName)

    def ThreadingSetup(self):
        # 行情订阅端口
        contextHbSub = zmq.Context()
        self.socketHbSub = contextHbSub.socket(zmq.SUB)
        self.socketHbSub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.tHb = threading.Thread(target=self.HbSub, args=())
        self.tHb.start()


    def HbSub(self):

        self.socketHbSub.connect(self.Address)
        while True:
            # 心跳信息
            HbData = self.socketHbSub.recv_json()
            self.logger.debug(HbData)
