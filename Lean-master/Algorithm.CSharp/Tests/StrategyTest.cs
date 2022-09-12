using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using QuantConnect;
using QuantConnect.Data.Market;
using QuantConnect.Securities;
using QuantConnect.Indicators;
using QuantConnect.Data;
using QuantConnect.Algorithm;
using QuantConnect.Data.Consolidators;
using QuantConnect.Brokerages;
using QuantConnect.Data.Custom.Intrinio;
using QuantConnect.Data.Custom;
using QuantConnect.Data.Custom.Tiingo;
using QuantConnect.Orders;
using QuantConnect.Data.UniverseSelection;
using QuantConnect.Orders.Fees;
using QuantConnect.Orders.Slippage;
using System.Collections;
using QuantConnect.Orders.Fills;

using QuantConnect.Algorithm.Framework.Selection;
using QuantConnect.Algorithm.Framework.Alphas;
using QuantConnect.Algorithm.Framework.Portfolio;
using QuantConnect.Algorithm.Framework.Risk;
using QuantConnect.Algorithm.Framework.Execution;

namespace QuantConnect.Algorithm.CSharp
{
    public class StrategyTest : QCAlgorithm
    {
        public decimal size;
        public string symbol;
        private Chart assetPlot;
        private Series asset;

        public override void Initialize()
        {
            symbol = "AAPL";

            SetStartDate(2002, 11, 06);
            SetEndDate(2019, 01, 17);

            if (!LiveMode)
            {
                SetAccountCurrency("USD");
                SetCash(100000);
                SetSecurityInitializer(x => x.SetDataNormalizationMode(DataNormalizationMode.Raw));
                AddEquity(symbol, Resolution.Daily, Market.USA);
                //Securities[symbol].FeeModel = new FxcmFeeModel();
                //SetBrokerageModel(BrokerageName.FxcmBrokerage, AccountType.Margin);
                //Transactions.MarketOrderFillTimeout = TimeSpan.FromMinutes(15);
                //size = 10000 * Securities[symbol].SymbolProperties.LotSize; //Minimum lot size

                

                var y = Securities[symbol].Subscriptions;

                
            }
            else
            {
                Log("Live Trading");
                AddForex(symbol, Resolution.Minute, Market.Oanda);
                Liquidate();
                size = 1 * Securities[symbol].SymbolProperties.LotSize; //Minimum lot size

            }

            //assetPlot = new Chart("Asset Plot");
            //asset = new Series(symbol, SeriesType.Candle);
            //assetPlot.AddSeries(asset);
            //AddChart(assetPlot);
        }

        public override void OnData(Slice slice)
        {
            if (LiveMode)
            {
                SetRuntimeStatistic(symbol, slice.QuoteBars[symbol].Close);
                Log($"Time: {Time}, Open: {slice.QuoteBars[symbol].Open}, High: {slice.QuoteBars[symbol].High}, " +
                    $"Low: {slice.QuoteBars[symbol].Low}, Close: {slice.QuoteBars[symbol].Close}");
            }

            if (!slice.Bars.ContainsKey(symbol)) return;

            Plot("AAPL", "Close", slice.Bars[symbol].Close);

            /*
             *asset.AddPoint(Time, slice.QuoteBars[symbol].Close); 
             *
            DateTime currentTime = Time;
            DateTime candleTime = slice.Time;

            decimal currentClose = slice.QuoteBars[symbol].Bid.Close;
            decimal currentOpen = slice.QuoteBars[symbol].Bid.Open;

            DayOfWeek weekDay = Time.DayOfWeek;
            DayOfWeek nextWeekDay = weekDay + 1;

            var filledOrders = Transactions.GetOrders(x => x.Status == OrderStatus.Filled).ToList();
            bool isFlat =  filledOrders.Count != 0 ? filledOrders.Sum(x => x.Quantity) == 0 : true;

            
            if (!Securities[symbol].Exchange.ExchangeOpen) return;

            if (weekDay == DayOfWeek.Sunday && isFlat)
            {
                OrderTicket open = MarketOrder(symbol, size, false, "OPEN " + nextWeekDay);
                //Log(open.Tag);
            }

            if (weekDay <= DayOfWeek.Thursday && isFlat) //End of Monday, Tuesday, Wednesday = Initial of Tuesday, Wednesday and Thursday
            {
                OrderTicket open = MarketOrder(symbol, size, false, "OPEN " + nextWeekDay);
                //Log(open.Tag);
            }

            else if (!isFlat && weekDay < DayOfWeek.Friday)
            {
                if (weekDay == DayOfWeek.Thursday) //End Of Thursday = Initial of Friday
                {
                    OrderTicket close = MarketOrder(symbol, -size, false, "CLOSE " + weekDay);
                    //Log(close.Tag);
                }

                else
                {
                    OrderTicket close = MarketOrder(symbol, -size, false, "CLOSE " + weekDay);
                    //Log(close.Tag);
                    OrderTicket open = MarketOrder(symbol, size, false, "OPEN " + nextWeekDay);
                    //Log(open.Tag);
                }
            }
            */
        }

        public override void OnEndOfDay()
        {
            DateTime time = Time;
        }        

        public override void OnOrderEvent(OrderEvent orderEvent)
        {
            if (orderEvent.Status == OrderStatus.Submitted)
            {
                
            }

            if (orderEvent.Status == OrderStatus.Filled)
            {
                //Log(orderEvent.OrderFee);
            }
        }        
    }
}
