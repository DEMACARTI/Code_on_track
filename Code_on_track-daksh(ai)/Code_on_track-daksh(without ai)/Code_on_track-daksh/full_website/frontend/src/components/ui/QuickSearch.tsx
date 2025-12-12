import React, { useState, useEffect, useMemo } from 'react';
import { Search, X, Command, ArrowRight, Package, Users, FileText } from 'lucide-react';
import Fuse from 'fuse.js';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '../../utils/cn';

// Mock data for search - in a real app, this would come from an API or context
const SEARCH_ITEMS = [
    { id: '1', type: 'page', title: 'Dashboard', path: '/dashboard', icon: Command },
    { id: '2', type: 'page', title: 'Items', path: '/items', icon: Package },
    { id: '3', type: 'page', title: 'Vendors', path: '/vendors', icon: Users },
    { id: '4', type: 'page', title: 'Import', path: '/import', icon: FileText },
    { id: '5', type: 'action', title: 'Create New Item', path: '/items/new', icon: Package },
    { id: '6', type: 'action', title: 'Add Vendor', path: '/vendors/new', icon: Users },
];

interface QuickSearchProps {
    trigger?: React.ReactNode;
}

export const QuickSearch = ({ trigger }: QuickSearchProps) => {
    const [isOpen, setIsOpen] = useState(false);
    const [query, setQuery] = useState('');
    const [activeIndex, setActiveIndex] = useState(0);
    const navigate = useNavigate();

    const fuse = useMemo(() => new Fuse(SEARCH_ITEMS, {
        keys: ['title', 'type'],
        threshold: 0.3,
    }), []);

    const results = useMemo(() => {
        if (!query) return SEARCH_ITEMS.slice(0, 5);
        return fuse.search(query).map(result => result.item);
    }, [query, fuse]);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                setIsOpen(prev => !prev);
            }
            if (e.key === 'Escape') {
                setIsOpen(false);
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, []);

    useEffect(() => {
        setActiveIndex(0);
    }, [results]);

    const handleSelect = (item: typeof SEARCH_ITEMS[0]) => {
        navigate(item.path);
        setIsOpen(false);
        setQuery('');
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            setActiveIndex(prev => (prev + 1) % results.length);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            setActiveIndex(prev => (prev - 1 + results.length) % results.length);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (results[activeIndex]) {
                handleSelect(results[activeIndex]);
            }
        }
    };

    return (
        <>
            {trigger ? (
                <div onClick={() => setIsOpen(true)}>
                    {trigger}
                </div>
            ) : (
                <button
                    onClick={() => setIsOpen(true)}
                    className="flex items-center gap-2 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-sm text-slate-500 transition-colors hover:border-primary-200 hover:bg-white hover:text-slate-700 w-64 justify-between"
                >
                    <div className="flex items-center gap-2">
                        <Search className="h-4 w-4" />
                        <span>Quick Search...</span>
                    </div>
                    <kbd className="hidden rounded border border-slate-200 bg-white px-1.5 py-0.5 text-xs font-medium text-slate-400 sm:inline-block">
                        Ctrl K
                    </kbd>
                </button>
            )}

            <AnimatePresence>
                {isOpen && (
                    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsOpen(false)}
                            className="fixed inset-0 bg-slate-900/20 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: -20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: -20 }}
                            className="relative w-full max-w-lg overflow-hidden rounded-xl border border-slate-200 bg-white shadow-2xl"
                        >
                            <div className="flex items-center border-b border-slate-100 px-4 py-3">
                                <Search className="mr-3 h-5 w-5 text-slate-400" />
                                <input
                                    autoFocus
                                    type="text"
                                    placeholder="Search pages, actions..."
                                    value={query}
                                    onChange={(e) => setQuery(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="flex-1 bg-transparent text-slate-900 placeholder-slate-400 outline-none"
                                />
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="rounded-lg p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                                >
                                    <X className="h-5 w-5" />
                                </button>
                            </div>

                            <div className="max-h-[60vh] overflow-y-auto p-2">
                                {results.length === 0 ? (
                                    <div className="py-12 text-center text-sm text-slate-500">
                                        No results found for "{query}"
                                    </div>
                                ) : (
                                    <div className="space-y-1">
                                        {results.map((item, index) => (
                                            <button
                                                key={item.id}
                                                onClick={() => handleSelect(item)}
                                                onMouseEnter={() => setActiveIndex(index)}
                                                className={cn(
                                                    "flex w-full items-center justify-between rounded-lg px-3 py-2 text-left text-sm transition-colors",
                                                    index === activeIndex
                                                        ? "bg-primary-50 text-primary-700"
                                                        : "text-slate-700 hover:bg-slate-50"
                                                )}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className={cn(
                                                        "flex h-8 w-8 items-center justify-center rounded-lg",
                                                        index === activeIndex ? "bg-primary-100 text-primary-600" : "bg-slate-100 text-slate-500"
                                                    )}>
                                                        <item.icon className="h-4 w-4" />
                                                    </div>
                                                    <div>
                                                        <div className="font-medium">{item.title}</div>
                                                        <div className={cn("text-xs", index === activeIndex ? "text-primary-500" : "text-slate-400")}>
                                                            {item.type}
                                                        </div>
                                                    </div>
                                                </div>
                                                {index === activeIndex && (
                                                    <ArrowRight className="h-4 w-4 opacity-50" />
                                                )}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <div className="border-t border-slate-100 bg-slate-50 px-4 py-2 text-xs text-slate-400 flex justify-between">
                                <span>
                                    <kbd className="font-medium text-slate-500">↑↓</kbd> to navigate
                                </span>
                                <span>
                                    <kbd className="font-medium text-slate-500">Enter</kbd> to select
                                </span>
                                <span>
                                    <kbd className="font-medium text-slate-500">Esc</kbd> to close
                                </span>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </>
    );
};
