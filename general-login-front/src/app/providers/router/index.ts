import { useRoutes } from "react-router-dom";
import { routeConfig } from "../../../shared/config/routeConfig";

export const AppRouter = () => {
  return useRoutes(routeConfig);
};
