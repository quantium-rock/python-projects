using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using QuantConnect.Algorithm.Framework.Alphas;
using QuantConnect.Data.UniverseSelection;

namespace QuantConnect.Algorithm.Framework.Portfolio
{
    public class MyPortfolioConstructionModel : PortfolioConstructionModel
    {
        private List<Symbol> _removedSymbols;
        private readonly InsightCollection _insightCollection;
        private string previous_direction;

        public MyPortfolioConstructionModel()
        {
            _removedSymbols = new List<Symbol>();
            _insightCollection = new InsightCollection();            
        }

        public override IEnumerable<IPortfolioTarget> CreateTargets(QCAlgorithmFramework algorithm, Insight[] insights)
        {
            var targets = new List<PortfolioTarget>();

            if (insights.Length == 0 && _removedSymbols.Count == 0) return targets;

            if (_removedSymbols.Count != 0)
            {
                var universeDeselectionTargets = _removedSymbols.Select(symbol => new PortfolioTarget(symbol, 0));
                targets.AddRange(universeDeselectionTargets);
                _removedSymbols = null;
            }

            _insightCollection.AddRange(insights);

            var expiredInsights = _insightCollection.RemoveExpiredInsights(algorithm.UtcTime);
            var activeInsights = _insightCollection.GetActiveInsights(algorithm.UtcTime);

            foreach (Symbol symbol in algorithm.Securities.Keys)
            {
                if (!_insightCollection.HasActiveInsights(symbol, algorithm.UtcTime)) continue;

                var insight_symbol = activeInsights.Where(insight => insight.Symbol == symbol).ToList();

                if (insight_symbol.Count > 1)
                {
                    bool are_insights_up = insight_symbol.FindAll(x => x.Direction == InsightDirection.Up).Count >= 3;
                    bool are_insights_down = insight_symbol.FindAll(x => x.Direction == InsightDirection.Down).Count >= 3;

                    if (!(are_insights_up || are_insights_down)) continue;                    

                    string side = are_insights_up ? "UP" : "DOWN";

                    if (previous_direction == null) previous_direction = side;
                    else
                    {
                        if (previous_direction == side) continue;
                        else algorithm.Plot(symbol.ToString(), side, algorithm.CurrentSlice.QuoteBars[symbol.ToString()].Close);
                    }
                }
            }

            return targets;
        }

        public override void OnSecuritiesChanged(QCAlgorithmFramework algorithm, SecurityChanges changes)
        {
            _removedSymbols = changes.RemovedSecurities.Select(x => x.Symbol).ToList();
            _insightCollection.Clear(_removedSymbols.ToArray());

            foreach (var added in changes.AddedSecurities)
            {
                algorithm.AddSeries(added.Symbol.ToString(), "UP", SeriesType.Scatter, "$");
                algorithm.AddSeries(added.Symbol.ToString(), "DOWN", SeriesType.Scatter, "$");
            }
        }
    }
}
