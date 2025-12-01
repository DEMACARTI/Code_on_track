import { Outlet, Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LogOut, LayoutDashboard, Package, Users, Tag } from 'lucide-react';

export default function AppLayout() {
    const { logout, role } = useAuth();
    const navigate = useNavigate();
    const isAdmin = role === 'admin';

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="flex h-screen bg-gray-100">
            {/* Sidebar */}
            <div className="w-64 bg-white shadow-md flex flex-col">
                <div className="p-6 border-b">
                    <h1 className="text-xl font-bold text-gray-800">IRF Tracker</h1>
                </div>
                <nav className="flex-1 p-4 space-y-2">
                    <Link to="/dashboard" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                        <LayoutDashboard size={20} />
                        Dashboard
                    </Link>
                    <Link to="/items" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                        <Package size={20} />
                        Items
                    </Link>
                    <Link to="/vendors" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                        <Users size={20} />
                        Vendors
                    </Link>
                    <Link to="/engravings" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                        <Tag size={20} />
                        Engravings
                    </Link>
                    {isAdmin && (
                        <Link to="/import/items" className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg">
                            <Package size={20} />
                            Import Items
                        </Link>
                    )}
                </nav>
                <div className="p-4 border-t">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg w-full"
                    >
                        <LogOut size={20} />
                        Logout
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto">
                <Outlet />
            </div>
        </div>
    );
}
