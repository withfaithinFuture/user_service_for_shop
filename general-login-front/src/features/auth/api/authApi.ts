import { baseApi } from "../../../shared/api/baseApi";
import type {
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from "../model/types";

export const authApi = {
  async login(data: LoginRequest) {
    const response = await baseApi.post<AuthResponse>("/auth/login", data);

    return response.data;
  },

  async register(data: RegisterRequest) {
    const response = await baseApi.post<AuthResponse>("/auth/register", data);

    return response.data;
  },

  async me() {
    const response = await baseApi.get("/auth/me");
    return response.data;
  },
};
