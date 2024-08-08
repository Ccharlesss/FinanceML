import React, { useState, useEffect } from "react";
import Navbar from "../../Components/NavBar/NavBar";
import { API_BASE_URL } from "../../apiConfig";
import UserTable from "./UserTable";
import FormDialog from "./UpdateDetails";
import axios from "axios";

const Users = () => {
  // 1) Define the States: Users, editingUser, and open (used for the update detail)
  const [open, setOpen] = useState(false);
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState({
    user_name: "",
    user_email: "",
    user_role: "",
    is_active: "",
    userId: null, // Make sure to include userId for editing
  });

  // 2.1) Fetch all users from the DB as background work:
  useEffect(() => {
    fetchUsers();
  }, []);

  // 2.2) Fetch all Users to display them in the table:
  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/list-users`);
      // 2.3) Set UserState to the response received (list of users):
      setUsers(response.data);
      // 2.4) Reset the EditingUser state:
      setEditingUser({
        user_name: "",
        user_email: "",
        user_role: "",
        is_active: "",
        userId: null,
      });
    } catch (error) {
      console.error("Error fetching users:", error);
    }
  };

  // 3) Handle the logic to close the update details field:
  const handleClose = () => {
    setOpen(false);
  };

  // 4) Handle the logic for editing the user:
  const handleEdit = (id) => {
    // 4.1) Add the user based on his id to the selected variable:
    const selected = users.find((user) => user.id === id); // Use `user.id` instead of `user.userId`
    // 4.2) Update the state of the EditingUser to the selected user:
    // setEditingUser(selected);
    setEditingUser({
      user_name: selected.user_name,
      user_email: selected.user_email,
      user_role: selected.user_role,
      is_active: selected.is_active,
      userId: selected.id, // Ensure correct assignment here
    });
    // 4.3) Set the Open state to true to access the form:
    setOpen(true);
  };

  // Purpose: Freeze a user account:
  const freezeUser = async (userId) => {
    // 1) Attempts to send the PUT request to the appropriate endpoint to the backend:
    try {
      await axios.put(`${API_BASE_URL}/users/block-user-account`, {
        user_id: userId,
      });
      console.log("Successfully blocked user with id:", userId);
      // 1.1) If task was successfull, update the list of users by fetching all users:
      fetchUsers();
    } catch (error) {
      console.error("Error freezing user:", error);
    }
  };

  // Purpose: Unfreeze a user account
  const unfreezeUser = async (userId) => {
    // 1) Attempts to send the PUT request to the appropriate endpoint to the backend:
    try {
      await axios.put(`${API_BASE_URL}/users/unblock-user-account`, {
        user_id: userId,
      });
      console.log("Successfully unblocked user with id:", userId);
      // 1.1) If task was successfull, update the list of users by fetching all users:
      fetchUsers();
    } catch (error) {
      console.error("Error unfreezing user:", error);
    }
  };

  // Purpose: Handle the logic when the user submits the registration form:
  const handleFormSubmit = async () => {
    // 1) Attempts to send the PUT request of the editingUser to the appropriate endpoint to the backend:
    console.log(editingUser.userId);
    console.log(editingUser.user_name);
    console.log(editingUser.user_role);

    try {
      if (editingUser.userId) {
        await axios.put(`${API_BASE_URL}/users/update-user-details`, {
          user_id: editingUser.userId,
          new_username: editingUser.user_name,
          new_user_role: editingUser.user_role,
        });
      }
      console.log("Success");
      fetchUsers();
    } catch (error) {
      console.error("Error saving User:", error);
    } finally {
      setEditingUser({
        user_name: "",
        user_email: "",
        user_role: "",
        is_active: "",
        userId: null,
      });
      handleClose(); // Close the dialog
    }
  };

  return (
    <>
      <Navbar />
      <UserTable
        users={users}
        freezeUser={freezeUser}
        unfreezeUser={unfreezeUser}
        editUser={handleEdit}
      />
      <FormDialog
        open={open}
        handleClose={handleClose}
        editingUser={editingUser}
        handleChange={(e) =>
          setEditingUser({ ...editingUser, [e.target.name]: e.target.value })
        }
        handleFormSubmit={handleFormSubmit}
      />
    </>
  );
};

export default Users;
