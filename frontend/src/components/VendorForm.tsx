import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createVendor, updateVendor, type Vendor, type VendorUpdate } from '../api/vendors';

interface VendorFormProps {
    vendor?: Vendor;
    onClose: () => void;
}

export default function VendorForm({ vendor, onClose }: VendorFormProps) {
    const [name, setName] = useState(vendor?.name || '');
    const [contactInfo, setContactInfo] = useState(
        vendor?.contact_info ? JSON.stringify(vendor.contact_info, null, 2) : ''
    );
    const [metadata, setMetadata] = useState(
        vendor?.metadata ? JSON.stringify(vendor.metadata, null, 2) : ''
    );
    const [error, setError] = useState('');

    const queryClient = useQueryClient();

    const createMutation = useMutation({
        mutationFn: createVendor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vendors'] });
            onClose();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Failed to create vendor');
        }
    });

    const updateMutation = useMutation({
        mutationFn: (data: VendorUpdate) => updateVendor(vendor!.id, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vendors'] });
            queryClient.invalidateQueries({ queryKey: ['vendor', vendor!.id] });
            onClose();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Failed to update vendor');
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        let parsedContactInfo = null;
        let parsedMetadata = null;

        try {
            if (contactInfo) parsedContactInfo = JSON.parse(contactInfo);
        } catch (e) {
            setError('Invalid JSON in Contact Info');
            return;
        }

        try {
            if (metadata) parsedMetadata = JSON.parse(metadata);
        } catch (e) {
            setError('Invalid JSON in Metadata');
            return;
        }

        if (vendor) {
            updateMutation.mutate({
                name,
                contact_info: parsedContactInfo,
                metadata: parsedMetadata
            });
        } else {
            createMutation.mutate({
                name,
                contact_info: parsedContactInfo,
                metadata: parsedMetadata
            });
        }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
                <h2 className="text-xl font-bold mb-4">{vendor ? 'Edit Vendor' : 'Create Vendor'}</h2>

                {error && (
                    <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2">
                            Name
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                            required
                        />
                    </div>

                    <div className="mb-4">
                        <label className="block text-gray-700 text-sm font-bold mb-2">
                            Contact Info (JSON)
                        </label>
                        <textarea
                            value={contactInfo}
                            onChange={(e) => setContactInfo(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline font-mono text-sm"
                            rows={4}
                            placeholder='{"email": "...", "phone": "..."}'
                        />
                    </div>

                    <div className="mb-6">
                        <label className="block text-gray-700 text-sm font-bold mb-2">
                            Metadata (JSON)
                        </label>
                        <textarea
                            value={metadata}
                            onChange={(e) => setMetadata(e.target.value)}
                            className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline font-mono text-sm"
                            rows={4}
                            placeholder='{"key": "value"}'
                        />
                    </div>

                    <div className="flex items-center justify-end gap-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            disabled={isLoading}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            disabled={isLoading}
                        >
                            {isLoading ? 'Saving...' : 'Save'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
