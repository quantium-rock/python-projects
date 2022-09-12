using QuantConnect;
using QuantConnect.Data;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;


public class CustomDynamicDataImplementation : BaseData
{
    //Set the defaults and define our data shape:
    public decimal Open = 0;
    public decimal High = 0;
    public decimal Low = 0;
    public decimal Close = 0;
    public decimal Volume = 0;

    /// <summary>
    /// 1. Create a default constructor: Custom data types need a default constructor.
    /// We search for a default constructor so please provide one here. 
    /// It won't be used for data, just to generate the "Factory".
    /// </summary>
    public CustomDynamicDataImplementation()
    {
        this.Symbol = "AAPL";
    }

    /// <summary>
    /// 2. RETURN THE STRING URL SOURCE LOCATION FOR YOUR DATA:
    /// This is a powerful and dynamic select source file method. If you have a large dataset, 10+mb we recommend you break it into smaller files. E.g. One zip per year.
    /// We can accept raw text or ZIP files. We read the file extension to determine if it is a zip file.
    /// </summary>
    /// <param name="config">Subscription data, symbol name, data type</param>
    /// <param name="date">Current date we're requesting. This allows you to break up the data source into daily files.</param>
    /// <param name="datafeed">Datafeed type: Backtesting or the Live data broker who will provide live data. You can specify a different source for live trading! </param>
    /// <returns>string URL end point.</returns>
    public override string GetSource(SubscriptionDataConfig config, DateTime date, DataFeedEndpoint datafeed)
    {
        return $@"C:\Users\invitado3\Downloads\{this.Symbol}.csv";
    }

    /// <summary>
    /// 3. READER METHOD: Read 1 line from data source and convert it into Object.
    /// Each line of the CSV File is presented in here. The backend downloads your file, loads it into memory and then line by line feeds it into your algorithm
    /// </summary>
    /// <param name="line">string line from the data source file submitted above</param>
    /// <param name="config">Subscription data, symbol name, data type</param>
    /// <param name="date">Current date we're requesting. This allows you to break up the data source into daily files.</param>
    /// <param name="datafeed">Datafeed type - Backtesting or LiveTrading</param>
    /// <returns>New Bitcoin Object which extends BaseData.</returns>
    public override BaseData Reader(SubscriptionDataConfig config, string line, DateTime date, DataFeedEndpoint datafeed)
    {
        //Create a new Data object that we'll return to Lean.
        CustomDynamicDataImplementation asset = new CustomDynamicDataImplementation();
        try
        {
            //Example File Format:
            //Date,      Open   High    Low     Close   Volume (BTC)    Volume (Currency)   Weighted Price
            //2011-09-13 5.8    6.0     5.65    5.97    58.37138238,    346.0973893944      5.929230648356
            string[] data = line.Split(',');
            asset.Time = DateTime.Parse(data[0]);
            asset.Open = Convert.ToDecimal(data[1]);
            asset.High = Convert.ToDecimal(data[2]);
            asset.Low = Convert.ToDecimal(data[3]);
            asset.Close = Convert.ToDecimal(data[4]);
            asset.Volume = Convert.ToDecimal(data[5]);
            asset.Symbol = this.Symbol;
            asset.Value = asset.Close;
        }
        catch { /* Do nothing, skip first title row */ }
        return asset;
    }
}

