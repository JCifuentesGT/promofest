import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import AuthPage    from './pages/AuthPage';
import ConfirmPage from './pages/ConfirmPage';
import AdminPage   from './pages/AdminPage';

/** Redirect logged-in users to the right page based on their role */
function HomeRedirect() {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={user?.role === 'admin' ? '/admin' : '/confirm'} replace />;
}

function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <>{children}</>;
  return <Navigate to={user?.role === 'admin' ? '/admin' : '/confirm'} replace />;
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />;
}

function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (user?.role !== 'admin') return <Navigate to="/confirm" replace />;
  return <>{children}</>;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={
        <PublicRoute><AuthPage /></PublicRoute>
      } />
      <Route path="/confirm" element={
        <ProtectedRoute><ConfirmPage /></ProtectedRoute>
      } />
      <Route path="/admin" element={
        <AdminRoute><AdminPage /></AdminRoute>
      } />
      <Route path="*" element={<HomeRedirect />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
