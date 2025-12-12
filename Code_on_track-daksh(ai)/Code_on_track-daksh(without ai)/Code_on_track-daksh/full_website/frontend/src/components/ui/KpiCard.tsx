import React from 'react';
import { Card } from './Card';
import { cn } from '../../utils/cn';
import { ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

interface KpiCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    trend?: {
        value: number;
        label: string;
        direction: 'up' | 'down' | 'neutral';
    };
    color?: 'brand' | 'accent' | 'primary' | 'secondary' | 'emerald' | 'rose' | 'amber';
    className?: string;
}

export const KpiCard: React.FC<KpiCardProps> = ({ title, value, icon, trend, color = 'brand', className }) => {
    const colorStyles = {
        brand: 'bg-brand-50 text-brand-600',
        accent: 'bg-accent-50 text-accent-600',
        primary: 'bg-brand-50 text-brand-600',
        secondary: 'bg-accent-50 text-accent-600',
        emerald: 'bg-emerald-50 text-emerald-600',
        rose: 'bg-rose-50 text-rose-600',
        amber: 'bg-amber-50 text-amber-600',
    };

    return (
        <Card className={cn("relative overflow-hidden hover:shadow-lg transition-shadow duration-300 min-h-[110px] flex flex-col justify-between", className)}>
            <div className="flex items-start justify-between">
                <div>
                    <p className="text-sm font-medium text-slate-500">{title}</p>
                    <h3 className="mt-2 text-3xl font-bold text-slate-900 tracking-tight">{value}</h3>
                </div>
                <div className={cn('rounded-xl p-3', colorStyles[color])}>
                    {icon}
                </div>
            </div>
            {trend && (
                <div className="mt-4 flex items-center text-sm">
                    <span
                        className={cn(
                            'flex items-center font-medium',
                            trend.direction === 'up' && 'text-emerald-600',
                            trend.direction === 'down' && 'text-rose-600',
                            trend.direction === 'neutral' && 'text-slate-500'
                        )}
                    >
                        {trend.direction === 'up' && <ArrowUpRight className="mr-1 h-4 w-4" />}
                        {trend.direction === 'down' && <ArrowDownRight className="mr-1 h-4 w-4" />}
                        {trend.direction === 'neutral' && <Minus className="mr-1 h-4 w-4" />}
                        {Math.abs(trend.value)}%
                    </span>
                    <span className="ml-2 text-slate-500">{trend.label}</span>
                </div>
            )}
        </Card>
    );
};
