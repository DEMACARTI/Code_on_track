import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../api/axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableLoading, TableEmpty } from '../components/ui/Table';
import { Button } from '../components/ui/Button';
import { SearchInput } from '../components/ui/SearchInput';
import { Chip } from '../components/ui/Chip';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface Item {
    uid: string;
    component_type: string;
    status: string;
    created_at?: string;
}

interface ItemsResponse {
    items: Item[];
    total: number;
    page: number;
    size: number;
}

export default function Items() {
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const pageSize = 10;

    const { data, isLoading, error } = useQuery<ItemsResponse | Item[]>({
        queryKey: ['items', search, page],
        queryFn: async () => {
            const res = await api.get('/items', { params: { q: search, page, page_size: pageSize } });
            // Handle both array (legacy) and paginated response
            if (Array.isArray(res.data)) {
                return res.data;
            }
            return res.data;
        }
    });

    const items = Array.isArray(data) ? data : data?.items || [];
    const total = Array.isArray(data) ? data.length : data?.total || 0;
    const totalPages = Math.ceil(total / pageSize);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Items</h1>
            </div>

            <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
                    <CardTitle>Inventory</CardTitle>
                    <div className="w-full sm:w-72">
                        <SearchInput
                            value={search}
                            onChange={(val) => { setSearch(val); setPage(1); }}
                            placeholder="Search items..."
                        />
                    </div>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>UID</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Created At</TableHead>
                                <TableHead>Actions</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {isLoading ? (
                                <TableLoading colSpan={5} />
                            ) : error ? (
                                <TableRow>
                                    <td colSpan={5} className="h-24 text-center text-red-500">
                                        Error loading items
                                    </td>
                                </TableRow>
                            ) : items.length > 0 ? (
                                items.map((item) => (
                                    <TableRow key={item.uid}>
                                        <TableCell className="font-medium">{item.uid}</TableCell>
                                        <TableCell>{item.component_type}</TableCell>
                                        <TableCell>
                                            <Chip
                                                label={item.status}
                                                variant={
                                                    item.status === 'active' ? 'success' :
                                                        item.status === 'failed' ? 'danger' : 'default'
                                                }
                                            />
                                        </TableCell>
                                        <TableCell>
                                            {item.created_at ? new Date(item.created_at).toLocaleDateString() : '-'}
                                        </TableCell>
                                        <TableCell>
                                            <Link to={`/items/${item.uid}`}>
                                                <Button variant="ghost" size="sm" className="text-primary-600 hover:text-primary-900 hover:bg-primary-50">
                                                    View
                                                </Button>
                                            </Link>
                                        </TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableEmpty colSpan={5} message="No items found" />
                            )}
                        </TableBody>
                    </Table>

                    {/* Pagination */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-end space-x-2 py-4">
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                            >
                                <ChevronLeft className="h-4 w-4" />
                            </Button>
                            <span className="text-sm text-gray-600">
                                Page {page} of {totalPages}
                            </span>
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                            >
                                <ChevronRight className="h-4 w-4" />
                            </Button>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}
