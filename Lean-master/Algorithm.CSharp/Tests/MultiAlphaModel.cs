
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

using QuantConnect.Data;
using QuantConnect.Algorithm.Framework;
using QuantConnect.Algorithm.Framework.Selection;
using QuantConnect.Algorithm.Framework.Alphas;
using QuantConnect.Algorithm.Framework.Portfolio;
using QuantConnect.Algorithm.Framework.Execution;
using QuantConnect.Algorithm.Framework.Risk;
using System.Drawing;

namespace QuantConnect.Algorithm.CSharp.Tests
{
    public class MultiAlphaModel : QCAlgorithmFramework
    {
        Dictionary<string, Series> series = new Dictionary<string, Series>();

        public override void Initialize()
        {
            List<Symbol> symbols = new List<Symbol>();
            foreach (string symb in new string[1] { "EURUSD" })
            {
                Symbol s = AddForex(symb, Resolution.Daily, Market.Oanda).Symbol;
                symbols.Add(s);

                Chart chart = new Chart(symb);
                Series serie_price = new Series("Candle Close", SeriesType.Candle, 0);
                chart.AddSeries(serie_price);

                Series serie_ema_fast = new Series("EMA Fast", SeriesType.Line, 0);
                chart.AddSeries(serie_ema_fast);
                Series serie_ema_low = new Series("EMA Low", SeriesType.Line, 0);
                chart.AddSeries(serie_ema_low);
                Series serie_macd = new Series("MACD", SeriesType.Line, 1);
                chart.AddSeries(serie_macd);
                Series serie_rsi = new Series("RSI", SeriesType.Line, 2);
                chart.AddSeries(serie_rsi);

                AddChart(chart);

                series.Add(symb, serie_price);
            }

            SetStartDate(2009, 6, 1);
            SetEndDate(2017, 12, 31);
            SetCash(100000);

            SetUniverseSelection(new ManualUniverseSelectionModel(symbols));

            SetAlpha(new CompositeAlphaModel(
                new EmaCrossAlphaModel(10, 20),
                new RsiAlphaModel(),
                new MacdAlphaModel(),
                new HistoricalReturnsAlphaModel(20)
                ));

            SetPortfolioConstruction(new MyPortfolioConstructionModel());

            SetExecution(new NullExecutionModel());

            SetRiskManagement(new NullRiskManagementModel());
        }

        public override void OnData(Slice slice)
        {
            foreach (Symbol symb in Securities.Keys)
            {
                series[symb.ToString()].AddPoint(Time, slice.QuoteBars[symb.ToString()].Close);
            }
        }
    }
}
