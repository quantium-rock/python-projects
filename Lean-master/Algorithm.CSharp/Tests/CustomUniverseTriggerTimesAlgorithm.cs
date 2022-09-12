

/*
 * QUANTCONNECT.COM - Democratizing Finance, Empowering Individuals.
 * Lean Algorithmic Trading Engine v2.0. Copyright 2014 QuantConnect Corporation.
 * 
 * Licensed under the Apache License, Version 2.0 (the "License"); 
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
 * 
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
*/

using System;
using System.Collections.Generic;
using QuantConnect.Data;
using QuantConnect.Data.Market;
using QuantConnect.Data.UniverseSelection;
using QuantConnect.Securities;

namespace QuantConnect.Algorithm.CSharp
{
    /// <summary>
    /// Basic template algorithm simply initializes the date range and cash
    /// </summary>
    public class CustomUniverseTriggerTimesAlgorithm : QCAlgorithm
    {
        /// <summary>
        /// Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.
        /// </summary>
        public override void Initialize()
        {
            SetStartDate(2013, 10, 07);  //Set Start Date
            SetEndDate(2013, 10, 11);    //Set End Date
            SetCash(100000);             //Set Strategy Cash
            // Find more symbols here: http://quantconnect.com/data
            AddSecurity(SecurityType.Equity, "SPY", Resolution.Second);

            AddUniverse(new PreMarketDailyUsEquityUniverse(UniverseSettings, TimeSpan.FromMinutes(10), dateTime =>
            {
                Debug("Universe selection trigger time: " + dateTime);
                // here's where you can do your custom selection logic, such as call a web service
                return new List<string> { "SPY" };
            }));
        }

        /// <summary>
        /// OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        /// </summary>
        /// <param name="data">Slice object keyed by symbol containing the stock data</param>
        public override void OnData(Slice data)
        {
            if (!Portfolio.Invested)
            {
                SetHoldings("SPY", 1);
                Debug("Purchased Stock");
            }
        }
    }

    /// <summary>
    /// Specifies a universe which fires before us-equity market open each day
    /// </summary>
    public class PreMarketDailyUsEquityUniverse : UserDefinedUniverse
    {
        private readonly TimeSpan _timeBeforeMarketOpen;

        public PreMarketDailyUsEquityUniverse(UniverseSettings universeSettings, TimeSpan timeBeforeMarketOpen, 
            Func<DateTime, IEnumerable<string>> selector)
            : base(CreateConfiguration(), universeSettings, TimeSpan.MaxValue, selector)
        {
            _timeBeforeMarketOpen = timeBeforeMarketOpen;
        }

        // this configuration is used internally, so we'll create a us-equity configuration
        private static SubscriptionDataConfig CreateConfiguration()
        {
            var symbol = Symbol.Create("pre-market-daily-us-equity-universe", SecurityType.Equity, QuantConnect.Market.USA);
            // use us-equity market hours for 'exchange is open' logic
            var marketHoursDbEntry = MarketHoursDatabase.FromDataFolder().GetEntry(QuantConnect.Market.USA, symbol, SecurityType.Equity);
            // this is the time zone the data is in, now in our case, our unvierse doesn't have 'data'
            var dataTimeZone = marketHoursDbEntry.DataTimeZone;
            var exchangeTimeZone = marketHoursDbEntry.ExchangeHours.TimeZone;
            
            return new SubscriptionDataConfig(typeof(Tick), symbol, Resolution.Daily, dataTimeZone, exchangeTimeZone, false, false, true);
        }

        /// <summary>
        /// This funtion is used to determine at what times to fire the selection function
        /// </summary>
        /// <param name="startTimeUtc">The start of the interval (first date in backtest, launch time in live)</param>
        /// <param name="endTimeUtc">The end of the interval (EOD last date in backtest, <see cref="Time.EndOfTime"/> in live</param>
        /// <param name="marketHoursDatabase">A market hours database instance for resolving market hours</param>
        /// <returns>The date time trigger times in UTC</returns>
        public override IEnumerable<DateTime> GetTriggerTimes(DateTime startTimeUtc, DateTime endTimeUtc, 
            MarketHoursDatabase marketHoursDatabase)
        {
            // convert times to local
            var startTimeLocal = startTimeUtc.ConvertFromUtc(TimeZones.NewYork);
            var endTimeLocal = endTimeUtc.ConvertFromUtc(TimeZones.NewYork);

            // get the us-equity market hours
            var exchangeHours = marketHoursDatabase.GetExchangeHours(QuantConnect.Market.USA, null, SecurityType.Equity);

            // loop over each tradeable date in our time frame
            foreach (var tradeableDate in Time.EachTradeableDay(exchangeHours, startTimeLocal, endTimeLocal))
            {
                // get the market open time for this date
                var marketOpen = exchangeHours.GetNextMarketOpen(tradeableDate, false);

                // subtract out how much time before market open we'd like to fire
                yield return marketOpen - _timeBeforeMarketOpen;
            }
        }
    }
}


