// import React, { useState } from "react";
// import { useLocation } from "react-router-dom";
// import axios from "axios";
// import CustomButton from "../../Components/Button/CustomButton"; // Assuming you have a CustomButton component
// import { API_BASE_URL } from "../../apiConfig"; // Assuming you have the base URL defined here

// const VerifyAccount = () => {
//   const location = useLocation();
//   const [status, setStatus] = useState("");

//   // Extract token and email from query parameters
//   const queryParams = new URLSearchParams(location.search);
//   const token = queryParams.get("token");
//   const email = queryParams.get("email");

//   // Function to handle the verification request
//   const handleVerification = async () => {
//     try {
//       const response = await axios.post(
//         `${API_BASE_URL}/users/verify-account`,
//         {
//           token,
//           email,
//         }
//       );
//       setStatus(response.data.message); // Show success message
//     } catch (error) {
//       setStatus("Verification failed. Please try again."); // Show error message
//     }
//   };

//   return (
//     <div>
//       <h2>Account Verification</h2>
//       <p>{status}</p>
//       {/* Show the button if the status is not success */}
//       {!status.includes("successfully") && (
//         <CustomButton onClick={handleVerification}>Verify Account</CustomButton>
//       )}
//     </div>
//   );
// };

// export default VerifyAccount;

import React, { useState } from "react";
import { useLocation } from "react-router-dom";
import axios from "axios";
import CustomButton from "../../Components/Button/CustomButton";
import { API_BASE_URL } from "../../apiConfig";
import "./VerifyAccount.css";

const VerifyAccount = () => {
  const location = useLocation();
  const [status, setStatus] = useState("");

  // Extract token and email from query parameters
  const queryParams = new URLSearchParams(location.search);
  const token = queryParams.get("token");
  const email = queryParams.get("email");

  // Function to handle the verification request
  const handleVerification = async () => {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/users/verify-account`,
        {
          token,
          email,
        }
      );
      setStatus(response.data.message); // Show success message
    } catch (error) {
      setStatus("Verification failed. Please try again."); // Show error message
    }
  };

  return (
    <div className="verify-account-container">
      <h1 className="verify-account-header">Welcome to Liquidity</h1>
      <p className="verify-account-subtext">
        Unleash the Power of AI Computing
      </p>
      <div className="verify-account-verification-container">
        <h2 className="verify-account-verification-header">
          Account Verification
        </h2>
        <p className="verify-account-status">{status}</p>
        {!status.includes("successfully") && (
          <CustomButton
            onClick={handleVerification}
            className="verify-account-button"
          >
            Verify Account
          </CustomButton>
        )}
      </div>
    </div>
  );
};

export default VerifyAccount;
