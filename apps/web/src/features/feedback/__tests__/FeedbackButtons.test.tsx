import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { FeedbackButtons } from "../FeedbackButtons";

// API クライアントをモック
vi.mock("@jyogi-navi/openapi/sdk", () => ({
  createFeedbackApiFeedbackPost: vi.fn(),
}));

import { createFeedbackApiFeedbackPost } from "@jyogi-navi/openapi/sdk";

function wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: { mutations: { retry: false } },
  });
  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}

describe("FeedbackButtons", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("👍と👎ボタンが描画されること", () => {
    render(<FeedbackButtons sessionId="sess-abc" />, {
      wrapper,
    });
    expect(screen.getByRole("button", { name: /good/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /bad/i })).toBeInTheDocument();
  });

  it("👍ボタンクリックで selected 状態になること", async () => {
    vi.mocked(createFeedbackApiFeedbackPost).mockResolvedValue({} as never);
    render(<FeedbackButtons sessionId="sess-abc" />, {
      wrapper,
    });

    const goodButton = screen.getByRole("button", { name: /good/i });
    fireEvent.click(goodButton);

    await waitFor(() => {
      expect(goodButton).toHaveAttribute("data-selected", "true");
    });
  });

  it("👎ボタンクリックで selected 状態になること", async () => {
    vi.mocked(createFeedbackApiFeedbackPost).mockResolvedValue({} as never);
    render(<FeedbackButtons sessionId="sess-abc" />, {
      wrapper,
    });

    const badButton = screen.getByRole("button", { name: /bad/i });
    fireEvent.click(badButton);

    await waitFor(() => {
      expect(badButton).toHaveAttribute("data-selected", "true");
    });
  });

  it("👍クリック後に再クリックで選択解除されること", async () => {
    vi.mocked(createFeedbackApiFeedbackPost).mockResolvedValue({} as never);
    render(<FeedbackButtons sessionId="sess-abc" />, {
      wrapper,
    });

    const goodButton = screen.getByRole("button", { name: /good/i });
    fireEvent.click(goodButton);

    await waitFor(() => {
      expect(goodButton).toHaveAttribute("data-selected", "true");
    });

    fireEvent.click(goodButton);
    await waitFor(() => {
      expect(goodButton).toHaveAttribute("data-selected", "false");
    });
  });

  it("👍クリック時にAPIが呼び出されること", async () => {
    vi.mocked(createFeedbackApiFeedbackPost).mockResolvedValue({} as never);
    render(<FeedbackButtons sessionId="sess-abc" />, {
      wrapper,
    });

    fireEvent.click(screen.getByRole("button", { name: /good/i }));

    await waitFor(() => {
      expect(createFeedbackApiFeedbackPost).toHaveBeenCalledWith(
        expect.objectContaining({
          body: expect.objectContaining({
            session_id: "sess-abc",
            rating: "good",
          }),
        })
      );
    });
  });
});
