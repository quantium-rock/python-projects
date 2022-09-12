using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Threading.Tasks;

using MathNet.Numerics.Statistics;

using QuantConnect.Brokerages;
using QuantConnect.Data;
using QuantConnect.Orders.Fees;
using QuantConnect.Indicators;

namespace QuantConnect.Algorithm.CSharp.MultiAlphaFactorStrategy
{
    class CAPM_Equities : QCAlgorithm
    {
        private Dictionary<string, RollingWindow<decimal>> queue_closes;
        private string asset;
        private string industry;
        private string market;

        private decimal cumulative_asset;
        private decimal cumulative_industry;
        private decimal cumulative_market;

        private int period_CAPM;
        private Dictionary<string, RollingWindow<double>> queue_CAPM;

        public override void Initialize()
        {
            SetStartDate(2004, 8, 12);
            SetEndDate(2016, 12, 31);
            SetCash(100000);

            cumulative_asset = 0;
            cumulative_industry = 0;
            cumulative_market = 0;

            asset = "WLK";
            industry = "Chemicals";

            market = "SPY";
            AddEquity(market, Resolution.Daily, Market.USA, true);

            string path_sector = Path.Combine(Globals.DataFolder, SecurityType.Equity.ToLower(), 
                Market.USA, "sectors_industry", "industries", industry + ".csv");
            string path_equities = Path.Combine(Globals.DataFolder, SecurityType.Equity.ToLower(),
                Market.USA, Resolution.Daily.ToLower());

            queue_closes = new Dictionary<string, RollingWindow<decimal>>();
            queue_closes.Add(market, new RollingWindow<decimal>(2));
            string[] lines = File.ReadAllLines(path_sector);
            foreach (string line in lines)
            {
                string ticker = line.Split(',')[0];
                if (!File.Exists(Path.Combine(path_equities, ticker + ".zip"))) continue;

                AddEquity(ticker, Resolution.Daily, Market.USA, true);
                queue_closes.Add(ticker, new RollingWindow<decimal>(2));
            }

            Plot($"Return %", asset, cumulative_asset);
            Plot($"Return %", industry, cumulative_industry);
            Plot($"Return %", market, cumulative_market);

            period_CAPM = 20;
            queue_CAPM = new Dictionary<string, RollingWindow<double>>();
            foreach (string instrument in new string[3] { asset,industry,market })
            {
                queue_CAPM.Add(instrument, new RollingWindow<double>(period_CAPM));
            }
        }

        public override void OnData(Slice slice)
        {
            foreach (string symb in Securities.Keys.Select(x => x.ToString()))
            {
                if (!slice.Bars.ContainsKey(Symbol(symb))) continue;

                queue_closes[symb].Add(slice.Bars[symb].Close);
            }

            decimal return_industry = 0;

            decimal count = 0m;
            foreach (KeyValuePair<string, RollingWindow<decimal>> symb in queue_closes.Where(x => x.Value.IsReady))
            {
                if (symb.Key == market || symb.Key == asset) continue;

                decimal return_ = LogReturn(queue_closes[symb.Key][1], queue_closes[symb.Key][0]);
                return_industry += return_;
                count++;
            }

            if (count == 0) return;

            cumulative_industry += return_industry / count;
            Plot($"Return %", industry, cumulative_industry);

            if (!slice.Bars.ContainsKey(Symbol(market)) || !queue_closes[market].IsReady) return;

            decimal return_market = LogReturn(queue_closes[market][1], queue_closes[market][0]);
            cumulative_market += return_market;
            Plot($"Return %", market, cumulative_market);

            if (!slice.Bars.ContainsKey(Symbol(asset)) || !queue_closes[asset].IsReady) return;

            decimal return_asset = LogReturn(queue_closes[asset][1], queue_closes[asset][0]);
            cumulative_asset += return_asset;
            Plot($"Return %", asset, cumulative_asset);

            queue_CAPM[asset].Add((double)return_asset);
            queue_CAPM[industry].Add((double)return_industry);
            queue_CAPM[market].Add((double)return_market);

            if (!queue_CAPM[asset].IsReady) return;

            var capm_asset = CAPM(queue_CAPM[asset].ToArray(), queue_CAPM[market].ToArray());
            Plot($"CAPM {asset}", $"Beta_{asset}", capm_asset.Item2);

            var capm_industry = CAPM(queue_CAPM[industry].ToArray(), queue_CAPM[market].ToArray());
            Plot($"CAPM {industry}", $"Beta_{industry}", capm_industry.Item2);
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
