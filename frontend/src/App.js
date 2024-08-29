// import React from "react";
// import { BrowserRouter, Route, Routes } from "react-router-dom";
// // Import my pages:
// import SignUp from "./Pages/SignUp/SignUp.js";
// import SignIn from "./Pages/Signin/SignIn.js";
// import ForgetPassword from "./Pages/ForgetPassword/ForgetPassword.js";
// import Home from "./Pages/Home/Home.js";

// function App() {
//   return (
//     <BrowserRouter>
//       <div className="App">
//         <Routes>
//           <Route>
//             <Route path="/" element={<SignIn />} />
//             <Route path="/sign-up" element={<SignUp />} />
//             <Route path="/Forgot-password" element={<ForgetPassword />} />
//             <Route path="/home" element={<Home />} />
//           </Route>
//         </Routes>
//       </div>
//     </BrowserRouter>
//   );
// }

// export default App;

import React from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
// Import my pages:
import SignUp from "./Pages/SignUp/SignUp.js";
import SignIn from "./Pages/Signin/SignIn.js";
import ForgetPassword from "./Pages/ForgetPassword/ForgetPassword.js";
import PrivateRoutes from "./Features/PrivateRoutes/PrivateRoutes.js";
import Home from "./Pages/Home/Home.js";
import Users from "./Pages/ListUsers/ListUsers.js";

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Routes>
          <Route element={<PrivateRoutes />}>
            <Route path="/home" element={<Home />} />
            <Route path="/users" element={<Users />} />
          </Route>

          <Route path="/" element={<SignIn />} />
          <Route path="/sign-up" element={<SignUp />} />
          <Route path="/forgot-password" element={<ForgetPassword />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
