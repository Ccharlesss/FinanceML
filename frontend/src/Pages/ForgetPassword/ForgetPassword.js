import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { API_BASE_URL } from "../../apiConfig";
import axios from "axios";

// Imports for CSS styling:
import "./ForgetPassword.css";
// Imports for Icons:
import { FaRegEyeSlash } from "react-icons/fa";
import Swal from "sweetalert2";

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
        Swal.fire({
          title: "Password was changed successfully",
          text: "You can now enter your new password to login.",
          icon: "success",
        });
        setDataSubmitted(true);
      }
    } catch (error) {
      console.log(
        "An error occurred in the forgot password process:",
        error.response ? error.response.data : error.message
      );
      Swal.fire({
        title: "Failed to reset password",
        text: "Error ensure the email & username are valid and the password is strong enough.",
        icon: "error",
      });
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
