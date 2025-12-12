import React, { useState } from 'react';
import Papa from 'papaparse';
import { Upload, AlertTriangle, Check, X, Loader2, FileSpreadsheet, ArrowRight } from 'lucide-react';
import { cn } from '../../utils/cn';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './Button';

interface ParsedItem {
    uid: string;
    component_type: string;
    lot_number: string;
    vendor_name: string;
    status: 'valid' | 'error';
    message?: string;
}

export const ImportPreview = () => {
    const [file, setFile] = useState<File | null>(null);
    const [parsedData, setParsedData] = useState<ParsedItem[]>([]);
    const [isDragging, setIsDragging] = useState(false);
    const [createMissingVendors, setCreateMissingVendors] = useState(false);
    const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.type === 'text/csv') {
            handleFile(droppedFile);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFile(e.target.files[0]);
        }
    };

    const handleFile = (file: File) => {
        setFile(file);
        setParsedData([]);

        Papa.parse(file, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
                const items: ParsedItem[] = results.data.map((row: any) => {
                    const isValid = row.uid && row.component_type && row.lot_number && row.vendor_name;
                    return {
                        uid: row.uid,
                        component_type: row.component_type,
                        lot_number: row.lot_number,
                        vendor_name: row.vendor_name,
                        status: isValid ? 'valid' : 'error',
                        message: isValid ? undefined : 'Missing required fields',
                    };
                });
                setParsedData(items);
            },
            error: (error) => {
                console.error('Error parsing CSV:', error);
            }
        });
    };

    const handleUpload = async () => {
        setUploadStatus('uploading');
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));
        setUploadStatus('success');
        // Reset after success
        setTimeout(() => {
            setFile(null);
            setParsedData([]);
            setUploadStatus('idle');
        }, 3000);
    };

    const validCount = parsedData.filter(i => i.status === 'valid').length;
    const errorCount = parsedData.filter(i => i.status === 'error').length;

    return (
        <div className="space-y-6">
            <AnimatePresence mode="wait">
                {!file ? (
                    <motion.div
                        key="dropzone"
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        className={cn(
                            "relative flex h-80 w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed transition-all duration-300",
                            isDragging
                                ? "border-brand-500 bg-brand-50/50 scale-[1.02] shadow-xl shadow-brand-500/10"
                                : "border-slate-200 bg-slate-50/50 hover:border-brand-400 hover:bg-slate-50 hover:shadow-lg hover:shadow-brand-500/5"
                        )}
                    >
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileSelect}
                            className="absolute inset-0 cursor-pointer opacity-0 z-10"
                        />
                        <div className={cn(
                            "flex h-20 w-20 items-center justify-center rounded-full bg-white shadow-lg ring-1 ring-slate-100 mb-6 transition-transform duration-300",
                            isDragging ? "scale-110 ring-brand-200" : ""
                        )}>
                            <Upload className={cn("h-10 w-10 transition-colors duration-300", isDragging ? "text-brand-600" : "text-slate-400")} />
                        </div>
                        <div className="text-center space-y-2 max-w-sm px-4">
                            <h3 className="text-lg font-bold text-slate-900">
                                Upload CSV File
                            </h3>
                            <p className="text-sm text-slate-500">
                                Drag and drop your file here, or <span className="text-brand-600 font-semibold group-hover:underline">browse</span> to upload.
                            </p>
                            <p className="text-xs text-slate-400 pt-2">
                                Supports .csv files up to 10MB
                            </p>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        key="preview"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="rounded-2xl border border-slate-200 bg-white/80 backdrop-blur-xl shadow-xl shadow-slate-200/50 overflow-hidden"
                    >
                        <div className="flex items-center justify-between border-b border-slate-100 p-6 bg-white/50">
                            <div className="flex items-center gap-4">
                                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-brand-50 text-brand-600 shadow-sm">
                                    <FileSpreadsheet className="h-6 w-6" />
                                </div>
                                <div>
                                    <h3 className="text-base font-bold text-slate-900">{file.name}</h3>
                                    <p className="text-sm text-slate-500 font-medium">
                                        {(file.size / 1024).toFixed(1)} KB • {parsedData.length} rows found
                                    </p>
                                </div>
                            </div>
                            <button
                                onClick={() => setFile(null)}
                                className="rounded-full p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition-colors"
                            >
                                <X className="h-5 w-5" />
                            </button>
                        </div>

                        <div className="bg-slate-50/50 px-6 py-4 border-b border-slate-100">
                            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                                <div className="flex gap-6 text-sm">
                                    <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-3 py-1.5 rounded-full border border-emerald-100">
                                        <Check className="h-4 w-4" />
                                        <span className="font-semibold">{validCount} valid</span>
                                    </div>
                                    {errorCount > 0 && (
                                        <div className="flex items-center gap-2 text-rose-600 bg-rose-50 px-3 py-1.5 rounded-full border border-rose-100">
                                            <AlertTriangle className="h-4 w-4" />
                                            <span className="font-semibold">{errorCount} errors</span>
                                        </div>
                                    )}
                                </div>
                                <label className="flex items-center gap-3 text-sm text-slate-700 cursor-pointer group select-none">
                                    <div className="relative flex items-center">
                                        <input
                                            type="checkbox"
                                            checked={createMissingVendors}
                                            onChange={(e) => setCreateMissingVendors(e.target.checked)}
                                            className="peer h-5 w-5 rounded border-slate-300 text-brand-600 focus:ring-brand-500 transition-all cursor-pointer"
                                        />
                                    </div>
                                    <span className="font-medium group-hover:text-brand-700 transition-colors">Create missing vendors automatically</span>
                                </label>
                            </div>
                        </div>

                        <div className="max-h-[400px] overflow-auto custom-scrollbar">
                            <table className="w-full text-left text-sm">
                                <thead className="bg-slate-50/80 sticky top-0 z-10 backdrop-blur-sm">
                                    <tr className="border-b border-slate-200">
                                        <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Status</th>
                                        <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">UID</th>
                                        <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Component</th>
                                        <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Lot Number</th>
                                        <th className="px-6 py-3 text-xs font-bold text-slate-500 uppercase tracking-wider">Vendor</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100 bg-white">
                                    {parsedData.map((item, index) => (
                                        <tr key={index} className={cn("hover:bg-brand-50/30 transition-colors", item.status === 'error' && "bg-rose-50/30 hover:bg-rose-50/50")}>
                                            <td className="px-6 py-3">
                                                {item.status === 'valid' ? (
                                                    <div className="h-6 w-6 rounded-full bg-emerald-100 flex items-center justify-center">
                                                        <Check className="h-3.5 w-3.5 text-emerald-600" />
                                                    </div>
                                                ) : (
                                                    <div className="group relative">
                                                        <div className="h-6 w-6 rounded-full bg-rose-100 flex items-center justify-center cursor-help">
                                                            <AlertTriangle className="h-3.5 w-3.5 text-rose-600" />
                                                        </div>
                                                        <div className="absolute left-8 top-1/2 -translate-y-1/2 hidden whitespace-nowrap rounded-lg bg-slate-800 px-3 py-2 text-xs font-medium text-white shadow-xl group-hover:block z-20">
                                                            {item.message}
                                                            <div className="absolute left-0 top-1/2 -translate-x-1 -translate-y-1/2 border-4 border-transparent border-r-slate-800"></div>
                                                        </div>
                                                    </div>
                                                )}
                                            </td>
                                            <td className="px-6 py-3 text-slate-900 font-mono text-xs font-medium">{item.uid || '-'}</td>
                                            <td className="px-6 py-3 text-slate-600 font-medium">{item.component_type || '-'}</td>
                                            <td className="px-6 py-3 text-slate-600">{item.lot_number || '-'}</td>
                                            <td className="px-6 py-3 text-slate-600">{item.vendor_name || '-'}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>

                        <div className="border-t border-slate-100 p-6 bg-slate-50/50 flex justify-end gap-3">
                            <Button
                                variant="ghost"
                                onClick={() => setFile(null)}
                                className="text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
                            >
                                Cancel
                            </Button>
                            <Button
                                onClick={handleUpload}
                                disabled={uploadStatus === 'uploading' || errorCount > 0}
                                className={cn(
                                    "min-w-[140px] shadow-lg transition-all duration-300",
                                    uploadStatus === 'success'
                                        ? "bg-emerald-500 hover:bg-emerald-600 shadow-emerald-500/25"
                                        : "bg-brand-600 hover:bg-brand-700 shadow-brand-500/25",
                                    (uploadStatus === 'uploading' || errorCount > 0) && "opacity-50 cursor-not-allowed shadow-none"
                                )}
                            >
                                {uploadStatus === 'uploading' ? (
                                    <>
                                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                        Importing...
                                    </>
                                ) : uploadStatus === 'success' ? (
                                    <>
                                        <Check className="h-4 w-4 mr-2" />
                                        Imported!
                                    </>
                                ) : (
                                    <>
                                        Import {validCount} Items
                                        <ArrowRight className="h-4 w-4 ml-2 opacity-80" />
                                    </>
                                )}
                            </Button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
