import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './layout/AppLayout';
import ProtectedRoute from './components/ProtectedRoute';
import Vendors from './pages/Vendors';
import VendorDetail from './pages/VendorDetail';

import { Login } from './pages/Login';
import Dashboard from './pages/Dashboard';
import Items from './pages/Items';
import ImportItems from './pages/ImportItems';

// Placeholder components for missing pages
const ItemDetail = () => <div className="p-8">Item Detail (Not Implemented)</div>;
const Engravings = () => <div className="p-8">Engravings (Not Implemented)</div>;

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
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
                <Route path="/engravings" element={<Engravings />} />
                <Route path="/import" element={<ImportItems />} />
              </Route>
            </Route>

            <Route path="/" element={
              <Navigate to="/dashboard" replace />
            } />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
