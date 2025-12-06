import React from 'react';
import { type ImportPreviewResponse } from '../api/import';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from './ui/Table';
import { AlertCircle, CheckCircle, FileText } from 'lucide-react';

interface ImportPreviewTableProps {
    preview: ImportPreviewResponse;
}

const ImportPreviewTable: React.FC<ImportPreviewTableProps> = ({ preview }) => {
    const { total_rows, valid_rows, invalid_rows } = preview;

    return (
        <div className="mt-8 space-y-6">
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-slate-900">Import Preview</h3>
            </div>

            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-sm font-medium text-slate-500">
                        <FileText className="h-4 w-4" />
                        Total Rows
                    </div>
                    <div className="mt-2 text-2xl font-bold text-slate-900">{total_rows}</div>
                </div>
                <div className="rounded-xl border border-emerald-100 bg-emerald-50 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-sm font-medium text-emerald-600">
                        <CheckCircle className="h-4 w-4" />
                        Valid Rows
                    </div>
                    <div className="mt-2 text-2xl font-bold text-emerald-700">{valid_rows}</div>
                </div>
                <div className="rounded-xl border border-rose-100 bg-rose-50 p-4 shadow-sm">
                    <div className="flex items-center gap-2 text-sm font-medium text-rose-600">
                        <AlertCircle className="h-4 w-4" />
                        Invalid Rows
                    </div>
                    <div className="mt-2 text-2xl font-bold text-rose-700">{invalid_rows.length}</div>
                </div>
            </div>

            {invalid_rows.length > 0 ? (
                <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                    <div className="border-b border-slate-100 bg-rose-50/50 px-4 py-3">
                        <h4 className="text-sm font-medium text-rose-700">Errors Found</h4>
                    </div>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead className="w-[80px]">Row #</TableHead>
                                <TableHead>UID</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Vendor</TableHead>
                                <TableHead>Errors</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {invalid_rows.map((item, idx) => (
                                <TableRow key={idx} className="bg-rose-50/30 hover:bg-rose-50/50">
                                    <TableCell className="font-medium text-slate-500">{item.row_number}</TableCell>
                                    <TableCell>{item.row['uid'] || '-'}</TableCell>
                                    <TableCell>{item.row['component_type'] || '-'}</TableCell>
                                    <TableCell>{item.row['vendor_name'] || '-'}</TableCell>
                                    <TableCell>
                                        <div className="flex items-center gap-2 text-rose-600 font-medium">
                                            <AlertCircle className="h-4 w-4 flex-shrink-0" />
                                            <span>{item.errors.join(', ')}</span>
                                        </div>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </div>
            ) : (
                <div className="flex flex-col items-center justify-center rounded-xl border border-emerald-100 bg-emerald-50 py-12 text-center">
                    <div className="mb-4 rounded-full bg-emerald-100 p-3 text-emerald-600">
                        <CheckCircle className="h-8 w-8" />
                    </div>
                    <h3 className="text-lg font-semibold text-emerald-900">All rows are valid!</h3>
                    <p className="mt-1 text-emerald-700">Your data is ready to be imported.</p>
                </div>
            )}
        </div>
    );
};

export default ImportPreviewTable;
