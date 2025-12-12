
import React from 'react';
import { X, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import type { Notification, NotificationMetadata } from '../../api/notifications';

interface LotBreakdownModalProps {
    notification: Notification;
    onClose: () => void;
    onMarkRead: (id: number) => void;
}

export const LotBreakdownModal: React.FC<LotBreakdownModalProps> = ({ notification, onClose, onMarkRead }) => {
    const navigate = useNavigate();
    const meta = notification.metadata as NotificationMetadata;

    if (!meta || !meta.by_lot) return null;

    const handleViewItems = (lotNo: string) => {
        // Mark as read when drilling down
        onMarkRead(notification.id);

        // Navigate with filters
        const params = new URLSearchParams();
        params.append('search', lotNo); // Using search for lot for now, ideally specific filter
        // If we have specific date range filters implemented in Items page:
        // params.append('expiry_start', meta.date_range.start_date || '');
        // params.append('expiry_end', meta.date_range.end_date);

        navigate(`/items?${params.toString()}`);
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-2xl max-h-[80vh] flex flex-col animate-in fade-in zoom-in-95 duration-200">

                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
                    <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                            {notification.title}
                            <span className="text-sm font-normal text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-0.5 rounded-full">
                                {meta.total_items} items
                            </span>
                        </h2>
                        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            Breakdown by Lot Number
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                    >
                        <X size={20} className="text-gray-500" />
                    </button>
                </div>

                {/* Content */}
                <div className="overflow-y-auto p-6">
                    <div className="grid gap-3">
                        {meta.by_lot.map((lot, idx) => (
                            <div
                                key={idx}
                                className="group flex items-center justify-between p-4 rounded-lg border border-gray-100 dark:border-gray-700 hover:border-blue-200 dark:hover:border-blue-800 hover:bg-blue-50/50 dark:hover:bg-blue-900/10 transition-all cursor-pointer"
                                onClick={() => handleViewItems(lot.lot_no)}
                            >
                                <div className="flex items-center gap-4">
                                    <div className="h-10 w-10 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-bold text-sm">
                                        #{idx + 1}
                                    </div>
                                    <div>
                                        <h3 className="font-semibold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors">
                                            {lot.lot_no}
                                        </h3>
                                        <div className="flex items-center gap-2 text-xs text-gray-500 mt-0.5">
                                            <span className="bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded">
                                                {lot.components || 'Mixed'}
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex items-center gap-4">
                                    <div className="text-right">
                                        <span className="block text-lg font-bold text-gray-900 dark:text-white">
                                            {lot.count}
                                        </span>
                                        <span className="text-xs text-gray-500">items</span>
                                    </div>
                                    <ArrowRight size={18} className="text-gray-300 group-hover:text-blue-500 transition-colors" />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Footer */}
                <div className="p-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 flex justify-end gap-3 rounded-b-xl">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        Close
                    </button>
                    {/* Add CSV export or bulk action here later */}
                </div>
            </div>
        </div>
    );
};
