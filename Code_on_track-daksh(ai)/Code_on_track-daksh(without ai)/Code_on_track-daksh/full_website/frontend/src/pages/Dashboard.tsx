import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { KpiCard } from '../components/ui/KpiCard';
import { Card } from '../components/ui/Card';
import { VendorReliabilityTable } from '../components/VendorReliabilityTable';
import { Package, AlertTriangle, Activity, Truck, Clock, ArrowRight, TrendingUp, AlertCircle } from 'lucide-react';
import {
    PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid
} from 'recharts';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { QuickLinks } from '../components/dashboard/QuickLinks';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableLoading, TableEmpty } from '../components/ui/Table';
import { Chip } from '../components/ui/Chip';
import { Button } from '../components/ui/Button';

interface Item {
    uid: string;
    component_type: string;
    status: string;
    created_at: string;
}





function DashboardCriticalCount() {
    const [criticalCount, setCriticalCount] = useState<number | null>(null);

    useEffect(() => {
        async function loadCritical() {
            try {
                const res = await fetch("http://localhost:8000/lot_health/?risk_level=CRITICAL");
                if (!res.ok) return;
                const data = await res.json();
                // Count unique lot numbers
                const lotNos = (data || []).map((r: any) => r.lot_no || r.lotNo || r.lotNumber);
                const unique = new Set(lotNos.filter(Boolean));
                setCriticalCount(unique.size);
            } catch (e) {
                console.error("Critical lots fetch failed", e);
            }
        }

        loadCritical();
        const id = setInterval(loadCritical, 60000);
        return () => clearInterval(id);
    }, []);

    useEffect(() => {
        if (criticalCount === null) return;
        // Target specifically the h3 inside the card which holds the value
        const tile = document.querySelector('#critical-lots-count') ||
            document.querySelector('.critical-kpi-card h3') ||
            document.querySelector('[data-qa="critical-count"]');
        if (tile) tile.textContent = String(criticalCount);
    }, [criticalCount]);

    return null;
}


