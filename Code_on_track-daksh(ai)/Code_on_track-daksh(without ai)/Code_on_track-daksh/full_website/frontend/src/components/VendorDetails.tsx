import { useQuery } from '@tanstack/react-query';
import { getVendor, listVendorItems } from '../api/vendors';
import { Package, Phone, Mail, MapPin, Calendar, FileText, AlertTriangle, Building2, Hash, Award } from 'lucide-react';
import { Button } from './ui/Button';
import { Chip } from './ui/Chip';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, TableEmpty, TableLoading } from './ui/Table';
import { Drawer } from './ui/Drawer';

interface VendorDetailsProps {
    vendorId: number | null;
    onClose: () => void;
}

export default function VendorDetails({ vendorId, onClose }: VendorDetailsProps) {
    const { data: vendor, isLoading: isVendorLoading, error: vendorError } = useQuery({
        queryKey: ['vendor', vendorId],
        queryFn: () => getVendor(vendorId!),
        enabled: !!vendorId
    });

    const { data: items, isLoading: isItemsLoading, error: itemsError } = useQuery({
        queryKey: ['vendor-items', vendorId],
        queryFn: () => listVendorItems(vendorId!),
        enabled: !!vendorId
    });

    // Calculate Reliability Score
    const calculateReliability = () => {
        if (!vendor || !vendor.items_count) return 100; // Default to 100 if no items
        const failed = vendor.failed_count || 0;
        const total = vendor.items_count;
        const score = Math.max(0, 100 - (failed / total * 100));
        return Math.round(score);
    };

    const reliabilityScore = calculateReliability();
    const scoreColor = reliabilityScore >= 90 ? 'text-emerald-600 bg-emerald-50 border-emerald-100' :
        reliabilityScore >= 70 ? 'text-amber-600 bg-amber-50 border-amber-100' :
            'text-rose-600 bg-rose-50 border-rose-100';

    return (
        <Drawer
            isOpen={!!vendorId}
            onClose={onClose}
            title="Vendor Details"
            width="max-w-xl"
        >
            <div className="space-y-8">
                {isVendorLoading ? (
                    <div className="space-y-4 animate-pulse">
                        <div className="h-4 bg-slate-100 rounded w-1/4"></div>
                        <div className="h-8 bg-slate-100 rounded w-3/4"></div>
                        <div className="space-y-2 pt-4">
                            <div className="h-4 bg-slate-100 rounded w-full"></div>
                            <div className="h-4 bg-slate-100 rounded w-full"></div>
                        </div>
                    </div>
                ) : vendorError ? (
                    <div className="bg-rose-50 border border-rose-100 rounded-lg p-4 flex gap-3 text-rose-700">
                        <AlertTriangle className="h-5 w-5 shrink-0" />
                        <div>
                            <p className="font-medium">Error loading vendor details</p>
                            <p className="text-sm opacity-90">{(vendorError as Error).message}</p>
                        </div>
                    </div>
                ) : vendor ? (
                    <>
                        {/* Reliability Score Card */}
                        <div className={`p-4 rounded-xl border ${scoreColor} flex items-center justify-between`}>
                            <div className="flex items-center gap-3">
                                <div className={`p-2 rounded-lg bg-white/50 backdrop-blur-sm`}>
                                    <Award className="h-6 w-6" />
                                </div>
                                <div>
                                    <p className="text-xs font-bold uppercase tracking-wider opacity-80">Reliability Score</p>
                                    <p className="text-2xl font-bold">{reliabilityScore}%</p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-xs font-semibold opacity-80">Defect Rate</p>
                                <p className="text-sm font-medium">
                                    {vendor.failed_count || 0} / {vendor.items_count} Items
                                </p>
                            </div>
                        </div>

                        {/* Section 1: Basic Info */}
                        <section className="space-y-4">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                                <Building2 className="h-4 w-4" />
                                Basic Information
                            </h3>
                            <div className="grid grid-cols-2 gap-4 bg-slate-50/50 p-4 rounded-xl border border-slate-100">
                                <div>
                                    <label className="text-xs font-semibold text-slate-500 block mb-1">Vendor Name</label>
                                    <p className="font-medium text-slate-900">{vendor.name}</p>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-slate-500 block mb-1">Vendor Code</label>
                                    <div className="flex items-center gap-1.5">
                                        <Hash className="h-3.5 w-3.5 text-slate-400" />
                                        <span className="font-mono text-sm font-medium text-slate-700">{vendor.vendor_code || '—'}</span>
                                    </div>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-slate-500 block mb-1">Items Supplied</label>
                                    <span className="font-mono text-sm font-medium text-slate-700">{vendor.items_count}</span>
                                </div>
                                <div>
                                    <label className="text-xs font-semibold text-slate-500 block mb-1">Warranty</label>
                                    <div className="flex items-center gap-1.5">
                                        <Calendar className="h-3.5 w-3.5 text-slate-400" />
                                        <span className="text-sm text-slate-700">{vendor.warranty_months ? `${vendor.warranty_months} months` : '—'}</span>
                                    </div>
                                </div>
                                <div className="col-span-2">
                                    <label className="text-xs font-semibold text-slate-500 block mb-1">Components Supplied</label>
                                    <div className="flex flex-wrap gap-1.5">
                                        {vendor.components_supplied && vendor.components_supplied.length > 0 ? (
                                            vendor.components_supplied.map((comp: string, idx: number) => (
                                                <Chip key={idx} label={comp} variant="default" className="text-xs" />
                                            ))
                                        ) : (
                                            <span className="text-sm text-slate-400 italic">No components listed</span>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </section>

                        {/* Section 2: Contact Info */}
                        <section className="space-y-4">
                            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                                <Phone className="h-4 w-4" />
                                Contact Information
                            </h3>
                            <div className="space-y-3 p-4 rounded-xl border border-slate-100">
                                <div className="flex sm:items-center gap-3 flex-col sm:flex-row sm:justify-between">
                                    <span className="text-sm text-slate-500">Contact Person</span>
                                    <span className="text-sm font-medium text-slate-900">{vendor.contact_name || '—'}</span>
                                </div>
                                <div className="border-t border-slate-50 my-2"></div>
                                <div className="flex sm:items-center gap-3 flex-col sm:flex-row sm:justify-between">
                                    <span className="text-sm text-slate-500 flex items-center gap-2"><Mail className="h-3.5 w-3.5" /> Email</span>
                                    <a href={`mailto:${vendor.contact_email}`} className="text-sm font-medium text-brand-600 hover:underline truncate max-w-[200px]">{vendor.contact_email || '—'}</a>
                                </div>
                                <div className="flex sm:items-center gap-3 flex-col sm:flex-row sm:justify-between">
                                    <span className="text-sm text-slate-500 flex items-center gap-2"><Phone className="h-3.5 w-3.5" /> Phone</span>
                                    <a href={`tel:${vendor.contact_phone}`} className="text-sm font-medium text-slate-900 hover:text-brand-600">{vendor.contact_phone || '—'}</a>
                                </div>
                                <div className="border-t border-slate-50 my-2"></div>
                                <div className="flex items-start gap-3 flex-col">
                                    <span className="text-sm text-slate-500 flex items-center gap-2"><MapPin className="h-3.5 w-3.5" /> Address</span>
                                    <p className="text-sm text-slate-700 leading-relaxed bg-slate-50 p-2 rounded-lg w-full">
                                        {vendor.address || 'No address provided'}
                                    </p>
                                </div>
                            </div>
                        </section>

                        {/* Section 3: Notes */}
                        {(vendor.notes) && (
                            <section className="space-y-4">
                                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                                    <FileText className="h-4 w-4" />
                                    Notes
                                </h3>
                                <div className="bg-amber-50/50 border border-amber-100 p-4 rounded-xl">
                                    <p className="text-sm text-amber-900 whitespace-pre-wrap">{vendor.notes}</p>
                                </div>
                            </section>
                        )}

                        {/* Section 4: Items Supplied */}
                        <section className="space-y-4 pt-4 border-t border-slate-100">
                            <div className="flex items-center justify-between">
                                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                                    <Package className="h-4 w-4" />
                                    Items Supplied
                                </h3>
                                <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                                    {items?.length || 0} items
                                </span>
                            </div>

                            <div className="border rounded-lg overflow-hidden">
                                <Table>
                                    <TableHeader>
                                        <TableRow className="bg-slate-50 hover:bg-slate-50">
                                            <TableHead className="h-9 text-xs">UID</TableHead>
                                            <TableHead className="h-9 text-xs">Type</TableHead>
                                            <TableHead className="h-9 text-xs">Status</TableHead>
                                            <TableHead className="h-9 text-xs text-right">Date</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {isItemsLoading ? (
                                            <TableLoading colSpan={4} />
                                        ) : itemsError ? (
                                            <TableRow>
                                                <TableCell colSpan={4} className="text-center text-rose-500 py-4 text-xs">Failed to load items</TableCell>
                                            </TableRow>
                                        ) : items && items.length > 0 ? (
                                            items.map((item: any) => (
                                                <TableRow key={item.uid} className="hover:bg-slate-50/50">
                                                    <TableCell className="py-2 text-xs font-mono font-medium text-brand-600">{item.uid}</TableCell>
                                                    <TableCell className="py-2 text-xs text-slate-600">{item.component_type}</TableCell>
                                                    <TableCell className="py-2">
                                                        <Chip
                                                            label={item.current_status || item.status}
                                                            variant={
                                                                (item.current_status || item.status) === 'manufactured' ? 'success' : 'default'
                                                            }
                                                            className="text-[10px] h-5 px-1.5"
                                                        />
                                                    </TableCell>
                                                    <TableCell className="py-2 text-xs text-slate-500 text-right">
                                                        {item.manufacture_date ? new Date(item.manufacture_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: '2-digit' }) : '—'}
                                                    </TableCell>
                                                </TableRow>
                                            ))
                                        ) : (
                                            <TableEmpty colSpan={4} message="No items supplied yet" />
                                        )}
                                    </TableBody>
                                </Table>
                            </div>
                        </section>
                    </>
                ) : null}
            </div>
            {/* Footer */}
            <div className="p-4 border-t border-slate-100 bg-slate-50/50 mt-8">
                <Button className="w-full" onClick={onClose} variant="outline">
                    Close
                </Button>
            </div>
        </Drawer>
    );
}
