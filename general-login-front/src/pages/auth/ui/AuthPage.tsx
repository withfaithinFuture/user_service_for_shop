import { useState } from "react";
import { Box } from "@mui/material";

import styles from "./AuthPage.module.css";

import { LoginForm } from "../../../features/auth/ui/LoginForm";
import { RegisterForm } from "../../../features/auth/ui/RegisterForm";

export const AuthPage = () => {
  const [isRegister, setIsRegister] = useState(false);

  const toggleMode = () => {
    setIsRegister((prev) => !prev);
  };

  return (
    <Box className={styles.root}>
      <Box
        className={`${styles.container} ${
          isRegister ? styles.registerMode : ""
        }`}
      >
        <Box className={styles.imagePanel}>
          <Box className={`${styles.image} ${styles.loginImage}`} />

          <Box className={`${styles.image} ${styles.registerImage}`} />
        </Box>

        <Box className={styles.formPanel}>
          <Box className={styles.formWrapper}>
            <LoginForm onSwitch={toggleMode} />
            <RegisterForm onSwitch={toggleMode} />
          </Box>
        </Box>
      </Box>
    </Box>
  );
};
