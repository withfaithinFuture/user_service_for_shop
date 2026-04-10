export const tokenService = {
  set(token: string) {
    localStorage.setItem("token", token);
  },

  get() {
    return localStorage.getItem("token");
  },

  remove() {
    localStorage.removeItem("token");
  },
};
