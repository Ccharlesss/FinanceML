import React, { useState, useEffect } from "react";
import { Navigate, NavLink } from "react-router-dom";
import axios from "axios";
import { API_BASE_URL } from "../../apiConfig";

// Imports for CSS styling:
import "./SignIn.css";
// Imports for Icons:
import { FaRegEyeSlash } from "react-icons/fa";

const SignIn = () => {
  // Sates that are involved in the Sign in process:
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [dataSubmitted, setDataSubmitted] = useState(false);

  // ======================================================================================================================
  // Purpose: Event handler function responsible for updating the state based on the change in the input fields:
  // e: Event obj that contains all required information about the event that occured (changes that has been made)
  // ...signUpData: creates a copy of current state to preserve changes from being directly applied to the current state:
  // if a change occured ie in id=username in input => values entered is mapped to the appropriate key of the state:
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  // ======================================================================================================================
  // Purpose: EvEnt handler function responsible for submitting the data to the backend:
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    try {
      const postData = { email: formData.email, password: formData.password };
      const response = await axios.post(API_BASE_URL + "/auth/login", postData);

      if (response.status === 200) {
        console.log("Login successful:", response.data);
        setDataSubmitted(true);
      }
    } catch (error) {
      console.log(
        "Error during login:",
        error.response ? error.response.data : error.message
      );
    }
  };

  // ======================================================================================================================
  // Purpose: UseEffect hook reponsible for calling a cleanup function after the functional component is about to unmount:
  // []: Array of dependencies that indicates the hook to run only once the functional component is about to unmount:
  // Enables the dataSubmitted state to be reset to false after the user submit the data:
  useEffect(() => {
    return () => {
      setDataSubmitted(false);
    };
  }, []);

  // ======================================================================================================================
  // Assess if the data was submitted correctly if yes => redirect the user to the home page:
  if (dataSubmitted) {
    return <Navigate to="home" />;
  }

  return (
    <div className="container-form">
      <div className="sign-in-form">
        <div className="form-content">
          <header>Login</header>
          <form onSubmit={handleSubmit}>
            <div className="field input-field">
              <input
                type="email"
                placeholder="Email"
                id="email"
                onChange={handleChange}
                value={formData.email}
              />
            </div>
            <div className="field input-field">
              <input
                type="password"
                placeholder="Password"
                id="password"
                onChange={handleChange}
                value={formData.password}
              />
              <i className="eye-icon">
                <FaRegEyeSlash />
              </i>
            </div>
            <div className="form-link">
              <NavLink to="/forgot-password" className="forgot-password">
                Forgot password
              </NavLink>
            </div>
            <div className="field button-field">
              <button>Sign In</button>
            </div>
            <div className="form-link">
              <span>Don't have an account?</span>
              <NavLink to="/sign-up" className="sign-up-link">
                {" "}
                Sign up
              </NavLink>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignIn;
