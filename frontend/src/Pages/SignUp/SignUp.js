import React, { useState, useEffect } from "react";
import { Navigate } from "react-router-dom";
import { API_BASE_URL } from "../../apiConfig.js";
import axios from "axios";
import Swal from "sweetalert2";

// Inports for CSS styling:
import "./SignUp.css";
// Imports for Icons:
import { FaRegEyeSlash } from "react-icons/fa";

const SignUp = () => {
  // Stores the state regarding the sign up prcess: Username, Email and password:
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  // Store the state of whether the data for the signup process was submitted:
  const [dataSubmitted, setDataSubmitted] = useState(false);

  // ======================================================================================================================
  // Purpose: Function responsible for handling updates to the form's input fields. Takes an event obj 'e' as parameter:
  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  // ======================================================================================================================
  // Purpose: Function responsible for submitting the sign up form to the fastAPI backend:
  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log(formData);
    try {
      const postData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
      };
      const response = await axios.post(
        API_BASE_URL + "/users/signup",
        postData
      );

      if (response.status === 200) {
        console.log("Account was successfully created:", response.data);
        Swal.fire({
          title: "Your account was successfully created!",
          text: "An verification link was send to your email, please verify your account before login in.",
          icon: "success",
        });
        setDataSubmitted(true);
      }
    } catch (error) {
      Swal.fire({
        title: "Failed to create a user account!",
        text: "Please ensure your username and email are valid and that your password is strong enough. The Password must be greater than 8 character in length, must contain a digit, at lease one upper and lower case character and a special character. ",
        icon: "error",
      });
      console.log(
        "An error occurred in the account creation",
        error.response ? error.response.data : error.message
      );
    }
  };

  // ======================================================================================================================
  // Purpose: After the component is about to unmount, return a cleanup function that reset the data submitted to false:
  // Array of dependencies []: enables the useEffect hook to only run once after the initial render and cleanup func run.
  // Enables the dataSubmitted state to be reset to false after a user successfully sign up.
  useEffect(() => {
    return () => {
      setDataSubmitted(false);
    };
  }, []);

  // ======================================================================================================================
  // Purpose: Assess if data was submitted. if true => redirect the user to /sign-in page:
  if (dataSubmitted) {
    return <Navigate to="/sign-in" />;
  }

  return (
    <div className="container-form">
      <div className="sign-up-form">
        <div className="form-content">
          <header>SignUp</header>
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
                type="text"
                placeholder="Username"
                id="username"
                onChange={handleChange}
                value={formData.username}
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

            <div className="field button-field">
              <button>Sign Up</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default SignUp;
