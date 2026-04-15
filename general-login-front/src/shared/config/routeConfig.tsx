import { type RouteObject } from "react-router-dom";
import { AuthPage } from "../../pages/auth/ui/AuthPage";

export const routeConfig: RouteObject[] = [
  {
    path: "/",
    element: <AuthPage />,
  },
];
