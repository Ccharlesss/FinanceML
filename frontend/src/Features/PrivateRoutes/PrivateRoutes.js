import React, { useEffect } from "react";
import { Outlet, Navigate } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { setIsAdminTrue, setIsAdminFalse } from "../../Reducers/RoleReducer";
import { API_BASE_URL } from "../../apiConfig";
import axios from "axios";
import { jwtDecode } from "jwt-decode";

const PrivateRoutes = () => {
  // 1) Get the token from local storage and check if the user is Authenticated:
  const token = localStorage.getItem("token");
  const isAuthenticated = Boolean(token);

  // 2) Try to Decode the JWT token
  let decode = null;
  if (isAuthenticated) {
    try {
      decode = jwtDecode(token);
    } catch (error) {
      console.error("Error Invalid token.");
    }
  }

  // 3) Check if the JWT token has expired:
  const jwtTimeSpan = decode?.exp * 1000;
  const currentTime = Date.now();
  const isExpired = currentTime >= jwtTimeSpan;
  // useDispatch(): Hook that allows to send actions to the Redux store to change the global state:
  const dispatch = useDispatch();
  // useSelector(): Hook that takes redux store state as arg and returns part of the state the component needs:
  // state => state.userRole.isAdmin: Selector function, it takes the current state of Redux store as parameter:
  // useSelector(): Retrieves the specific value isAdmin from the userRole slice of the state.
  const isAdmin = useSelector((state) => state.userRole.isAdmin);

  // 4) Attempt to fetch the role of the current user based on his JWT token:
  useEffect(() => {
    const fetchUserRole = async () => {
      console.log("Fetching user role...");
      if (isAuthenticated && !isExpired) {
        try {
          const response = await axios.get(
            `${API_BASE_URL}/roles/get-user-role`,
            {
              headers: {
                Authorization: `Bearer ${token}`,
              },
            }
          );

          if (response.status === 200) {
            const userRole = response.data; // Assuming this is the returned role
            if (userRole === "Admin") {
              dispatch(setIsAdminTrue());
              //console.log("User role == Admin");
            } else {
              dispatch(setIsAdminFalse());
              //console.log("User role != Admin");
            }
          }
        } catch (error) {
          console.error("Couldn't retrieve user's role from the backend");
        }
      }
    };

    fetchUserRole();
  }, [dispatch, isAuthenticated, isExpired, token]);

  console.log("isAdmin= ", isAdmin);

  return isAuthenticated && !isExpired ? <Outlet /> : <Navigate to="/" />;
};

export default PrivateRoutes;
