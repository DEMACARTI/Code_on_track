import React from 'react';
import { motion } from 'framer-motion';
import { ImportPreview } from '../components/ui/ImportPreview';
import { FileDown } from 'lucide-react';
import { Button } from '../components/ui/Button';

const ImportItems: React.FC = () => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
        >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Import Items</h1>
                    <p className="text-slate-500 mt-1">
                        Bulk create items by uploading a CSV file.
                    </p>
                </div>
                <a href="/template.csv" download tabIndex={-1}>
                    <Button variant="outline" className="bg-white hover:bg-slate-50 text-slate-700 border-slate-200">
                        <FileDown className="mr-2 h-4 w-4 text-brand-600" />
                        Download Template
                    </Button>
                </a>
            </div>

            <ImportPreview />
        </motion.div>
    );
};

export default ImportItems;
