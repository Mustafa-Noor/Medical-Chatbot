// import axios from "axios";

// const API = axios.create({
//   baseURL: "http://localhost:8000",
// });

// API.interceptors.request.use((config) => {
//   const token = localStorage.getItem("token");
//   if (token) config.headers.Authorization = `Bearer ${token}`;
//   return config;
// });

// export default API;

// import axios from "axios";

// const API = axios.create({
//   baseURL: "http://localhost:8000",
// });

// // Attach Authorization token
// API.interceptors.request.use((config) => {
//   const token = localStorage.getItem("token");  // 🔁 back to "token"
//   if (token) {
//     config.headers.Authorization = `Bearer ${token}`;
//   }
//   return config;
// });

// // Optional: log backend errors
// API.interceptors.response.use(
//   (response) => response,
//   (error) => {
//     console.error("API error:", error.response || error.message);
//     return Promise.reject(error);
//   }
// );

// export default API;



import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
});

// Attach Authorization token
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Optional: log backend errors
API.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error:", error.response || error.message);
    return Promise.reject(error);
  }
);

export default API;