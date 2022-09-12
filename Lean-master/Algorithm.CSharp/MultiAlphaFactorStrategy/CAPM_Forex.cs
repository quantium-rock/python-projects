
using System;
using System.IO;
using System.Linq;
using System.Text;
using System.Drawing;
using System.Threading.Tasks;
using System.Collections.Generic;

using MathNet.Numerics.Statistics;

using QuantConnect.Brokerages;
using QuantConnect.Data;
using QuantConnect.Orders.Fees;
using QuantConnect.Indicators;

namespace QuantConnect.Algorithm.CSharp.MultiAlphaFactorStrategy
{
    public class CAPM_Forex : QCAlgorithm
    {
        private Dictionary<string, int> powerCurrency;
        private Dictionary<string, RollingWindow<decimal>> queue_closes;

        private decimal cumulative_asset;
        private decimal cumulative_marketIndex;
        private decimal cumulative_base_;
        private decimal cumulative_term_;

        private string asset;
        private string _base;
        private string _term;
        
        private RollingWindow<int> assets_missing;

        private int period_CAPM;
        private Dictionary<string, RollingWindow<double>> queue_CAPM;

        public override void Initialize()
        {
            SetStartDate(2005, 1, 1);
            SetEndDate(2016, 12, 31);
            SetAccountCurrency("EUR");
            SetCash(100000);

            asset = "EURUSD";
            _base = asset.Substring(0, 3);
            _term = asset.Substring(3, 3);

            cumulative_asset = 0;
            cumulative_marketIndex = 0;
            cumulative_base_ = 0;
            cumulative_term_ = 0;

            period_CAPM = 20;
            queue_CAPM = new Dictionary<string, RollingWindow<double>>();
            foreach (string instrument in new string[4] { "MARKET", asset, _base, _term })
            {
                queue_CAPM.Add(instrument, new RollingWindow<double>(period_CAPM));
            }

            queue_closes = new Dictionary<string, RollingWindow<decimal>>();
            assets_missing = new RollingWindow<int>(2);

            // Adding 28 Pairs
            powerCurrency = new Dictionary<string, int>()
            {
                //EUR > GBP > AUD > NZD > USD > CAD > CHF > JPY
                { "EUR", 0 }, { "GBP", 1 }, { "AUD", 2 }, { "NZD", 3 }, { "USD", 4 }, { "CAD", 5 }, { "CHF", 6 }, { "JPY", 7 }
            };
            foreach (string baseCurr in powerCurrency.Keys)
            {
                //Indexs
                queue_closes.Add(baseCurr, new RollingWindow<decimal>(2));

                //28 pairs
                foreach (string termCurr in powerCurrency.Keys)
                {
                    if (powerCurrency[baseCurr] >= powerCurrency[termCurr]) continue;

                    string symbol = baseCurr + termCurr;
                    AddForex(symbol, Resolution.Daily, Market.Oanda, true);
                    Securities[symbol].FeeModel = new FxcmFeeModel();
                    SetBrokerageModel(BrokerageName.FxcmBrokerage, AccountType.Margin);
                    Transactions.MarketOrderFillTimeout = TimeSpan.FromMinutes(15);
                    queue_closes.Add(symbol, new RollingWindow<decimal>(2));
                }
            }

            Plot($"{asset} Return %", asset, cumulative_asset);
            Plot("Market Return %", "MARKET 28 PAIRS", cumulative_marketIndex);
            Plot("Decoupled Index Return %", _base, cumulative_base_);
            Plot("Decoupled Index Return %", _term, cumulative_term_);
        }

