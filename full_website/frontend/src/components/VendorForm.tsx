import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createVendor, updateVendor, type Vendor, type VendorUpdate } from '../api/vendors';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { AlertCircle } from 'lucide-react';

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
        <div className="space-y-6">
            {error && (
                <div className="flex items-center gap-2 rounded-lg bg-rose-50 p-3 text-sm text-rose-600">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <p>{error}</p>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="Name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    placeholder="Vendor Name"
                />

                <div>
                    <label className="mb-1.5 block text-sm font-medium text-slate-700">
                        Contact Info (JSON)
                    </label>
                    <textarea
                        value={contactInfo}
                        onChange={(e) => setContactInfo(e.target.value)}
                        className="flex min-h-[100px] w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-mono text-slate-900 placeholder:text-slate-400 focus:border-primary-500 focus:outline-none focus:ring-4 focus:ring-primary-500/10"
                        placeholder='{"email": "...", "phone": "..."}'
                    />
                </div>

                <div>
                    <label className="mb-1.5 block text-sm font-medium text-slate-700">
                        Metadata (JSON)
                    </label>
                    <textarea
                        value={metadata}
                        onChange={(e) => setMetadata(e.target.value)}
                        className="flex min-h-[100px] w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-mono text-slate-900 placeholder:text-slate-400 focus:border-primary-500 focus:outline-none focus:ring-4 focus:ring-primary-500/10"
                        placeholder='{"key": "value"}'
                    />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4">
                    <Button
                        type="button"
                        variant="ghost"
                        onClick={onClose}
                        disabled={isLoading}
                    >
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        isLoading={isLoading}
                    >
                        {vendor ? 'Save Changes' : 'Create Vendor'}
                    </Button>
                </div>
            </form>
        </div>
    );
}
