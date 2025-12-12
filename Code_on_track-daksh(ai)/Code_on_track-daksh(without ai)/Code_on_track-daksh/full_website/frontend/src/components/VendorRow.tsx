import { Link } from 'react-router-dom';
import { type Vendor } from '../api/vendors';
import { useAuth } from '../context/AuthContext';
import { TableRow, TableCell } from './ui/Table';
import { Button } from './ui/Button';
import { Chip } from './ui/Chip';
import { Eye, Edit, Trash2 } from 'lucide-react';

interface VendorRowProps {
    vendor: Vendor;
    onEdit: (vendor: Vendor) => void;
    onDelete: (id: number) => void;
}

export default function VendorRow({ vendor, onEdit, onDelete }: VendorRowProps) {
    const { role } = useAuth();
    const isAdmin = role === 'admin';

    return (
        <TableRow className="hover:bg-brand-50/30 transition-colors border-b border-slate-50 last:border-0">
            <TableCell className="pl-6 font-mono text-xs font-medium text-slate-700">
                {vendor.id}
            </TableCell>
            <TableCell className="font-medium">
                <Link
                    to={`/vendors/${vendor.id}`}
                    className="text-slate-900 hover:text-brand-600 transition-colors font-semibold"
                >
                    {vendor.name}
                </Link>
            </TableCell>
            <TableCell className="text-slate-600 text-sm">
                {vendor.items_count} items
            </TableCell>
            <TableCell className="text-slate-600 text-sm font-mono text-xs">
                {new Date(vendor.created_at).toLocaleDateString()}
            </TableCell>
            <TableCell>
                <Chip
                    label={vendor.is_active ? 'Active' : 'Inactive'}
                    variant={vendor.is_active ? 'success' : 'danger'}
                    className="shadow-sm"
                />
            </TableCell>
            <TableCell className="pr-6">
                <div className="flex gap-2">
                    <Link to={`/vendors/${vendor.id}`}>
                        <Button variant="ghost" size="sm" className="text-brand-600 hover:text-brand-700 hover:bg-brand-50">
                            <Eye className="h-4 w-4 mr-1" />
                            View
                        </Button>
                    </Link>
                    {isAdmin && (
                        <>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onEdit(vendor)}
                                className="text-blue-600 hover:text-blue-700 hover:bg-blue-50"
                            >
                                <Edit className="h-4 w-4 mr-1" />
                                Edit
                            </Button>
                            <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => onDelete(vendor.id)}
                                className="text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                            >
                                <Trash2 className="h-4 w-4 mr-1" />
                                Deactivate
                            </Button>
                        </>
                    )}
                </div>
            </TableCell>
        </TableRow>
    );
}
