import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Chip } from '../components/ui/Chip';
import { Zap, Save, Truck, Clock, MapPin } from 'lucide-react';
import { motion } from 'framer-motion';

interface RouteStop {
    lot_no: string;
    risk: string;
    task: string;
    eta: string;
}

interface TeamRoute {
    team: string;
    depot: string;
    total_hours: number;
    lots: RouteStop[];
}

interface OptimizationResult {
    routes: TeamRoute[];
}

export default function SchedulerOptimized() {
    const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
    const [isOptimizing, setIsOptimizing] = useState(false);

    // Fetch existing saved routes on load
    useQuery({
        queryKey: ['scheduler_routes'],
        queryFn: async () => {
            const res = await api.get('/schedule/routes');
            if (res.data && res.data.length > 0) {
                setOptimizationResult({ routes: res.data });
            }
            return res.data;
        }
    });

    const handleOptimize = async () => {
        setIsOptimizing(true);
        try {
            const res = await api.post('/schedule/optimize', { limit_hours: 8 });
            setOptimizationResult(res.data);
        } catch (e) {
            console.error(e);
        } finally {
            setIsOptimizing(false);
        }
    };

    const handleSave = async () => {
        if (!optimizationResult) return;
        try {
            await api.post('/schedule/save_optimized', optimizationResult);
            // Optionally show toast
        } catch (e) {
            console.error(e);
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
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Intelligent Scheduler</h1>
                    <p className="text-slate-500 mt-1">AI-powered maintenance routing using OR-Tools.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        onClick={handleOptimize}
                        disabled={isOptimizing}
                        className="bg-white hover:bg-slate-50"
                    >
                        <Zap className={`h-4 w-4 mr-2 ${isOptimizing ? 'animate-pulse' : 'text-amber-500'}`} />
                        {isOptimizing ? 'Optimizing...' : 'Generate Optimal Schedule'}
                    </Button>
                    <Button
                        onClick={handleSave}
                        disabled={!optimizationResult}
                        className="bg-brand-600 hover:bg-brand-700 text-white shadow-sm"
                    >
                        <Save className="h-4 w-4 mr-2" />
                        Save Schedule
                    </Button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {(optimizationResult?.routes || []).map((route, idx) => (
                    <Card key={idx} className="glass border-0 shadow-lg shadow-slate-200/50">
                        <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-slate-100/50">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-indigo-50 rounded-lg">
                                    <Truck className="h-5 w-5 text-indigo-600" />
                                </div>
                                <div>
                                    <CardTitle className="text-lg font-bold text-slate-900">{route.team}</CardTitle>
                                    <div className="flex items-center text-xs text-slate-500 mt-1">
                                        <MapPin className="h-3 w-3 mr-1" />
                                        Depot: {route.depot}
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="flex items-center bg-slate-100 px-2 py-1 rounded text-xs font-medium text-slate-600">
                                    <Clock className="h-3 w-3 mr-1" />
                                    {route.total_hours} hrs
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent className="pt-4">
                            <div className="space-y-4">
                                {route.lots.map((stop, sIdx) => (
                                    <div key={sIdx} className="relative pl-6 pb-2 border-l-2 border-slate-200 last:border-0 last:pb-0">
                                        <div className="absolute -left-[5px] top-0 h-2.5 w-2.5 rounded-full bg-slate-300 ring-4 ring-white" />
                                        <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
                                            <div className="flex justify-between items-start mb-1">
                                                <span className="font-mono text-sm font-semibold text-slate-700">{stop.lot_no}</span>
                                                <span className="text-xs text-slate-400">{stop.eta}</span>
                                            </div>
                                            <div className="flex justify-between items-center">
                                                <span className="text-sm text-slate-600">{stop.task}</span>
                                                <Chip
                                                    label={stop.risk}
                                                    variant={stop.risk === 'CRITICAL' ? 'danger' : stop.risk === 'HIGH' ? 'warning' : 'default'}
                                                    className="scale-90 origin-right"
                                                />
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ))}

                {(!optimizationResult || optimizationResult.routes.length === 0) && !isOptimizing && (
                    <div className="col-span-1 lg:col-span-2 text-center py-12 text-slate-400 bg-slate-50/50 rounded-xl border border-dashed border-slate-200">
                        <Zap className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                        <p>No optimized schedule generated yet.</p>
                        <Button variant="ghost" onClick={handleOptimize}>Click to Generate</Button>
                    </div>
                )}
            </div>
        </motion.div>
    );
}
