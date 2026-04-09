import path from "node:path";
import { mkdir } from "node:fs/promises";
import { test, type Page } from "@playwright/test";

const SCREENSHOT_DIR = path.resolve(process.cwd(), "screenshots");

const demoUser = {
  id: 42,
  email: "tester@acme.example",
  username: "tester",
  full_name: "William One",
  is_active: true,
  created_at: "2024-01-02T12:00:00Z",
};

const sampleDocuments = [
  {
    uri: "https://intranet.acme.example/docs/rollout-playbook",
    source: "web",
    title: "Rollout Playbook",
    chunk_count: 42,
    first_ingested_at: "2024-02-10T10:00:00Z",
  },
  {
    uri: "s3://bucket/customer-success-handbook.pdf",
    source: "file",
    title: "Customer Success Handbook",
    chunk_count: 31,
    first_ingested_at: "2024-02-13T14:23:00Z",
  },
];

const embeddingConfig = {
  embedding_provider: "openai" as const,
  embedding_model: "text-embedding-3-large",
  available_providers: [
    {
      value: "openai" as const,
      label: "OpenAI (managed)",
      description: "Azure hosted text-embedding-3-large",
    },
    {
      value: "local" as const,
      label: "Sentence Transformers (self-hosted)",
      description: "BGE base on our GPU nodes",
    },
  ],
};

async function registerApiMocks(page: Page) {
  await mkdir(SCREENSHOT_DIR, { recursive: true });

  await page.route("**/api/auth/me", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(demoUser),
    });
  });

  await page.route("**/chat", async (route) => {
    const body = (route.request().postDataJSON?.() ?? {}) as { question?: string };
    const question = body.question || "your question";
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        answer: `Here's the executive-ready summary for "${question}": revenue is up 18% QoQ, retention hit 96%, and rollout tasks are on track. See linked sources for details.`,
        sources: [
          "https://intranet.acme.example/weekly-memo",
          "https://intranet.acme.example/dashboards/kpi",
        ],
      }),
    });
  });

  await page.route("**/admin/documents*", (route) => {
    if (route.request().method() === "DELETE") {
      route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          ok: true,
          message: "Deleted",
          chunks_deleted: 16,
        }),
      });
      return;
    }

    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        documents: sampleDocuments,
        total: sampleDocuments.length,
        limit: 100,
        offset: 0,
      }),
    });
  });

  await page.route("**/admin/config/embedding-provider", (route) => {
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(embeddingConfig),
    });
  });

  await page.route("**/ingest", (route) => {
    const body = (route.request().postDataJSON?.() ?? {}) as { source?: string };
    route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        ok: true,
        message: `Triggered ingest for ${body.source || "all"} sources`,
      }),
    });
  });
}

async function capture(pathName: string, page: Page) {
  await page.waitForTimeout(600);
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, pathName),
    fullPage: true,
  });
}

test("home page screenshot", async ({ page }) => {
  await registerApiMocks(page);
  await page.goto("/");
  await page.waitForSelector("text=Chatbot console");
  const input = page.getByPlaceholder(/Ask anything/);
  await input.fill("what docs are you using");
  await Promise.all([
    page.waitForResponse("**/chat"),
    page.getByRole("button", { name: "Send" }).click(),
  ]);
  await page.waitForTimeout(1000);
  await capture("home.png", page);
});

test("admin page screenshot", async ({ page }) => {
  await registerApiMocks(page);
  await page.goto("/admin");
  await page.waitForSelector("text=Rollout Playbook");
  await capture("admin.png", page);
});

test("profile page screenshot", async ({ page }) => {
  await registerApiMocks(page);
  await page.goto("/profile");
  await page.waitForSelector("text=Subscriber workspace");
  await capture("profile.png", page);
});
