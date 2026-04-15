import { useState } from "react";
import {
  Button,
  TextField,
  Typography,
  Box,
  FormControlLabel,
  Checkbox,
} from "@mui/material";
import styles from "./AuthForms.module.css";
import { authApi } from "../api/authApi";
import { tokenService } from "../../../shared/lib/token";

interface Props {
  onSwitch: () => void;
}

interface FormData {
  login: string;
  password: string;
  confirmPassword: string;
  firstName: string;
  lastName: string;
  patronymic: string;
  birthDate: string;
  city: string;
  telegram: string;
}

export const RegisterForm = ({ onSwitch }: Props) => {
  const [step, setStep] = useState(0);
  const [isSeller, setIsSeller] = useState(false);

  const [form, setForm] = useState<FormData>({
    login: "",
    password: "",
    confirmPassword: "",
    firstName: "",
    lastName: "",
    patronymic: "",
    birthDate: "",
    city: "",
    telegram: "",
  });

  const [errors, setErrors] = useState<Partial<FormData>>({});

  const handleChange = (field: keyof FormData, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const validateStep = (): boolean => {
    const newErrors: Partial<FormData> = {};

    // STEP 1
    if (step === 0) {
      if (!form.login.trim()) {
        newErrors.login = "Login is required";
      } else if (form.login.length < 4) {
        newErrors.login = "Minimum 4 characters";
      } else if (!/^[a-zA-Z0-9_]+$/.test(form.login)) {
        newErrors.login = "Only letters, numbers and _ allowed";
      }

      if (!form.password) {
        newErrors.password = "Password is required";
      } else if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(form.password)) {
        newErrors.password = "Min 8 chars, 1 uppercase, 1 lowercase, 1 number";
      }

      if (!form.confirmPassword) {
        newErrors.confirmPassword = "Confirm your password";
      } else if (form.confirmPassword !== form.password) {
        newErrors.confirmPassword = "Passwords do not match";
      }
    }

    // STEP 2
    if (step === 1) {
      const nameRegex = /^[A-Za-zА-Яа-яЁё\s-]+$/;

      if (!form.firstName.trim()) {
        newErrors.firstName = "First name is required";
      } else if (!nameRegex.test(form.firstName)) {
        newErrors.firstName = "Only letters allowed";
      }

      if (!form.lastName.trim()) {
        newErrors.lastName = "Last name is required";
      } else if (!nameRegex.test(form.lastName)) {
        newErrors.lastName = "Only letters allowed";
      }

      if (form.patronymic && !nameRegex.test(form.patronymic)) {
        newErrors.patronymic = "Only letters allowed";
      }
    }

    // STEP 3
    if (step === 2) {
      if (!form.birthDate) {
        newErrors.birthDate = "Birth date is required";
      } else {
        const birth = new Date(form.birthDate);
        const today = new Date();
        let age = today.getFullYear() - birth.getFullYear();
        const m = today.getMonth() - birth.getMonth();

        if (m < 0 || (m === 0 && today.getDate() < birth.getDate())) {
          age--;
        }

        if (age < 18) {
          newErrors.birthDate = "You must be 18+";
        }
      }

      if (!form.city.trim()) {
        newErrors.city = "City is required";
      }

      if (!form.telegram.trim()) {
        newErrors.telegram = "Telegram is required";
      } else if (!/^@?[A-Za-z0-9_]{5,32}$/.test(form.telegram)) {
        newErrors.telegram = "Invalid Telegram username";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep()) {
      if (step < 2) setStep((prev) => prev + 1);
    }
  };

  const prevStep = () => {
    if (step > 0) setStep((prev) => prev - 1);
  };

  const handleSubmit = async () => {
    if (!validateStep()) return;

    try {
      const data = await authApi.register({
        login: form.login,
        password: form.password,
        firstName: form.firstName,
        lastName: form.lastName,
        patronymic: form.patronymic,
        dateOfBirth: form.birthDate,
        city: form.city,
        telegram: form.telegram,
        isSeller,
      });

      tokenService.set(data.token);

      const targetUrl = data.user.isSeller
        ? "http://localhost:5172"
        : "http://localhost:5171";

      window.location.href = `${targetUrl}?token=${data.token}`;
    } catch (e: any) {
      alert(e.response?.data?.detail || "Register failed");
    }
  };

  return (
    <Box className={styles.form}>
      <Box className={styles.logoContainer}>
        <img
          src="/mainlogo.png"
          alt="Marketplace Logo"
          className={styles.logo}
        />
      </Box>

      <Box className={styles.content}>
        <Typography variant="h4" className={styles.title}>
          Register
        </Typography>

        <Typography className={styles.subtitle}>
          Step {step + 1} of 3
        </Typography>

        <Box key={step} className={`${styles.step} ${styles.stepAnimation}`}>
          {step === 0 && (
            <>
              <TextField
                label="Login"
                fullWidth
                value={form.login}
                onChange={(e) => handleChange("login", e.target.value)}
                error={!!errors.login}
                helperText={errors.login}
              />
              <TextField
                label="Password"
                type="password"
                fullWidth
                value={form.password}
                onChange={(e) => handleChange("password", e.target.value)}
                error={!!errors.password}
                helperText={errors.password}
              />
              <TextField
                label="Confirm Password"
                type="password"
                fullWidth
                value={form.confirmPassword}
                onChange={(e) =>
                  handleChange("confirmPassword", e.target.value)
                }
                error={!!errors.confirmPassword}
                helperText={errors.confirmPassword}
              />
            </>
          )}

          {step === 1 && (
            <>
              <TextField
                label="First Name"
                fullWidth
                value={form.firstName}
                onChange={(e) => handleChange("firstName", e.target.value)}
                error={!!errors.firstName}
                helperText={errors.firstName}
              />
              <TextField
                label="Last Name"
                fullWidth
                value={form.lastName}
                onChange={(e) => handleChange("lastName", e.target.value)}
                error={!!errors.lastName}
                helperText={errors.lastName}
              />
              <TextField
                label="Patronymic"
                fullWidth
                value={form.patronymic}
                onChange={(e) => handleChange("patronymic", e.target.value)}
                error={!!errors.patronymic}
                helperText={errors.patronymic}
              />
            </>
          )}

          {step === 2 && (
            <>
              <TextField
                label="Date of Birth"
                type="date"
                InputLabelProps={{ shrink: true }}
                fullWidth
                value={form.birthDate}
                onChange={(e) => handleChange("birthDate", e.target.value)}
                error={!!errors.birthDate}
                helperText={errors.birthDate}
              />
              <TextField
                label="City"
                fullWidth
                value={form.city}
                onChange={(e) => handleChange("city", e.target.value)}
                error={!!errors.city}
                helperText={errors.city}
              />
              <TextField
                label="Telegram"
                fullWidth
                value={form.telegram}
                onChange={(e) => handleChange("telegram", e.target.value)}
                error={!!errors.telegram}
                helperText={errors.telegram}
              />

              <FormControlLabel
                control={
                  <Checkbox
                    checked={isSeller}
                    onChange={(e) => setIsSeller(e.target.checked)}
                  />
                }
                label="Register as Seller"
              />
            </>
          )}
        </Box>

        <Box className={styles.buttons}>
          {step > 0 && (
            <Button onClick={prevStep} fullWidth>
              Back
            </Button>
          )}

          {step < 2 ? (
            <Button
              variant="contained"
              size="large"
              onClick={nextStep}
              fullWidth
            >
              Next
            </Button>
          ) : (
            <Button
              variant="contained"
              size="large"
              onClick={handleSubmit}
              fullWidth
            >
              Register
            </Button>
          )}
        </Box>

        <Typography className={styles.switch}>
          Already have an account?{" "}
          <Box
            component="span"
            onClick={onSwitch}
            className={styles.switchLink}
          >
            Sign In
          </Box>
        </Typography>
      </Box>
    </Box>
  );
};
