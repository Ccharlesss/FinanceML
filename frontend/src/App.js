// import logo from './logo.svg';
// import './App.css';

import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
// Import my pages:
import SignUp from "./Pages/SignUp/SignUp.js";
import SignIn from "./Pages/Signin/SignIn.js";
import ForgetPassword from "./Pages/ForgetPassword/ForgetPassword.js";

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route>
            <Route path="/" element={<SignIn />} />
            <Route path="/sign-up" element={<SignUp />} />
            <Route path="/Forgot-password" element={<ForgetPassword />} />
          </Route>
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
