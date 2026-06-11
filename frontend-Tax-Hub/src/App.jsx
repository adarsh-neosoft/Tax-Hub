import {
  IronStackApp,
  AuthProvider,
  ThemeProvider,
} from "iron-stack-ui";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community';
import TDSOpinionFormPage from "./pages/TDSOpinionFormPage";

const queryClient = new QueryClient();

const customRoutes = [
  { path: "/tds-opinion/create", element: <TDSOpinionFormPage /> },
  { path: "/tds-opinion/:id/edit", element: <TDSOpinionFormPage /> },
];

function App() {
  return (
    <ThemeProvider>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <IronStackApp customRoutes={customRoutes} />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  </ThemeProvider>
  );
}

ModuleRegistry.registerModules([AllCommunityModule]);

export default App;