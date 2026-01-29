import { dbConnect } from "./dbConnect";

export const authAPI = {
  login: async (username, password) => {
    const response = await dbConnect.post("/api/auth/login/", {
      username,
      password,
    });
    return response.data;
  },

  logout: async () => {
    await dbConnect.post("/api/auth/logout/");
  },

  getCurrentUser: async () => {
    const response = await dbConnect.get("/api/auth/me/");
    return response.data;
  },
};
