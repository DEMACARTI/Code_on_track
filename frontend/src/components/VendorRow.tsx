import { Link } from 'react-router-dom';
import { Vendor } from '../api/vendors';
import { useAuth } from '../hooks/useAuth';

interface VendorRowProps {
    vendor: Vendor;
    onEdit: (vendor: Vendor) => void;
    onDelete: (id: number) => void;
}

export default function VendorRow({ vendor, onEdit, onDelete }: VendorRowProps) {
    const { role } = useAuth();
    const isAdmin = role === 'admin';

    return (
        <tr className="hover:bg-gray-50">
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {vendor.id}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                <Link to={`/vendors/${vendor.id}`} className="text-blue-600 hover:text-blue-900">
                    {vendor.name}
                </Link>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {vendor.items_count}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {new Date(vendor.created_at).toLocaleDateString()}
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm">
                <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${vendor.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                    {vendor.is_active ? 'Active' : 'Inactive'}
                </span>
            </td>
            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div className="flex gap-2">
                    <Link to={`/vendors/${vendor.id}`} className="text-indigo-600 hover:text-indigo-900">
                        View
                    </Link>
                    {isAdmin && (
                        <>
                            <button
                                onClick={() => onEdit(vendor)}
                                className="text-blue-600 hover:text-blue-900"
                            >
                                Edit
                            </button>
                            <button
                                onClick={() => onDelete(vendor.id)}
                                className="text-red-600 hover:text-red-900"
                            >
                                Deactivate
                            </button>
                        </>
                    )}
                </div>
            </td>
        </tr>
    );
}
