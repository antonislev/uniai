import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
    //port: 3000, // preferred port, but Vite may shift to 3001
    css: {
    postcss: './postcss.config.cjs'
    },
    server: {
    proxy: {
      "/toc": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/chat": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});





