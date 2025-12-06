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
    created_at: string;
    vendor_id: number;
    metadata: Record<string, any>;
    events: {
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
                {/* Main Info */}
                <Card className="lg:col-span-2">
                    <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                            <span className="flex items-center gap-2">
                                <Package className="text-primary-600" />
                                {item.uid}
                            </span>
                            <Chip
                                label={item.status}
                                variant={item.status === 'active' ? 'success' : 'default'}
                            />
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-sm font-medium text-gray-500">Component Type</label>
                                <p className="text-lg font-medium text-gray-900">{item.component_type}</p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Created At</label>
                                <p className="text-lg font-medium text-gray-900">
                                    {new Date(item.created_at).toLocaleString()}
                                </p>
                            </div>
                            <div>
                                <label className="text-sm font-medium text-gray-500">Vendor ID</label>
                                <p className="text-lg font-medium text-gray-900">{item.vendor_id}</p>
                            </div>
                        </div>

                        <div>
                            <label className="text-sm font-medium text-gray-500 mb-2 block">Metadata</label>
                            <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm overflow-x-auto border border-gray-200">
                                <pre>{JSON.stringify(item.metadata, null, 2)}</pre>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Timeline */}
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
            </div>
        </div>
    );
}
