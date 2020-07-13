"""
This algorithm uses RSI and FSO as momentum indicators, and it is currently a long-only strategy.

Possible optimizations in the future include using short plays as well as long plays, and optimizing portfolio leverage to balance returns and risk.
"""
import quantopian.algorithm as algo
import quantopian.optimize as opt
from quantopian.pipeline import Pipeline
from quantopian.pipeline.data.builtin import USEquityPricing
from quantopian.pipeline.filters import Q500US
from quantopian.pipeline.factors import SimpleMovingAverage
from quantopian.pipeline.domain import US_EQUITIES
from quantopian.pipeline.factors import RSI
from quantopian.pipeline.factors import FastStochasticOscillator
from quantopian.pipeline.factors import SimpleBeta
from quantopian.pipeline.data import builtin, morningstar as mstar
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.factors.morningstar import MarketCap
from quantopian.pipeline.classifiers.morningstar import Sector

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    set_commission(commission.PerTrade(cost=0)) 
   
    # Rebalance every day, 1 hour after market open.
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

    # Record tracking variables at the end of each day.
    algo.schedule_function(
        record_vars,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

    # Create our dynamic stock selector.
    algo.attach_pipeline(make_pipeline(context), 'pipe')


def make_pipeline(context):
    
    base_universe = Q500US()
    
    rsi_factor = RSI(window_length=5)
    fso_factor = FastStochasticOscillator()
    beta = SimpleBeta(target=sid(8554), regression_length=260)
    

    pipe = Pipeline(
        columns={
            'rsi': rsi_factor,
            'fso': fso_factor,
            'beta': beta
        },
        screen=base_universe & rsi_factor.notnull() & fso_factor.notnull())
   
    context.sma_short= SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=20)  
    pipe.add(context.sma_short, "sma_short")  
    context.sma_long= SimpleMovingAverage(inputs=[USEquityPricing.close], window_length=50)  
    pipe.add(context.sma_long, "sma_long")
    
    return pipe

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.output = algo.pipeline_output('pipe')
    log.info(context.output[:20])
    context.stocks = context.output.index.tolist()


def rebalance(context, data):
    pipeline_data = context.output
    i = 0
    for stock in context.stocks:
        
        if (pipeline_data.sma_short[i] > pipeline_data.sma_long[i] and pipeline_data.rsi[i] < 30
            and pipeline_data.fso[i] < 20):
            # if we don't have open positions then order stock
            if stock not in get_open_orders() and data.can_trade(stock):
                order_target_percent(stock, .01)
            
            
        elif pipeline_data.sma_short[i] < pipeline_data.sma_long[i]:
            # if we have open positions then sell them
            order_target_percent(stock, 0)
            
        i = i + 1
        
    log.info(context.portfolio.positions)
    log.info(context.portfolio.cash)
    log.info(context.account.leverage)
    
    """
    Execute orders according to our schedule_function() timing.
    """
    #if context.sma_short > context.sma_long and context.portfolio.positions_value == 0:  
     
    
    


def record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass


def handle_data(context, data):
    """
    Called every minute.
    """
    pass
