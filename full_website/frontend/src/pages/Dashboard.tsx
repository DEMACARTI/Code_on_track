import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { KpiCard } from '../components/ui/KpiCard';
import { ChartCard } from '../components/ui/ChartCard';
import { Card } from '../components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableLoading, TableEmpty } from '../components/ui/Table';
import { Package, Users, AlertTriangle, Clock, ArrowRight } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts';
import { Chip } from '../components/ui/Chip';
import { Button } from '../components/ui/Button';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

interface DashboardSummary {
    total_items: number;
    counts_by_status: Record<string, number>;
    failures_by_vendor: { vendor_name: string; count: number }[];
    engravings_last_30_days: { date: string; count: number }[];
    warranty_expiring_in_30_days: number;
}

interface Item {
    uid: string;
    component_type: string;
    status: string;
    created_at: string;
}

const COLORS = ['#6366f1', '#ec4899', '#8b5cf6', '#f59e0b', '#ef4444'];

export default function Dashboard() {
    const { data: summary, isLoading: isLoadingSummary } = useQuery<DashboardSummary>({
        queryKey: ['dashboard-summary'],
        queryFn: async () => {
            const res = await api.get('/reports/summary');
            return res.data;
        }
    });

    const { data: recentItems, isLoading: isLoadingItems } = useQuery<Item[]>({
        queryKey: ['recent-items'],
        queryFn: async () => {
            const res = await api.get('/items', { params: { page: 1, page_size: 5 } });
            return res.data;
        }
    });

    const pieData = summary?.counts_by_status
        ? Object.entries(summary.counts_by_status).map(([name, value]) => ({ name, value }))
        : [];

    const areaData = summary?.engravings_last_30_days || [];

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
            <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-slate-900">Dashboard Overview</h1>
                <div className="text-sm text-slate-500">
                    Last updated: {new Date().toLocaleTimeString()}
                </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Total Items"
                        value={summary?.total_items || 0}
                        icon={<Package className="h-6 w-6" />}
                        color="primary"
                        trend={{ value: 12, label: 'vs last month', direction: 'up' }}
                        className="h-full"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Total Vendors"
                        value={summary?.failures_by_vendor?.length || 0}
                        icon={<Users className="h-6 w-6" />}
                        color="secondary"
                        className="h-full"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Warranty Expiring"
                        value={summary?.warranty_expiring_in_30_days || 0}
                        icon={<Clock className="h-6 w-6" />}
                        color="amber"
                        trend={{ value: 5, label: 'due soon', direction: 'neutral' }}
                        className="h-full"
                    />
                </motion.div>
                <motion.div variants={item} className="h-full">
                    <KpiCard
                        title="Failures"
                        value={pieData.find(d => d.name === 'failed')?.value || 0}
                        icon={<AlertTriangle className="h-6 w-6" />}
                        color="rose"
                        trend={{ value: 2, label: 'vs last month', direction: 'down' }}
                        className="h-full"
                    />
                </motion.div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <motion.div variants={item} className="lg:col-span-2 h-[450px]">
                    <ChartCard title="Activity Overview" subtitle="Engravings over the last 30 days" className="h-full">
                        {isLoadingSummary ? (
                            <div className="h-full flex items-center justify-center text-slate-400">Loading chart data...</div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={areaData}>
                                    <defs>
                                        <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis
                                        dataKey="date"
                                        tick={{ fontSize: 12, fill: '#64748b' }}
                                        tickLine={false}
                                        axisLine={false}
                                        tickFormatter={(val: string) => new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                    />
                                    <YAxis
                                        tick={{ fontSize: 12, fill: '#64748b' }}
                                        tickLine={false}
                                        axisLine={false}
                                    />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }}
                                        itemStyle={{ color: '#1e293b' }}
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="count"
                                        stroke="#6366f1"
                                        strokeWidth={3}
                                        fillOpacity={1}
                                        fill="url(#colorCount)"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        )}
                    </ChartCard>
                </motion.div>

                <motion.div variants={item} className="h-[450px]">
                    <ChartCard title="Status Distribution" subtitle="Current item status breakdown" className="h-full">
                        {isLoadingSummary ? (
                            <div className="h-full flex items-center justify-center text-slate-400">Loading chart data...</div>
                        ) : (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={pieData}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={80}
                                        outerRadius={110}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {pieData.map((_, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: '1px solid #e2e8f0' }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        )}
                    </ChartCard>
                </motion.div>
            </div>

            {/* Recent Items Table */}
            <motion.div variants={item}>
                <Card>
                    <div className="flex items-center justify-between mb-6">
                        <div>
                            <h3 className="text-lg font-semibold text-slate-900">Recent Items</h3>
                            <p className="text-sm text-slate-500">Latest items added to the system</p>
                        </div>
                        <Link to="/items">
                            <Button variant="ghost" size="sm" rightIcon={<ArrowRight className="h-4 w-4" />}>
                                View All
                            </Button>
                        </Link>
                    </div>

                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>UID</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Created At</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoadingItems ? (
                                <TableLoading colSpan={4} />
                            ) : recentItems && recentItems.length > 0 ? (
                                recentItems.map((item) => (
                                    <TableRow key={item.uid}>
                                        <TableCell className="font-medium text-slate-900">{item.uid}</TableCell>
                                        <TableCell>{item.component_type}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={item.status}
                                                variant={
                                                    item.status === 'active' ? 'success' :
                                                        item.status === 'failed' ? 'danger' : 'default'
                                                }
                                            />
                                        </TableCell>
                                        <TableCell>
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
        </motion.div>
    );
}
