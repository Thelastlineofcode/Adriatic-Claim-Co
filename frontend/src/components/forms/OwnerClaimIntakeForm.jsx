import React, { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";
import "./OwnerClaimIntakeForm.css";

// Get API URL from environment variable
const API_URL = process.env.REACT_APP_API_URL || "";

export default function OwnerClaimIntakeForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm();

  const [submitSuccess, setSubmitSuccess] = useState(null);
  const [submitError, setSubmitError] = useState(null);

  const onSubmit = async (data) => {
    setSubmitError(null);
    setSubmitSuccess(null);

    try {
      const response = await axios.post(`${API_URL}/api/owners`, data);
      setSubmitSuccess(
        `Owner created successfully with ID: ${response.data.id}`
      );
      reset(); // Clear form after successful submission
    } catch (err) {
      const errorMessage =
        err.response?.data?.error || err.message || "An error occurred";
      setSubmitError(`Error submitting form: ${errorMessage}`);
    }
  };

  return (
    <div className="form-container">
      <form
        onSubmit={handleSubmit(onSubmit)}
        className="form-card space-y-6 p-4"
      >
        <h2 className="form-title">Owner Claim Intake Form</h2>
        <p className="form-subtitle">
          Please fill out all required information below
        </p>

        {submitSuccess && (
          <div className="alert alert-success" role="alert">
            <svg className="alert-icon" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <strong className="alert-title">Success!</strong>
              <span className="alert-message"> {submitSuccess}</span>
            </div>
          </div>
        )}

        {submitError && (
          <div className="alert alert-error" role="alert">
            <svg className="alert-icon" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
            <div>
              <strong className="alert-title">Error!</strong>
              <span className="alert-message"> {submitError}</span>
            </div>
          </div>
        )}

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="first_name" className="form-label">
              First Name <span className="required-mark">*</span>
            </label>
            <input
              id="first_name"
              {...register("first_name", {
                required: "First name is required",
              })}
              className={`form-input ${errors.first_name ? "form-input-error" : ""}`}
              aria-required="true"
              aria-invalid={errors.first_name ? "true" : "false"}
              aria-describedby={
                errors.first_name ? "first_name_error" : undefined
              }
              autoComplete="given-name"
            />
            {errors.first_name && (
              <span
                id="first_name_error"
                className="form-error-text"
                role="alert"
              >
                {errors.first_name.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="last_name" className="form-label">
              Last Name <span className="required-mark">*</span>
            </label>
            <input
              id="last_name"
              {...register("last_name", { required: "Last name is required" })}
              className={`form-input ${errors.last_name ? "form-input-error" : ""}`}
              aria-required="true"
              aria-invalid={errors.last_name ? "true" : "false"}
              aria-describedby={
                errors.last_name ? "last_name_error" : undefined
              }
              autoComplete="family-name"
            />
            {errors.last_name && (
              <span
                id="last_name_error"
                className="form-error-text"
                role="alert"
              >
                {errors.last_name.message}
              </span>
            )}
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="middle_name" className="form-label">
              Middle Name
            </label>
            <input
              id="middle_name"
              {...register("middle_name")}
              className="form-input"
              autoComplete="additional-name"
            />
          </div>

          <div className="form-group">
            <label htmlFor="date_of_birth" className="form-label">
              Date of Birth
            </label>
            <input
              id="date_of_birth"
              type="date"
              {...register("date_of_birth")}
              className="form-input"
              autoComplete="bday"
            />
          </div>
        </div>

        <h3 className="form-section-title">Contact Information</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              id="email"
              type="email"
              {...register("email", {
                pattern: {
                  value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                  message: "Invalid email address",
                },
              })}
              className={`form-input ${errors.email ? "form-input-error" : ""}`}
              aria-invalid={errors.email ? "true" : "false"}
              aria-describedby={errors.email ? "email_error" : undefined}
              autoComplete="email"
            />
            {errors.email && (
              <span id="email_error" className="form-error-text" role="alert">
                {errors.email.message}
              </span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="phone" className="form-label">
              Phone
            </label>
            <input
              id="phone"
              type="tel"
              {...register("phone", {
                pattern: {
                  value: /^[\d\s\-()+]+$/,
                  message: "Invalid phone number format",
                },
                minLength: {
                  value: 10,
                  message: "Phone number must be at least 10 digits",
                },
              })}
              className={`form-input ${errors.phone ? "form-input-error" : ""}`}
              placeholder="(555) 123-4567"
              aria-invalid={errors.phone ? "true" : "false"}
              aria-describedby={errors.phone ? "phone_error" : undefined}
              autoComplete="tel"
            />
            {errors.phone && (
              <span id="phone_error" className="form-error-text" role="alert">
                {errors.phone.message}
              </span>
            )}
          </div>
        </div>

        <h3 className="form-section-title">Address</h3>
        <div className="form-group">
          <label htmlFor="address_line1" className="form-label">
            Address Line 1
          </label>
          <input
            id="address_line1"
            {...register("address_line1")}
            className="form-input"
            autoComplete="address-line1"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="city" className="form-label">
              City
            </label>
            <input
              id="city"
              {...register("city")}
              className="form-input"
              autoComplete="address-level2"
            />
          </div>

          <div className="form-group">
            <label htmlFor="state" className="form-label">
              State
            </label>
            <input
              id="state"
              maxLength={2}
              {...register("state", {
                maxLength: {
                  value: 2,
                  message: "State must be 2 characters",
                },
                pattern: {
                  value: /^[A-Z]{2}$/i,
                  message: "State must be 2 letter code (e.g., TX, CA)",
                },
              })}
              className={`form-input ${errors.state ? "form-input-error" : ""}`}
              placeholder="TX"
              aria-invalid={errors.state ? "true" : "false"}
              aria-describedby={errors.state ? "state_error" : undefined}
              autoComplete="address-level1"
            />
            {errors.state && (
              <span id="state_error" className="form-error-text" role="alert">
                {errors.state.message}
              </span>
            )}
          </div>
        </div>

        <button type="submit" disabled={isSubmitting} className="form-submit">
          {isSubmitting ? (
            <span className="submit-spinner">
              <svg className="spinner-icon" fill="none" viewBox="0 0 24 24">
                <circle
                  style={{ opacity: 0.25 }}
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  style={{ opacity: 0.75 }}
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              Submitting...
            </span>
          ) : (
            "Submit Claim"
          )}
        </button>
      </form>
    </div>
  );
}
