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
import DscTrackerFormPage from "./pages/DscTrackerFormPage";
import PoaTrackerFormPage from "./pages/PoaTrackerFormPage";
import FileAwareListView from "./pages/FileAwareListView";
import FormManagementFormPage from "./pages/FormManagementFormPage";
import ItrStatusManagementFormPage from "./pages/ItrStatusManagementFormPage";
import ComplianceManagementFormPage from "./pages/ComplianceManagementFormPage";
import OpinionManagementFormPage from "./pages/OpinionManagementFormPage";
import ValuationReportManagementFormPage from "./pages/ValuationReportManagementFormPage";
import TaskTrackerFormPage from "./pages/TaskTrackerFormPage";

const queryClient = new QueryClient();

const customRoutes = [
  { path: "/tds-opinion/create", element: <TDSOpinionFormPage /> },
  { path: "/tds-opinion/:id/edit", element: <TDSOpinionFormPage /> },
  { path: "/remittance-report", element: <RemittanceReportPage /> },
  { path: "/remittance-report/:id/edit", element: <RemittanceReportDetailPage /> },
  { path: "/dsc-tracker/create", element: <DscTrackerFormPage /> },
  { path: "/dsc-tracker/:id/edit", element: <DscTrackerFormPage /> },
  { path: "/poa-tracker/create", element: <PoaTrackerFormPage /> },
  { path: "/poa-tracker/:id/edit", element: <PoaTrackerFormPage /> },
  { path: "/poa-tracker", element: <FileAwareListView /> },
  { path: "/valuation-report-management", element: <FileAwareListView /> },
  { path: "/opinion-management", element: <FileAwareListView /> },
  { path: "/form-management/create", element: <FormManagementFormPage /> },
  { path: "/form-management/:id/edit", element: <FormManagementFormPage /> },
  { path: "/itr-status-management/create", element: <ItrStatusManagementFormPage /> },
  { path: "/itr-status-management/:id/edit", element: <ItrStatusManagementFormPage /> },
  { path: "/compliance-management/create", element: <ComplianceManagementFormPage /> },
  { path: "/compliance-management/:id/edit", element: <ComplianceManagementFormPage /> },
  { path: "/opinion-management/create", element: <OpinionManagementFormPage /> },
  { path: "/opinion-management/:id/edit", element: <OpinionManagementFormPage /> },
  { path: "/valuation-report-management/create", element: <ValuationReportManagementFormPage /> },
  { path: "/valuation-report-management/:id/edit", element: <ValuationReportManagementFormPage /> },
  { path: "/task-tracker/create", element: <TaskTrackerFormPage /> },
  { path: "/task-tracker/:id/edit", element: <TaskTrackerFormPage /> },
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