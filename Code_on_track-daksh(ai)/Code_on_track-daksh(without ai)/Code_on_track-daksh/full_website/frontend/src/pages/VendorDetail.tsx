import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getVendor } from '../api/vendors';
import { useAuth } from '../hooks/useAuth';
import VendorForm from '../components/VendorForm';
import { Edit, ArrowLeft } from 'lucide-react';
import api from '../api/axios';

export default function VendorDetail() {
    const { id } = useParams<{ id: string }>();
    const { role } = useAuth();
    const isAdmin = role === 'admin';
    const [isFormOpen, setIsFormOpen] = useState(false);

    const { data: vendor, isLoading, error } = useQuery({
        queryKey: ['vendor', id],
        queryFn: () => getVendor(Number(id)),
        enabled: !!id
    });

    // Fetch items for this vendor
    const { data: items } = useQuery({
        queryKey: ['vendor-items', id],
        queryFn: async () => {
            const res = await api.get(`/items?vendor_id=${id}&page=1&page_size=20`);
            return res.data;
        },
        enabled: !!id
    });

    if (isLoading) return <div className="p-8 text-center">Loading...</div>;
    if (error || !vendor) return <div className="p-8 text-center text-red-600">Vendor not found</div>;

    return (
        <div className="container mx-auto px-4 py-8">
            <Link to="/vendors" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
                <ArrowLeft size={20} className="mr-2" />
                Back to Vendors
            </Link>

            <div className="bg-white shadow rounded-lg p-6 mb-8">
                <div className="flex justify-between items-start mb-6">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 mb-2">{vendor.name}</h1>
                        <span className={`px-2 py-1 text-xs font-semibold rounded-full ${vendor.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {vendor.is_active ? 'Active' : 'Inactive'}
                        </span>
                    </div>
                    {isAdmin && (
                        <button
                            onClick={() => setIsFormOpen(true)}
                            className="flex items-center gap-2 text-blue-600 hover:text-blue-800"
                        >
                            <Edit size={20} />
                            Edit Vendor
                        </button>
                    )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div>
                        <h3 className="text-lg font-semibold mb-3">Contact Info</h3>
                        <div className="bg-gray-50 p-4 rounded text-sm space-y-2">
                            <p><span className="font-semibold">Name:</span> {vendor.contact_name || 'N/A'}</p>
                            <p><span className="font-semibold">Email:</span> {vendor.contact_email || 'N/A'}</p>
                            <p><span className="font-semibold">Phone:</span> {vendor.contact_phone || 'N/A'}</p>
                            <p><span className="font-semibold">Address:</span> {vendor.address || 'N/A'}</p>
                        </div>
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold mb-3">Details</h3>
                        <div className="bg-gray-50 p-4 rounded text-sm space-y-2">
                            <p><span className="font-semibold">Vendor Code:</span> {vendor.vendor_code || 'N/A'}</p>
                            <p><span className="font-semibold">Warranty:</span> {vendor.warranty_months ? `${vendor.warranty_months} months` : 'N/A'}</p>
                            <p><span className="font-semibold">Components:</span> {vendor.components_supplied?.join(', ') || 'N/A'}</p>
                            <div className="mt-2">
                                <span className="font-semibold">Notes:</span>
                                <p className="mt-1 whitespace-pre-wrap text-gray-600">{vendor.notes || 'No notes'}</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-6 text-sm text-gray-500">
                    Created on: {new Date(vendor.created_at).toLocaleString()}
                </div>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-xl font-bold mb-4">Items ({vendor.items_count})</h2>
                {items && items.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="min-w-full divide-y divide-gray-200">
                            <thead className="bg-gray-50">
                                <tr>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">UID</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Component</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created At</th>
                                </tr>
                            </thead>
                            <tbody className="bg-white divide-y divide-gray-200">
                                {items.map((item: any) => (
                                    <tr key={item.uid} className="hover:bg-gray-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <Link to={`/items/${item.uid}`} className="text-blue-600 hover:text-blue-900">
                                                {item.uid}
                                            </Link>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {item.component_type}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {item.status}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                            {new Date(item.created_at).toLocaleDateString()}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <p className="text-gray-500">No items found for this vendor.</p>
                )}
            </div>

            {isFormOpen && (
                <VendorForm
                    vendor={vendor}
                    onClose={() => setIsFormOpen(false)}
                />
            )}
        </div>
    );
}
