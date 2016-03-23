修改AnalyticPortfolio.java中的updatePositions()的功能以适应股票+期货同时工作：

目标：
-   更新positions列表{security:list<position>} 已经完全平仓的需要移除
    新开仓的头寸在这里才实际生成
-   更新持仓价值：
       持股的市值 + 期货未了结的收益情况 currentPositionValue
       现金 currentCash:
            初始化后便只在processTrading中增或者间
       冻结资金：期货保证金 + 股票(日间未生成仓位时冻结)
       reservedCash: 
            对于股票：在placeOrder时会冻结order所需要的资金
                     在cancelOrder时会取消相应order的冻结资金
                     在processTrading时会取消order成功交易的冻结资金: 
                     在overNight时取消未执行order的冻结资金
                     在processSettlement中执行期货的隔夜持仓结算(保证金+-会造成currentCash的变化)
-   更新持仓时间
-   更新了结盈亏，浮动盈亏
-   维护开仓与平仓历史记录
-   维护高点与最大回撤

注意：
-   多空双方向
-   既有持仓的要考虑是平仓还是同方向开仓还是相反方向开仓？
-   对于股票 PRCA：
-   avgPrice: 指定价格 + 滑点价格 
    charge: avgPrice*filledAmount + 交易成本
    initialMargin: 0

    对于期货PRCFutures:
    executeOrder时如果平仓会检查是否有反向持仓但不进行仓位检验
    filledVolume为   执行的交易量(以手为单位)
    orderAmount为    订单表面价值
    avgPrice: 指定价格，为点数，即标价（如IF2900点，就是2900的价格，但实际的一手价值不一定）
    charge: avgPrice*filledAmount + 交易成本
    initialMargin: 冻结金额

    先计算点数对应的价格，实际价值*保证金比例 为实际开仓使用的保证金
    estimateOverallCostRate: 交易费用百分百比例(实际持仓价值, 非保证金)
    estimateOpeningExpense:  估算开仓费用（保证金 + 交易费）
processTrading:
    注意对于期货需要根据交易类型，对保证金的（冻结金额的计算）有区别
    开仓时增加保证金、平仓时释放保证金

-   OrderExec中
    avgPrice: 交易所标价
    filledVolume: 以交易说最小单位为准，股票为 股， 期货为 手
    charge: 从current中扣除的金额(股票中 为 市值+交易费， 期货中只包含交易费)
    initialMargin: 冻结金额 (股票为0，期货为保证金)