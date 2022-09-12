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

namespace QuantConnect.Algorithm.CSharp.Tests
{
    public class PairCommodityTrading : QCAlgorithm
    {
        private string symbol1, symbol2;
        private Dictionary<string,RollingWindow<QuoteBar>> queues;
        private decimal size;

        #region Helper Functions

        public decimal Return(RollingWindow<QuoteBar> roll_window)
        {
            return (roll_window[0].Close / roll_window[1].Close) - 1;
        }

        #endregion

        public override void Initialize()
        {
            symbol1 = "XAUUSD";
            symbol2 = "XAGUSD";
            size = 10000m;
            queues = new Dictionary<string, RollingWindow<QuoteBar>>();

            decimal comission = (0.0025m / 100m) * size; //0.005% Ida y Vuelta

            SetStartDate(2006, 03, 20);
            SetEndDate(2019, 01, 17);

            SetAccountCurrency("USD");
            SetCash("USD", 100000);

            foreach (string symb in new string[2] { symbol1, symbol2 })
            {
                AddCfd(symb, Resolution.Daily, Market.Oanda, true);
                Securities[symb].FeeModel = new ConstantFeeModel(comission);
                queues.Add(symb, new RollingWindow<QuoteBar>(2));

                

                //Friday before market close, close positions 10 minutes before
                Schedule.On(DateRules.WeekEnd(symb), TimeRules.BeforeMarketClose(symb, 10), () =>
                {
                    foreach (var holding in Portfolio.Values)
                    {
                        if (holding.HoldingsValue != 0m)
                        {
                            MarketOrder(holding.Symbol, -holding.Quantity, false, "LIQUIDATE " + Time.DayOfWeek);
                        }
                    }
                });
            }

            Transactions.MarketOrderFillTimeout = TimeSpan.FromMinutes(15);
        }

        public override void OnData(Slice slice)
        {
            DayOfWeek weekDay = Time.DayOfWeek;
            DayOfWeek nextDay = weekDay != DayOfWeek.Sunday ? Time.DayOfWeek + 1 : DayOfWeek.Monday;

            foreach (string symb in Securities.Keys)
            {
                queues[symb].Add(slice.QuoteBars[symb]);
            }

            if (!queues[symbol1].IsReady) return;

            decimal diff = Return(queues[symbol2]) - Return(queues[symbol1]);

            Plot("Difference Chart", "Diff", diff);

            if (weekDay == DayOfWeek.Friday || weekDay == DayOfWeek.Sunday) return;

            foreach (var holding in Portfolio.Values)
            {
                if (holding.HoldingsValue != 0m)
                {
                    MarketOrder(holding.Symbol, -holding.Quantity, false, "LIQUIDATE " + weekDay);
                }
            }

            //Open a position on MarketClose Monday (Tuesday); Tuesday (Wednesday); Wednesday (Thursday); Thursday (Friday)
            if (Math.Abs(diff) > 0.005m)
            {
                if (diff > 0)
                {
                    MarketOrder(symbol2, -size / slice.QuoteBars[symbol2].Bid.Close, false, "OPEN " + nextDay);
                    MarketOrder(symbol1, size / slice.QuoteBars[symbol1].Ask.Close, false, "OPEN " + nextDay);
                }
                else
                {
                    MarketOrder(symbol2, size / slice.QuoteBars[symbol2].Ask.Close, false, "OPEN " + nextDay);
                    MarketOrder(symbol1, -size / slice.QuoteBars[symbol1].Bid.Close, false, "OPEN " + nextDay);
                }
            }
        }        
    }
}
