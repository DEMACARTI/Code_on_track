import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableLoading, TableEmpty } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { SearchInput } from '../components/ui/SearchInput';
import { Chip } from '../components/ui/Chip';
import { ChevronLeft, ChevronRight, Trash2, AlertTriangle, RefreshCw, CheckCircle, XCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Item {
    uid: string;
    component_type: string;
    status: string;
    current_status?: string;
    lot_number?: string;
    vendor_id?: number;
    quantity?: number;
    warranty_years?: number;
    manufacture_date?: string;
    qr_image_url?: string;
    metadata?: string;
    created_at?: string;
    updated_at?: string;
}

interface ItemsResponse {
    items: Item[];
    total: number;
    page: number;
    size: number;
}

export default function Items() {
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
    const [viewingQR, setViewingQR] = useState<Item | null>(null);
    const [notification, setNotification] = useState<{ type: 'success' | 'error', message: string } | null>(null);
    const pageSize = 20; // Increased page size
    const queryClient = useQueryClient();

    const { data, isLoading, error } = useQuery<ItemsResponse | Item[]>({
        queryKey: ['items', search, page],
        queryFn: async () => {
            const res = await api.get('/items', { params: { q: search, page, page_size: pageSize } });
            // Handle both array (legacy) and paginated response
            if (Array.isArray(res.data)) {
                return res.data;
            }
            return res.data;
        }
    });

    const items = Array.isArray(data) ? data : data?.items || [];
    const total = Array.isArray(data) ? data.length : data?.total || 0;
    const totalPages = Math.ceil(total / pageSize);

    // Delete mutations
    const deleteMutation = useMutation({
        mutationFn: async (uids: string[]) => {
            const response = await api.post('/items/bulk-delete', uids);
            return response.data;
        },
        onSuccess: (data, uids) => {
            queryClient.invalidateQueries({ queryKey: ['items'] });
            setSelectedItems(new Set());
            setShowDeleteConfirm(false);
            
            let message = data.message || `Successfully deleted ${data.deleted_count || uids.length} item${uids.length > 1 ? 's' : ''}`;
            if (data.warning) {
                message += ` (${data.warning})`;
            }
            
            setNotification({
                type: 'success',
                message
            });
            setTimeout(() => setNotification(null), 5000);
        },
        onError: (error: any) => {
            setShowDeleteConfirm(false);
            const errorDetail = error.response?.data?.detail || 'Failed to delete items';
            setNotification({
                type: 'error',
                message: errorDetail
            });
            setTimeout(() => setNotification(null), 8000);
        }
    });

    const deleteAllMutation = useMutation({
        mutationFn: async () => {
            await api.delete('/items/all', {
                params: { confirm: 'DELETE_ALL_ITEMS' }
            });
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['items'] });
            setSelectedItems(new Set());
            setShowDeleteAllConfirm(false);
            setNotification({
                type: 'success',
                message: `Successfully deleted all items from inventory`
            });
            setTimeout(() => setNotification(null), 5000);
        },
        onError: (error: any) => {
            setShowDeleteAllConfirm(false);
            setNotification({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to delete all items'
            });
            setTimeout(() => setNotification(null), 5000);
        }
    });

    const handleSelectAll = () => {
        if (selectedItems.size === items.length) {
            setSelectedItems(new Set());
        } else {
            setSelectedItems(new Set(items.map(item => item.uid)));
        }
    };

    const handleSelectItem = (uid: string) => {
        const newSelected = new Set(selectedItems);
        if (newSelected.has(uid)) {
            newSelected.delete(uid);
        } else {
            newSelected.add(uid);
        }
        setSelectedItems(newSelected);
    };

    const handleDeleteSelected = () => {
        deleteMutation.mutate(Array.from(selectedItems));
    };

    const handleDeleteAll = () => {
        deleteAllMutation.mutate();
    };

    const handleRefresh = () => {
        queryClient.invalidateQueries({ queryKey: ['items'] });
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900">Items</h1>
                    <p className="text-sm text-gray-500 mt-1">Total: {total.toLocaleString()} items in inventory</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="text-primary-600 hover:text-primary-700 hover:bg-primary-50"
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    {selectedItems.size > 0 && (
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowDeleteConfirm(true)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete Selected ({selectedItems.size})
                        </Button>
                    )}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setShowDeleteAllConfirm(true)}
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete All
                    </Button>
                </div>
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                    <CardTitle>Inventory</CardTitle>
                    <div className="w-full sm:w-72">
                        <SearchInput
                            value={search}
                            onChange={(val) => { setSearch(val); setPage(1); }}
                            placeholder="Search items..."
                        />
                    </div>
                </CardHeader>
                <CardContent>
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead className="w-12">
                                        <input
                                            type="checkbox"
                                            checked={items.length > 0 && selectedItems.size === items.length}
                                            onChange={handleSelectAll}
                                            className="rounded border-gray-300"
                                        />
                                    </TableHead>
                                    <TableHead>QR</TableHead>
                                    <TableHead>UID</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Lot #</TableHead>
                                    <TableHead>Vendor</TableHead>
                                    <TableHead>Qty</TableHead>
                                    <TableHead>Warranty</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Mfg Date</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableLoading colSpan={11} />
                                ) : error ? (
                                    <TableRow>
                                        <td colSpan={11} className="h-24 text-center">
                                            <div className="text-red-500 mb-2">Error loading items</div>
                                            <div className="text-sm text-gray-600">
                                                {error instanceof Error ? error.message : 'Unknown error'}
                                            </div>
                                            <div className="text-xs text-gray-500 mt-2">
                                                Make sure you're logged in and the backend is running on port 8001
                                            </div>
                                        </td>
                                    </TableRow>
                                ) : items.length > 0 ? (
                                    items.map((item) => (
                                        <TableRow key={item.uid}>
                                            <TableCell>
                                                <input
                                                    type="checkbox"
                                                    checked={selectedItems.has(item.uid)}
                                                    onChange={() => handleSelectItem(item.uid)}
                                                    className="rounded border-gray-300"
                                                />
                                            </TableCell>
                                            <TableCell>
                                                {item.qr_image_url ? (
                                                    <button
                                                        onClick={() => setViewingQR(item)}
                                                        className="hover:opacity-75 transition-opacity"
                                                    >
                                                        <img 
                                                            src={item.qr_image_url} 
                                                            alt="QR" 
                                                            className="w-10 h-10 object-contain border rounded"
                                                        />
                                                    </button>
                                                ) : (
                                                    <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center text-gray-400 text-xs">
                                                        N/A
                                                    </div>
                                                )}
                                            </TableCell>
                                            <TableCell className="font-mono text-xs max-w-[200px] truncate" title={item.uid}>
                                                {item.uid}
                                            </TableCell>
                                            <TableCell className="font-medium">{item.component_type}</TableCell>
                                            <TableCell className="text-sm text-gray-600">{item.lot_number || '-'}</TableCell>
                                            <TableCell className="text-sm text-gray-600">{item.vendor_id || '-'}</TableCell>
                                            <TableCell className="text-sm text-gray-600">{item.quantity || 1}</TableCell>
                                            <TableCell className="text-sm text-gray-600">{item.warranty_years ? `${item.warranty_years}y` : '-'}</TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={item.current_status || item.status || 'unknown'}
                                                    variant={
                                                        (item.current_status || item.status) === 'manufactured' ? 'success' :
                                                        (item.current_status || item.status) === 'installed' ? 'info' :
                                                        (item.current_status || item.status) === 'rejected' ? 'danger' : 'default'
                                                    }
                                                />
                                            </TableCell>
                                            <TableCell className="text-sm text-gray-600">
                                                {item.manufacture_date ? new Date(item.manufacture_date).toLocaleDateString() : '-'}
                                            </TableCell>
                                            <TableCell>
                                                <Link to={`/items/${item.uid}`}>
                                                    <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-900 hover:bg-primary-50">
                                                        View
                                                    </Button>
                                                </Link>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableEmpty colSpan={11} message="No items found" />
                                )}
                            </TableBody>
                        </Table>
                    </div>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-end space-x-2 py-4">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </Button>
                            <span className="text-sm text-gray-600">
                                Page {page} of {totalPages}
                            </span>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                            >
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Delete Selected Confirmation Modal */}
            {showDeleteConfirm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                                <AlertTriangle className="h-6 w-6 text-red-600" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Delete Selected Items</h3>
                                <p className="text-sm text-gray-500">This action cannot be undone</p>
                            </div>
                        </div>
                        <p className="text-gray-600 mb-6">
                            Are you sure you want to delete {selectedItems.size} selected item(s)? 
                            This will permanently remove them from the database.
                        </p>
                        <div className="flex justify-end gap-3">
                            <Button
                                variant="outline"
                                onClick={() => setShowDeleteConfirm(false)}
                                disabled={deleteMutation.isPending}
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="danger"
                                onClick={handleDeleteSelected}
                                disabled={deleteMutation.isPending}
                                className="min-w-[120px]"
                            >
                                {deleteMutation.isPending ? (
                                    <span className="flex items-center gap-2">
                                        <RefreshCw className="h-4 w-4 animate-spin" />
                                        Deleting...
                                    </span>
                                ) : 'Delete Items'}
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {/* Delete All Confirmation Modal */}
            {showDeleteAllConfirm && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 flex items-center justify-center">
                                <AlertTriangle className="h-6 w-6 text-red-600" />
                            </div>
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Delete All Items</h3>
                                <p className="text-sm text-red-600 font-medium">⚠️ DANGER ZONE</p>
                            </div>
                        </div>
                        <p className="text-gray-600 mb-4">
                            Are you sure you want to delete <strong>ALL {total} items</strong>? 
                            This will permanently remove every item from the database.
                        </p>
                        <div className="bg-red-50 border border-red-200 rounded-md p-3 mb-6">
                            <p className="text-sm text-red-800 font-medium">
                                This action is irreversible and will delete all QR codes, inspection records, 
                                and related data for all items.
                            </p>
                        </div>
                        <div className="flex justify-end gap-3">
                            <Button
                                variant="outline"
                                onClick={() => setShowDeleteAllConfirm(false)}
                                disabled={deleteAllMutation.isPending}
                            >
                                Cancel
                            </Button>
                            <Button
                                variant="danger"
                                onClick={handleDeleteAll}
                                disabled={deleteAllMutation.isPending}
                                className="min-w-[140px]"
                            >
                                {deleteAllMutation.isPending ? (
                                    <span className="flex items-center gap-2">
                                        <RefreshCw className="h-4 w-4 animate-spin" />
                                        Deleting...
                                    </span>
                                ) : 'Delete Everything'}
                            </Button>
                        </div>
                    </div>
                </div>
            )}

            {/* QR Code Viewer Modal */}
            {viewingQR && (
                <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={() => setViewingQR(null)}>
                    <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4" onClick={(e) => e.stopPropagation()}>
                        <div className="flex justify-between items-start mb-4">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">QR Code Details</h3>
                                <p className="text-sm text-gray-500 font-mono mt-1">{viewingQR.uid}</p>
                            </div>
                            <button
                                onClick={() => setViewingQR(null)}
                                className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
                            >
                                ×
                            </button>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            {/* QR Code Image */}
                            <div className="flex flex-col items-center justify-center bg-gray-50 rounded-lg p-6">
                                {viewingQR.qr_image_url ? (
                                    <img 
                                        src={viewingQR.qr_image_url} 
                                        alt="QR Code" 
                                        className="w-64 h-64 object-contain border-4 border-white shadow-lg rounded"
                                    />
                                ) : (
                                    <div className="w-64 h-64 bg-gray-200 rounded flex items-center justify-center text-gray-400">
                                        No QR Code
                                    </div>
                                )}
                                {viewingQR.qr_image_url && (
                                    <a 
                                        href={viewingQR.qr_image_url} 
                                        download={`${viewingQR.uid}.png`}
                                        className="mt-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
                                    >
                                        Download QR Code
                                    </a>
                                )}
                            </div>

                            {/* Item Details */}
                            <div className="space-y-3">
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Component Type</label>
                                    <p className="text-sm font-medium text-gray-900">{viewingQR.component_type}</p>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Lot Number</label>
                                    <p className="text-sm text-gray-900">{viewingQR.lot_number || 'N/A'}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="text-xs font-semibold text-gray-500 uppercase">Vendor ID</label>
                                        <p className="text-sm text-gray-900">{viewingQR.vendor_id || 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-semibold text-gray-500 uppercase">Quantity</label>
                                        <p className="text-sm text-gray-900">{viewingQR.quantity || 1}</p>
                                    </div>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <div>
                                        <label className="text-xs font-semibold text-gray-500 uppercase">Warranty</label>
                                        <p className="text-sm text-gray-900">{viewingQR.warranty_years ? `${viewingQR.warranty_years} years` : 'N/A'}</p>
                                    </div>
                                    <div>
                                        <label className="text-xs font-semibold text-gray-500 uppercase">Status</label>
                                        <Chip
                                            label={viewingQR.current_status || viewingQR.status || 'unknown'}
                                            variant={
                                                (viewingQR.current_status || viewingQR.status) === 'manufactured' ? 'success' :
                                                (viewingQR.current_status || viewingQR.status) === 'installed' ? 'info' :
                                                (viewingQR.current_status || viewingQR.status) === 'rejected' ? 'danger' : 'default'
                                            }
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Manufacture Date</label>
                                    <p className="text-sm text-gray-900">
                                        {viewingQR.manufacture_date ? new Date(viewingQR.manufacture_date).toLocaleDateString() : 'N/A'}
                                    </p>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-gray-500 uppercase">Created</label>
                                    <p className="text-sm text-gray-900">
                                        {viewingQR.created_at ? new Date(viewingQR.created_at).toLocaleString() : 'N/A'}
                                    </p>
                                </div>
                                {viewingQR.metadata && (
                                    <div>
                                        <label className="text-xs font-semibold text-gray-500 uppercase">Metadata</label>
                                        <pre className="text-xs text-gray-700 bg-gray-50 p-2 rounded mt-1 overflow-x-auto">
                                            {JSON.stringify(JSON.parse(viewingQR.metadata), null, 2)}
                                        </pre>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="mt-6 flex justify-end gap-3">
                            <Button variant="outline" onClick={() => setViewingQR(null)}>
                                Close
                            </Button>
                            <Link to={`/items/${viewingQR.uid}`}>
                                <Button variant="primary">
                                    View Full Details
                                </Button>
                            </Link>
                        </div>
                    </div>
                </div>
            )}

            {/* Toast Notification */}
            <AnimatePresence>
                {notification && (
                    <motion.div
                        initial={{ opacity: 0, y: 50 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 50 }}
                        className={`fixed bottom-6 right-6 z-50 p-4 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] ${
                            notification.type === 'success' 
                                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' 
                                : 'bg-rose-50 text-rose-800 border border-rose-200'
                        }`}
                    >
                        {notification.type === 'success' ? (
                            <CheckCircle className="h-5 w-5 flex-shrink-0" />
                        ) : (
                            <XCircle className="h-5 w-5 flex-shrink-0" />
                        )}
                        <p className="font-medium flex-1">{notification.message}</p>
                        <button
                            onClick={() => setNotification(null)}
                            className="ml-2 p-1 hover:bg-black/5 rounded-full flex-shrink-0"
                        >
                            <span className="sr-only">Close</span>
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
