import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { previewImport, commitImport, type ImportPreviewResponse } from '../api/import';
import ImportPreviewTable from '../components/ImportPreviewTable';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Upload, Check, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const ImportItems: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [createVendors, setCreateVendors] = useState(false);
    const [previewData, setPreviewData] = useState<ImportPreviewResponse | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [successMsg, setSuccessMsg] = useState<string | null>(null);

    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const previewMutation = useMutation({
        mutationFn: (formData: FormData) => previewImport(formData),
        onSuccess: (data) => {
            setPreviewData(data);
            setError(null);
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Failed to preview import');
            setPreviewData(null);
        },
    });

    const commitMutation = useMutation({
        mutationFn: (formData: FormData) => commitImport(formData),
        onSuccess: (data) => {
            setSuccessMsg(`Successfully imported ${data.created_items.length} items.`);
            setPreviewData(null);
            setFile(null);
            queryClient.invalidateQueries({ queryKey: ['items'] });
            setTimeout(() => navigate('/items'), 2000);
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Failed to commit import');
        },
    });

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            setPreviewData(null);
            setError(null);
            setSuccessMsg(null);
        }
    };

    const handlePreview = () => {
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('create_vendors', createVendors.toString());
        previewMutation.mutate(formData);
    };

    const handleCommit = () => {
        if (!file) return;
        const formData = new FormData();
        formData.append('file', file);
        formData.append('create_vendors', createVendors.toString());
        formData.append('commit', 'true');
        commitMutation.mutate(formData);
    };

    const isProcessing = previewMutation.isPending || commitMutation.isPending;
    const canCommit = previewData && previewData.invalid_rows.length === 0;

    return (
        <div className="space-y-6 max-w-5xl mx-auto">
            <h1 className="text-2xl font-bold text-gray-900">Import Items</h1>

            <Card>
                <CardHeader>
                    <CardTitle>Upload CSV</CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:bg-gray-50 transition-colors relative">
                        <input
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                            disabled={isProcessing}
                        />
                        <div className="flex flex-col items-center justify-center space-y-2 pointer-events-none">
                            <div className="h-12 w-12 bg-primary-50 text-primary-600 rounded-full flex items-center justify-center">
                                <Upload size={24} />
                            </div>
                            <p className="text-sm font-medium text-gray-900">
                                {file ? file.name : "Click to upload or drag and drop"}
                            </p>
                            <p className="text-xs text-gray-500">CSV files only</p>
                        </div>
                    </div>

                    <div className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            id="create-vendors"
                            checked={createVendors}
                            onChange={(e) => setCreateVendors(e.target.checked)}
                            className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                            disabled={isProcessing}
                        />
                        <label htmlFor="create-vendors" className="text-sm text-gray-700">
                            Create missing vendors automatically
                        </label>
                    </div>



                    <div className="flex justify-end gap-3">
                        <Button
                            onClick={handlePreview}
                            disabled={!file || isProcessing}
                            isLoading={previewMutation.isPending}
                        >
                            Preview Import
                        </Button>
                        <Button
                            onClick={handleCommit}
                            disabled={!canCommit || isProcessing}
                            isLoading={commitMutation.isPending}
                            variant="primary"
                            className={!canCommit ? "opacity-50 cursor-not-allowed" : "bg-green-600 hover:bg-green-700"}
                        >
                            Commit Import
                        </Button>
                    </div>
                </CardContent>
            </Card>

            {previewData && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <ImportPreviewTable preview={previewData} />
                </motion.div>
            )}
            {/* Toast Notifications */}
            {(successMsg || error) && (
                <motion.div
                    initial={{ opacity: 0, y: 50 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 50 }}
                    className={`fixed bottom-6 right-6 z-50 p-4 rounded-lg shadow-lg flex items-center gap-3 ${successMsg ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-rose-50 text-rose-800 border border-rose-200'
                        }`}
                >
                    {successMsg ? <Check className="h-5 w-5" /> : <AlertCircle className="h-5 w-5" />}
                    <p className="font-medium">{successMsg || (typeof error === 'string' ? error : 'An error occurred')}</p>
                    <button
                        onClick={() => { setSuccessMsg(null); setError(null); }}
                        className="ml-2 p-1 hover:bg-black/5 rounded-full"
                    >
                        <span className="sr-only">Close</span>
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </motion.div>
            )}
        </div>
    );
};

export default ImportItems;
