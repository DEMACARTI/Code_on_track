import React from 'react';
import { cn } from '../../utils/cn';

export const Table = React.forwardRef<HTMLTableElement, React.HTMLAttributes<HTMLTableElement>>(
    ({ className, ...props }, ref) => (
        <div className="w-full overflow-auto">
            <table
                ref={ref}
                className={cn('w-full caption-bottom text-sm', className)}
                {...props}
            />
        </div>
    )
);
Table.displayName = 'Table';

export const TableHeader = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
    ({ className, ...props }, ref) => (
        <thead ref={ref} className={cn('[&_tr]:border-b bg-slate-50/50', className)} {...props} />
    )
);
TableHeader.displayName = 'TableHeader';

export const TableBody = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
    ({ className, ...props }, ref) => (
        <tbody ref={ref} className={cn('[&_tr:last-child]:border-0', className)} {...props} />
    )
);
TableBody.displayName = 'TableBody';

export const TableFooter = React.forwardRef<HTMLTableSectionElement, React.HTMLAttributes<HTMLTableSectionElement>>(
    ({ className, ...props }, ref) => (
        <tfoot
            ref={ref}
            className={cn('bg-slate-900 font-medium text-slate-50', className)}
            {...props}
        />
    )
);
TableFooter.displayName = 'TableFooter';

export const TableRow = React.forwardRef<HTMLTableRowElement, React.HTMLAttributes<HTMLTableRowElement>>(
    ({ className, ...props }, ref) => (
        <tr
            ref={ref}
            className={cn(
                'border-b border-slate-100 transition-colors hover:bg-slate-50/50 data-[state=selected]:bg-slate-50',
                className
            )}
            {...props}
        />
    )
);
TableRow.displayName = 'TableRow';

export const TableHead = React.forwardRef<HTMLTableCellElement, React.ThHTMLAttributes<HTMLTableCellElement>>(
    ({ className, ...props }, ref) => (
        <th
            ref={ref}
            className={cn(
                'h-10 px-4 text-left align-middle font-medium text-slate-500 [&:has([role=checkbox])]:pr-0',
                className
            )}
            {...props}
        />
    )
);
TableHead.displayName = 'TableHead';

export const TableCell = React.forwardRef<HTMLTableCellElement, React.TdHTMLAttributes<HTMLTableCellElement>>(
    ({ className, ...props }, ref) => (
        <td
            ref={ref}
            className={cn('p-4 align-middle [&:has([role=checkbox])]:pr-0 text-slate-700', className)}
            {...props}
        />
    )
);
TableCell.displayName = 'TableCell';

export const TableCaption = React.forwardRef<HTMLTableCaptionElement, React.HTMLAttributes<HTMLTableCaptionElement>>(
    ({ className, ...props }, ref) => (
        <caption
            ref={ref}
            className={cn('mt-4 text-sm text-slate-500', className)}
            {...props}
        />
    )
);
TableCaption.displayName = 'TableCaption';

export const TableLoading = ({ colSpan }: { colSpan: number }) => (
    <TableRow>
        <TableCell colSpan={colSpan} className="h-24 text-center">
            <div className="flex items-center justify-center text-slate-500">
                Loading data...
            </div>
        </TableCell>
    </TableRow>
);

export const TableEmpty = ({ colSpan, message = "No results." }: { colSpan: number, message?: string }) => (
    <TableRow>
        <TableCell colSpan={colSpan} className="h-24 text-center text-slate-500">
            {message}
        </TableCell>
    </TableRow>
);
