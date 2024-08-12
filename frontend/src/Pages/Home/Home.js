import React, { useState } from "react";
import { API_BASE_URL } from "../../apiConfig";
import axios from "axios";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import Navbar from "../../Components/NavBar/NavBar.js";
import CustomButton from "../../Components/Button/CustomButton";
import { GoArrowUpRight } from "react-icons/go";
import { FiArrowDownRight } from "react-icons/fi";
import "./Home.css"; // Import the CSS file

const stockTickers = [
  "MSFT",
  "AAPL",
  "NVDA",
  "AMZN",
  "META",
  "GOOGL",
  "GOOG",
  "LLY",
  "JPM",
  "AVGO",
  "XOM",
  "UNH",
  "V",
  "TSLA",
  "PG",
  "MA",
  "JNJ",
  "HD",
  "MRK",
  "COST",
  "ABBV",
  "CVX",
  "CRM",
  "BAC",
  "WMT",
  "NFLX",
  "PEP",
  "AMD",
  "KO",
  "WFC",
  "LIN",
  "TMO",
  "ADBE",
  "DIS",
  "ACN",
  "MCD",
  "CSCO",
  "ABT",
  "ORCL",
  "CAT",
  "QCOM",
  "INTU",
  "GE",
  "IBM",
  "VZ",
  "CMCSA",
  "DHR",
  "AMAT",
  "COP",
  "TXN",
  "PM",
  "NOW",
  "PFE",
  "AMGN",
  "INTC",
  "UNP",
  "UBER",
  "LOW",
  "GS",
  "NEE",
  "RTX",
  "AXP",
  "SPGI",
  "ISRG",
  "HON",
  "PGR",
  "ELV",
  "MU",
  "BKNG",
  "ETN",
  "C",
  "T",
  "MS",
  "LRCX",
  "NKE",
  "SCHW",
  "TJX",
  "SYK",
  "DE",
  "MDT",
  "UPS",
  "BLK",
  "VRTX",
  "CB",
  "LMT",
  "BMY",
  "CI",
  "SBUX",
  "ADP",
  "BSX",
  "MMC",
  "PLD",
  "BA",
  "REGN",
  "ADI",
  "MDLZ",
  "CVS",
  "FI",
  "BX",
  "PANW",
  "KLAC",
  "GILD",
  "TMUS",
  "SNPS",
  "AMT",
  "CMG",
  "SO",
  "DUK",
  "CME",
  "TGT",
  "ICE",
  "MO",
  "EOG",
  "WM",
  "CDNS",
  "FCX",
  "SLB",
  "SHW",
  "CL",
  "MPC",
  "EQIX",
  "TT",
  "ABNB",
  "NOC",
  "CSX",
  "GD",
  "MCK",
  "TDG",
  "PYPL",
  "ITW",
  "PSX",
  "ZTS",
  "APH",
  "PH",
  "BDX",
  "EMR",
  "FDX",
  "HCA",
  "ORLY",
  "PNC",
  "AON",
  "ANET",
  "USB",
  "CTAS",
  "ROP",
  "PCAR",
  "MAR",
  "MCO",
  "MSI",
  "CEG",
  "ECL",
  "NXPI",
  "VLO",
  "NSC",
  "COF",
  "WELL",
  "DXCM",
  "APD",
  "AJG",
  "TRV",
  "MMM",
  "TFC",
  "AZO",
  "HLT",
  "EW",
  "GM",
  "AIG",
  "F",
  "ALL",
  "AEP",
  "CPRT",
  "ROST",
  "NUE",
  "ADSK",
  "SPG",
  "OKE",
  "WMB",
  "CARR",
  "TEL",
  "MCHP",
  "SRE",
  "AFL",
  "O",
  "KMB",
  "DHI",
  "PSA",
  "CCI",
  "NEM",
  "FTNT",
  "BK",
  "GWW",
  "CNC",
  "MSCI",
  "LULU",
  "MET",
  "D",
  "HES",
  "GIS",
  "OXY",
  "DLR",
  "FIS",
  "STZ",
  "PRU",
  "AMP",
  "AME",
  "JCI",
  "URI",
  "IQV",
  "COR",
  "IR",
  "PCG",
  "DOW",
  "CMI",
  "PAYX",
  "LEN",
  "FAST",
  "A",
  "FANG",
  "LHX",
  "IDXX",
  "CTVA",
  "MNST",
  "EXC",
  "RSG",
  "SMCI",
  "HUM",
  "KR",
  "OTIS",
  "SYY",
  "ODFL",
  "MLM",
  "YUM",
  "KMI",
  "KDP",
  "CSGP",
  "DVN",
  "HAL",
  "EL",
  "GPN",
  "PEG",
  "ACGL",
  "VRSK",
  "VMC",
  "ADM",
  "BKR",
  "CTSH",
  "DFS",
  "CDW",
  "PWR",
  "IT",
  "DD",
  "MRNA",
  "ED",
  "DG",
  "ANSS",
  "DAL",
  "BIIB",
  "PPG",
  "FICO",
  "XEL",
  "HSY",
  "FTV",
  "HIG",
  "KHC",
  "ROK",
  "XYL",
  "WST",
  "EA",
  "MPWR",
  "EXR",
  "RCL",
  "VICI",
  "VST",
  "TSCO",
  "NVR",
  "TRGP",
  "CHTR",
  "PHM",
  "RJF",
  "ON",
  "KEYS",
  "CAH",
  "LYB",
  "RMD",
  "GLW",
  "AVB",
  "HWM",
  "ZBH",
  "FITB",
  "WTW",
  "DLTR",
  "HPQ",
  "EIX",
  "MTD",
  "EFX",
  "WEC",
  "CBRE",
  "CHD",
  "DOV",
  "TROW",
  "EBAY",
  "NDAQ",
  "MTB",
  "WAB",
  "FE",
  "PTC",
  "AWK",
  "ALGN",
  "WY",
  "HPE",
  "GRMN",
  "CBOE",
  "HBAN",
  "ULTA",
  "AEE",
  "BRO",
  "NTAP",
  "STT",
  "HUBB",
  "IRM",
  "STLD",
  "TDY",
  "ES",
  "BR",
  "TTWO",
  "APTV",
  "IFF",
  "CINF",
  "EQR",
  "ETR",
  "PPL",
  "AXON",
  "GPC",
  "STE",
  "BAX",
  "BALL",
  "DECK",
  "WDC",
  "DTE",
  "INVH",
  "MOH",
  "CPAY",
  "CTRA",
  "SBAC",
  "BLDR",
  "WBD",
  "LUV",
  "TSN",
  "HOLX",
  "LH",
  "CLX",
  "FSLR",
  "CF",
  "CMS",
  "OMC",
  "CAG",
  "SWKS",
  "PFG",
  "DPZ",
  "EXPE",
  "RF",
  "ATO",
  "CNP",
  "PKG",
  "BG",
  "TER",
  "TXT",
  "DRI",
  "EG",
  "MAS",
  "ILMN",
  "EQT",
  "J",
  "K",
  "MAA",
  "AVY",
  "IEX",
  "STX",
  "LDOS",
  "JBL",
  "VRSN",
  "ARE",
  "MKC",
  "EXPD",
  "AKAM",
  "UAL",
  "WRB",
  "MRO",
  "CE",
  "TYL",
  "NRG",
  "FDS",
  "COO",
  "VTR",
  "ENPH",
  "LVS",
  "SYF",
  "CFG",
  "WAT",
  "NTRS",
  "ESS",
  "POOL",
  "EVRG",
  "JBHT",
  "PNR",
  "ALB",
  "SNA",
  "ZBRA",
  "SJM",
  "EMN",
  "IP",
  "HST",
  "HII",
  "CCL",
  "WRK",
  "AMCR",
  "FFIV",
  "LKQ",
  "GEN",
  "UDR",
  "DGX",
  "LNT",
  "JKHY",
  "SWK",
  "AES",
  "VTRS",
  "MGM",
  "KEY",
  "LYV",
  "NDSN",
  "PODD",
  "TAP",
  "EPAM",
  "IPG",
  "RVTY",
  "KMX",
  "ALLE",
  "NI",
  "WBA",
  "DOC",
  "TRMB",
  "L",
  "KIM",
  "AOS",
  "CRL",
  "LW",
  "BBY",
  "ROL",
  "JNPR",
  "FMC",
  "REG",
  "PNW",
  "AAL",
  "HRL",
  "RHI",
  "APA",
  "BBWI",
  "FRT",
  "CHRW",
  "DVA",
  "CTLT",
  "IVZ",
  "HAS",
  "BWA",
  "BEN",
  "MTCH",
  "CZR",
  "WYNN",
  "DAY",
  "NWSA",
  "CPB",
  "INCY",
  "TPR",
  "FOXA",
  "BF.B",
  "TFX",
  "QRVO",
  "BXP",
  "CPT",
  "AIZ",
  "ETSY",
  "CMA",
  "RL",
  "HSIC",
  "MKTX",
  "PAYC",
  "MOS",
  "TECH",
  "NCLH",
  "GNRC",
  "UHS",
  "NWS",
  "PARA",
  "FOX",
  "GL",
  "MHK",
  "BIO",
];

