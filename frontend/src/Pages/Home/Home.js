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

const Home = () => {
  // States required for the Home functional component:
  const [isPressed, setIsPressed] = useState(false);
  const [fetchedData, setFetchedData] = useState({
    cluster0: [],
    cluster1: [],
    cluster2: [],
    cluster3: [],
  });

  // ======================================================================================================================
  // Purpose: Add the response from the Kmean algorithm to the appropriate cluster:
  const organizeDataAccordingToClusters = (data) => {
    // 1) Initialise a cluster object comprising of 4 clusters:
    const clusters = {
      cluster0: [],
      cluster1: [],
      cluster2: [],
      cluster3: [],
    };

    // 2) Iterate over each object in fetchData:
    Object.entries(data).forEach(([key, value]) => {
      // 3) Look at cluster key, if value is 1: Append the object to the cluster1:
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

  // ======================================================================================================================
  // Purpose: Event handler function responsible for sending the GET request to the backend API for Kmeans:
  const handleSubmit = async (e) => {
    // 1) Attempt to send the logout request to the appropriate endpoint to the backend:
    try {
      const response = await axios.get(
        `${API_BASE_URL}/visualze/kmean-cluster`
      );
      // 2) If the request is successful set the pressed button as true and FetchedData to response.data:
      // 2) Convert the JSON response from the backend to a JS Object then store JS object in  the state:
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

  // ======================================================================================================================
  // Purpose: Organize the data to be displayed when the cursor clicks on a point:
  // active: Indicates the tooltip is active. Payload contains the data of the hovered point in the graph:
  const CustomTooltip = ({ active, payload }) => {
    // 1) Ensures that the tooltip only renders if it is active and if there is at least one data point in the payload array:
    if (active && payload && payload.length) {
      // 2) payload[0].payload is used to access the data of the first data point being hovered over:
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
      <div className="button-container">
        <button onClick={handleSubmit}>Press button</button>
        {isPressed && (
          <div>
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
    </div>
  );
};

export default Home;
