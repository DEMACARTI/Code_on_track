import React, { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { previewImport, commitImport, type ImportPreviewResponse } from '../api/import';
import ImportPreviewTable from '../components/ImportPreviewTable';

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
            // Invalidate items query to refresh list
            queryClient.invalidateQueries({ queryKey: ['items'] });
            // Redirect after short delay
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
        commitMutation.mutate(formData);
    };

    const isProcessing = previewMutation.isPending || commitMutation.isPending;
    const canCommit = previewData && previewData.invalid_rows.length === 0;

    return (
        <div className="max-w-4xl mx-auto p-6">
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Import Items</h1>

            <div className="bg-white shadow rounded-lg p-6 mb-6">
                <div className="mb-6">
                    <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
                        Select CSV File
                    </label>
                    <input
                        id="file-upload"
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-gray-500
                            file:mr-4 file:py-2 file:px-4
                            file:rounded-md file:border-0
                            file:text-sm file:font-semibold
                            file:bg-indigo-50 file:text-indigo-700
                            hover:file:bg-indigo-100"
                        disabled={isProcessing}
                    />
                    <p className="mt-1 text-sm text-gray-500">
                        Required columns: uid, component_type. Optional: vendor_name, lot_no, metadata.
                    </p>
                </div>

                <div className="mb-6">
                    <label className="flex items-center space-x-2">
                        <input
                            type="checkbox"
                            checked={createVendors}
                            onChange={(e) => setCreateVendors(e.target.checked)}
                            className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            disabled={isProcessing}
                        />
                        <span className="text-sm text-gray-700">Create missing vendors automatically</span>
                    </label>
                </div>

                <div className="flex space-x-4">
                    <button
                        onClick={handlePreview}
                        disabled={!file || isProcessing}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                    >
                        {previewMutation.isPending ? 'Uploading...' : 'Preview Import'}
                    </button>

                    <button
                        onClick={handleCommit}
                        disabled={!canCommit || isProcessing}
                        className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:bg-gray-400"
                    >
                        {commitMutation.isPending ? 'Importing...' : 'Commit Import'}
                    </button>
                </div>

                {error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
                        {typeof error === 'string' ? error : JSON.stringify(error)}
                    </div>
                )}

                {successMsg && (
                    <div className="mt-4 p-4 bg-green-50 text-green-700 rounded-md">
                        {successMsg}
                    </div>
                )}
            </div>

            {previewData && <ImportPreviewTable preview={previewData} />}
        </div>
    );
};

export default ImportItems;
