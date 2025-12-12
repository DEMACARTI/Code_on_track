import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { generateSchedule, applySchedule, type SchedulePreview } from '../api/scheduler';
import { Modal } from './ui/Modal';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { Calendar, Clock, Truck, Zap } from 'lucide-react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

interface SchedulerModalProps {
    isOpen: boolean;
    onClose: () => void;
    preselectedLots?: string[];
}

export default function SchedulerModal({ isOpen, onClose, preselectedLots = [] }: SchedulerModalProps) {
    const [name, setName] = useState('');
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [schedulePreview, setSchedulePreview] = useState<SchedulePreview | null>(null);
    const [lotsInput, setLotsInput] = useState(preselectedLots.join(', '));

    const generateMutation = useMutation({
        mutationFn: generateSchedule,
        onSuccess: (data) => {
            setSchedulePreview(data);
        }
    });

    const applyMutation = useMutation({
        mutationFn: applySchedule,
        onSuccess: () => {
            onClose();
            // Could trigger a toast here
        }
    });

    const handleGenerate = () => {
        const lots = lotsInput.split(',').map(l => l.trim()).filter(Boolean);
        generateMutation.mutate({
            name: name || `Schedule for ${date}`,
            date,
            lots: lots.length > 0 ? lots : ['LOT-001', 'LOT-002'] // Default specific lots for testing if empty
        });
    };

    const handleApply = () => {
        if (schedulePreview?.id) {
            applyMutation.mutate(schedulePreview.id);
        }
    };


    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Generate Pickup Schedule"
        >
            <div className="space-y-6">
                {!schedulePreview ? (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-4"
                    >
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Schedule Name</label>
                            <Input
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="e.g. Weekly Returns Pickup"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Pickup Date</label>
                            <div className="relative">
                                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                                <input
                                    type="date"
                                    value={date}
                                    onChange={(e) => setDate(e.target.value)}
                                    className="w-full pl-10 h-10 rounded-lg border border-slate-200 bg-slate-50 focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500 outline-none transition-all text-sm"
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Target Lots (comma separated)</label>
                            <Input
                                value={lotsInput}
                                onChange={(e) => setLotsInput(e.target.value)}
                                placeholder="LOT-XP-001, LOT-XP-002..."
                            />
                            <p className="text-xs text-slate-400 mt-1">Leave empty to use defaults or auto-select.</p>
                        </div>

                        <div className="pt-4 flex justify-end">
                            <Button
                                onClick={handleGenerate}
                                disabled={generateMutation.isPending}
                                className="bg-brand-600 hover:bg-brand-700 text-white"
                            >
                                {generateMutation.isPending ? 'Generating...' : 'Generate Preview'}
                            </Button>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        className="space-y-6"
                    >
                        <div className="bg-slate-50 border border-slate-100 rounded-xl p-4">
                            <div className="flex items-start gap-3">
                                <div className="p-2 bg-blue-100 rounded-lg">
                                    <Truck className="h-5 w-5 text-blue-600" />
                                </div>
                                <div className="flex-1">
                                    <h4 className="font-medium text-slate-900">Schedule Preview Generated</h4>
                                    <p className="text-sm text-slate-500 mt-1">
                                        ID: <span className="font-mono">{schedulePreview.id}</span>
                                    </p>
                                    <div className="flex gap-4 mt-3">
                                        <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                            <Calendar className="h-3.5 w-3.5" />
                                            {date}
                                        </div>
                                        <div className="flex items-center gap-1.5 text-xs text-slate-600">
                                            <Clock className="h-3.5 w-3.5" />
                                            {schedulePreview.preview.length} Tasks
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="border rounded-lg overflow-hidden">
                            <table className="w-full text-sm text-left">
                                <thead className="bg-slate-50 text-slate-500 font-medium">
                                    <tr>
                                        <th className="px-4 py-3">Task</th>
                                        <th className="px-4 py-3">Type</th>
                                        <th className="px-4 py-3 text-right">Est. Time</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {schedulePreview.preview.map((task: any, i: number) => (
                                        <tr key={i} className="hover:bg-slate-50/50">
                                            <td className="px-4 py-3 font-medium text-slate-900">{task.action}</td>
                                            <td className="px-4 py-3 text-slate-600">{task.lot || 'General'}</td>
                                            <td className="px-4 py-3 text-right font-mono text-slate-500">
                                                {task.details?.est_time_mins ? `${task.details.est_time_mins} min` : '-'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="pt-2 flex justify-between gap-2">
                            <Button
                                variant="outline"
                                onClick={onClose}
                                className="w-full sm:w-auto"
                            >
                                Cancel
                            </Button>
                            <Link to="/scheduler-optimized" className="w-full sm:w-auto">
                                <Button
                                    variant="ghost"
                                    className="w-full text-brand-600 hover:text-brand-700 hover:bg-brand-50"
                                >
                                    <Zap className="h-4 w-4 mr-2" />
                                    Use AI Optimized Mode
                                </Button>
                            </Link>
                            <Button
                                className="w-full sm:w-auto bg-brand-600 hover:bg-brand-700 text-white"
                                onClick={handleApply}
                                disabled={!schedulePreview?.id || applyMutation.isPending}
                            >
                                {applyMutation.isPending ? 'Applying...' : 'Apply Schedule'}
                            </Button>
                        </div>
                    </motion.div>
                )}
            </div>
        </Modal>
    );
}
