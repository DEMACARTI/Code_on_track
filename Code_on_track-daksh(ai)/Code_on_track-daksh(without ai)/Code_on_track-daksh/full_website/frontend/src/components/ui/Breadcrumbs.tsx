import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

export const Breadcrumbs = () => {
    const location = useLocation();
    const pathnames = location.pathname.split('/').filter((x) => x);

    const formatSegment = (segment: string) => {
        // Handle special cases or formatting (e.g., lot-quality -> Lot Quality)
        if (segment === 'lot-quality') return 'Lot Quality';
        if (segment === 'lot-health') return 'Lot Health';
        if (segment === 'scheduler-optimized') return 'Scheduler';
        // Capitalize first letter
        return segment.charAt(0).toUpperCase() + segment.slice(1);
    };

    return (
        <nav aria-label="Breadcrumb" className="flex items-center text-sm text-slate-500">
            <Link
                to="/dashboard"
                className="flex items-center hover:text-brand-600 transition-colors"
                title="Dashboard"
            >
                <Home className="h-4 w-4" />
            </Link>

            {pathnames.length > 0 && <ChevronRight className="h-4 w-4 mx-2 text-slate-400" />}

            {pathnames.map((name, index) => {
                const routeTo = `/${pathnames.slice(0, index + 1).join('/')}`;
                const isLast = index === pathnames.length - 1;
                const displayName = formatSegment(name);

                return (
                    <div key={name} className="flex items-center">
                        {isLast ? (
                            <span className="font-semibold text-slate-900">{displayName}</span>
                        ) : (
                            <Link
                                to={routeTo}
                                className="hover:text-brand-600 transition-colors"
                            >
                                {displayName}
                            </Link>
                        )}
                        {!isLast && <ChevronRight className="h-4 w-4 mx-2 text-slate-400" />}
                    </div>
                );
            })}
        </nav>
    );
};
