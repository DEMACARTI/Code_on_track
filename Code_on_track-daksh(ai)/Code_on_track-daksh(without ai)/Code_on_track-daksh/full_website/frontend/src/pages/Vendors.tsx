import { useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '../api/axios';
import VendorForm from '../components/VendorForm';
import VendorDetails from '../components/VendorDetails';
import { useAuth } from '../context/AuthContext';
import { RefreshCw, AlertTriangle, XCircle, Store, Plus } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableHead, TableHeader, TableRow, TableLoading, TableEmpty, TableCell } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { SearchInput } from '../components/ui/SearchInput';
import { Modal } from '../components/ui/Modal';
import { motion } from 'framer-motion';

interface Vendor {
    id: number;
    name: string;
    vendor_code: string;
    component_supplied: string; // Backend returns string (implied from SQL) or I should parse it if it's JSON? 
    // Backend: "component_supplied": row.component_supplied. 
    // If postgres table has it as text, it's text. 
    // Previous code treated it as string[]: vendor.components_supplied?.join(', ')
    // Let's assume backend returns string or we adjust display.
    items_count: number;
}

interface VendorsResponse {
    vendors: Vendor[];
    total: number;
}

export default function Vendors() {
    const [inputValue, setInputValue] = useState('');
    const [searchId, setSearchId] = useState('');
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [selectedVendorId, setSelectedVendorId] = useState<number | null>(null);

    const { role } = useAuth();
    const isAdmin = role === 'admin';
    const queryClient = useQueryClient();

    const { data, isLoading, error } = useQuery<VendorsResponse>({
        queryKey: ['vendors', searchId],
        queryFn: async () => {
            try {
                const res = await api.get('/vendors');
                console.log("Vendors Data:", res.data);
                return res.data;
            } catch (err: any) {
                console.error("Vendors Fetch Error:", err.response?.status, err.response?.data);
                throw err;
            }
        }
    });

    const allVendors = data?.vendors || [];
    const vendors = searchId
        ? allVendors.filter(v => v.id.toString() === searchId || v.vendor_code.includes(searchId))
        : allVendors;

    const handleRefresh = () => {
        queryClient.invalidateQueries({ queryKey: ['vendors'] });
    };

    const handleCreate = () => {
        setIsFormOpen(true);
    };

    const handleCloseForm = () => {
        setIsFormOpen(false);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Vendors</h1>
                    <p className="text-slate-500 mt-1">Manage your suppliers and partners.</p>
                </div>
                <div className="flex flex-wrap gap-2">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={handleRefresh}
                        disabled={isLoading}
                        className="bg-white hover:bg-slate-50"
                    >
                        <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
                        Refresh
                    </Button>
                    {isAdmin && (
                        <Button
                            onClick={handleCreate}
                            className="bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-700 hover:to-brand-600 shadow-lg shadow-brand-500/25 border-0"
                        >
                            <Plus className="mr-2 h-4 w-4" />
                            Create Vendor
                        </Button>
                    )}
                </div>
            </div>

            <Card className="glass border-0 shadow-lg shadow-slate-200/50 overflow-hidden">
                <CardHeader className="flex flex-col md:flex-row items-start md:items-center justify-between space-y-4 md:space-y-0 pb-6 border-b border-slate-100/50">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-brand-50 rounded-lg">
                            <Store className="h-5 w-5 text-brand-600" />
                        </div>
                        <div>
                            <CardTitle className="text-lg font-bold text-slate-900">All Vendors</CardTitle>
                            <p className="text-sm text-slate-500">
                                {vendors ? `${vendors.length} vendors found` : 'Loading...'}
                            </p>
                        </div>
                    </div>
                    <div className="w-full md:w-96 space-y-2">
                        <SearchInput
                            value={inputValue}
                            onChange={setInputValue}
                            onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                    setSearchId(inputValue.trim());
                                }
                            }}
                            placeholder="Search by Vendor Code or ID..."
                            className="bg-slate-50/50 border-slate-200 focus:ring-brand-500/20"
                        />
                        <p className="text-xs text-slate-400 pl-1">Press Enter to search</p>
                    </div>
                </CardHeader>
                <CardContent className="p-0">
                    {searchId && (
                        <div className="px-6 py-3 bg-brand-50/30 border-b border-brand-100/50 flex items-center justify-between">
                            <div className="flex items-center gap-2 text-sm text-brand-700">
                                <span>Showing results for: <strong>{searchId}</strong></span>
                            </div>
                            <button
                                onClick={() => {
                                    setInputValue('');
                                    setSearchId('');
                                }}
                                className="text-slate-400 hover:text-slate-600 p-1 hover:bg-white rounded-full transition-colors"
                            >
                                <XCircle className="h-4 w-4" />
                            </button>
                        </div>
                    )}
                    <div className="overflow-x-auto">
                        <Table>
                            <TableHeader>
                                <TableRow className="bg-slate-50/50 hover:bg-slate-50/50">
                                    <TableHead className="pl-6 text-xs uppercase tracking-wider font-semibold text-slate-500">ID</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Name</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Code</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Items Count</TableHead>
                                    <TableHead className="text-xs uppercase tracking-wider font-semibold text-slate-500">Component Supplied</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {isLoading ? (
                                    <TableLoading colSpan={5} />
                                ) : error ? (
                                    <TableRow>
                                        <td colSpan={5} className="h-32 text-center text-rose-500">
                                            <div className="flex flex-col items-center justify-center">
                                                <AlertTriangle className="h-8 w-8 mb-2" />
                                                <p>Error loading vendors</p>
                                            </div>
                                        </td>
                                    </TableRow>
                                ) : vendors.length > 0 ? (
                                    vendors.map((vendor) => (
                                        <TableRow
                                            key={vendor.id}
                                            className="hover:bg-brand-50/30 transition-colors border-b border-slate-50 last:border-0 cursor-pointer"
                                            onClick={() => setSelectedVendorId(vendor.id)}
                                        >
                                            <TableCell className="pl-6 font-mono text-sm font-medium text-brand-600">
                                                {vendor.id}
                                            </TableCell>
                                            <TableCell className="font-medium text-slate-900">
                                                {vendor.name}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-600 font-mono">
                                                {vendor.vendor_code}
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-600">
                                                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-800">
                                                    {vendor.items_count ?? 0}
                                                </span>
                                            </TableCell>
                                            <TableCell className="text-sm text-slate-600">
                                                {vendor.component_supplied || '—'}
                                            </TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableEmpty colSpan={5} message="No vendors found" />
                                )}
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card >

            <Modal
                isOpen={isFormOpen}
                onClose={handleCloseForm}
                title="Create Vendor"
            >
                <VendorForm
                    onClose={handleCloseForm}
                />
            </Modal>

            <VendorDetails
                vendorId={selectedVendorId}
                onClose={() => setSelectedVendorId(null)}
            />
        </motion.div >
    );
}
