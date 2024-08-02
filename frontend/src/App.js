// import logo from './logo.svg';
// import './App.css';

import React from "react";
import { BrowserRouter, Route } from "react-router-dom";
// Import my pages:
import SignUp from "./Pages/SignUp/SignUp";
import SignIn from "./Pages/Signin/SignIn";
import ForgetPassword from "./Pages/ForgetPassword/ForgetPassword";

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Route>
          <Route path="/sign-in" element={<SignIn />} />
          <Route path="/sign-up" element={<SignUp />} />
          <Route path="/Forgot-password" element={<ForgetPassword />} />
        </Route>
      </div>
    </BrowserRouter>
  );
}

export default App;
