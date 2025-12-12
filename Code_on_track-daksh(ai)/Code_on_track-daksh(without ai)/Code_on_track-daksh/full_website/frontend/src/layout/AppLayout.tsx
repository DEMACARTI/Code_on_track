import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';


export const AppLayout = () => {
    return (
        <div className="min-h-screen bg-slate-50 bg-hero-pattern">
            <Sidebar />
            <div className="ml-64 flex min-h-screen flex-col transition-all duration-300">
                <Topbar />
                <main className="flex-1 p-6 md:p-8 animate-fade-in relative z-0">
                    {/* Background Gradients */}
                    <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                        <div className="absolute top-[-10%] right-[-5%] w-[500px] h-[500px] rounded-full bg-brand-400/20 blur-[100px] animate-pulse-soft" />
                        <div className="absolute bottom-[-10%] left-[10%] w-[400px] h-[400px] rounded-full bg-accent-400/20 blur-[100px] animate-pulse-soft" style={{ animationDelay: '1s' }} />
                    </div>

                    <div className="mx-auto max-w-7xl">
                        <Outlet />
                    </div>
                </main>
            </div>

        </div>
    );
};
