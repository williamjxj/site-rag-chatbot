import { defineConfig, devices } from "@playwright/test";

const PORT = 3100;
const HOST = "127.0.0.1";

export default defineConfig({
  testDir: "./tests/e2e",
  timeout: 120 * 1000,
  expect: {
    timeout: 5000,
  },
  reporter: [["list"]],
  use: {
    baseURL: `http://${HOST}:${PORT}`,
    viewport: { width: 1400, height: 900 },
    trace: "off",
    video: "off",
    screenshot: "off",
  },
  projects: [
    {
      name: "chromium",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 1400, height: 900 },
      },
    },
  ],
  webServer: {
    command: `NEXT_PUBLIC_API_URL=http://localhost:8000 PORT=${PORT} pnpm dev --hostname ${HOST} --port ${PORT}`,
    url: `http://${HOST}:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
    stdout: "pipe",
    stderr: "pipe",
  },
});
