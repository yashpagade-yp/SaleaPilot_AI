import { createBrowserRouter } from "react-router-dom";

import { RootLayout } from "../components/layout/root-layout";
import { AppShellLayout } from "../components/layout/app-shell-layout";
import { LandingPage } from "../features/landing/landing-page";
import { AdminWorkspacePage } from "../features/admin/admin-workspace-page";
import { AcceptInvitationPage } from "../features/auth/accept-invitation-page";
import { SalesWorkspacePage } from "../features/training/sales-workspace-page";

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      {
        index: true,
        element: <LandingPage />,
      },
      {
        path: "accept-invitation",
        element: <AcceptInvitationPage />,
      },
      {
        path: "admin",
        element: <AppShellLayout mode="admin" />,
        children: [
          {
            index: true,
            element: <AdminWorkspacePage />,
          },
        ],
      },
      {
        path: "workspace",
        element: <AppShellLayout mode="sales" />,
        children: [
          {
            index: true,
            element: <SalesWorkspacePage />,
          },
        ],
      },
    ],
  },
]);
