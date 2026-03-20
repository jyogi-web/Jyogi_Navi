import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: "../api/openapi.json",
  output: {
    path: "src/client",
    postProcess: ["prettier"],
  },
  plugins: [
    {
      name: "@hey-api/client-fetch",
    },
    "@hey-api/sdk",
    "@hey-api/typescript",
    "zod",
    {
      name: "@tanstack/react-query",
      queryOptions: true,
      includeInEntry: true,
    },
  ],
});
