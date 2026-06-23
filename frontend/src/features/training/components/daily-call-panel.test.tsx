import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { DailyCallPanel } from "./daily-call-panel";

const dailyMocks = vi.hoisted(() => {
  const join = vi.fn();
  const leave = vi.fn();
  const destroy = vi.fn();
  const createFrame = vi.fn(() => ({
    join,
    leave,
    destroy,
  }));

  return {
    join,
    leave,
    destroy,
    createFrame,
  };
});

vi.mock("@daily-co/daily-js", () => ({
  default: {
    createFrame: dailyMocks.createFrame,
  },
}));

describe("DailyCallPanel", () => {
  beforeEach(() => {
    dailyMocks.join.mockReset();
    dailyMocks.leave.mockReset();
    dailyMocks.destroy.mockReset();
    dailyMocks.createFrame.mockClear();
    dailyMocks.join.mockResolvedValue(undefined);
    dailyMocks.leave.mockResolvedValue(undefined);
  });

  it("joins the practice room with the meeting token", async () => {
    const user = userEvent.setup();

    render(
      <DailyCallPanel
        roomUrl="https://example.daily.co/demo-room"
        token="secure-meeting-token"
        sessionReference="conversation-123"
      />,
    );

    await user.click(screen.getByRole("button", { name: "Join secure practice call" }));

    await waitFor(() => {
      expect(dailyMocks.createFrame).toHaveBeenCalledTimes(1);
      expect(dailyMocks.join).toHaveBeenCalledWith({
        url: "https://example.daily.co/demo-room",
        token: "secure-meeting-token",
      });
    });
  });

  it("shows the empty state until a room is available", () => {
    render(<DailyCallPanel roomUrl={null} token={null} sessionReference={null} />);

    expect(screen.getByText("Your call link will appear here")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Join secure practice call" })).not.toBeInTheDocument();
  });
});
