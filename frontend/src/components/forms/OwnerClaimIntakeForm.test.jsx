import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import "@testing-library/jest-dom";
import OwnerClaimIntakeForm from "./OwnerClaimIntakeForm";
import axios from "axios";

jest.mock("axios");

describe("OwnerClaimIntakeForm", () => {
  test("renders and submits form successfully", async () => {
    axios.post.mockResolvedValue({ data: { id: 1 } });

    render(<OwnerClaimIntakeForm />);

    // Fill out form
    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: "Doe" },
    });

    // Submit form
    fireEvent.click(screen.getByText(/Submit Claim/i));

    // Wait for success message to appear
    await waitFor(() => {
      expect(
        screen.getByText(/Owner created successfully with ID: 1/i)
      ).toBeInTheDocument();
    });
  });

  test("displays validation errors for invalid email", async () => {
    render(<OwnerClaimIntakeForm />);

    // Fill in invalid email
    fireEvent.change(screen.getByLabelText(/Email/i), {
      target: { value: "invalid-email" },
    });

    // Trigger validation by blurring
    fireEvent.blur(screen.getByLabelText(/Email/i));

    // Try to submit
    fireEvent.click(screen.getByText(/Submit Claim/i));

    // Wait for error message
    await waitFor(() => {
      expect(screen.getByText(/Invalid email address/i)).toBeInTheDocument();
    });
  });

  test("displays validation errors for invalid phone", async () => {
    render(<OwnerClaimIntakeForm />);

    // Fill in required fields first
    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: "Doe" },
    });

    // Fill in invalid phone (too short)
    fireEvent.change(screen.getByLabelText(/Phone/i), {
      target: { value: "123" },
    });

    // Try to submit
    fireEvent.click(screen.getByText(/Submit Claim/i));

    // Wait for error message
    await waitFor(() => {
      expect(
        screen.getByText(/Phone number must be at least 10 digits/i)
      ).toBeInTheDocument();
    });
  });

  test("displays error message on submission failure", async () => {
    axios.post.mockRejectedValue({
      response: { data: { error: "Server error occurred" } },
    });

    render(<OwnerClaimIntakeForm />);

    // Fill out required fields
    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: "Doe" },
    });

    // Submit form
    fireEvent.click(screen.getByText(/Submit Claim/i));

    // Wait for error message
    await waitFor(() => {
      expect(
        screen.getByText(/Error submitting form: Server error occurred/i)
      ).toBeInTheDocument();
    });
  });

  test("disables submit button during submission", async () => {
    let resolveSubmit;
    axios.post.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolveSubmit = resolve;
        })
    );

    render(<OwnerClaimIntakeForm />);

    // Fill out required fields
    fireEvent.change(screen.getByLabelText(/First Name/i), {
      target: { value: "John" },
    });
    fireEvent.change(screen.getByLabelText(/Last Name/i), {
      target: { value: "Doe" },
    });

    const submitButton = screen.getByRole("button", { name: /Submit Claim/i });

    // Submit form
    fireEvent.click(submitButton);

    // Button should show "Submitting..." and be disabled
    await waitFor(() => {
      expect(
        screen.getByRole("button", {
          name: /Submitting.../i,
        })
      ).toBeInTheDocument();
    });

    const loadingButton = screen.getByRole("button", {
      name: /Submitting.../i,
    });
    expect(loadingButton).toBeDisabled();

    // Resolve the promise
    resolveSubmit({ data: { id: 1 } });
  });
});
