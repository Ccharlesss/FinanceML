// import React, { useState, useEffect } from "react";
// import { Navigate } from "react-router-dom";
// import { API_BASE_URL } from "../../apiConfig";
// import axios from "axios";

// // Imports for CSS styling:
// import "./ForgetPassword.css";
// // Imports for Icons:
// import { FaRegEyeSlash } from "react-icons/fa";

// const ForgetPassword = () => {
//   // States involed in the reset password process:
//   const [formData, setFormData] = useState({
//     username: "",
//     email: "",
//     password: "",
//   });
//   const [dataSubmitted, setDataSubmitted] = useState(false);

//   // ======================================================================================================================
//   // Purpose: Event handler function that updates the state based on changes on the input fields:
//   // e: Event obj that contains all information about the event that occured (change in text field):
//   // ...formData: Creates a copy of the state so that the current state isn't affected by recent changes in inputs:
//   // [e.target.id]:e.target.value: Mapps changes from textfield to its according key property name:
//   const handleChange = (e) => {
//     setFormData({ ...formData, [e.target.id]: e.target.value });
//   };

//   // ======================================================================================================================
//   // Purpose: Event handler function that Attempts to send the data to the appropriate backend endpoints:
//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     console.log(formData);
//     try {
//       const putData = {
//         username: formData.username,
//         email: formData.email,
//         password: formData.password,
//       };
//       const response = await axios.put(
//         "auth/reset-password",
//         API_BASE_URL,
//         putData
//       );

//       if (response.status === 200) {
//         console.log("Password was successfully changed", response.data);
//         setDataSubmitted(true);
//       }
//     } catch (error) {
//       console.log(
//         "An error occured in forget password process:",
//         error.response ? error.response.data : error.message
//       );
//     }
//   };

//   // ======================================================================================================================
//   // Purpose: UseEffect hook  enables to reset the state of isSubmitted to false once component is about to unmount:
//   // []: Array of dependencies that indicates the hook to run only once the component is about to unmount:
//   useEffect(() => {
//     return () => {
//       setDataSubmitted(false);
//     };
//   }, []);

//   if (dataSubmitted) {
//     return <Navigate to="/signin" />;
//   }

//   return (
//     <div className="container-form">
//       <div className="forgot-password-form">
//         <div className="form-content">
//           <header>Forgot Password</header>
//           <form onSubmit={handleSubmit}>
//             <div className="field input-field">
//               <input
//                 type="email"
//                 placeholder="Email"
//                 id="email"
//                 onChange={handleChange}
//                 value={formData.email}
//               />
//             </div>

//             <div className="field input-field">
//               <input
//                 type="username"
//                 placeholder="Username"
//                 id="username"
//                 onChange={handleChange}
//                 value={formData.username}
//               />
//             </div>

//             <div className="field input-field">
//               <input
//                 type="password"
//                 placeholder="new password"
//                 id="newPassword"
//                 onChange={handleChange}
//                 value={formData.newPassword}
//               />

//               <i className="eye-icon">
//                 <FaRegEyeSlash />
//               </i>
//             </div>

//             <div className="field button-field">
//               <button>Reset password</button>
//             </div>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ForgetPassword;

// ======================================================

// import React, { useState, useEffect } from "react";
// import { Navigate } from "react-router-dom";
// import { API_BASE_URL } from "../../apiConfig";
// import axios from "axios";

// // Imports for CSS styling:
// import "./ForgetPassword.css";
// // Imports for Icons:
// import { FaRegEyeSlash } from "react-icons/fa";

// const ForgetPassword = () => {
//   // States involved in the reset password process:
//   const [formData, setFormData] = useState({
//     username: "",
//     email: "",
//     password: "",
//     newPassword: "", // Add this line
//   });
//   const [dataSubmitted, setDataSubmitted] = useState(false);

//   const handleChange = (e) => {
//     setFormData({ ...formData, [e.target.id]: e.target.value });
//   };

