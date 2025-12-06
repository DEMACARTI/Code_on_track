

export const Topbar = () => {
    return (
        <header className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-slate-200 bg-white/80 px-6 backdrop-blur-md transition-all">
            <div className="flex items-center gap-4">
                <h2 className="text-lg font-semibold text-slate-800">Overview</h2>
            </div>

            <div className="flex items-center gap-4">
                {/* Add user profile or other minimal elements here if needed in future */}
            </div>
        </header>
    );
};
