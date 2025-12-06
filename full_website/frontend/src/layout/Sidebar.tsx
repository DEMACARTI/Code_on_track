
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, Users, Upload, LogOut, QrCode } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { cn } from '../utils/cn';

export const Sidebar = () => {
    const { logout, user } = useAuth();

    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', to: '/dashboard' },
        { icon: Package, label: 'Items', to: '/items' },
        { icon: Users, label: 'Vendors', to: '/vendors' },
        { icon: Upload, label: 'Import', to: '/import' },
    ];

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-slate-200 bg-white transition-transform">
            <div className="flex h-full flex-col">
                {/* Logo Area */}
                <div className="flex h-16 items-center border-b border-slate-100 px-6">
                    <div className="flex items-center gap-2 text-primary-600">
                        <QrCode className="h-8 w-8" />
                        <span className="text-xl font-bold tracking-tight text-slate-900">QR Track</span>
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex-1 overflow-y-auto px-3 py-4">
                    <nav className="space-y-1">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) =>
                                    cn(
                                        'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200',
                                        isActive
                                            ? 'bg-primary-50 text-primary-700 shadow-sm'
                                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                    )
                                }
                            >
                                <item.icon className={cn("h-5 w-5 flex-shrink-0")} />
                                {item.label}
                            </NavLink>
                        ))}
                    </nav>
                </div>

                {/* User Profile & Logout */}
                <div className="border-t border-slate-100 p-4">
                    <div className="mb-4 flex items-center gap-3 rounded-xl bg-slate-50 p-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-100 text-primary-700 font-bold">
                            {(user as any)?.username?.charAt(0).toUpperCase()}
                        </div>
                        <div className="overflow-hidden">
                            <p className="truncate text-sm font-medium text-slate-900">{(user as any)?.username}</p>
                            <p className="truncate text-xs text-slate-500 capitalize">{(user as any)?.role}</p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition-colors hover:bg-rose-50 hover:text-rose-600"
                    >
                        <LogOut className="h-5 w-5" />
                        Sign Out
                    </button>
                </div>
            </div>
        </aside>
    );
};