//   const handleSubmit = async (e) => {
//     e.preventDefault();
//     console.log(formData);
//     try {
//       const putData = {
//         username: formData.username,
//         email: formData.email,
//         password: formData.newPassword, // Update this line
//       };
//       const response = await axios.put(
//         `${API_BASE_URL}/auth/reset-password`, // Fix the API URL
//         putData
//       );

//       if (response.status === 200) {
//         console.log("Password was successfully changed", response.data);
//         setDataSubmitted(true);
//       }
//     } catch (error) {
//       console.log(
//         "An error occurred in forget password process:",
//         error.response ? error.response.data : error.message
//       );
//     }
//   };

//   useEffect(() => {
//     return () => {
//       setDataSubmitted(false);
//     };
//   }, []);

//   if (dataSubmitted) {
//     return <Navigate to="/signin" />;
//   }

//   return (
//     <div className="container-form">
//       <div className="forgot-password-form">
//         <div className="form-content">
//           <header>Forgot Password</header>
//           <form onSubmit={handleSubmit}>
//             <div className="field input-field">
//               <input
//                 type="email"
//                 placeholder="Email"
//                 id="email"
//                 onChange={handleChange}
//                 value={formData.email}
//               />
//             </div>

//             <div className="field input-field">
//               <input
//                 type="text" // Update to correct input type
//                 placeholder="Username"
//                 id="username"
//                 onChange={handleChange}
//                 value={formData.username}
//               />
//             </div>

//             <div className="field input-field">
//               <input
//                 type="password"
//                 placeholder="New Password"
//                 id="newPassword"
//                 onChange={handleChange}
//                 value={formData.newPassword} // Corrected value reference
//               />

//               <i className="eye-icon">
//                 <FaRegEyeSlash />
//               </i>
//             </div>

//             <div className="field button-field">
//               <button>Reset Password</button>
//             </div>
//           </form>
//         </div>
//       </div>
//     </div>
//   );
// };

// export default ForgetPassword;

import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { API_BASE_URL } from "../../apiConfig";
import axios from "axios";

// Imports for CSS styling:
import "./ForgetPassword.css";
// Imports for Icons:
import { FaRegEyeSlash } from "react-icons/fa";

const ForgetPassword = () => {
  // States involved in the reset password process:
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    newPassword: "",
  });
  const [dataSubmitted, setDataSubmitted] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    try {
      const putData = {
        email: formData.email,
        username: formData.username,
        new_password: formData.newPassword,
      };
      const response = await axios.put(
        `${API_BASE_URL}/auth/reset-password`,
        putData
      );

      if (response.status === 200) {
        console.log("Password was successfully changed", response.data);
        setDataSubmitted(true);
      }
    } catch (error) {
      console.log(
        "An error occurred in the forgot password process:",
        error.response ? error.response.data : error.message
      );
    }
  };

  useEffect(() => {
    return () => {
      setDataSubmitted(false);
    };
  }, []);

  if (dataSubmitted) {
    return <Navigate to="/" />;
  }

  return (
    <div className="container-form">
      <div className="forgot-password-form">
        <div className="form-content">
          <header>Forgot Password</header>
          <form onSubmit={handleSubmit}>
            {/* Email Input Field */}
            <div className="field input-field">
              <input
                type="email"
                placeholder="Email"
                id="email"
                name="user_email" // Use a unique name attribute
                autoComplete="email" // Explicitly set autoComplete
                onChange={handleChange}
                value={formData.email}
              />
            </div>

            {/* Username Input Field */}
            <div className="field input-field">
              <input
                type="text"
                placeholder="Username"
                id="username"
                name="user_name" // Use a unique name attribute
                autoComplete="username" // Explicitly set autoComplete
                onChange={handleChange}
                value={formData.username}
              />
            </div>

            {/* New Password Input Field */}
            <div className="field input-field">
              <input
                type="password"
                placeholder="New Password"
                id="newPassword"
                name="new_password" // Use a unique name attribute
                autoComplete="new-password" // Explicitly set autoComplete
                onChange={handleChange}
                value={formData.newPassword}
              />
              <i className="eye-icon">
                <FaRegEyeSlash />
              </i>
            </div>

            <div className="field button-field">
              <button>Reset Password</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default ForgetPassword;
