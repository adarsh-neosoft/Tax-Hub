import {
  IronStackApp,
  AuthProvider,
  ThemeProvider,
} from "iron-stack-ui";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useLocation, BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import TDSOpinionFormPage from "./pages/TDSOpinionFormPage";
import ApprovalPage from "./pages/ApprovalPage";
import RemittanceReportPage from "./pages/RemittanceReportPage";
import RemittanceReportDetailPage from "./pages/RemittanceReportDetailPage";

const queryClient = new QueryClient();

const customRoutes = [
  { path: "/tds-opinion/create", element: <TDSOpinionFormPage /> },
  { path: "/tds-opinion/:id/edit", element: <TDSOpinionFormPage /> },
  { path: "/remittance-report", element: <RemittanceReportPage /> },
  { path: "/remittance-report/:id/edit", element: <RemittanceReportDetailPage /> },
];

function AppLayout() {
  const location = useLocation();

  // Render /approval/:token outside AuthProvider — no sidebar, no login required
  if (location.pathname.startsWith("/approval/")) {
    return (
      <>
        <Toaster richColors closeButton position="top-right" />
        <Routes>
          <Route path="/approval/:token" element={<ApprovalPage />} />
        </Routes>
      </>
    );
  }

  return (
    <AuthProvider>
      <Toaster richColors closeButton position="top-right" />
      <IronStackApp customRoutes={customRoutes} />
    </AuthProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </QueryClientProvider>
  </ThemeProvider>
  );
}

ModuleRegistry.registerModules([AllCommunityModule]);

export default App;