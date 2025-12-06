import React from 'react';
import { cn } from '../../utils/cn';

interface ChipProps {
    label: string;
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
    size?: 'sm' | 'md';
    className?: string;
}

export const Chip: React.FC<ChipProps> = ({ label, variant = 'default', size = 'sm', className }) => {
    const variants = {
        default: 'bg-slate-100 text-slate-700',
        primary: 'bg-primary-50 text-primary-700 border border-primary-100',
        success: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
        warning: 'bg-amber-50 text-amber-700 border border-amber-100',
        danger: 'bg-rose-50 text-rose-700 border border-rose-100',
        info: 'bg-sky-50 text-sky-700 border border-sky-100',
    };

    const sizes = {
        sm: 'px-2.5 py-0.5 text-xs',
        md: 'px-3 py-1 text-sm',
    };

    return (
        <span
            className={cn(
                'inline-flex items-center rounded-full font-medium',
                variants[variant],
                sizes[size],
                className
            )}
        >
            {label}
        </span>
    );
};
