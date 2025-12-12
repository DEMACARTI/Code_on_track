import { Breadcrumbs } from '../components/ui/Breadcrumbs';
import { QuickSearch } from '../components/ui/QuickSearch';
import { Settings, Search } from 'lucide-react';
import { NotificationBell } from '../components/NotificationBell';

export const Topbar = () => {
    return (
        <header className="sticky top-0 z-30 flex h-20 w-full items-center justify-between px-8 transition-all">
            <div className="glass flex h-14 w-full items-center justify-between rounded-2xl px-4">
                <div className="flex items-center gap-4">
                    <Breadcrumbs />
                </div>

                <div className="flex items-center gap-4">
                    <div className="hidden md:block">
                        <QuickSearch trigger={
                            <div className="group flex h-9 w-64 cursor-pointer items-center gap-2 rounded-xl border-0 bg-slate-100/50 px-3 text-sm text-slate-500 transition-all hover:bg-white hover:shadow-inner hover:ring-1 hover:ring-brand-200">
                                <Search className="h-4 w-4 text-slate-400 group-hover:text-brand-500" />
                                <span>Search...</span>
                                <kbd className="ml-auto flex h-5 items-center gap-1 rounded border border-slate-200 bg-white px-1.5 font-sans text-[10px] font-medium text-slate-500">
                                    <span className="text-xs">⌘</span>K
                                </kbd>
                            </div>
                        } />
                    </div>

                    <div className="flex items-center gap-2">
                        <NotificationBell />

                        <button className="flex h-9 w-9 items-center justify-center rounded-full text-slate-500 hover:bg-brand-50 hover:text-brand-600 transition-colors">
                            <Settings className="h-5 w-5" />
                        </button>
                    </div>

                    <div className="h-6 w-px bg-slate-200 mx-1" />

                    <div className="h-9 w-9 rounded-full bg-gradient-to-br from-brand-100 to-accent-100 flex items-center justify-center text-brand-700 font-bold text-sm ring-2 ring-white shadow-sm">
                        AD
                    </div>
                </div>
            </div>
        </header>
    );
};
