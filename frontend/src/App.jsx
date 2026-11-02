import { Navigate, Route, Routes } from "react-router";

import GuestOnly from "./components/auth/GuestOnly.jsx";
import ProtectedRoute from "./components/auth/ProtectedRoute.jsx";
import AppShell from "./components/layout/AppShell.jsx";
import AuditLogsPage from "./pages/AuditLogsPage.jsx";
import DashboardPage from "./pages/DashboardPage.jsx";
import LoginPage from "./pages/auth/LoginPage.jsx";
import ProductsPage from "./pages/ProductsPage.jsx";
import RegisterPage from "./pages/auth/RegisterPage.jsx";
import StockistsPage from "./pages/StockistsPage.jsx";
import { AuthProvider } from "./contexts/AuthContext.jsx";

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route
          path="/login"
          element={(
            <GuestOnly>
              <LoginPage />
            </GuestOnly>
          )}
        />
        <Route
          path="/register"
          element={(
            <GuestOnly>
              <RegisterPage />
            </GuestOnly>
          )}
        />
        <Route
          element={(
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          )}
        >
          <Route index element={<DashboardPage />} />
          <Route path="products" element={<ProductsPage />} />
          <Route path="stockists" element={<StockistsPage />} />
          <Route path="audit-logs" element={<AuditLogsPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AuthProvider>
  );
}
