import { useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import {
    ChevronLeft, ChevronRight, AlertTriangle, RefreshCw, Package, FileText, History
} from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { SearchInput } from '../components/ui/SearchInput';
import { Chip } from '../components/ui/Chip';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableEmpty, TableLoading } from '../components/ui/Table';
import { Drawer } from '../components/ui/Drawer';
import { motion } from 'framer-motion';

interface Item {
    id: number;
    uid: string;
    lot_no: string;
    component_type: string;
    status: string;
    manufacture_date?: string;
    expiry_date?: string;
    vendor_id?: number;
    depot?: string;
    manufacture?: string;
}

interface ItemsResponse {
    items: Item[];
    total: number;
}

interface InspectionReport {
    id: number;
    inspection_date: string;
    result_summary: string; // JSON string
    inspector_id: string;
    image_path?: string;
}

export default function Items() {
    const [searchParams, setSearchParams] = useSearchParams();

    // Search state
    const [uidSearch, setUidSearch] = useState(searchParams.get('uid') || '');
    const [lotSearch, setLotSearch] = useState(searchParams.get('lot_no') || '');

    // Pagination state
    const [page, setPage] = useState(1);
    const pageSize = 20;

    // Drawer state
    const [selectedItem, setSelectedItem] = useState<Item | null>(null);
    const [isDrawerOpen, setIsDrawerOpen] = useState(false);

    const queryClient = useQueryClient();

    const { data, isLoading, error } = useQuery<ItemsResponse>({
        queryKey: ['items', uidSearch, lotSearch, page],
        queryFn: async () => {
            const params: any = { page, size: pageSize };
            if (uidSearch) params.uid = uidSearch;
            if (lotSearch) params.lot_no = lotSearch;

            try {
                const res = await api.get('/items', { params });
                console.log("Items Data:", res.data);
                return res.data;
            } catch (err: any) {
                console.error("Items Fetch Error:", err.response?.status, err.response?.data);
                throw err;
            }
        }
    });

    // Fetch history for selected item
    const { data: historyData, isLoading: isLoadingHistory } = useQuery<InspectionReport[]>({
        queryKey: ['inspection_history', selectedItem?.uid],
        queryFn: async () => {
            if (!selectedItem?.uid) return [];
            try {
                const res = await api.get(`/api/vision/history/${selectedItem.uid}`);
                return res.data;
            } catch (e) {
                return [];
            }
        },
        enabled: !!selectedItem?.uid,
    });

    const items = data?.items || [];
    const total = data?.total || 0;
    const totalPages = Math.ceil(total / pageSize);

    const handleSearch = () => {
        const newParams: any = {};
        if (uidSearch) newParams.uid = uidSearch;
        if (lotSearch) newParams.lot_no = lotSearch;
        setSearchParams(newParams);
        setPage(1);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter') {
            handleSearch();
        }
    };

    const clearSearch = () => {
        setUidSearch('');
        setLotSearch('');
        setSearchParams({});
        setPage(1);
    };

    const handleRefresh = () => {
        queryClient.invalidateQueries({ queryKey: ['items'] });
    };

    const openHistory = (item: Item) => {
        setSelectedItem(item);
        setIsDrawerOpen(true);
    };

    const renderStatusBadge = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active':
            case 'installed':
                return <Chip label="Installed" variant="success" className="shadow-sm border-emerald-200 bg-emerald-50 text-emerald-700" />;
            case 'failed':
            case 'rejected':
                return <Chip label="Failed" variant="danger" className="shadow-sm border-rose-200 bg-rose-50 text-rose-700" />;
            case 'manufactured':
                return <Chip label="Manufactured" className="shadow-sm border-blue-200 bg-blue-50 text-blue-700" />;
            case 'inspected':
                return <Chip label="Inspected" className="shadow-sm border-amber-200 bg-amber-50 text-amber-700" />;
            default:
                return <Chip label={status} variant="default" className="shadow-sm" />;
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Items Inventory</h1>
                    <p className="text-slate-500 mt-1">Manage and track your inventory items.</p>
                </div>
                <div className="flex flex-wrap gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="bg-white hover:bg-slate-50"
                    >
                        <RefreshCw className={`h - 4 w - 4 mr - 2 ${isLoading ? 'animate-spin' : ''} `} />
                        Refresh
                    </Button>
                </div>
            </div>

            <Card className="glass border-0 shadow-lg shadow-slate-200/50 overflow-hidden">
                <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-4 md:space-y-0 pb-6 border-b border-slate-100/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-brand-50 rounded-lg">
                            <Package className="h-5 w-5 text-brand-600" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-bold text-slate-900">All Items</CardTitle>
                            <p className="text-sm text-slate-500">Total: {total.toLocaleString()} items</p>
                        </div>
                    </div>
                    <div className="flex flex-col md:flex-row gap-2 w-full md:w-auto">
                        <div className="w-full md:w-64">
                            <SearchInput
                                value={uidSearch}
                                onChange={setUidSearch}
                                onKeyDown={handleKeyDown}
                                placeholder="Search by UID..."
                                className="bg-slate-50/50 border-slate-200"
                            />
                        </div>
                        <div className="w-full md:w-48">
                            <SearchInput
                                value={lotSearch}
                                onChange={setLotSearch}
                                onKeyDown={handleKeyDown}
                                placeholder="Filter by Lot No..."
                                className="bg-slate-50/50 border-slate-200"
                            />
                        </div>
                        <Button onClick={handleSearch} variant="secondary">Search</Button>
                        {(uidSearch || lotSearch) && (
                            <Button onClick={clearSearch} variant="ghost" className="text-slate-500">Clear</Button>
                        )}
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 pl-6">UID</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Type</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Status</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Lot No</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Depot</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Manufacture</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 pr-6">Action</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableLoading colSpan={7} />
                                ) : error ? (
                                    <TableRow>
                                        <td colSpan={7} className="h-32 text-center text-rose-500">
                                            <div className="flex flex-col items-center justify-center">
                                                <AlertTriangle className="h-8 w-8 mb-2" />
                                                <p>Error loading items</p>
                                            </div>
                                        </td>
                                    </TableRow>
                                ) : items.length > 0 ? (
                                    items.map((item) => (
                                        <TableRow key={item.id} className="hover:bg-brand-50/30 transition-colors border-b border-slate-50">
                                            <TableCell className="pl-6 font-mono text-sm font-medium text-brand-600">
                                                {item.uid}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-700">{item.component_type}</TableCell>
                                            <TableCell>
                                                {renderStatusBadge(item.status)}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-700 font-mono">{item.lot_no || '—'}</TableCell>
                                            <TableCell className="text-sm text-slate-700">{item.depot || '—'}</TableCell>
                                            <TableCell className="text-sm text-slate-600 font-mono">
                                                {item.manufacture || item.manufacture_date || '—'}
                                            </TableCell>
                                            <TableCell className="pr-6">
                                                <Button size="sm" variant="ghost" onClick={() => openHistory(item)} title="View History">
                                                    <History className="h-4 w-4 text-slate-500 hover:text-brand-600" />
                                                </Button>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableEmpty colSpan={7} message="No items found" />
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100 bg-slate-50/30">
                            <div className="text-sm text-slate-500">
                                Showing page <span className="font-medium text-slate-900">{page}</span> of <span className="font-medium text-slate-900">{totalPages}</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage(p => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    className="h-8 w-8 p-0"
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                    className="h-8 w-8 p-0"
                                >
                                    <ChevronRight className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* History Drawer */}
            <Drawer
                isOpen={isDrawerOpen}
                onClose={() => setIsDrawerOpen(false)}
                title={`Item History: ${selectedItem?.uid} `}
                width="max-w-xl"
            >
                {selectedItem && (
                    <div className="space-y-6">
                        {/* Summary Card */}
                        <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Lot Number</p>
                                    <p className="font-mono text-sm font-medium text-slate-900">{selectedItem.lot_no}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Type</p>
                                    <p className="text-sm font-medium text-slate-900">{selectedItem.component_type}</p>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Status</p>
                                    <div className="mt-1">{renderStatusBadge(selectedItem.status)}</div>
                                </div>
                                <div>
                                    <p className="text-xs text-slate-500 uppercase tracking-wider font-semibold">Manufactured</p>
                                    <p className="text-sm text-slate-700">{selectedItem.manufacture_date}</p>
                                </div>
                            </div>
                        </div>

                        {/* Lifecycle Timeline - Disabled as no API data available yet */}

                        {/* Inspection History */}
                        <div className="pt-4 border-t border-slate-100">
                            <h3 className="text-sm font-bold text-slate-900 mb-4 flex items-center gap-2">
                                <FileText className="h-4 w-4 text-brand-500" />
                                AI Inspection Reports
                            </h3>
                            {isLoadingHistory ? (
                                <div className="flex justify-center py-4">
                                    <RefreshCw className="h-6 w-6 animate-spin text-slate-400" />
                                </div>
                            ) : historyData && historyData.length > 0 ? (
                                <div className="space-y-3">
                                    {historyData.map((report) => {
                                        let result = { issue: 'Unknown', confidence: 0, severity: 'UNKNOWN' };
                                        try {
                                            if (typeof report.result_summary === 'string') {
                                                // Try parsing if it's a JSON string, otherwise use as is or mock
                                                // The backend might return object or string. `vision / history` returns `result_summary` which is JSON type in DB but potentially object here?
                                                // Let's assume it's an object or parseable string
                                                // Actually checking `backend / routes / vision.py`, it returns `result.result_summary` directly.
                                                // If it's stored as JSONB in Postgres, SQLAlchemy might return dict. If Text, string.
                                                // Safety check:
                                                result = typeof report.result_summary === 'string' ? JSON.parse(report.result_summary) : report.result_summary;
                                            } else {
                                                result = report.result_summary;
                                            }
                                        } catch (e) {
                                            // fallback
                                        }

                                        return (
                                            <div key={report.id} className="bg-white p-3 rounded-lg border border-slate-200 shadow-sm flex gap-3">
                                                <div className="h-16 w-16 bg-slate-100 rounded-md flex-shrink-0 overflow-hidden">
                                                    {/* We could try to show image if we had a real path, for now placeholder */}
                                                    <div className="w-full h-full flex items-center justify-center text-slate-400 text-xs">IMG</div>
                                                </div>
                                                <div>
                                                    <div className="flex items-center gap-2">
                                                        <span className="font-semibold text-slate-900 text-sm">{result.issue || 'Inspection'}</span>
                                                        <span className={`text - [10px] px - 1.5 py - 0.5 rounded font - medium ${result.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' :
                                                            result.severity === 'HIGH' ? 'bg-amber-100 text-amber-700' :
                                                                'bg-emerald-100 text-emerald-700'
                                                            } `}>
                                                            {result.severity}
                                                        </span>
                                                    </div>
                                                    <p className="text-xs text-slate-500 mt-1">
                                                        Confidence: {result.confidence ? (result.confidence * 100).toFixed(1) : 0}%
                                                    </p>
                                                    <p className="text-[10px] text-slate-400 mt-1">
                                                        {new Date(report.inspection_date).toLocaleString()}
                                                    </p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <p className="text-sm text-slate-500 italic">No inspection history found.</p>
                            )}
                        </div>
                    </div>
                )}
            </Drawer>
        </motion.div>
    );
}
