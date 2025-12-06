import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { listVendors, deleteVendor, type Vendor } from '../api/vendors';
import VendorRow from '../components/VendorRow';
import VendorForm from '../components/VendorForm';
import { useAuth } from '../context/AuthContext';
import { Plus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableHead, TableHeader, TableRow, TableLoading, TableEmpty } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { SearchInput } from '../components/ui/SearchInput';
import { Modal } from '../components/ui/Modal';

export default function Vendors() {
    const [search, setSearch] = useState('');
    const [page] = useState(1);
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
        <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <h1 className="text-2xl font-bold text-gray-900">Vendors</h1>
                {isAdmin && (
                    <Button onClick={handleCreate}>
                        <Plus className="mr-2 h-4 w-4" />
                        Create Vendor
                    </Button>
                )}
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                    <CardTitle>All Vendors</CardTitle>
                    <div className="w-full sm:w-72">
                        <SearchInput
                            value={search}
                            onChange={setSearch}
                            placeholder="Search vendors..."
                        />
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>ID</TableHead>
                                <TableHead>Name</TableHead>
                                <TableHead>Items</TableHead>
                                <TableHead>Created At</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                <TableLoading colSpan={6} />
                            ) : error ? (
                                <TableRow>
                                    <td colSpan={6} className="h-24 text-center text-red-500">
                                        Error loading vendors
                                    </td>
                                </TableRow>
                            ) : vendors && vendors.length > 0 ? (
                                vendors.map((vendor) => (
                                    <VendorRow
                                        key={vendor.id}
                                        vendor={vendor}
                                        onEdit={handleEdit}
                                        onDelete={handleDelete}
                                    />
                                ))
                            ) : (
                                <TableEmpty colSpan={6} message="No vendors found" />
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Modal
                isOpen={isFormOpen}
                onClose={handleCloseForm}
                title={editingVendor ? 'Edit Vendor' : 'Create Vendor'}
            >
                <VendorForm
                    vendor={editingVendor}
                    onClose={handleCloseForm}
                />
            </Modal>
        </div>
    );
}
