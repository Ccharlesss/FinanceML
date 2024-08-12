// import React from "react";
// import Navbar from "../../Components/NavBar/NavBar.js";
// import Accordion from "@mui/material/Accordion";
// import AccordionSummary from "@mui/material/AccordionSummary";
// import AccordionDetails from "@mui/material/AccordionDetails";
// import Typography from "@mui/material/Typography";
// import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

// // Import the image
// import computeKmeanX from "../../Assets/Kmeans/compute_kmean_X.png";
// import computeElbowscurve from "../../Assets/Kmeans/perform_elbows-curve.png";
// import curve from "../../Assets/Kmeans/plot_elbows_curve.png";
// import kmean_code from "../../Assets/Kmeans/kmeans.png";
// import remove_outlier_code from "../../Assets/Kmeans/remove_outliers.png";
// import kmean_math from "../../Assets/Kmeans/kmean_math.png";

// const Kmeans = () => {
//   return (
//     <div>
//       <Navbar />
//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel1-content"
//           id="panel1-header"
//         >
//           <Typography>What is the Kmeans algorithm?</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             The K-Means algorithm is an iterative algorithm that divides a group
//             of n data points into k non-overlapping subgroups or (clusters)
//             based on their inherent similarities. The algorithm minimizes the
//             variance within each cluster to ensure that the data points within a
//             cluster are as close as possible to the centroid of that cluster.
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel2-content"
//           id="panel2-header"
//         >
//           <Typography>
//             Mathematical intuition behind the Kmeans model
//           </Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             {/* Display the image */}
//             <img
//               src={kmean_math}
//               alt="Mathematical intuition cheat sheet"
//               style={{ maxWidth: "100%" }}
//             />
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel3-content"
//           id="panel3-header"
//         >
//           <Typography>Challenges associated with the Kmeans model</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             <ul>
//               <li>
//                 Choosing k: The number of clusters, <code>k</code>, must be
//                 chosen carefully. Common methods include the Elbow Method and
//                 Silhouette Analysis.
//               </li>
//               <li>
//                 Local Minima: K-Means may converge to a local minimum, meaning
//                 the final clusters might not be the global optimum. This can be
//                 mitigated by running the algorithm multiple times with different
//                 initial centroids.
//               </li>
//               <li>
//                 Assumption of Spherical Clusters: K-Means assumes that clusters
//                 are spherical in shape and of equal size, which may not always
//                 be true in real-world data.
//               </li>
//             </ul>
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel4-content"
//           id="panel4-header"
//         >
//           <Typography>Computing Financial features X</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             <p>
//               Below is displayed the code that I developped to compute the
//               average annual return and volatility for each stocks from the
//               S&P500.
//             </p>
//             {/* Display the image */}
//             <img
//               src={computeKmeanX}
//               alt="Computing Financial Features X"
//               style={{ maxWidth: "100%" }}
//             />
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel5-content"
//           id="panel5-header"
//         >
//           <Typography>Computing the optimum number of clusters K</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             <p>
//               In order to select the most appropriate number of clusters to
//               segregate your dataset based on similarities, multiple methods
//               have been developed. One of the methods used in this web
//               application is based on the Elbow method. The Elbow optimization
//               method plots the objective function against the number of clusters
//               K. From here, two approaches can be used. One approach sets the
//               optimal value of k according to the number of clusters that cause
//               the largest decrease in the value of the objective function.
//               Another approach to identifying the most suitable K is to choose
//               the K before the objective function enters a steady state.
//             </p>
//             {/* Display the image */}
//             <img
//               src={computeElbowscurve}
//               alt="Computint the Elbow curve"
//               style={{ maxWidth: "100%" }}
//             />
//             <img
//               src={curve}
//               alt="plotting the Elbow curve"
//               style={{ maxWidth: "100%" }}
//             />
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel6-content"
//           id="panel6-header"
//         >
//           <Typography>Fitting the dataset to the model</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             {/* Display the image */}
//             <img
//               src={kmean_code}
//               alt="Computing Financial Features X"
//               style={{ maxWidth: "100%" }}
//             />
//           </Typography>
//         </AccordionDetails>
//       </Accordion>

