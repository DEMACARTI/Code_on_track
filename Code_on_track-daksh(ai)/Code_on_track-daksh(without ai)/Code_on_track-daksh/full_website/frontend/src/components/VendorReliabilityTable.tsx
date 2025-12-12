import { useState, Fragment } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getVendorReliability, type VendorReliability } from '../api/reliability';
import { Dialog, Transition } from '@headlessui/react';
import { BarChart2, ArrowUpDown } from 'lucide-react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    RadarChart,
    PolarGrid,
    PolarAngleAxis,
    PolarRadiusAxis,
    Radar
} from 'recharts';

export const VendorReliabilityTable = () => {
    const [sort, setSort] = useState<string>('score_desc');
    const [selectedVendor, setSelectedVendor] = useState<VendorReliability | null>(null);

    const { data: vendors, isLoading } = useQuery({
        queryKey: ['vendorReliability', sort],
        queryFn: () => getVendorReliability(sort),
    });

    const handleSort = (field: string) => {
        if (field === 'score') {
            setSort(prev => prev === 'score_desc' ? 'score_asc' : 'score_desc');
        } else if (field === 'name') {
            setSort('name_asc');
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 90) return 'text-emerald-600 bg-emerald-50 ring-emerald-500/20';
        if (score >= 80) return 'text-blue-600 bg-blue-50 ring-blue-500/20';
        if (score >= 70) return 'text-amber-600 bg-amber-50 ring-amber-500/20';
        return 'text-rose-600 bg-rose-50 ring-rose-500/20';
    };



    if (isLoading) return <div className="h-64 flex items-center justify-center text-slate-400">Loading reliability data...</div>;

    return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
            <div className="px-6 py-5 border-b border-slate-50 flex items-center justify-between">
                <div>
                    <h3 className="font-semibold text-slate-900 flex items-center gap-2">
                        <BarChart2 className="h-5 w-5 text-indigo-500" />
                        Vendor Reliability Comparison
                    </h3>

                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => handleSort('score')}
                        className="px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors flex items-center gap-1"
                    >
                        <ArrowUpDown className="h-3 w-3" />
                        Sort by Score
                    </button>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-500 uppercase bg-slate-50/50">
                        <tr>
                            <th className="px-6 py-3 font-medium">Vendor</th>

                            <th className="px-6 py-3 font-medium text-right">Reliability Score</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-50">
                        {vendors?.map((vendor) => (
                            <tr
                                key={vendor.vendor_id}
                                className="group hover:bg-slate-50/50 transition-colors cursor-pointer"
                                onClick={() => setSelectedVendor(vendor)}
                            >
                                <td className="px-6 py-4 font-medium text-slate-900">
                                    {vendor.vendor_name}
                                </td>

                                <td className="px-6 py-4 text-right">
                                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ring-1 ring-inset ${getScoreColor(vendor.reliability_score)}`}>
                                        {vendor.reliability_score.toFixed(1)}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* Comparison Chart */}
            <div className="px-6 py-6 border-t border-slate-50">
                <h4 className="text-xs font-semibold text-slate-500 uppercase mb-4">Score Overview</h4>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={vendors} layout="horizontal">
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis
                                dataKey="vendor_name"
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 10, fill: '#64748b' }}
                                interval={0}
                            />
                            <YAxis
                                axisLine={false}
                                tickLine={false}
                                tick={{ fontSize: 10, fill: '#64748b' }}
                                domain={[0, 100]}
                                label={{ value: 'Reliability Score', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle', fill: '#94a3b8', fontSize: 10 } }}
                            />
                            <Tooltip
                                cursor={{ fill: '#f8fafc' }}
                                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                formatter={(value: number) => [`${value.toFixed(1)}`, 'Score']}
                            />
                            <Bar
                                dataKey="reliability_score"
                                name="Reliability Score"
                                fill="#6366f1"
                                radius={[4, 4, 0, 0]}
                                barSize={40}
                                activeBar={{ fill: '#4f46e5' }}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Details Modal */}
            <Transition appear show={!!selectedVendor} as={Fragment}>
                <Dialog as="div" className="relative z-50" onClose={() => setSelectedVendor(null)}>
                    <Transition.Child
                        as={Fragment}
                        enter="ease-out duration-300"
                        enterFrom="opacity-0"
                        enterTo="opacity-100"
                        leave="ease-in duration-200"
                        leaveFrom="opacity-100"
                        leaveTo="opacity-0"
                    >
                        <div className="fixed inset-0 bg-black/25 backdrop-blur-sm" />
                    </Transition.Child>

                    <div className="fixed inset-0 overflow-y-auto">
                        <div className="flex min-h-full items-center justify-center p-4 text-center">
                            <Transition.Child
                                as={Fragment}
                                enter="ease-out duration-300"
                                enterFrom="opacity-0 scale-95"
                                enterTo="opacity-100 scale-100"
                                leave="ease-in duration-200"
                                leaveFrom="opacity-100 scale-100"
                                leaveTo="opacity-0 scale-95"
                            >
                                <Dialog.Panel className="w-full max-w-2xl transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
                                    {selectedVendor && (
                                        <>
                                            <Dialog.Title
                                                as="h3"
                                                className="text-lg font-bold leading-6 text-slate-900 flex justify-between items-center"
                                            >
                                                <span>{selectedVendor.vendor_name} Detailed Analysis</span>
                                                <span className={`text-sm px-3 py-1 rounded-full ${getScoreColor(selectedVendor.reliability_score)}`}>
                                                    Score: {selectedVendor.reliability_score.toFixed(1)}
                                                </span>
                                            </Dialog.Title>

                                            <div className="mt-6 grid grid-cols-2 gap-6">
                                                <div className="h-64 sticky top-0">
                                                    <ResponsiveContainer width="100%" height="100%">
                                                        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={[
                                                            { subject: 'OTR', A: selectedVendor.otr * 100, fullMark: 100 },
                                                            { subject: 'QR', A: selectedVendor.qr * 100, fullMark: 100 },
                                                            { subject: 'FR', A: selectedVendor.fr * 100, fullMark: 100 },
                                                            { subject: 'RTS', A: selectedVendor.rts * 100, fullMark: 100 },
                                                            { subject: 'CCR', A: selectedVendor.ccr * 100, fullMark: 100 },
                                                        ]}>
                                                            <PolarGrid stroke="#e2e8f0" />
                                                            <PolarAngleAxis dataKey="subject" tick={{ fill: '#64748b', fontSize: 12 }} />
                                                            <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                                            <Radar
                                                                name={selectedVendor.vendor_name}
                                                                dataKey="A"
                                                                stroke="#6366f1"
                                                                strokeWidth={2}
                                                                fill="#6366f1"
                                                                fillOpacity={0.2}
                                                            />
                                                            <Tooltip />
                                                        </RadarChart>
                                                    </ResponsiveContainer>
                                                </div>

                                                <div className="space-y-4">
                                                    <div className="bg-slate-50 p-4 rounded-xl">
                                                        <h4 className="font-semibold text-slate-900 mb-2 text-sm">Metric Breakdown</h4>
                                                        <ul className="space-y-3 text-sm">
                                                            <li className="flex justify-between">
                                                                <span className="text-slate-500">On-Time Rate (30%)</span>
                                                                <span className="font-medium text-slate-900">{(selectedVendor.otr * 100).toFixed(1)}%</span>
                                                            </li>
                                                            <li className="flex justify-between">
                                                                <span className="text-slate-500">Quality Rate (30%)</span>
                                                                <span className="font-medium text-slate-900">{(selectedVendor.qr * 100).toFixed(1)}%</span>
                                                            </li>
                                                            <li className="flex justify-between">
                                                                <span className="text-slate-500">Fulfillment Rate (20%)</span>
                                                                <span className="font-medium text-slate-900">{(selectedVendor.fr * 100).toFixed(1)}%</span>
                                                            </li>
                                                            <li className="flex justify-between">
                                                                <span className="text-slate-500">Response Time (10%)</span>
                                                                <span className="font-medium text-slate-900">{(selectedVendor.rts * 100).toFixed(1)}%</span>
                                                            </li>
                                                            <li className="flex justify-between">
                                                                <span className="text-slate-500">Claims Compliance (10%)</span>
                                                                <span className="font-medium text-slate-900">{(selectedVendor.ccr * 100).toFixed(1)}%</span>
                                                            </li>
                                                        </ul>
                                                    </div>
                                                </div>
                                            </div>

                                            <div className="mt-6 flex justify-end">
                                                <button
                                                    type="button"
                                                    className="inline-flex justify-center rounded-lg border border-transparent bg-slate-100 px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-slate-500 focus-visible:ring-offset-2"
                                                    onClick={() => setSelectedVendor(null)}
                                                >
                                                    Close Analysis
                                                </button>
                                            </div>
                                        </>
                                    )}
                                </Dialog.Panel>
                            </Transition.Child>
                        </div>
                    </div>
                </Dialog>
            </Transition>
        </div>
    );
};
