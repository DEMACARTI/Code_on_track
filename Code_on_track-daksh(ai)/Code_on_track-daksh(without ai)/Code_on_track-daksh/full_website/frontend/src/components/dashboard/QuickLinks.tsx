import { useNavigate } from 'react-router-dom';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { Zap, AlertTriangle, RefreshCw, Layers } from 'lucide-react';
import api from '../../api/axios';
import { useToast } from '../ui/Toast';

export const QuickLinks = () => {
    const navigate = useNavigate();
    const { addToast } = useToast();

    const fetchDebugStatus = async () => {
        try {
            const res = await api.get('/debug/status');
            console.log('Debug Status:', res.data);
            // We could update a global state here if we had one, 
            // but for now relying on window.location.reload meant we refresh entire UI anyway.
            // The prompt asks to "Refresh UI counters". 
            // Since we don't have global state for counters easily accessible, 
            // let's just trigger a query invalidation if we had react-query client accessible, 
            // or use the window reload as a brute force (or just let the user click Refresh).
            // Actually, `window.location.reload()` is available in the Dashboard, maybe we can inject failure/success toast.
            return res.data;
        } catch (e) {
            console.error(e);
        }
    };

    const runHealthJob = async () => {
        try {
            addToast('Running Health Score Analysis...', 'info');
            const res = await api.post('/lot_health/run_job');
            const stats = res.data.stats;
            addToast(`Health Job: Processed ${stats.processed}, Upserted ${stats.upserted}`, 'success');
            await fetchDebugStatus();
            // Optional: trigger refresh
            setTimeout(() => window.location.reload(), 2000);
        } catch (e: any) {
            const errorMsg = e.response?.data?.error || e.message;
            addToast(`Failed to start Health Job: ${errorMsg}`, 'error');
        }
    };

    const runAnomalyJob = async () => {
        try {
            addToast('Running Anomaly Detection...', 'info');
            // 1. Run Anomaly Job
            await api.post('/lot_quality/run_job');
            addToast('Anomaly Job Complete. Starting Health Job...', 'success');

            // 2. Run Health Job
            const res = await api.post('/lot_health/run_job');
            const stats = res.data.stats;

            // 3. Show Final Summary
            addToast(`Sequence Complete! Health Stats: Processed ${stats.processed}`, 'success');

            await fetchDebugStatus();
            setTimeout(() => window.location.reload(), 2000);
        } catch (e: any) {
            const errorMsg = e.response?.data?.error || e.message;
            addToast(`Job Sequence Failed: ${errorMsg}`, 'error');
        }
    };

    return (
        <Card className="p-6">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
                <Zap className="h-5 w-5 text-amber-500 fill-amber-500" />
                Quick Actions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col gap-2 items-center justify-center hover:border-rose-200 hover:bg-rose-50"
                    onClick={() => navigate('/lot-health?risk_level=CRITICAL')}
                >
                    <AlertTriangle className="h-6 w-6 text-rose-500" />
                    <span className="text-slate-700 font-medium">View Critical Lots</span>
                </Button>

                <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col gap-2 items-center justify-center hover:border-brand-200 hover:bg-brand-50"
                    onClick={() => navigate('/lot-quality')}
                >
                    <Layers className="h-6 w-6 text-brand-600" />
                    <span className="text-slate-700 font-medium">Lot Quality</span>
                </Button>

                <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col gap-2 items-center justify-center hover:border-emerald-200 hover:bg-emerald-50"
                    onClick={runHealthJob}
                >
                    <RefreshCw className="h-6 w-6 text-emerald-500" />
                    <span className="text-slate-700 font-medium">Run Health Job</span>
                </Button>

                <Button
                    variant="outline"
                    className="h-auto py-4 flex flex-col gap-2 items-center justify-center hover:border-indigo-200 hover:bg-indigo-50"
                    onClick={runAnomalyJob}
                >
                    <RefreshCw className="h-6 w-6 text-indigo-500" />
                    <span className="text-slate-700 font-medium">Check Anomalies</span>
                </Button>
            </div>
        </Card>
    );
};
