import time

EMPTY_STRING = ''
EMPTY_INT = 0
EMPTY_FLOAT = 0.0
########################################################################
class QVBaseData(object):
    """回调函数推送数据的基础类，其他数据类继承于此"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.ApiType = EMPTY_INT
        self.rawData = None                     # 原始数据


########################################################################
class QVTickData(QVBaseData):
    """Tick行情数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVTickData, self).__init__()

        # 代码相关

        self.InstrumentID = EMPTY_STRING              # 合约代码
        self.ExchangeID = EMPTY_STRING            # 交易所代码
        self.TradingDay = EMPTY_STRING


        # 成交数据
        self.LastPrice = EMPTY_FLOAT            # 最新成交价
        self.LastVolume = EMPTY_INT             # 最新成交量
        self.Volume = EMPTY_INT                 # 今天总成交量
        self.OpenInterest = EMPTY_INT           # 持仓量
        self.UpdateTime = EMPTY_STRING                # 时间
        self.UpdateMillisec = EMPTY_INT                #

        # 常规行情
        self.OpenPrice = EMPTY_FLOAT            # 今日开盘价
        self.HighestPrice = EMPTY_FLOAT            # 今日最高价
        self.LowestPrice = EMPTY_FLOAT             # 今日最低价
        self.PreClosePrice = EMPTY_FLOAT
        self.PreSettlementPrice = EMPTY_FLOAT
        self.PreOpenInterest = EMPTY_FLOAT
        self.Turnover = EMPTY_FLOAT

        self.UpperLimit = EMPTY_FLOAT           # 涨停价
        self.LowerLimit = EMPTY_FLOAT           # 跌停价

        # 五档行情
        self.BidPrice1 = EMPTY_FLOAT
        self.BidPrice2 = EMPTY_FLOAT
        self.BidPrice3 = EMPTY_FLOAT
        self.BidPrice4 = EMPTY_FLOAT
        self.BidPrice5 = EMPTY_FLOAT

        self.AskPrice1 = EMPTY_FLOAT
        self.AskPrice2 = EMPTY_FLOAT
        self.AskPrice3 = EMPTY_FLOAT
        self.AskPrice4 = EMPTY_FLOAT
        self.AskPrice5 = EMPTY_FLOAT

        self.BidVolume1 = EMPTY_INT
        self.BidVolume2 = EMPTY_INT
        self.BidVolume3 = EMPTY_INT
        self.BidVolume4 = EMPTY_INT
        self.BidVolume5 = EMPTY_INT

        self.AskVolume1 = EMPTY_INT
        self.AskVolume2 = EMPTY_INT
        self.AskVolume3 = EMPTY_INT
        self.AskVolume4 = EMPTY_INT
        self.AskVolume5 = EMPTY_INT


########################################################################
class QVTradeData(QVBaseData):
    """成交数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVTradeData, self).__init__()

        # 代码编号相关
        self.BizCode = EMPTY_INT
        self.UserRef = EMPTY_INT
        self.RtnSeqNo = EMPTY_INT

        self.InstrumentID = EMPTY_STRING                # 合约代码
        self.ExchangeID = EMPTY_STRING                  # 交易所代码


        self.TradeID = EMPTY_STRING                     # 成交编号
        self.OrderSysID = EMPTY_STRING                  # 订单编号

        # 成交相关
        self.Direction = EMPTY_INT                      # 成交方向
        self.OffsetFlag = EMPTY_INT                     # 成交开平仓
        self.HedgeFlag = EMPTY_INT
        self.Price = EMPTY_FLOAT                        # 成交价格
        self.Volume = EMPTY_INT                         # 成交数量
        self.TradeTime = EMPTY_STRING                   # 成交时间


########################################################################
class QVOrderData(QVBaseData):
    """订单数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVOrderData, self).__init__()

        self.BizCode = EMPTY_INT
        self.UserRef = EMPTY_INT

        self.InstrumentID = EMPTY_STRING    # 合约代码
        self.ExchangeID = EMPTY_STRING      # 交易所代码

        # 报单相关
        self.LimitPrice = EMPTY_FLOAT       # 报单价格
        self.TradedVolume = EMPTY_INT       # 报单成交数量
        self.TotalVolume = EMPTY_INT        # 报单总数量
        self.OrderTime = EMPTY_STRING       # 撤单时间
        self.CancelTime = EMPTY_STRING      # 撤单时间
        self.SubmitStatus = EMPTY_INT       # 报单提交状态
        self.Status = EMPTY_INT             # 报单状态


########################################################################
class QVPositionData(QVBaseData):
    """持仓数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVPositionData, self).__init__()

        self.BizCode = EMPTY_INT
        self.UserRef = EMPTY_INT

        # 代码编号相关
        self.InstrumentID = EMPTY_STRING              # 合约代码

        # 持仓相关
        self.PosiDirection = EMPTY_INT                # 持仓方向
        self.Position = EMPTY_INT                     # 持仓量
        self.PositionDate = EMPTY_INT
        self.HedgeFlag = EMPTY_INT



########################################################################
class QVAccountData(QVBaseData):
    """账户数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVAccountData, self).__init__()

        # 账号代码相关
        self.BizCode = EMPTY_INT
        self.UserRef = EMPTY_INT
        self.BrokerID = EMPTY_STRING            # 账户代码
        self.AccountID = EMPTY_STRING           # 账户代码


        # 数值相关
        self.PreBalance = EMPTY_FLOAT           # 昨日账户结算净值
        self.Balance = EMPTY_FLOAT              # 账户净值
        self.Available = EMPTY_FLOAT            # 可用资金
        self.Commission = EMPTY_FLOAT           # 今日手续费
        self.CurrMargin = EMPTY_FLOAT           # 保证金占用
        self.PreMargin = EMPTY_FLOAT            # 保证金占用
        self.CloseProfit = EMPTY_FLOAT          # 平仓盈亏
        self.PositionProfit = EMPTY_FLOAT       # 持仓盈亏


########################################################################
class QVErrorData(QVBaseData):
    """错误数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVErrorData, self).__init__()

        self.UserRef = EMPTY_INT
        self.ErrorID = EMPTY_STRING             # 错误代码
        self.ErrorMsg = EMPTY_STRING            # 错误信息
        self.AdditionalInfo = EMPTY_INT         # 补充信息

        self.ErrorTime = time.strftime('%X', time.localtime())    # 错误生成时间


########################################################################
class QVLogData(QVBaseData):
    """日志数据类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVLogData, self).__init__()

        self.logTime = time.strftime('%X', time.localtime())     # 日志生成时间
        self.logContent = EMPTY_STRING                           # 日志信息


########################################################################
class QVContractData(QVBaseData):
    """合约详细信息类"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        super(QVContractData, self).__init__()
        self.BizCode = EMPTY_INT
        self.UserRef = EMPTY_INT

        self.InstrumentID = EMPTY_STRING              # 代码
        self.ExchangeID = EMPTY_STRING                # 交易所代码

        self.ProductID = EMPTY_STRING                 # 合约类型
        self.Size = EMPTY_INT                         # 合约大小
        self.PriceTick = EMPTY_FLOAT                  # 合约最小价格TICK
        self.DeliveryYear = EMPTY_INT
        self.DeliveryMonth = EMPTY_INT