const Home = () => {
  const [isPressed, setIsPressed] = useState(false);
  const [fetchedData, setFetchedData] = useState({
    cluster0: [],
    cluster1: [],
    cluster2: [],
    cluster3: [],
  });
  const [selectedTicker, setSelectedTicker] = useState(stockTickers[0]);
  const [predictionResult, setPredictionResult] = useState(null);

  const organizeDataAccordingToClusters = (data) => {
    const clusters = {
      cluster0: [],
      cluster1: [],
      cluster2: [],
      cluster3: [],
    };

    Object.entries(data).forEach(([key, value]) => {
      if (value.Cluster === 0) {
        clusters.cluster0.push(value);
      } else if (value.Cluster === 1) {
        clusters.cluster1.push(value);
      } else if (value.Cluster === 2) {
        clusters.cluster2.push(value);
      } else if (value.Cluster === 3) {
        clusters.cluster3.push(value);
      }
    });

    return clusters;
  };

  const handleSubmit = async (e) => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/visualze/kmean-cluster`
      );
      if (response.status === 200) {
        console.log("success", response.data);
        setIsPressed(true);
        const organizedData = organizeDataAccordingToClusters(
          JSON.parse(response.data)
        );
        setFetchedData(organizedData);
      }
    } catch (error) {
      console.log(
        "An error occurred while fetching the data:",
        error.response ? error.response.data : error.message
      );
    }
  };

  const handlePrediction = async () => {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/predict_next_closing_trend/predict_closing_price_trend?ticker=${selectedTicker}`
      );
      if (response.status === 200) {
        const result = response.data.result; // Assuming the result is returned in this format
        console.log(result);
        console.log("The result of the prediction is:", result);
        setPredictionResult(result);
      }
    } catch (error) {
      console.log(
        "An error occurred while fetching the prediction:",
        error.response ? error.response.data : error.message
      );
    }
  };

  const handleTickerChange = (e) => {
    setSelectedTicker(e.target.value);
    setPredictionResult(null); // Reset prediction result when ticker changes
  };

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="label">{`Ticker: ${data.Ticker}`}</p>
          <p className="intro">{`Average Annual Return: ${data["Avr Annual Return"]}`}</p>
          <p className="intro">{`Average Annual Volatility: ${data["Avr Annual Volatility"]}`}</p>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="home-container">
      <Navbar /> {/* Add the Navbar here */}
      <div
        className={`button-container ${isPressed ? "expanded" : "collapsed"}`}
      >
        <p>
          The K-Means algorithm is an iterative algorithm that divides a group
          of n data points into k non-overlapping subgroups (clusters) based on
          their inherent similarities. The algorithm minimizes the variance
          within each cluster to ensure that the data points within a cluster
          are as close as possible to the centroid of that cluster.
        </p>
        <CustomButton className="custom-button" onClick={handleSubmit}>
          Show Clusters
        </CustomButton>
        {isPressed && (
          <div className="graph-container">
            <ResponsiveContainer width="100%" height={400}>
              <ScatterChart>
                <CartesianGrid />
                <XAxis
                  type="number"
                  dataKey="Avr Annual Return"
                  name="Average Annual Return"
                  label={{
                    value: "Average Annual Return",
                    position: "outsideBottomMiddle",
                    dx: 10,
                    dy: 10,
                  }}
                />
                <YAxis
                  type="number"
                  dataKey="Avr Annual Volatility"
                  name="Average Annual Volatility"
                  label={{
                    value: "Average Annual Volatility",
                    angle: -90,
                    position: "outsideMiddle",
                    dx: -10,
                    dy: -10,
                  }}
                />
                <Tooltip
                  content={<CustomTooltip />}
                  cursor={{ strokeDasharray: "3 3" }}
                />
                <Legend />
                <Scatter
                  name="Cluster 0"
                  data={fetchedData.cluster0}
                  fill="#8884d8"
                />
                <Scatter
                  name="Cluster 1"
                  data={fetchedData.cluster1}
                  fill="#82ca9d"
                />
                <Scatter
                  name="Cluster 2"
                  data={fetchedData.cluster2}
                  fill="#ffc658"
                />
                <Scatter
                  name="Cluster 3"
                  data={fetchedData.cluster3}
                  fill="#ff8042"
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      {/* New Box for Stock Prediction */}
      <div className="prediction-container">
        <h3>Stock Price Prediction</h3>
        <select
          value={selectedTicker}
          onChange={handleTickerChange} // Update the handler here
        >
          {stockTickers.map((ticker) => (
            <option key={ticker} value={ticker}>
              {ticker}
            </option>
          ))}
        </select>
        <CustomButton className="custom-button" onClick={handlePrediction}>
          Predict Closing Price Trend
        </CustomButton>
        {predictionResult !== null && (
          <div className="prediction-result">
            {predictionResult === 1 ? (
              <>
                {console.log("Prediction is 1 - should show green arrow")}
                <GoArrowUpRight size={30} color="green" />
              </>
            ) : (
              <>
                {console.log("Prediction is not 1 - should show red arrow")}
                <FiArrowDownRight size={30} color="red" />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Home;
