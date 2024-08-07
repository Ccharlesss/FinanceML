import { configureStore } from "@reduxjs/toolkit";
import roleReducer from "../Reducers/RoleReducer";
// roleReducer can be called anything

// 1) Create the Store responsible to store the global state: isAdmin:
// 1) Key: slide name = userRole, Value = roleReducer (Reducer in RoleReducer.js)
const store = configureStore({
  reducer: {
    userRole: roleReducer,
  },
});

export default store;
