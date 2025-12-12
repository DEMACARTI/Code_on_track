import { useState, useRef, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useSearchParams } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, Camera, CheckCircle, AlertTriangle, RefreshCw, Save, History } from 'lucide-react';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Chip } from '../components/ui/Chip';
import { Drawer } from '../components/ui/Drawer';
import { inspectComponent, getInspectionHistory, type InspectionReport } from '../api/vision';
import { Link } from 'react-router-dom';

export default function Inspection() {
    const [searchParams] = useSearchParams();
    const initialUid = searchParams.get('uid') || '';
    const initialLot = searchParams.get('lot_no') || '';

    const [uid, setUid] = useState(initialUid);
    const [lotNo, setLotNo] = useState(initialLot);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [previewUrl, setPreviewUrl] = useState<string | null>(null);
    const [result, setResult] = useState<InspectionReport | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);

    const mutation = useMutation({
        mutationFn: (file: File) => inspectComponent(file, uid, lotNo),
        onSuccess: (data) => {
            setResult(data);
        },
    });

    const { data: history } = useQuery({
        queryKey: ['inspection-history', uid],
        queryFn: () => getInspectionHistory(uid),
        enabled: !!uid,
    });

    useEffect(() => {
        if (selectedFile) {
            const url = URL.createObjectURL(selectedFile);
            setPreviewUrl(url);
            return () => URL.revokeObjectURL(url);
        }
    }, [selectedFile]);

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setSelectedFile(e.target.files[0]);
            setResult(null);
        }
    };

    const handleAnalyze = () => {
        if (selectedFile && uid) {
            mutation.mutate(selectedFile);
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'CRITICAL': return 'bg-rose-100 text-rose-700 border-rose-200';
            case 'HIGH': return 'bg-orange-100 text-orange-700 border-orange-200';
            case 'MEDIUM': return 'bg-amber-100 text-amber-700 border-amber-200';
            default: return 'bg-emerald-100 text-emerald-700 border-emerald-200';
        }
    };

    const [isHistoryOpen, setIsHistoryOpen] = useState(false);

    return (
        <div className="space-y-8">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 tracking-tight">AI Defect Inspection</h1>
                    <p className="text-slate-500 mt-1">Upload component images to detect rust, cracks, and defects.</p>
                </div>
                <div className="flex gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsHistoryOpen(true)}
                        disabled={!uid}
                    >
                        <History className="h-4 w-4 mr-2" />
                        History
                    </Button>
                    <Link to="/items">
                        <Button variant="outline" size="sm">Back to Items</Button>
                    </Link>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Upload Section */}
                <div className="space-y-6">
                    <Card className="p-6">
                        <h3 className="text-lg font-bold text-slate-900 mb-4">Component Details</h3>
                        <div className="grid grid-cols-2 gap-4 mb-6">
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">UID</label>
                                <input
                                    type="text"
                                    value={uid}
                                    onChange={(e) => setUid(e.target.value)}
                                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                                    placeholder="Enter Component UID"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Lot No (Optional)</label>
                                <input
                                    type="text"
                                    value={lotNo}
                                    onChange={(e) => setLotNo(e.target.value)}
                                    className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm bg-slate-50 focus:outline-none focus:ring-2 focus:ring-brand-500/20 focus:border-brand-500"
                                    placeholder="Enter Lot Number"
                                />
                            </div>
                        </div>

                        <div
                            onClick={() => fileInputRef.current?.click()}
                            className="border-2 border-dashed border-slate-200 rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:border-brand-500 hover:bg-brand-50/50 transition-all min-h-[300px] relative overflow-hidden"
                        >
                            {previewUrl ? (
                                <>
                                    <img src={previewUrl} alt="Preview" className="absolute inset-0 w-full h-full object-contain bg-slate-100" />
                                    {result && result.bbox && result.bbox.length === 4 && (
                                        <div
                                            className="absolute border-2 border-rose-500 bg-rose-500/20 shadow-[0_0_15px_rgba(244,63,94,0.5)] transition-all duration-500"
                                            style={{
                                                left: result.bbox[0],
                                                top: result.bbox[1],
                                                width: result.bbox[2],
                                                height: result.bbox[3]
                                            }}
                                        >
                                            <div className="absolute -top-6 left-0 bg-rose-600 text-white text-xs px-2 py-0.5 rounded shadow-sm font-bold tracking-wide">
                                                {result.issue}
                                            </div>
                                        </div>
                                    )}
                                    <div className="absolute bottom-4 right-4 flex gap-2">
                                        <Button
                                            size="sm"
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                fileInputRef.current?.click();
                                            }}
                                            className="bg-white/90 backdrop-blur text-slate-700 hover:bg-white border border-slate-200 shadow-sm"
                                        >
                                            Change Image
                                        </Button>
                                    </div>
                                </>
                            ) : (
                                <div className="pointer-events-none">
                                    <div className="h-16 w-16 bg-brand-50 text-brand-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                                        <Upload className="h-8 w-8" />
                                    </div>
                                    <p className="text-lg font-medium text-slate-900">Click to upload or drag and drop</p>
                                    <p className="text-sm text-slate-500 mt-1">Supports JPG, PNG (Max 10MB)</p>
                                </div>
                            )}
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept="image/*"
                                onChange={handleFileChange}
                                className="hidden"
                            />
                        </div>

                        <div className="mt-6 flex justify-end">
                            <Button
                                onClick={handleAnalyze}
                                disabled={!selectedFile || !uid || mutation.isPending}
                                isLoading={mutation.isPending}
                                leftIcon={<RefreshCw className={`h-4 w-4 ${mutation.isPending ? 'animate-spin' : ''}`} />}
                                className="w-full sm:w-auto"
                            >
                                {mutation.isPending ? 'Analyzing...' : 'Run Analysis'}
                            </Button>
                        </div>
                    </Card>
                </div>

                {/* Results Section */}
                <div className="space-y-6">
                    <AnimatePresence mode="wait">
                        {result ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ duration: 0.3 }}
                            >
                                <Card className="p-6 border-l-4 border-l-brand-600">
                                    <div className="flex items-start justify-between mb-6">
                                        <div>
                                            <h3 className="text-lg font-bold text-slate-900">Analysis Report</h3>
                                            <p className="text-sm text-slate-500">Generated just now</p>
                                        </div>
                                        <div className={`px-3 py-1 rounded-full text-xs font-bold border ${getSeverityColor(result.severity)}`}>
                                            {result.severity} SEVERITY
                                        </div>
                                    </div>

                                    <div className="space-y-6">
                                        <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                                            <p className="text-sm font-medium text-slate-500 mb-1">Detected Issue</p>
                                            <div className="flex items-center gap-2">
                                                <AlertTriangle className={`h-5 w-5 ${result.issue === 'No Issues Detected' ? 'text-emerald-500' : 'text-rose-500'}`} />
                                                <span className="text-lg font-bold text-slate-900">{result.issue}</span>
                                            </div>
                                        </div>

                                        <div>
                                            <div className="flex justify-between text-sm mb-2">
                                                <span className="font-medium text-slate-700">AI Confidence</span>
                                                <span className="text-slate-500">{(result.confidence * 100).toFixed(1)}%</span>
                                            </div>
                                            <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: `${result.confidence * 100}%` }}
                                                    transition={{ duration: 1, ease: 'easeOut' }}
                                                    className={`h-full rounded-full ${result.confidence > 0.8 ? 'bg-emerald-500' : 'bg-brand-500'}`}
                                                />
                                            </div>
                                        </div>

                                        <div className="bg-white border server-slate-200 rounded-xl p-4 shadow-sm">
                                            <h4 className="font-medium text-slate-900 mb-2 flex items-center gap-2">
                                                <CheckCircle className="h-4 w-4 text-brand-600" />
                                                Recommended Action
                                            </h4>
                                            <p className="text-slate-600 text-sm leading-relaxed">
                                                {result.recommended_action}
                                            </p>
                                        </div>

                                        <div className="flex gap-3 pt-2">
                                            <Button variant="outline" className="flex-1">
                                                <Save className="h-4 w-4 mr-2" /> Save Report
                                            </Button>
                                            {result.severity === 'CRITICAL' || result.severity === 'HIGH' ? (
                                                <Link to={`/scheduler-optimized?lot=${lotNo}`} className="flex-1">
                                                    <Button className="w-full bg-rose-600 hover:bg-rose-700 text-white">
                                                        Schedule Replacement
                                                    </Button>
                                                </Link>
                                            ) : null}
                                        </div>
                                    </div>
                                </Card>
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="h-full flex flex-col items-center justify-center p-12 text-center border-2 border-dashed border-slate-200 rounded-2xl bg-slate-50/50"
                            >
                                <div className="h-16 w-16 bg-white rounded-2xl shadow-sm flex items-center justify-center mb-4">
                                    <Camera className="h-8 w-8 text-slate-400" />
                                </div>
                                <h3 className="text-lg font-bold text-slate-900">Ready to Analyze</h3>
                                <p className="text-slate-500 max-w-xs mt-2">Upload a component image to start the AI inspection process.</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* History Drawer */}
                    <Drawer
                        isOpen={isHistoryOpen}
                        onClose={() => setIsHistoryOpen(false)}
                        title={`Inspection History${uid ? ` for ${uid}` : ''}`}
                        width="w-[500px]"
                    >
                        {history && history.length > 0 ? (
                            <div className="space-y-4 p-4">
                                {history.map((h, i) => (
                                    <div key={i} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow">
                                        <div className="flex items-center justify-between mb-2">
                                            <div className="flex items-center gap-2">
                                                <div className={`h-2.5 w-2.5 rounded-full ${h.severity === 'CRITICAL' ? 'bg-rose-500' : h.severity === 'HIGH' ? 'bg-orange-500' : 'bg-emerald-500'}`} />
                                                <span className="font-bold text-slate-900">{h.issue}</span>
                                            </div>
                                            <span className="text-xs text-slate-500">{new Date(h.created_at!).toLocaleString()}</span>
                                        </div>
                                        <p className="text-sm text-slate-600 mb-3">{h.recommended_action || 'No action recommended'}</p>
                                        <div className="flex items-center justify-between">
                                            <Chip label={h.severity} variant={h.severity === 'CRITICAL' ? 'danger' : 'default'} size="sm" />
                                            <span className="text-xs font-mono text-slate-400">Confidence: {(h.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="p-8 text-center text-slate-500">
                                <History className="h-12 w-12 mx-auto mb-3 text-slate-300" />
                                <p>No inspection history found.</p>
                            </div>
                        )}
                    </Drawer>
                </div>
            </div>
        </div>
    );
}
