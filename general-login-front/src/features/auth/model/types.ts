import type { User } from "../../../entities/user/model/types";

export interface LoginRequest {
  login: string;
  password: string;
}

export interface RegisterRequest {
  login: string;
  password: string;
  firstName: string;
  lastName: string;
  patronymic?: string;
  dateOfBirth: string;
  city: string;
  telegram: string;
  isSeller: boolean;
  marketName?: string;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  token: string;
}
