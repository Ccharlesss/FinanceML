import * as React from "react";
import Button from "@mui/material/Button";

export default function CustomButton({ onClick, children }) {
  return (
    <Button variant="outlined" onClick={onClick}>
      {children}
    </Button>
  );
}
