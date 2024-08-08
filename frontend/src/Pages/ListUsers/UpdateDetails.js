// // FormDialog.js
// import * as React from "react";
// import Button from "@mui/material/Button";
// import TextField from "@mui/material/TextField";
// import Dialog from "@mui/material/Dialog";
// import DialogActions from "@mui/material/DialogActions";
// import DialogContent from "@mui/material/DialogContent";
// import DialogContentText from "@mui/material/DialogContentText";
// import DialogTitle from "@mui/material/DialogTitle";

// export default function FormDialog({
//   open,
//   editingUser,
//   handleClose,
//   handleChange,
//   handleFormSubmit,
// }) {
//   return (
//     <React.Fragment>
//       <Dialog
//         open={open}
//         onClose={handleClose}
//         PaperProps={{
//           component: "form",
//           onSubmit: (event) => {
//             event.preventDefault();
//             handleFormSubmit();
//             handleClose();
//           },
//         }}
//       >
//         <DialogTitle>Update data</DialogTitle>
//         <DialogContent>
//           <DialogContentText>Add your new name and Email</DialogContentText>
//           <TextField
//             autoFocus
//             required
//             margin="dense"
//             id="name"
//             name="user_email"
//             label="Email Address"
//             type="email"
//             fullWidth
//             variant="standard"
//             value={editingUser.user_email || ""}
//             onChange={handleChange}
//           />

//           <TextField
//             autoFocus
//             required
//             margin="dense"
//             id="name"
//             name="user_name"
//             label="Username"
//             type="text"
//             fullWidth
//             variant="standard"
//             value={editingUser.user_name || ""}
//             onChange={handleChange}
//           />
//         </DialogContent>
//         <DialogActions>
//           <Button onClick={handleClose}>Cancel</Button>
//           <Button type="submit" onClick={() => handleFormSubmit(editingUser)}>
//             Submit
//           </Button>
//         </DialogActions>
//       </Dialog>
//     </React.Fragment>
//   );
// }

// =======================================================================
import * as React from "react";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Dialog from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";

export default function FormDialog({
  open,
  editingUser,
  handleClose,
  handleChange,
  handleFormSubmit,
}) {
  return (
    <Dialog
      open={open}
      onClose={handleClose}
      PaperProps={{
        component: "form",
        onSubmit: (event) => {
          event.preventDefault();
          handleFormSubmit(); // Call handleFormSubmit on form submission
          handleClose();
        },
      }}
    >
      <DialogTitle>Update User Data</DialogTitle>
      <DialogContent>
        <DialogContentText>Update the user's information</DialogContentText>
        <TextField
          autoFocus
          required
          margin="dense"
          name="user_name"
          label="New Username"
          type="text"
          fullWidth
          variant="standard"
          value={editingUser.user_name || ""}
          onChange={handleChange}
        />
        <TextField
          required
          margin="dense"
          name="user_email"
          label="Email"
          type="email"
          fullWidth
          variant="standard"
          value={editingUser.user_email || ""}
          onChange={handleChange}
        />
        <TextField
          required
          margin="dense"
          name="user_role"
          label="New Role"
          type="text"
          fullWidth
          variant="standard"
          value={editingUser.user_role || ""}
          onChange={handleChange}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Cancel</Button>
        <Button type="submit">Submit</Button>
      </DialogActions>
    </Dialog>
  );
}
