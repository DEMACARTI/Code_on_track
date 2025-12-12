import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Package, Users, Upload, LogOut, ChevronRight } from 'lucide-react';
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
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 glass border-r-0 transition-transform">
            <div className="flex h-full flex-col">
                {/* Logo Area */}
                <div className="flex h-40 items-center justify-start pl-8">
                    <div className="flex flex-col items-center gap-2">
                        <div className="flex items-center gap-0">
                            <img
                                src="/logo.png"
                                alt="Rail Chinh Logo"
                                className="h-28 w-auto object-contain"
                            />
                            <span className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent">RailChinh</span>
                        </div>
                    </div>
                </div>

                {/* Navigation */}
                <div className="flex-1 overflow-y-auto px-4 py-6">
                    <nav className="space-y-2">
                        {navItems.map((item) => (
                            <NavLink
                                key={item.to}
                                to={item.to}
                                className={({ isActive }) =>
                                    cn(
                                        'group flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium transition-all duration-300',
                                        isActive
                                            ? 'bg-gradient-to-r from-brand-50 to-transparent text-brand-700 shadow-sm'
                                            : 'text-slate-600 hover:bg-white/50 hover:text-slate-900 hover:shadow-sm'
                                    )
                                }
                            >
                                <div className="flex items-center gap-3">
                                    <item.icon className={cn("h-5 w-5 transition-colors",
                                        ({ isActive }: { isActive: boolean }) => isActive ? "text-brand-600" : "text-slate-400 group-hover:text-brand-500"
                                    )} />
                                    {item.label}
                                </div>
                                <ChevronRight className={cn("h-4 w-4 opacity-0 transition-all duration-300 -translate-x-2",
                                    ({ isActive }: { isActive: boolean }) => isActive ? "opacity-100 translate-x-0 text-brand-400" : "group-hover:opacity-100 group-hover:translate-x-0"
                                )} />
                            </NavLink>
                        ))}
                    </nav>
                </div>

                {/* User Profile & Logout */}
                <div className="p-4">
                    <div className="glass rounded-2xl p-4 mb-2">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-brand-100 to-accent-100 text-brand-700 font-bold shadow-inner">
                                {(user as any)?.username?.charAt(0).toUpperCase()}
                            </div>
                            <div className="overflow-hidden">
                                <p className="truncate text-sm font-bold text-slate-900">{(user as any)?.username}</p>
                                <p className="truncate text-xs text-slate-500 capitalize">{(user as any)?.role}</p>
                            </div>
                        </div>
                        <button
                            onClick={logout}
                            className="flex w-full items-center justify-center gap-2 rounded-lg bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600 transition-all hover:bg-rose-50 hover:text-rose-600 hover:shadow-sm"
                        >
                            <LogOut className="h-3.5 w-3.5" />
                            Sign Out
                        </button>
                    </div>
                </div>
            </div>
        </aside>
    );
};
