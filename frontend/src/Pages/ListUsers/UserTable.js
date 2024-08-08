// import * as React from "react";
// import { DataGrid } from "@mui/x-data-grid";
// import Box from "@mui/material/Box";
// import LockPersonIcon from "@mui/icons-material/LockPerson"; // Lock closed
// import LockOpenIcon from "@mui/icons-material/LockOpen"; // Lock open
// import EditIcon from "@mui/icons-material/Edit";
// import IconButton from "@mui/material/IconButton";
// import { useSelector } from "react-redux";

// // Passed as props: users, freezeUser, unfreezeUser, editUser
// const UserTable = ({ users, freezeUser, unfreezeUser, editUser }) => {
//   const isAdmin = useSelector((state) => state.isAdmin);

//   // Debugging: log users data to inspect its structure
//   console.log("Users Data:", users);

//   // 1) Define columns in the table:
//   const columns = [
//     { field: "id", headerName: "ID", width: 90 },
//     { field: "user_name", headerName: "Username", width: 150 },
//     { field: "user_email", headerName: "Email", width: 200 },
//     { field: "user_role", headerName: "Role", width: 150 },
//     {
//       field: "actions",
//       headerName: "Actions",
//       width: 150,
//       renderCell: (params) => (
//         <div>
//           {isAdmin && (
//             <IconButton
//               aria-label="freeze-user"
//               size="small"
//               onClick={() => freezeUser(params.row.id)} // Use params.row.id
//             >
//               <LockPersonIcon />
//             </IconButton>
//           )}
//           <IconButton
//             aria-label="unfreeze-user"
//             size="small"
//             onClick={() => unfreezeUser(params.row.id)} // Use params.row.id
//           >
//             <LockOpenIcon />
//           </IconButton>
//           <IconButton
//             aria-label="edit-user"
//             size="small"
//             onClick={() => editUser(params.row.id)} // Use params.row.id
//           >
//             <EditIcon />
//           </IconButton>
//         </div>
//       ),
//     },
//   ];

//   // Define rows
//   const rows = users.map((user) => ({
//     id: user.id, // Use the id from your user object
//     user_name: user.username,
//     user_email: user.email,
//     user_role: user.role,
//   }));

//   return (
//     <Box sx={{ height: 400, width: "100%" }}>
//       <DataGrid
//         rows={rows}
//         columns={columns}
//         pageSize={5}
//         checkboxSelection
//         disableSelectionOnClick
//       />
//     </Box>
//   );
// };

// export default UserTable;

// =============================
import * as React from "react";
import { DataGrid } from "@mui/x-data-grid";
import Box from "@mui/material/Box";
import LockPersonIcon from "@mui/icons-material/LockPerson"; // Lock closed
import LockOpenIcon from "@mui/icons-material/LockOpen"; // Lock open
import EditIcon from "@mui/icons-material/Edit";
import IconButton from "@mui/material/IconButton";

// Passed as props: users, freezeUser, unfreezeUser, editUser
const UserTable = ({ users, freezeUser, unfreezeUser, editUser }) => {
  // Debugging: log users data to inspect its structure
  console.log("Users Data:", users);

  // 1) Define columns in the table:
  const columns = [
    { field: "id", headerName: "ID", width: 90 },
    { field: "user_name", headerName: "Username", width: 150 },
    { field: "user_email", headerName: "Email", width: 200 },
    { field: "user_role", headerName: "Role", width: 150 },
    { field: "is_active", headerName: "Status", width: 150 },
    {
      field: "actions",
      headerName: "Actions",
      width: 150,
      renderCell: (params) => (
        <div>
          <IconButton
            aria-label="freeze-user"
            size="small"
            onClick={() => freezeUser(params.row.id)} // Use params.row.id
          >
            <LockPersonIcon />
          </IconButton>

          <IconButton
            aria-label="unfreeze-user"
            size="small"
            onClick={() => unfreezeUser(params.row.id)} // Use params.row.id
          >
            <LockOpenIcon />
          </IconButton>
          <IconButton
            aria-label="edit-user"
            size="small"
            onClick={() => editUser(params.row.id)} // Use params.row.id
          >
            <EditIcon />
          </IconButton>
        </div>
      ),
    },
  ];

  // Define rows
  const rows = users.map((user) => ({
    id: user.id, // Use the id from your user object
    user_name: user.username,
    user_email: user.email,
    user_role: user.role,
    is_active: user.is_active,
  }));

  return (
    <Box sx={{ height: 400, width: "100%" }}>
      <DataGrid
        rows={rows}
        columns={columns}
        pageSize={5}
        checkboxSelection
        disableSelectionOnClick
      />
    </Box>
  );
};

export default UserTable;
