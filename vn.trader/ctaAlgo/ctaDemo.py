# encoding: UTF-8

"""
这里的Demo是一个最简单的策略实现，并未考虑太多实盘中的交易细节，如：
1. 委托价格超出涨跌停价导致的委托失败
2. 委托未成交，需要撤单后重新委托
3. 断网后恢复交易状态
4. 等等
这些点是作者选择特意忽略不去实现，因此想实盘的朋友请自己多多研究CTA交易的一些细节，
做到了然于胸后再去交易，对自己的money和时间负责。
也希望社区能做出一个解决了以上潜在风险的Demo出来。
"""


from ctaBase import *
from ctaTemplate import CtaTemplate


########################################################################
class CAAlpha(CtaTemplate):
    """CAAlpha策略Demo"""
    '''
    测试策略: 追涨杀跌
    '''
    """
    基于tick级别粒度生成变长K线range bar，思路如下：
    1 - 大趋势：识别市场状态（单边/震荡）
    2 - 变长range bar: 
        变长bar固定O-C价格差（非H-L价格差），带单影线的K线，O或者C等于H或L，且影线不产生新一根bar（双方向还可以不一致，具体需要研究变长bar生成策略）
        单边 短，震荡 长：这样单边情况下生成的bar数量更多，震荡下少，bar越多则交易机会越多
        为了一致性，整点时间时产生自然截断，生成新的bar
    3 - 交易算法

    00- PCNN识别趋势状态，识别bar长度
        买卖信号
        日内交易策略
    """
    className = 'CAAlpha'
    author = u'by-hurenqiang'
    
    # 策略参数
    initDays = 10   # 初始化数据所用的天数
    
    # 策略变量
    bar = None
    barMinute = EMPTY_STRING
    
    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'fastK',
                 'slowK']    
    
    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos',
               'fastMa0',
               'fastMa1',
               'slowMa0',
               'slowMa1']  

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(CAAlpha, self).__init__(ctaEngine, setting)
        self.ticks = [] # 存储tick级别的数据
        self.bars = []
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略初始化')
        
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)
        
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        # 计算K线
        self.ticks.insert(0, tick)
        # 只使用最新的数据
        if len(self.ticks) > 20:
            self.ticks = self.ticks[:20]

        '''
        if crossOver:
            if self.pos == 0:
                self.buy(bar.close, 1)
            elif self.pos < 0:
                self.cover(bar.close, 1)
                self.buy(bar.close, 1)
        elif crossBelow:
            if self.pos == 0:
                self.short(bar.close, 1)
            elif self.pos > 0:
                self.sell(bar.close, 1)
                self.short(bar.close, 1)
        '''
        # 发出状态更新事件
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
        self.bars.insert(0, bar)
        if len(self.bars) > 100:
            self.bars = self.bars[0:100]
            
        ma5 = 0
        if len(self.bars) < 100:
            return
        for data in self.bars[0:30]:
            ma5 += data.close
        
        ma10 = 0
        for data in self.bars[0:60]:
            ma10 += data.close
            
        ma5 = ma5/30
        ma10= ma10/60
        crossOver = False
        crossBelow = False
        if ma5 > ma10:
            crossOver = True
        else:
            crossBelow = True
        if crossOver:
            if self.pos == 0:
                self.buy(bar.close, 1)
            elif self.pos < 0:
                self.cover(bar.close, 1)
                self.buy(bar.close, 1)
        elif crossBelow:
            if self.pos == 0:
                self.short(bar.close, 1)
            elif self.pos > 0:
                self.sell(bar.close, 1)
                self.short(bar.close, 1)
        pass
        
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
    
########################################################################################
## 基于tick级别细粒度撤单追单测试demo

class OrderManagementDemo(CtaTemplate):
    """追撤单策略Demo"""
    className = 'OrderManagementDemo'
    author = u'用Python的交易员'
    
    # 策略参数

    initDays = 10   # 初始化数据所用的天数
    
    # 策略变量
    bar = None
    barMinute = EMPTY_STRING
    
    
    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol']
    
    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(OrderManagementDemo, self).__init__(ctaEngine, setting)
		
	self.lastOrder = None
        self.orderType = ''
	
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略初始化')
        
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)
        
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略启动')
        self.putEvent()
    
    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'双EMA演示策略停止')
        self.putEvent()
        
    #----------------------------------------------------------------------
    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""

	# 建立不成交买单测试单	
	if self.lastOrder == None:
	    self.buy(tick.lastprice - 10.0, 1)

	# CTA委托类型映射
        if self.lastOrder != None and self.lastOrder.direction == u'多' and self.lastOrder.offset == u'开仓':
            self.orderType = u'买开'

        elif self.lastOrder != None and self.lastOrder.direction == u'多' and self.lastOrder.offset == u'平仓':
            self.orderType = u'买平'

        elif self.lastOrder != None and self.lastOrder.direction == u'空' and self.lastOrder.offset == u'开仓':
            self.orderType = u'卖开'

        elif self.lastOrder != None and self.lastOrder.direction == u'空' and self.lastOrder.offset == u'平仓':
            self.orderType = u'卖平'
		
	# 不成交，即撤单，并追单
        if self.lastOrder != None and self.lastOrder.status == u'未成交':

            self.cancelOrder(self.lastOrder.vtOrderID)
            self.lastOrder = None
        elif self.lastOrder != None and self.lastOrder.status == u'已撤销':
	# 追单并设置为不能成交
            
            self.sendOrder(self.orderType, self.tick.lastprice - 10, 1)
            self.lastOrder = None
    #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""
	pass
    
    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        self.lastOrder = order
    
    #----------------------------------------------------------------------
    def onTrade(self, trade):
        """收到成交推送（必须由用户继承实现）"""
        # 对于无需做细粒度委托控制的策略，可以忽略onOrder
        pass
    
