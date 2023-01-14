<style>
div {
    margin-bottom: 20px;
}
.tag {
    padding: 5px;
    border-radius: 5px;
    color: white;
    font-size: 12px;
}
.red {
    background-color: #ff3300;
}
.blue {
    background-color: #0099ff;
}
</style>

## Possible indicators
### RSI (Relative Strength Index)
<div>
    <span class="tag red">Momentum oscillator</span>
    <span class="tag blue">Combine</span>
</div>


RSI measures the speed and magnitude of a price change to evaluate overvalued or undervalued conditions in the price of that asset. The RSI is displayed as an oscillator (a line graph that moves between two extremes) and can have a reading from 0 to 100. 
The RSI is considered:
- Over<b>bought</b> when above 70 
- Over<b>sold</b> when below 30.

It can also indicate assets that may be primed for a trend reversal or corrective pullback in price. It can signal when to buy or sell an asset.

- Provices signals about bullish or bearish price momentum, often plotted beneath the graph of an asset's price.
- The RSI line crossing  below the overbought line or above the oversold line can be used as a signal to buy or sell an asset.
- RSI works best in trading ranges rather than trending markets.

#### How it works
As a momentum indicator, the relative strength index compares an assets strength on days when prices go up to its strength on days when prices go down. Relating the result of this comparison to price action can give traders an idea of how an asset may perform. The RSI, used in conjuction with other thenical indicators, can help traders make better-informed trading decisions.

#### Calculating the RSI
RSI uses a two-part calculation that starts with the following formula:
```math
RSI_{step one} = 100 - \ {\frac{100}{ 1 + \frac{average gain}{average loss}}}
```

The average gain and loss in this calculation is tha average percentage gain or loss during a look-back period. The formula uses a positive value for the average loss. Periods with price increases are counted as zero in the calculations of average loss.
The standard number of periods to calculate the initial RSI value is 14. For example, imagine the market closed higher sever out of the past 14 days with an average gain of 1%. The remaining seven days all closed lower with an average loss of -0.8%. The RSI would be calculated as follows:
```math

```

#### Risks
Fully relying on RSI would not be good since it doesn'ta take econimic news, earnings and fundamental data into account. It is a good idea to combine it with other indicators. Additionally, RSI can remain overbought or oversold for long periods of time. Usually paired with volume and the overall trend of the asset.


#### RSI Example


### Accumulation/Distribution indicator
<div>
    <span class="tag red">Oscilator</span>
    <span class="tag blue">Combine</span>
</div>

#### How it works
The A/D indicator is a volume-measurement tool that assesses the cumulative inflow and outflow of money of a given asset. It measures price and colume of tha asset for ascertain wether iti is being accumulated or distributed. It provides insight on the strength of the current trend and can be used to identify potential reversals. If the A/D line is rising, it indicates that the asset is being accumulated. If the A/D line is falling, it indicates that the asset is being distributed. Having a rising asset but a falling A/D line indicates that the asset is being distributed at a faster rate than it is being accumulated. This can be a sign of a potential reversal. It looks at the relation between the value and the volume of the asset. Accumulations refers to the buying level fot that security given a specific period.
Distributuions refers to the selling level for that security given a specific period.

```math
Money Flow Multiplier = \frac{(Close - Low) - (High - Close)}{High - Low}
```

```math
Money Flow Volume = Money Flow Multiplier \times Volume
```

```math
Accumulation/Distribution = \sum_{i=1}^{n} Money Flow Volume
```

### Average True Range

#### How it works
Measure volatility in terms of pips or movements in price.
Rising ATR means the volatility is increasing. Whilst the falling ATR means the volatility is decreasing. Can be used to know when to exit a trade. If you enter a long buying period and the ATR is rising, you can expect the price to rise more. If you enter a short selling period and the ATR is rising, you can expect the price to fall more. If you enter a long buying period and the ATR is falling, you can expect the price to rise less. If you enter a short selling period and the ATR is falling, you can expect the price to fall less.

This is a subjective measure, meaning that it is open to interpretation. There is no single ATR value that will tell you with any certainty that a trend is about to reverse or not. Instead, ATR eadings should always be compared against earlier readings to get a feel of a trend’s strength or weakness.

#### Formula
```math
TR = max[(High - Low), Abs(High - Close_{previous}), Abs(Low - Close_{previous})]
```

```math
ATR = (\frac{1}{n}) \sum_{i=1}^{n} TR_{i}
```


### Bollinger Bands

