import { render, screen } from "@testing-library/react";
import { createMemoryRouter, RouterProvider } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { LandingPage } from "./landing-page";

describe("LandingPage", () => {
  it("renders the main landing message and flow CTAs", () => {
    const router = createMemoryRouter(
      [
        {
          path: "/",
          element: <LandingPage />,
        },
      ],
      {
        initialEntries: ["/"],
      },
    );

    render(<RouterProvider router={router} />);

    expect(
      screen.getByText("Dark, focused training for real sales conversations."),
    ).toBeInTheDocument();
    expect(screen.getByText("Start salesperson flow")).toBeInTheDocument();
    expect(screen.getAllByText("Admin login")).toHaveLength(2);
  });
});
