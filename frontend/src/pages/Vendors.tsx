import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listVendors, deleteVendor, Vendor } from '../api/vendors';
import VendorRow from '../components/VendorRow';
import VendorForm from '../components/VendorForm';
import { useAuth } from '../hooks/useAuth';
import { Plus, Search } from 'lucide-react';

export default function Vendors() {
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [editingVendor, setEditingVendor] = useState<Vendor | undefined>(undefined);

    const { role } = useAuth();
    const isAdmin = role === 'admin';
    const queryClient = useQueryClient();

    const { data: vendors, isLoading, error } = useQuery({
        queryKey: ['vendors', search, page],
        queryFn: () => listVendors({ q: search, page, page_size: 20 })
    });

    const deleteMutation = useMutation({
        mutationFn: deleteVendor,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['vendors'] });
        }
    });

    const handleEdit = (vendor: Vendor) => {
        setEditingVendor(vendor);
        setIsFormOpen(true);
    };

    const handleDelete = (id: number) => {
        if (window.confirm('Are you sure you want to deactivate this vendor?')) {
            deleteMutation.mutate(id);
        }
    };

    const handleCreate = () => {
        setEditingVendor(undefined);
        setIsFormOpen(true);
    };

    const handleCloseForm = () => {
        setIsFormOpen(false);
        setEditingVendor(undefined);
    };

    return (
        <div className="container mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">Vendors</h1>
                {isAdmin && (
                    <button
                        onClick={handleCreate}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
                    >
                        <Plus size={20} />
                        Create Vendor
                    </button>
                )}
            </div>

            <div className="mb-6 relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Search className="h-5 w-5 text-gray-400" />
                </div>
                <input
                    type="text"
                    placeholder="Search vendors..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="pl-10 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm py-2 border"
                />
            </div>

            {isLoading ? (
                <div className="text-center py-8">Loading...</div>
            ) : error ? (
                <div className="text-center py-8 text-red-600">Error loading vendors</div>
            ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                    <table className="min-w-full divide-y divide-gray-200">
                        <thead className="bg-gray-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Name</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Items</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-gray-200">
                            {vendors?.map((vendor) => (
                                <VendorRow
                                    key={vendor.id}
                                    vendor={vendor}
                                    onEdit={handleEdit}
                                    onDelete={handleDelete}
                                />
                            ))}
                            {vendors?.length === 0 && (
                                <tr>
                                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                                        No vendors found
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            )}

            {isFormOpen && (
                <VendorForm
                    vendor={editingVendor}
                    onClose={handleCloseForm}
                />
            )}
        </div>
    );
}
