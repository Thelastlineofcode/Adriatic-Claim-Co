import React, { useState } from "react";
import { useForm } from "react-hook-form";
import axios from "axios";

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
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 max-w-md mx-auto p-4"
    >
      <h2 className="text-xl font-semibold mb-4">Owner Claim Intake Form</h2>

      {submitSuccess && (
        <div
          className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <strong className="font-bold">Success!</strong>
          <span className="block sm:inline"> {submitSuccess}</span>
        </div>
      )}

      {submitError && (
        <div
          className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4"
          role="alert"
        >
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {submitError}</span>
        </div>
      )}

      <div>
        <label htmlFor="first_name" className="block font-medium mb-1">
          First Name*
        </label>
        <input
          id="first_name"
          {...register("first_name", { required: "First name is required" })}
          className="border p-2 w-full"
          aria-required="true"
          aria-invalid={errors.first_name ? "true" : "false"}
          aria-describedby={errors.first_name ? "first_name_error" : undefined}
        />
        {errors.first_name && (
          <span
            id="first_name_error"
            className="text-red-600 text-sm"
            role="alert"
          >
            {errors.first_name.message}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="last_name" className="block font-medium mb-1">
          Last Name*
        </label>
        <input
          id="last_name"
          {...register("last_name", { required: "Last name is required" })}
          className="border p-2 w-full"
          aria-required="true"
          aria-invalid={errors.last_name ? "true" : "false"}
          aria-describedby={errors.last_name ? "last_name_error" : undefined}
        />
        {errors.last_name && (
          <span
            id="last_name_error"
            className="text-red-600 text-sm"
            role="alert"
          >
            {errors.last_name.message}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="middle_name" className="block font-medium mb-1">
          Middle Name
        </label>
        <input
          id="middle_name"
          {...register("middle_name")}
          className="border p-2 w-full"
        />
      </div>

      <div>
        <label htmlFor="date_of_birth" className="block font-medium mb-1">
          Date of Birth
        </label>
        <input
          id="date_of_birth"
          type="date"
          {...register("date_of_birth")}
          className="border p-2 w-full"
        />
      </div>

      <div>
        <label htmlFor="email" className="block font-medium mb-1">
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
          className="border p-2 w-full"
          aria-invalid={errors.email ? "true" : "false"}
          aria-describedby={errors.email ? "email_error" : undefined}
          autoComplete="email"
        />
        {errors.email && (
          <span id="email_error" className="text-red-600 text-sm" role="alert">
            {errors.email.message}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="phone" className="block font-medium mb-1">
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
          className="border p-2 w-full"
          placeholder="(555) 123-4567"
          aria-invalid={errors.phone ? "true" : "false"}
          aria-describedby={errors.phone ? "phone_error" : undefined}
          autoComplete="tel"
        />
        {errors.phone && (
          <span id="phone_error" className="text-red-600 text-sm" role="alert">
            {errors.phone.message}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="address_line1" className="block font-medium mb-1">
          Address Line 1
        </label>
        <input
          id="address_line1"
          {...register("address_line1")}
          className="border p-2 w-full"
          autoComplete="address-line1"
        />
      </div>

      <div>
        <label htmlFor="city" className="block font-medium mb-1">
          City
        </label>
        <input
          id="city"
          {...register("city")}
          className="border p-2 w-full"
          autoComplete="address-level2"
        />
      </div>

      <div>
        <label htmlFor="state" className="block font-medium mb-1">
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
          className="border p-2 w-full"
          placeholder="TX"
          aria-invalid={errors.state ? "true" : "false"}
          aria-describedby={errors.state ? "state_error" : undefined}
          autoComplete="address-level1"
        />
        {errors.state && (
          <span id="state_error" className="text-red-600 text-sm" role="alert">
            {errors.state.message}
          </span>
        )}
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className={`px-4 py-2 rounded mt-4 transition-colors ${
          isSubmitting
            ? "bg-gray-400 cursor-not-allowed"
            : "bg-blue-600 hover:bg-blue-700 text-white"
        }`}
      >
        {isSubmitting ? "Submitting..." : "Submit Claim"}
      </button>
    </form>
  );
}
