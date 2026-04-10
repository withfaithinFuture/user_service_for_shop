import { type ReactNode } from "react";
import { Box } from "@mui/material";
import styles from "./MainLayout.module.css";

interface Props {
  children: ReactNode;
}

export const MainLayout = ({ children }: Props) => {
  return (
    <Box className={styles.background}>
      <Box className={styles.container}>
        {children}
      </Box>
    </Box>
  );
};