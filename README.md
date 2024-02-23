# Recreating the Richard Dennis turtle trading experiment using Python
For this project, I wanted to recreate the famous Turtle Trading experiment done by Richard Dennis in the 1980's. If you are unfamiliar, turtle trading is a trend following trading system designed to catch large price movements on breakouts. It is called "turtle trading" as Richard Dennis went on a trip to singapore, and came back with the idea to "grow traders like they grow turtles in Singapore". He selected a handful of students who became known as turtles. The turtles followed very specific sets of rules that can be found online, although not all sets of rules available seem to be the same. For this project, I mainly used ideas from [https://oxfordstrat.com/coasdfASD32/uploads/2016/01/turtle-rules.pdf)] and [https://www.financialwisdomforum.org/gummy-stuff/turtle-trading.htm]. 

There were two sets of rules the turtles could follow, but I chose to follow just the first set for my experiment. Basically, you enter a trade on a 20 day breakout, and only if the previous 20 day breakout would have resulted in a losing trade. You would then exit the trade if the price broke a 10 day high or low in the opposite direction, or if the trade went "2N" (stop loss) in the opposite direction before an exit symbol. We will get to what "N" means later. However, after some experimentation, I found that exiting after a 20 day high or low was broken was much more profitable. I will show examples for each. The last important thing to mention is how the turtles sized their positions. They used a calculation to get their "Unit" which was 1% of their account value divided by what they called the "Market Dollar Volatility". MDV was calcuated by another turtle term called "N" multiplied by dollars per point. N was just the 20 day ATR, and since this system was designed for futures trading, dollars per point was essentially the contract size. I would recommend reading the Oxfordstrat article I linked if you want to understand this further. However, since I will be using stock data not furtures, we will treat dollars per point as just the stock price. They also had rules for adding to winning positions, which I incorporated into my code, but again, the Oxfordstrat article provides a much clearer description than I briefly could.

# Examples
When running my code, you can get a numpy array of your portfolio value for every day over your backtesting range by calling .get_portfolio_values(). You can then compute the log returns from this array and compare with the returns from some baseline metric. For mine, I chose the DJI. Then, using matplotlib, I visualized the returns for this system if you traded 10 random stocks chosen from the S&P500, assuming you close below a 10 day breakout in the opposite direction of your trade.

<img width="840" alt="Screen Shot 2024-02-23 at 10 59 43 AM" src="https://github.com/gabe-walter/Turtles/assets/113553473/0634c8b9-5332-4cd3-bf66-aff05b363331">

As you can see, this strategy solidly outperformed the buy and hold market strategy, getting about a 605% since 2000. Next, I want to show the strategy with the exit condition being a 20 day breakout instead of 10. You can do this by changing the numbers in the _get_and_prepare_data(self) function if you want to try.

<img width="832" alt="Screen Shot 2024-02-23 at 11 04 43 AM" src="https://github.com/gabe-walter/Turtles/assets/113553473/4ad79e2f-1ec0-400f-a930-3514ce144160">

With the 20 day exit condition, this strategy returned nearly 1350% in 24 years. These are huge numbers. It is definitely important to note, that the 20 day exit condition has much more volatility than the 10 day however. 

The only problem with these current graphs are that they only represent one backtest on 10 random stocks from the S&P500. First of all, the turtles were recommended to trade as many different contracts as they could to catch as many trades as possible. Second, we should probably run this simulation multiple times and get an average total return from all of the trials. 

I'll start with the first part. Using 50 random stocks instead of 10, lets see what the returns look like for a 10 and 20 day exit condition.

20 Day:
<img width="852" alt="Screen Shot 2024-02-23 at 11 11 26 AM" src="https://github.com/gabe-walter/Turtles/assets/113553473/c6310051-b558-4bc0-a1f2-8505ce8966bb">

10 Day:
<img width="837" alt="Screen Shot 2024-02-23 at 11 12 23 AM" src="https://github.com/gabe-walter/Turtles/assets/113553473/bf087127-194b-44d3-a522-54d580d9f973">

Both strategies put up insane numbers. Now, if we run a loop, we can check for the average return for both.
