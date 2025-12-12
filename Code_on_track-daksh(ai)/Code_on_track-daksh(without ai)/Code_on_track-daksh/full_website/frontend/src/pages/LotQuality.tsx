import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableHead, TableHeader, TableRow, TableCell, TableLoading, TableEmpty } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { RefreshCw, Activity, Eye, AlertTriangle } from 'lucide-react';
import { motion } from 'framer-motion';
import { useToast } from '../components/ui/Toast';

// Matches backend response EXACTLY
interface LotQualityData {
    lot_no: string;
    component: string;
    vendor_id: number;
    item_count: number;
    failed: number;
    rate: number;
    anomaly_score: number;
    reason: string;
    status: string; // FAILED, PASSED, WARNING, CRITICAL
    last_inspected: string;
}

export default function LotQuality() {
    const [showOnlyAnomalous, setShowOnlyAnomalous] = useState(false);
    const { addToast } = useToast();

    const { data: lots, isLoading, error, refetch } = useQuery<LotQualityData[]>({
        queryKey: ['lot_quality'],
        queryFn: async () => {
            // Frontend Fetch URL match
            const res = await api.get('/lot_quality/');
            // Note: Added trailing slash to avoid 308 redirect issues seen in curl
            return res.data;
        }
    });

    const filteredLots = lots
        ? (showOnlyAnomalous ? lots.filter(l => l.status !== 'PASSED') : lots)
        : [];

    const getStatusVariant = (status: string) => {
        switch (status) {
            case 'FAILED': return 'danger';
            case 'CRITICAL': return 'danger';
            case 'WARNING': return 'warning';
            case 'PASSED': return 'success';
            default: return 'default';
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
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Lot Quality</h1>
                    <p className="text-slate-500 mt-1">Monitor quality metrics and anomalies per lot.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => refetch()}
                        disabled={isLoading}
                        className="bg-white hover:bg-slate-50"
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    <Button
                        size="sm"
                        onClick={async () => {
                            try {
                                await api.post('/lot_quality/recompute');
                                addToast('Analysis job started successfully', 'success');
                                setTimeout(() => refetch(), 2000); // Wait for job
                            } catch (e) {
                                console.error(e);
                                addToast('Failed to start analysis job', 'error');
                            }
                        }}
                        className="bg-brand-600 hover:bg-brand-700 text-white shadow-sm"
                    >
                        <Activity className="h-4 w-4 mr-2" />
                        Recompute Analysis
                    </Button>
                </div>
            </div>

            <Card className="glass border-0 shadow-lg shadow-slate-200/50 overflow-hidden">
                <CardHeader className="flex flex-col md:flex-row items-center justify-between pb-6 border-b border-slate-100/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-brand-50 rounded-lg">
                            <Activity className="h-5 w-5 text-brand-600" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-bold text-slate-900">Lot Performance</CardTitle>
                            <p className="text-sm text-slate-500">
                                {filteredLots.length} lots found
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <label className="flex items-center gap-2 text-sm font-medium text-slate-700 cursor-pointer">
                            <input
                                type="checkbox"
                                checked={showOnlyAnomalous}
                                onChange={(e) => setShowOnlyAnomalous(e.target.checked)}
                                className="rounded border-slate-300 text-brand-600 focus:ring-brand-500"
                            />
                            Show only anomalies
                        </label>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
                                    <TableHead className="pl-6 text-xs uppercase tracking-wider font-semibold text-slate-500">Lot No</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Component</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Vendor ID</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-right">Items</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-center">Status</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-center">Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableLoading colSpan={6} />
                                ) : error ? (
                                    <TableRow>
                                        <td colSpan={6} className="h-32 text-center text-rose-500">
                                            <div className="flex flex-col items-center justify-center">
                                                <AlertTriangle className="h-8 w-8 mb-2" />
                                                <p>Error loading lot quality data</p>
                                            </div>
                                        </td>
                                    </TableRow>
                                ) : filteredLots.length > 0 ? (
                                    filteredLots.map((lot) => (
                                        <TableRow
                                            key={lot.lot_no}
                                            className={`transition-colors border-b border-slate-50 last:border-0 ${lot.status !== 'PASSED' ? 'bg-rose-50/50 hover:bg-rose-100/50' : 'hover:bg-brand-50/30'}`}
                                        >
                                            <TableCell className="pl-6 font-mono text-sm font-medium text-brand-600">
                                                {lot.lot_no}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-700">{lot.component}</TableCell>
                                            <TableCell className="text-sm text-slate-700">{lot.vendor_id}</TableCell>
                                            <TableCell className="text-sm text-slate-700 text-right">{lot.item_count}</TableCell>
                                            <TableCell className="text-center">
                                                <Chip
                                                    label={lot.status}
                                                    variant={getStatusVariant(lot.status) as any}
                                                    className="shadow-sm"
                                                />
                                            </TableCell>
                                            <TableCell className="text-center">
                                                <Link to={`/items?lot_no=${lot.lot_no}`}>
                                                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                                                        <Eye className="h-4 w-4 text-slate-500 hover:text-brand-600" />
                                                    </Button>
                                                </Link>
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableEmpty colSpan={6} message="No lot quality data found" />
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