#### How it works
It is used as an indicator to measure volatility and can also be used to measure if an asset is overbought or oversold. To see if the asset value is oversold or overbought, you can compare the current price to the upper and lower bands. If the price is above the upper band, it is considered overbought. If the price is below the lower band, it is considered oversold. The bands can also be used to identify potential reversals. If the price is above the upper band and the price starts to fall, it can be a sign of a potential reversal. If the price is below the lower band and the price starts to rise, it can be a sign of a potential reversal.

Roughly 90% of the asset price actions occur between the two bands. Any breakout above or below the bands can be considered a major event. The breakout is not a trading signal. Breakouts provice no clue as to the direction and extend of future price movement.

#### Formula
```math
Typical Price = \frac{High + Low + Close}{3}
```

```math
Upper BollingerBand = Moving Average(Typical Price, periods) + m * Standard Deviation(Typical Price, periods)
```

```math
Lower BollingerBand = Moving Average(Typical Price, periods) - m * Standard Deviation(Typical Price, periods)
```


### Moving Average Convergence Divergence (MACD)


#### How it works
MACD is a trend-following momentum indicator that shows the relationship between the two moving averages of a security's price. The MACD is calculated by subtracting th 26-period exponential moving average (EMA) from the 12-period EMA, these periods can be adjusted but these are the commonly used values.

An exponential moving average (EMA) is a type of moving average (MA) that places a greater weight and significance on the most recent data points.

MACD is a lagging indicator. After all, all the data used in MACD is based on the historical price action of the stock. Since it is based on historical data, it must necessarily "lag" in price. However, some traders use MACD histograms to predict when a change in trend will occur. For these traders, this aspect of the MACD might be viewed as a leading indicator for future trend changes.

#### Formula
```math
MACD = EMA_{12} - EMA_{26}
```



### Money Flow Index (MFI)

#### How it works
It is a technical indicator that generates overbought or oversold signals. It incorporates both price and volume data, as opposed to just price. For this reason, some analysts call MFI the volume-weighted RSI.

An MSI reading abond 80 is considered overbought and and MFI reading below 20 is considered oversold, although levels of 90 and 10 are also often used as thresholds.

A divergence between the indicator and price is noteworthy. For example, if the indicator is rising while the price is falling or flat. The price could start rising.

#### Formula
```math
Money Flow Index = 100 - \frac{100}{1 + Money Flow Ratio}
```
```math
Money Flow Ratio = \frac{14 Period Positive Money Flow}{14 Period Negative Money Flow}
```
```math
Raw Money Flow = Typical Price \times Volume
```
```math
Typical Price = \frac{High + Low + Close}{3}
```

### Parabolic SAR indicator

#### How it works
The Parabolic SAR indicator, is used by traders to determine trend direction and portential reversal price. The indicator uses a trailing stop and reverse method called Stop And Reverse (SAR), to identify suitable exit and entry points. Traders also refer to the indicator as the parabolic stop and reverse, parabolic SAR, or PSAR.

The PSAR indicator appears on a chart as a series of dots, either above or below and asset's price, depending on the direction the price is moving. A dot is placed below the price when it is trending upward, and above the price when it is trending downward.

- Used to spot trend and potential reversals
- Utilizes a system of dots superimposed onto a price chart
- A reversal occurs when these dots flip, but a reversal signal in the SAR does not necessarily mean a reversal in the price. A PSAR only means that the price and indicator have crossed.

#### Formula
```math
RisingPSAR = PSAR_{previous} + AF
```
```math
FallingPSAR = PSAR_{previous} - AF
```
##### Where 
- AF = Acceleration Factor (starts with 0.02 and increases by 0.02 each time the SAR changes direction, up to a maximum of 0.2)
- EP = Extreme Point (the highest high for a long position, or the lowest low for a short position)


### Tripple Exponential Moving Average (TEMA)


#### How it works
The TEMA was designed to smooth price fluctuations, thereby making it easier to identify trends without the lag associated with traditional moving averages. It does this by taking multiple EMAs of the original EMA and subtracting out some of the lag.
The TEMA is used like other MAs. It can help identify trend direction, signal potential short-term trend changes or pullbacks, and provice support or resistance. The TEMA can be compared to the double exponential moving average (DEMA).

#### Formula
```math
TEMA = (3 * EMA_{1}) - (3 * EMA_{2}) + EMA_{3}
```
##### Where
- EMA_{1} = Exponential Moving Average of the price
- EMA_{2} = Exponential Moving Average of EMA_{1}
- EMAS_{3} = Exponential Moving Average of EMA_{2}

