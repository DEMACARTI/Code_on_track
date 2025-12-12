import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/ui/Toast';
import { AppLayout } from './layout/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import Vendors from './pages/Vendors';
import VendorDetail from './pages/VendorDetail';

import { Login } from './pages/Login';
import Dashboard from './pages/Dashboard';
import Items from './pages/Items';
import ItemDetail from './pages/ItemDetail';
import ImportItems from './pages/ImportItems';
import LotHealth from './pages/LotHealth';
import SchedulerOptimized from './pages/SchedulerOptimized';
import Inspection from './pages/Inspection';

import LotQuality from './pages/LotQuality';

// Placeholder components for missing pages
const Engravings = () => <div className="p-8">Engravings (Not Implemented)</div>;

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ToastProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/login" element={<Login />} />

              <Route element={<AppLayout />}>
                <Route element={<ProtectedRoute allowedRoles={['admin', 'viewer']} />}>
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/items" element={<Items />} />
                  <Route path="/items/:uid" element={<ItemDetail />} />
                  <Route path="/vendors" element={<Vendors />} />
                  <Route path="/vendors/:id" element={<VendorDetail />} />
                  <Route path="/lot-quality" element={<LotQuality />} />
                  <Route path="/lot-health" element={<LotHealth />} />
                  <Route path="/scheduler-optimized" element={<SchedulerOptimized />} />
                  <Route path="/inspection" element={<Inspection />} />
                  <Route path="/engravings" element={<Engravings />} />
                  <Route path="/import" element={<ImportItems />} />
                </Route>
              </Route>

              <Route path="/" element={
                <Navigate to="/dashboard" replace />
              } />
            </Routes>
          </BrowserRouter>
        </ToastProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
