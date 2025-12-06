import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const AppLayout = () => {
    return (
        <div className="min-h-screen bg-slate-50">
            <Sidebar />
            <div className="ml-64 flex min-h-screen flex-col transition-all duration-300">
                <Topbar />
                <main className="flex-1 p-6 md:p-8 animate-fade-in">
                    <div className="mx-auto max-w-7xl">
                        <Outlet />
                    </div>
                </main>
            </div>
        </div>
    );
};
