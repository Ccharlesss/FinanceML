import * as React from "react";
import Button from "@mui/material/Button";

export default function CustomButton({ onClick }) {
  return (
    <Button variant="outlined" onClick={onClick}>
      Compute K-means
    </Button>
  );
}