        public override void OnData(Slice slice)
        {           
            bool addLastValue = true;
            int number_symb_missing = 0;
            foreach (string index in powerCurrency.Keys)
            {
                //One way of computing the indexs
                decimal index_close = 1m;
                foreach (string symb in Securities.Keys.Select(x => x.ToString()))
                {
                    if (!slice.QuoteBars.ContainsKey(symb))
                    {
                        number_symb_missing++;
                        continue;
                    }

                    if (addLastValue) queue_closes[symb].Add(slice.QuoteBars[symb].Close);

                    if (symb.Substring(0, 3) == index) index_close += 1m / slice.QuoteBars[symb].Close;
                    else if (symb.Substring(3, 3) == index) index_close += slice.QuoteBars[symb].Close;
                }

                addLastValue = false;
                index_close = 1m / (index_close / Securities.Count);
                queue_closes[index].Add(index_close);
            }

            assets_missing.Add(number_symb_missing);
            if (!queue_closes.All(x => x.Value.IsReady) || assets_missing.Any(x => x != 0)) return;

            decimal return_market = 0;
            decimal return_base = 0;
            decimal return_term = 0;
            foreach (string symbol in Securities.Keys.Select(x => x.ToString()))
            {
                //Another way of computing the indexs
                decimal return_ = LogReturn(queue_closes[symbol][1], queue_closes[symbol][0]);

                return_market += return_;

                if (symbol.Substring(0, 3) == _base) return_base += return_;
                else if (symbol.Substring(3, 3) == _base) return_base -= return_;

                if (symbol.Substring(0, 3) == _term) return_term += return_;
                else if (symbol.Substring(3, 3) == _term) return_term -= return_;
            }

            cumulative_marketIndex += return_market;
            cumulative_base_ += return_base;
            cumulative_term_ += return_term;

            Plot("Market Return %", "MARKET 28 PAIRS", cumulative_marketIndex);
            Plot("Decoupled Index Return %", _base, cumulative_base_);
            Plot("Decoupled Index Return %", _term, cumulative_term_);

            if (!slice.QuoteBars.ContainsKey(Symbol(asset))) return;

            decimal return_asset = LogReturn(queue_closes[asset][1], queue_closes[asset][0]);            
            cumulative_asset += return_asset;
            Plot($"{asset} Return %", asset, cumulative_asset);

            queue_CAPM[asset].Add((double)return_asset);
            queue_CAPM["MARKET"].Add((double)return_market);
            queue_CAPM[_base].Add((double)return_base);
            queue_CAPM[_term].Add((double)return_term);

            if (!queue_CAPM[asset].IsReady) return;

            var capm_asset = CAPM(queue_CAPM[asset].ToArray(), queue_CAPM["MARKET"].ToArray());
            Plot("CAPM ASSET", $"Beta_{asset}", capm_asset.Item2);

            var capm_base = CAPM(queue_CAPM[_base].ToArray(), queue_CAPM["MARKET"].ToArray());
            Plot("CAPM Decoupled indexs", $"Beta_{_base}", capm_base.Item2);

            var capm_term = CAPM(queue_CAPM[_term].ToArray(), queue_CAPM["MARKET"].ToArray());
            Plot("CAPM Decoupled indexs", $"Beta_{_term}", capm_term.Item2);
        }

        public decimal LogReturn(decimal prev_value, decimal current_value)
        {
            return (decimal)Math.Log((double)current_value / (double)prev_value);
        }

        public Tuple<double, double> CAPM(double[] returnsAsset, double[] returnsMarket,
            double riskFreeRate = 0)
        {
            //E[ReturnAsset] = RiskFreeRate + Beta * (E[MarketReturn] - RiskFreeRate) + trackingError
            double corr_pears = Correlation.Pearson(returnsAsset, returnsMarket);
            double std_asset = new DescriptiveStatistics(returnsAsset).StandardDeviation;
            double std_market = new DescriptiveStatistics(returnsMarket).StandardDeviation;
            double beta = corr_pears * (std_asset / std_market); //correlated relative volatility
            double trackingError = returnsAsset.Zip(returnsMarket,
                (ret1, ret2) => (ret1 - riskFreeRate) - beta * (ret2 - riskFreeRate)).Mean();

            return Tuple.Create(trackingError, beta);
        }
    }
}