export default function Dashboard() {
    const [totalItems, setTotalItems] = useState(0);
    const [criticalLots, setCriticalLots] = useState(0);
    const [healthLots, setHealthLots] = useState(0);
    const [vendorCount, setVendorCount] = useState(0);

    useEffect(() => {
        async function load() {
            try {
                const resp = await api.get("/debug/status");
                const d = resp.data;
                setTotalItems(d.items || 0);
                // For critical lots, we might need a separate query or rely on what debug returns if it breaks it down
                // The prompt says "setCriticalLots(d.lot_quality)".
                setCriticalLots(d.lot_quality || 0);
                setHealthLots(d.lot_health || 0);
                setVendorCount(d.vendors || 0);
            } catch (e) {
                console.error("Dashboard load failed", e);
            }
        }
        load();
    }, []);

    // We still fetch recent items as that is real data
    const { data: recentItems, isLoading: isLoadingItems } = useQuery<Item[]>({
        queryKey: ['recent-items'],
        queryFn: async () => {
            const res = await api.get('/items', { params: { page: 1, page_size: 5 } });
            return res.data.items || res.data || [];
        }
    });

    // We fetch detailed health to populate the Pie Chart correctly if possible
    // UseEffect is one way, or keep useQuery for this since it returns array
    // Analytics Queries
    const { data: weeklyDefects } = useQuery({
        queryKey: ['weekly-defects'],
        queryFn: async () => {
            try {
                const res = await api.get('/analytics/weekly_defects');
                return res.data;
            } catch (e) { return []; }
        }
    });

    const { data: healthDistribution } = useQuery({
        queryKey: ['health-distribution'],
        queryFn: async () => {
            try {
                const res = await api.get('/analytics/health_distribution');
                return res.data;
            } catch (e) { return []; }
        }
    });

    const { data: systemActivity } = useQuery({
        queryKey: ['system-activity'],
        queryFn: async () => {
            try {
                const res = await api.get('/analytics/system_activity');
                return res.data;
            } catch (e) { return []; }
        }
    });

    // Removing weeklyDefectsData and areaData as they were mock/summary based.

    const container = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const item = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0 }
    };

    return (
        <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="space-y-6"
        >

            <DashboardCriticalCount />
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Dashboard Overview</h1>
                    <p className="text-slate-500 mt-1">Real-time insights on railway component lifecycle.</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="text-sm font-medium text-slate-500 bg-white px-3 py-1.5 rounded-lg border border-slate-200 shadow-sm">
                        Updated: {new Date().toLocaleTimeString()}
                    </div>
                    <Button variant="outline" size="sm" onClick={() => window.location.reload()} leftIcon={<Activity className="h-4 w-4" />}>
                        Refresh
                    </Button>
                </div>
            </div>

            {/* Quick Links Section */}
            <motion.div variants={item}>
                <QuickLinks />
            </motion.div>

            {/* Top Level Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Total Items"
                        value={totalItems}
                        icon={<Package className="h-6 w-6" />}
                        color="brand"
                        // trend={{ value: 0, label: 'Recorded', direction: 'neutral' }}
                        className="h-full"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Critical Lots"
                        value={criticalLots}
                        icon={<AlertTriangle className="h-6 w-6" />}
                        color="rose"
                        // trend={{ value: 0, label: 'High Risk Lots', direction: 'neutral' }}
                        className="h-full critical-kpi-card"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Analyzed Lots"
                        value={healthLots}
                        icon={<Activity className="h-6 w-6" />}
                        color="amber"
                        // trend={{ value: 0, label: 'Processed', direction: 'neutral' }}
                        className="h-full"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <Link to="/vendors">
                        <KpiCard
                            title="Active Vendors"
                            value={vendorCount}
                            icon={<Truck className="h-6 w-6" />}
                            color="accent"
                            // trend={{ value: 0, label: 'Total', direction: 'neutral' }}
                            className="h-full cursor-pointer hover:ring-2 hover:ring-indigo-500/20"
                        />
                    </Link>
                </motion.div>
            </div>

            <div className="grid grid-cols-12 gap-6">
                {/* Weekly Defects & Activity */}
                <motion.div variants={item} className="col-span-12 lg:col-span-8 h-[350px]">
                    <Card className="h-full p-5 flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <h3 className="font-semibold text-slate-700">Weekly Defects Trend</h3>
                                <p className="text-xs text-slate-400">Failures detected by vision system</p>
                            </div>
                            <TrendingUp className="h-4 w-4 text-slate-400" />
                        </div>
                        <div className="flex-1 w-full min-h-0">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={
                                    (weeklyDefects || []).sort((a: any, b: any) => {
                                        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
                                        return days.indexOf(a.day) - days.indexOf(b.day);
                                    })
                                }>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                    <XAxis
                                        dataKey="day"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#64748b', fontSize: 12 }}
                                        dy={10}
                                    />
                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{ fill: '#64748b', fontSize: 12 }}
                                    />
                                    <Tooltip
                                        cursor={{ fill: '#f8fafc' }}
                                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                    />
                                    <Bar
                                        dataKey="count"
                                        fill="#fbbf24" /* Amber/Orange color usually looks better for defects than red, or keep user's choice */
                                        radius={[4, 4, 0, 0]}
                                        barSize={32}
                                    />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </motion.div>

                {/* Pie Chart of Risk Distribution */}
                <motion.div variants={item} className="col-span-12 lg:col-span-4 h-[350px]">
                    <Card className="h-full p-5 flex flex-col justify-between">
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="font-semibold text-slate-700">Health Risk Distribution</h3>
                            <Activity className="h-4 w-4 text-slate-400" />
                        </div>
                        <div className="flex-1 w-full min-h-0 relative">
                            {(!healthDistribution || healthDistribution.length === 0) && (
                                <div className="absolute inset-0 flex items-center justify-center text-slate-400 text-sm">
                                    No Data
                                </div>
                            )}
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={healthDistribution || []}
                                        dataKey="value"
                                        nameKey="name"
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                    >
                                        {(healthDistribution || []).map((entry: any, index: number) => {
                                            let color = '#10b981';
                                            if (entry.name === 'CRITICAL') color = '#f43f5e';
                                            if (entry.name === 'HIGH') color = '#f59e0b';
                                            if (entry.name === 'MEDIUM') color = '#3b82f6';
                                            return <Cell key={`cell-${index}`} fill={color} stroke="none" />;
                                        })}
                                    </Pie>
                                    <Tooltip />
                                    <Legend verticalAlign="bottom" height={36} iconType="circle" />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </motion.div>

                {/* Vendor Reliability Table */}
                <motion.div variants={item} className="col-span-12 lg:col-span-8">
                    <VendorReliabilityTable />
                </motion.div>

                {/* System Activity */}
                <motion.div variants={item} className="col-span-12 lg:col-span-4">
                    <Card className="h-full p-5 flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-slate-700">System Activity</h3>
                            <Activity className="h-4 w-4 text-slate-400" />
                        </div>
                        <div className="space-y-4 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar">
                            {systemActivity && systemActivity.map((act: any, idx: number) => (
                                <div key={idx} className="flex gap-3 items-start pb-3 border-b border-slate-50 last:border-0 last:pb-0">
                                    <div className="mt-1 p-1.5 rounded-full bg-slate-100 flex-shrink-0">
                                        <AlertCircle className="h-3 w-3 text-slate-500" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-slate-800">
                                            Anomaly Check: {act.subject}
                                        </p>
                                        <p className="text-xs text-slate-500">
                                            Score: {(act.value * 100).toFixed(1)}% | {new Date(act.timestamp).toLocaleTimeString()}
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {(!systemActivity || systemActivity.length === 0) && (
                                <div className="text-center text-slate-400 text-sm py-8">No recent activity</div>
                            )}
                        </div>
                    </Card>
                </motion.div>

                {/* Recent Items Table */}
                <motion.div variants={item} className="col-span-12 lg:col-span-8">
                    <Card className="glass border-0 shadow-lg shadow-slate-200/50 overflow-hidden">
                        <div className="flex items-center justify-between mb-6 px-2">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-brand-50 rounded-lg">
                                    <Clock className="h-5 w-5 text-brand-600" />
                                </div>
                                <h3 className="text-lg font-bold text-slate-900">Recent Items</h3>
                            </div>
                            <Link to="/items">
                                <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="h-4 w-4" />}>
                                    View All
                                </Button>
                            </Link>
                        </div>

                        <Table>
                            <TableHeader>
                                <TableRow className="hover:bg-transparent border-b border-slate-100">
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">UID</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Type</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Status</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Created At</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoadingItems ? (
                                    <TableLoading colSpan={4} />
                                ) : recentItems && recentItems.length > 0 ? (
                                    recentItems.map((item) => (
                                        <TableRow key={item.uid} className="hover:bg-brand-50/30 transition-colors border-b border-slate-50 last:border-0">
                                            <TableCell className="font-medium text-slate-900">{item.uid}</TableCell>
                                            <TableCell className="text-slate-600">{item.component_type}</TableCell>
                                            <TableCell>
                                                <Chip
                                                    label={item.status}
                                                    variant={
                                                        item.status === 'active' ? 'success' :
                                                            item.status === 'failed' ? 'danger' : 'default'
                                                    }
                                                    className="shadow-sm"
                                                />
                                            </TableCell>
                                            <TableCell className="text-slate-500 font-mono text-xs">
                                                {item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableEmpty colSpan={4} />
                                )}
                            </TableBody>
                        </Table>
                    </Card>
                </motion.div>
            </div>
        </motion.div>
    );
}
