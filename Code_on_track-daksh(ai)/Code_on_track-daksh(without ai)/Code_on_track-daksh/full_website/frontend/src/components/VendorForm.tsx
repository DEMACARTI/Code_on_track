import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createVendor, updateVendor, type Vendor, type VendorCreate, type VendorUpdate } from '../api/vendors';
import { Button } from './ui/Button';
import { Input } from './ui/Input';
import { AlertCircle, Save, X } from 'lucide-react';

interface VendorFormProps {
    vendor?: Vendor;
    onClose: () => void;
}

export default function VendorForm({ vendor, onClose }: VendorFormProps) {
    const [formData, setFormData] = useState<Partial<VendorCreate>>({
        name: vendor?.name || '',
        vendor_code: vendor?.vendor_code || '',
        contact_name: vendor?.contact_name || '',
        contact_email: vendor?.contact_email || '',
        contact_phone: vendor?.contact_phone || '',
        address: vendor?.address || '',
        warranty_months: vendor?.warranty_months,
        notes: vendor?.notes || ''
    });

    // Errors state
    const [errors, setErrors] = useState<Record<string, string>>({});
    const [apiError, setApiError] = useState('');

    const queryClient = useQueryClient();

    const createMutation = useMutation({
        mutationFn: createVendor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vendors'] });
            onClose();
        },
        onError: (err: any) => {
            setApiError(err.response?.data?.detail || 'Failed to create vendor');
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
            setApiError(err.response?.data?.detail || 'Failed to update vendor');
        }
    });

    const validate = () => {
        const newErrors: Record<string, string> = {};

        if (!formData.name?.trim() || formData.name.length < 3) {
            newErrors.name = 'Name must be at least 3 characters';
        }

        if (!vendor && (!formData.vendor_code?.trim())) {
            // vendor_code required for creation mostly, or logically required
            // User: "vendor_code (string) — Unique vendor code... optional but if provided must be unique"
            // Wait, request said: "Required: name, vendor_code".
            // So I will make it required.
            newErrors.vendor_code = 'Vendor Code is required';
        }

        if (formData.contact_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.contact_email)) {
            newErrors.contact_email = 'Invalid email address';
        }

        if (formData.contact_phone && !/^\+?[\d\s-]{10,}$/.test(formData.contact_phone)) {
            // Basic phone validation: allows +, digits, space, dash, min 10 chars
            newErrors.contact_phone = 'Invalid phone number format';
        }

        if (formData.warranty_months !== undefined && formData.warranty_months !== null && formData.warranty_months < 0) {
            newErrors.warranty_months = 'Warranty must be positive';
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setApiError('');

        if (!validate()) return;

        if (vendor) {
            updateMutation.mutate(formData as VendorUpdate);
        } else {
            createMutation.mutate(formData as VendorCreate);
        }
    };

    const isLoading = createMutation.isPending || updateMutation.isPending;

    const handleChange = (field: keyof VendorCreate, value: any) => {
        setFormData(prev => ({ ...prev, [field]: value }));
        // Clear error for field
        if (errors[field]) {
            setErrors(prev => {
                const newErrors = { ...prev };
                delete newErrors[field];
                return newErrors;
            });
        }
    };

    return (
        <div className="space-y-6">
            {apiError && (
                <div className="flex items-center gap-2 rounded-lg bg-rose-50 p-3 text-sm text-rose-600 border border-rose-100">
                    <AlertCircle className="h-4 w-4 flex-shrink-0" />
                    <p className="font-medium">{apiError}</p>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <Input
                            label="Name *"
                            value={formData.name}
                            onChange={(e) => handleChange('name', e.target.value)}
                            placeholder="ACME Rails Pvt Ltd"
                            error={errors.name}
                            className={errors.name ? "border-rose-300 focus:ring-rose-200" : ""}
                        />
                    </div>
                    <div className="space-y-1">
                        <Input
                            label="Vendor Code *"
                            value={formData.vendor_code}
                            onChange={(e) => handleChange('vendor_code', e.target.value)}
                            placeholder="ACME-01"
                            error={errors.vendor_code}
                            className={errors.vendor_code ? "border-rose-300 focus:ring-rose-200" : ""}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <Input
                            label="Contact Name"
                            value={formData.contact_name}
                            onChange={(e) => handleChange('contact_name', e.target.value)}
                            placeholder="Ramesh Kumar"
                        />
                    </div>
                    <div className="space-y-1">
                        <Input
                            label="Contact Email"
                            type="email"
                            value={formData.contact_email}
                            onChange={(e) => handleChange('contact_email', e.target.value)}
                            placeholder="ramesh@acme.com"
                            error={errors.contact_email}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1">
                        <Input
                            label="Contact Phone"
                            value={formData.contact_phone}
                            onChange={(e) => handleChange('contact_phone', e.target.value)}
                            placeholder="+91 98xxxxxxx"
                            error={errors.contact_phone}
                        />
                    </div>
                    <div className="space-y-1">
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            Default Warranty (Months)
                        </label>
                        <Input
                            type="number"
                            value={formData.warranty_months ?? ''}
                            onChange={(e) => handleChange('warranty_months', e.target.value ? parseInt(e.target.value) : null)}
                            placeholder="24"
                            error={errors.warranty_months}
                        />
                        <p className="text-xs text-slate-500 mt-1">If left blank, item-level warranty will be used where present.</p>
                    </div>
                </div>

                <div className="space-y-1">
                    <Input
                        label="Address"
                        value={formData.address}
                        onChange={(e) => handleChange('address', e.target.value)}
                        placeholder="Plot 12, Industrial Area, Pune"
                    />
                </div>

                <div className="space-y-1">
                    <label className="block text-sm font-medium text-slate-700 mb-1">
                        Notes
                    </label>
                    <textarea
                        value={formData.notes || ''}
                        onChange={(e) => handleChange('notes', e.target.value)}
                        className="flex min-h-[80px] w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 placeholder:text-slate-400 focus:border-brand-500 focus:outline-none focus:ring-4 focus:ring-brand-500/10 transition-all shadow-sm"
                        placeholder="Preferred vendor for..."
                    />
                </div>

                <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
                    <Button
                        type="button"
                        variant="ghost"
                        onClick={onClose}
                        disabled={isLoading}
                        className="hover:bg-slate-100 text-slate-600"
                    >
                        <X className="h-4 w-4 mr-2" />
                        Cancel
                    </Button>
                    <Button
                        type="submit"
                        isLoading={isLoading}
                        className="bg-brand-600 hover:bg-brand-700 text-white shadow-lg shadow-brand-500/25"
                    >
                        <Save className="h-4 w-4 mr-2" />
                        {vendor ? 'Save Changes' : 'Create Vendor'}
                    </Button>
                </div>
            </form>
        </div>
    );
}
