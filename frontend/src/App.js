import React from "react";
import OwnerClaimIntakeForm from "./components/forms/OwnerClaimIntakeForm";
import "./components/forms/OwnerClaimIntakeForm.css";

export default function App() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px",
      }}
    >
      <OwnerClaimIntakeForm />
    </div>
  );
}
