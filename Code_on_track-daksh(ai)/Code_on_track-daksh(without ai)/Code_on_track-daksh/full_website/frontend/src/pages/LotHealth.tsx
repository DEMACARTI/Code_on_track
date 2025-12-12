import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableHead, TableHeader, TableRow, TableCell, TableLoading, TableEmpty } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { RefreshCw, HeartPulse, Eye, AlertTriangle, Filter } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface LotHealthData {
    lot_no: string;
    component_type: string;
    health_score: number;
    risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    recommended_action: string;
    next_suggested_inspection_date: string;
}

export default function LotHealth() {
    const [searchParams] = useSearchParams();
    const riskFilter = searchParams.get('risk_level');
    const [filterAction, setFilterAction] = useState<string>('all');

    const { data: lots, isLoading, error, refetch } = useQuery<LotHealthData[]>({
        queryKey: ['lot_health', riskFilter],
        queryFn: async () => {
            const params: any = {};
            if (riskFilter) params.risk_level = riskFilter;

            const res = await api.get('/lot_health/', { params });
            return res.data;
        }
    });

    const triggerScoring = async () => {
        try {
            await api.post('/lot_health/run_job');
            refetch();
        } catch (e) {
            console.error(e);
        }
    };

    const uniqueActions = useMemo(() => {
        if (!lots) return [];
        return Array.from(new Set(lots.map(l => l.recommended_action))).filter(Boolean).sort();
    }, [lots]);

    const filteredLots = useMemo(() => {
        if (!lots) return [];
        return lots.filter(lot => {
            if (filterAction === 'all') return true;
            return lot.recommended_action === filterAction;
        });
    }, [lots, filterAction]);

    const getRiskColor = (risk: string) => {
        switch (risk) {
            case 'CRITICAL': return 'danger';
            case 'HIGH': return 'warning';
            case 'MEDIUM': return 'warning'; // Or yellow if available, defaulting to warning
            case 'LOW': return 'success';
            default: return 'default';
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 80) return 'text-emerald-600';
        if (score >= 60) return 'text-amber-600';
        if (score >= 40) return 'text-orange-600';
        return 'text-rose-600';
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                        {riskFilter ? `${riskFilter.charAt(0) + riskFilter.slice(1).toLowerCase()} Component Health` : 'Component Health'}
                    </h1>
                    <p className="text-slate-500 mt-1">Predictive health scoring and risk management.</p>
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
                        onClick={triggerScoring}
                        className="bg-brand-600 hover:bg-brand-700 text-white shadow-sm"
                    >
                        <HeartPulse className="h-4 w-4 mr-2" />
                        Update Scores
                    </Button>
                </div>
            </div>

            <Card className="glass border-0 shadow-lg shadow-slate-200/50 overflow-hidden">
                <CardHeader className="flex flex-col md:flex-row items-center justify-between pb-6 border-b border-slate-100/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-rose-50 rounded-lg">
                            <HeartPulse className="h-5 w-5 text-rose-600" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-bold text-slate-900">Health Overview</CardTitle>
                            <p className="text-sm text-slate-500">
                                {filteredLots.length} lots found
                            </p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2">
                        <Filter className="h-4 w-4 text-slate-500" />
                        <select
                            value={filterAction}
                            onChange={(e) => setFilterAction(e.target.value)}
                            className="h-9 rounded-md border border-slate-300 bg-white px-3 py-1 text-sm shadow-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500 cursor-pointer"
                        >
                            <option value="all">All Actions</option>
                            {uniqueActions.map(action => (
                                <option key={action} value={action}>{action}</option>
                            ))}
                        </select>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
                                    <TableHead className="pl-6 text-xs uppercase tracking-wider font-semibold text-slate-500">Lot No</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Component</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-center">Health Score</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-center">Risk Level</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Recommended Action</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Next Inspection</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500 text-center">Actions</TableHead>
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
                                                <p>Error loading health data</p>
                                            </div>
                                        </td>
                                    </TableRow>
                                ) : filteredLots && filteredLots.length > 0 ? (
                                    filteredLots.map((lot) => (
                                        <TableRow
                                            key={lot.lot_no}
                                            className={`transition-colors border-b border-slate-50 last:border-0 ${lot.risk_level === 'CRITICAL' ? 'bg-rose-50/30' :
                                                lot.risk_level === 'HIGH' ? 'bg-orange-50/30' : ''
                                                }`}
                                        >
                                            <TableCell className="pl-6 font-mono text-sm font-medium text-slate-700">
                                                {lot.lot_no}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-600">{lot.component_type}</TableCell>
                                            <TableCell className="text-center">
                                                <span className={`text-lg font-bold ${getScoreColor(lot.health_score)}`}>
                                                    {lot.health_score.toFixed(0)}
                                                </span>
                                            </TableCell>
                                            <TableCell className="text-center">
                                                <Chip
                                                    label={lot.risk_level}
                                                    variant={getRiskColor(lot.risk_level) as any}
                                                    className="font-bold shadow-sm"
                                                />
                                            </TableCell>
                                            <TableCell className="text-sm font-medium text-slate-700">
                                                {lot.recommended_action}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-500">
                                                {new Date(lot.next_suggested_inspection_date).toLocaleDateString()}
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
                                    <TableEmpty colSpan={7} message="No health data found." />
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </motion.div>
    );
}
