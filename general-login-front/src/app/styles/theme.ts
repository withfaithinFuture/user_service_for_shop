import { createTheme } from "@mui/material/styles";

export const theme = createTheme({
  palette: {
    mode: "light",

    primary: {
      main: "#6C5CE7",
    },

    secondary: {
      main: "#00B894",
    },

    background: {
      default: "#F8F9FB",
      paper: "#FFFFFF",
    },
  },

  typography: {
    fontFamily:
      "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

    h4: {
      fontWeight: 700,
    },

    body1: {
      color: "#4A4A4A",
    },
  },

  shape: {
    borderRadius: 12,
  },
});