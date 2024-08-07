import { createSlice } from "@reduxjs/toolkit";

// =========================================================================================
// Configure the reducers and actions:
// Reducers: Reducers: Take action and accordingly update the state in the redux store
// Actions: Actions: Method that indicates the manner to update the state in the redux
// =========================================================================================

// 1) Define the initial state:
const initialState = { isAdmin: false };

// 2) Define the slice => represents a portion of the Redux state:
// 2) Each slice manages its own part of the global state
const roleSlice = createSlice({
  name: "userRole",
  initialState,
  reducers: {
    // Actions:
    setIsAdminTrue: (state) => {
      state.isAdmin = true;
    },
    setIsAdminFalse: (state) => {
      state.isAdmin = false;
    },
  },
});

// 3) Export actions creators and reducers:
export const { setIsAdminTrue, setIsAdminFalse } = roleSlice.actions;
export default roleSlice.reducer;
