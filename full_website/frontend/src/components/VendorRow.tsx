import { Link } from 'react-router-dom';
import { type Vendor } from '../api/vendors';
import { useAuth } from '../context/AuthContext';
import { TableRow, TableCell } from './ui/Table';
import { Button } from './ui/Button';
import { Chip } from './ui/Chip';

interface VendorRowProps {
    vendor: Vendor;
    onEdit: (vendor: Vendor) => void;
    onDelete: (id: number) => void;
}

export default function VendorRow({ vendor, onEdit, onDelete }: VendorRowProps) {
    const { role } = useAuth();
    const isAdmin = role === 'admin';

    return (
        <TableRow>
            <TableCell className="font-medium text-gray-500">
                {vendor.id}
            </TableCell>
            <TableCell className="font-medium">
                <Link
                    to={`/vendors/${vendor.id}`}
                    className="text-primary-600 hover:text-primary-900 hover:underline"
                >
                    {vendor.name}
                </Link>
            </TableCell>
            <TableCell className="text-gray-500">
                {vendor.items_count}
            </TableCell>
            <TableCell className="text-gray-500">
                {new Date(vendor.created_at).toLocaleDateString()}
            </TableCell>
            <TableCell>
                <Chip
                    label={vendor.is_active ? 'Active' : 'Inactive'}
                    variant={vendor.is_active ? 'success' : 'danger'}
                />
            </TableCell>
            <TableCell>
                <div className="flex gap-2">
                    <Link to={`/vendors/${vendor.id}`}>
                        <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-900">
                            View
                        </Button>
                    </Link>
                    {isAdmin && (
                        <>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onEdit(vendor)}
                                className="text-blue-600 hover:text-blue-900"
                            >
                                Edit
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onDelete(vendor.id)}
                                className="text-red-600 hover:text-red-900"
                            >
                                Deactivate
                            </Button>
                        </>
                    )}
                </div>
            </TableCell>
        </TableRow>
    );
}
