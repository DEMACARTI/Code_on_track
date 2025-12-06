import React from 'react';
import { Card } from './Card';
import { cn } from '../../utils/cn';

interface ChartCardProps {
    title: string;
    subtitle?: string;
    children: React.ReactNode;
    action?: React.ReactNode;
    className?: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({ title, subtitle, children, action, className }) => {
    return (
        <Card className={cn("flex flex-col h-full hover:shadow-lg transition-shadow duration-300", className)}>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
                    {subtitle && <p className="text-sm text-slate-500">{subtitle}</p>}
                </div>
                {action && <div>{action}</div>}
            </div>
            <div className="flex-1 w-full min-h-[300px]">
                {children}
            </div>
        </Card>
    );
};
