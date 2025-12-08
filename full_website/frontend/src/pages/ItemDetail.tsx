import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { ArrowLeft, Clock, Package } from 'lucide-react';
import { motion } from 'framer-motion';

interface ItemDetail {
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
    metadata?: string | Record<string, any>;
    created_at: string;
    updated_at?: string;
    events?: {
        id: number;
        event_type: string;
        timestamp: string;
        details: Record<string, any>;
    }[];
}

export default function ItemDetail() {
    const { uid } = useParams<{ uid: string }>();

    const { data: item, isLoading, error } = useQuery<ItemDetail>({
        queryKey: ['item', uid],
        queryFn: async () => {
            const res = await api.get(`/items/${uid}`);
            return res.data;
        }
    });

    if (isLoading) return <div className="p-8 text-center">Loading...</div>;
    if (error || !item) return <div className="p-8 text-center text-red-600">Item not found</div>;

    return (
        <div className="space-y-6">
            <div className="flex items-center gap-4">
                <Link to="/items">
                    <Button variant="ghost" size="icon">
                        <ArrowLeft size={20} />
                    </Button>
                </Link>
                <h1 className="text-2xl font-bold text-gray-900">Item Details</h1>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* QR Code Card */}
                {item.qr_image_url && (
                    <Card>
                        <CardHeader>
                            <CardTitle>QR Code</CardTitle>
                        </CardHeader>
                        <CardContent className="flex flex-col items-center">
                            <img 
                                src={item.qr_image_url} 
                                alt="QR Code" 
                                className="w-full max-w-xs border-4 border-gray-200 rounded-lg shadow-lg"
                            />
                            <a 
                                href={item.qr_image_url} 
                                download={`${item.uid}.png`}
                                className="mt-4 text-sm text-primary-600 hover:text-primary-700 font-medium"
                            >
                                Download QR Code
                            </a>
                        </CardContent>
                    </Card>
                )}

                {/* Main Info */}
                <Card className={item.qr_image_url ? 'lg:col-span-2' : 'lg:col-span-3'}>
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            <span className="flex items-center gap-2">
                                <Package className="text-primary-600" />
                                {item.uid}
                            </span>
                            <Chip
                                label={item.current_status || item.status}
                                variant={
                                    (item.current_status || item.status) === 'manufactured' ? 'success' :
                                    (item.current_status || item.status) === 'installed' ? 'info' :
                                    (item.current_status || item.status) === 'rejected' ? 'danger' :
                                    (item.current_status || item.status) === 'active' ? 'success' : 'default'
                                }
                            />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            <div>
                                <label className="text-sm font-medium text-gray-500">Component Type</label>
                                <p className="text-lg font-medium text-gray-900">{item.component_type}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Lot Number</label>
                                <p className="text-lg font-medium text-gray-900">{item.lot_number || 'N/A'}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Vendor ID</label>
                                <p className="text-lg font-medium text-gray-900">{item.vendor_id || 'N/A'}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Quantity</label>
                                <p className="text-lg font-medium text-gray-900">{item.quantity || 1}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Warranty</label>
                                <p className="text-lg font-medium text-gray-900">
                                    {item.warranty_years ? `${item.warranty_years} years` : 'N/A'}
                                </p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Manufacture Date</label>
                                <p className="text-lg font-medium text-gray-900">
                                    {item.manufacture_date ? new Date(item.manufacture_date).toLocaleDateString() : 'N/A'}
                                </p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Created At</label>
                                <p className="text-lg font-medium text-gray-900">
                                    {new Date(item.created_at).toLocaleString()}
                                </p>
                            </div>
                            {item.updated_at && (
                                <div>
                                    <label className="text-sm font-medium text-gray-500">Updated At</label>
                                    <p className="text-lg font-medium text-gray-900">
                                        {new Date(item.updated_at).toLocaleString()}
                                    </p>
                                </div>
                            )}
                        </div>

                        {item.metadata && (
                            <div>
                                <label className="text-sm font-medium text-gray-500 mb-2 block">Metadata</label>
                                <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm overflow-x-auto border border-gray-200">
                                    <pre>{typeof item.metadata === 'string' ? JSON.stringify(JSON.parse(item.metadata), null, 2) : JSON.stringify(item.metadata, null, 2)}</pre>
                                </div>
                            </div>
                        )}
                    </CardContent>
                </Card>

                {/* Timeline */}
                {!item.qr_image_url && (
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <Clock size={20} />
                                Timeline
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <div className="relative border-l border-gray-200 ml-3 space-y-6">
                                {item.events?.map((event, index) => (
                                    <motion.div
                                        key={event.id}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: index * 0.1 }}
                                        className="ml-6 relative"
                                    >
                                        <span className="absolute -left-[31px] top-1 h-4 w-4 rounded-full bg-white border-2 border-primary-500" />
                                        <div className="flex flex-col">
                                            <span className="text-sm font-semibold text-gray-900">{event.event_type}</span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(event.timestamp).toLocaleString()}
                                            </span>
                                            {event.details && Object.keys(event.details).length > 0 && (
                                                <div className="mt-2 text-xs bg-gray-50 p-2 rounded border border-gray-100">
                                                    <pre className="whitespace-pre-wrap">
                                                        {JSON.stringify(event.details, null, 2)}
                                                    </pre>
                                                </div>
                                            )}
                                        </div>
                                    </motion.div>
                                ))}
                                {(!item.events || item.events.length === 0) && (
                                    <div className="ml-6 text-sm text-gray-500">No events recorded</div>
                                )}
                            </div>
                        </CardContent>
                    </Card>
                )}
            </div>
        </div>
    );
}