//       <Accordion>
//         <AccordionSummary
//           expandIcon={<ExpandMoreIcon />}
//           aria-controls="panel7-content"
//           id="panel7-header"
//         >
//           <Typography>Removing outliers with QRS methof</Typography>
//         </AccordionSummary>
//         <AccordionDetails>
//           <Typography>
//             {/* Display the image */}
//             <img
//               src={remove_outlier_code}
//               alt="Removing outliers"
//               style={{ maxWidth: "100%" }}
//             />
//           </Typography>
//         </AccordionDetails>
//       </Accordion>
//     </div>
//   );
// };

// export default Kmeans;

import React from "react";
import Navbar from "../../Components/NavBar/NavBar.js";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

// Import the image
import computeKmeanX from "../../Assets/Kmeans/compute_kmean_X.png";
import computeElbowscurve from "../../Assets/Kmeans/perform_elbows-curve.png";
import curve from "../../Assets/Kmeans/plot_elbows_curve.png";
import kmean_code from "../../Assets/Kmeans/kmeans.png";
import remove_outlier_code from "../../Assets/Kmeans/remove_outliers.png";
import kmean_math from "../../Assets/Kmeans/kmean_math.png";

// Import the CSS file
import "./Kmeans.css";

const Kmeans = () => {
  return (
    <div>
      <Navbar />
      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel1-content"
          id="panel1-header"
        >
          <Typography className="accordion-title">
            What is the Kmeans algorithm?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            The K-Means algorithm is an iterative algorithm that divides a group
            of n data points into k non-overlapping subgroups or (clusters)
            based on their inherent similarities. The algorithm minimizes the
            variance within each cluster to ensure that the data points within a
            cluster are as close as possible to the centroid of that cluster.
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel2-content"
          id="panel2-header"
        >
          <Typography className="accordion-title">
            Mathematical intuition behind the Kmeans model
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <img
              src={kmean_math}
              alt="Mathematical intuition cheat sheet"
              style={{ maxWidth: "100%" }}
            />
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel3-content"
          id="panel3-header"
        >
          <Typography className="accordion-title">
            Challenges associated with the Kmeans model
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <ul>
              <li>
                Choosing k: The number of clusters, <code>k</code>, must be
                chosen carefully. Common methods include the Elbow Method and
                Silhouette Analysis.
              </li>
              <li>
                Local Minima: K-Means may converge to a local minimum, meaning
                the final clusters might not be the global optimum. This can be
                mitigated by running the algorithm multiple times with different
                initial centroids.
              </li>
              <li>
                Assumption of Spherical Clusters: K-Means assumes that clusters
                are spherical in shape and of equal size, which may not always
                be true in real-world data.
              </li>
            </ul>
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel4-content"
          id="panel4-header"
        >
          <Typography className="accordion-title">
            Computing Financial features X
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <p>
              Below is displayed the code that I developped to compute the
              average annual return and volatility for each stocks from the
              S&P500.
            </p>
            <img
              src={computeKmeanX}
              alt="Computing Financial Features X"
              style={{ maxWidth: "100%" }}
            />
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel5-content"
          id="panel5-header"
        >
          <Typography className="accordion-title">
            Computing the optimum number of clusters K
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <p>
              In order to select the most appropriate number of clusters to
              segregate your dataset based on similarities, multiple methods
              have been developed. One of the methods used in this web
              application is based on the Elbow method. The Elbow optimization
              method plots the objective function against the number of clusters
              K. From here, two approaches can be used. One approach sets the
              optimal value of k according to the number of clusters that cause
              the largest decrease in the value of the objective function.
              Another approach to identifying the most suitable K is to choose
              the K before the objective function enters a steady state.
            </p>
            <img
              src={computeElbowscurve}
              alt="Computint the Elbow curve"
              style={{ maxWidth: "100%" }}
            />
            <img
              src={curve}
              alt="plotting the Elbow curve"
              style={{ maxWidth: "100%" }}
            />
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel6-content"
          id="panel6-header"
        >
          <Typography className="accordion-title">
            Fitting the dataset to the model
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <img
              src={kmean_code}
              alt="Computing Financial Features X"
              style={{ maxWidth: "100%" }}
            />
          </Typography>
        </AccordionDetails>
      </Accordion>

      <Accordion>
        <AccordionSummary
          expandIcon={<ExpandMoreIcon />}
          aria-controls="panel7-content"
          id="panel7-header"
        >
          <Typography className="accordion-title">
            Removing outliers with QRS methof
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            <img
              src={remove_outlier_code}
              alt="Removing outliers"
              style={{ maxWidth: "100%" }}
            />
          </Typography>
        </AccordionDetails>
      </Accordion>
    </div>
  );
};

export default Kmeans;
