import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { queryAssistant, type AssistantAction } from '../api/assistant';
import { inspectComponent } from '../api/vision';
import { Send, Bot, Sparkles, ChevronDown, Camera } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from './ui/Button';
import { useNavigate } from 'react-router-dom';
import SchedulerModal from './SchedulerModal';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    text: string;
    image?: string;
    actions?: AssistantAction[];
    visionResult?: any;
}

export default function AssistantWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        { id: 'init', role: 'assistant', text: 'Hi! I can help you find items, check expiry buckets, or schedule pickups. Try asking "Which lots are expiring?"' }
    ]);
    const [isSchedulerOpen, setIsSchedulerOpen] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const navigate = useNavigate();
    const scrollRef = useRef<HTMLDivElement>(null);

    const mutation = useMutation({
        mutationFn: queryAssistant,
        onSuccess: (data) => {
            const assistantMsg: Message = {
                id: Date.now().toString(),
                role: 'assistant',
                text: data.answer,
                actions: data.actions
            };
            setMessages(prev => [...prev, assistantMsg]);

            if (data.actions) {
                data.actions.forEach(action => {
                    handleAction(action);
                });
            }
        },
        onError: () => {
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', text: 'Sorry, I encountered an error connecting to the server.' }]);
        }
    });

    const visionMutation = useMutation({
        mutationFn: ({ file, uid }: { file: File, uid: string }) => inspectComponent(file, uid),
        onSuccess: (data) => {
            const assistantMsg: Message = {
                id: Date.now().toString(),
                role: 'assistant',
                text: `Analysis complete.Detected: ${data.issue} (${data.severity}). recommended action: ${data.recommended_action} `,
                visionResult: data
            };
            setMessages(prev => [...prev, assistantMsg]);
        },
        onError: () => {
            setMessages(prev => [...prev, { id: Date.now().toString(), role: 'assistant', text: 'Sorry, I encountered an error processing the image.' }]);
        }
    })

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages, isOpen]);

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg: Message = {
            id: Date.now().toString(),
            role: 'user',
            text: input
        };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        mutation.mutate(input);
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleAction = (action: AssistantAction) => {
        if (action.type === 'open_scheduler') {
            setIsSchedulerOpen(true);
        } else if (action.type === 'open_optimized_scheduler') {
            navigate('/scheduler-optimized');
        } else if (action.type === 'open_bucket') {
            navigate('/items');
        } else if (action.type === 'open_inspection_history') {
            if (action.data?.uid) {
                navigate(`/inspection?uid=${action.data.uid}`);
            }
        } else if (action.type === 'navigate') {
            if (action.data?.url) {
                navigate(action.data.url);
            }
        }
    };

    const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            const userMsg: Message = {
                id: Date.now().toString(),
                role: 'user',
                text: 'Analyzing this image...',
                image: URL.createObjectURL(file)
            };
            setMessages(prev => [...prev, userMsg]);

            // For demo, we might not have UID from chat context easily unless we parse it or ask.
            // Using a default placeholder UID or 'unknown' for assistant uploads as per prompt requirement "uid OR lot_no"
            // The prompt says "uid OR lot_no". If chat context doesn't have it, maybe we use a dummy?
            // "When user uploads an image through assistant widget, call POST /api/vision/inspect."
            // I'll send 'assistant_upload' as UID for now.
            visionMutation.mutate({ file, uid: 'assistant_upload' });
        }
    }

    return (
        <>
            <AnimatePresence>
                {isOpen ? (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="fixed bottom-6 right-6 z-40 w-80 md:w-96 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col max-h-[600px] h-[500px]"
                    >
                        {/* Header */}
                        <div className="p-4 bg-gradient-to-r from-violet-600 to-indigo-600 flex items-center justify-between text-white">
                            <div className="flex items-center gap-2">
                                <Sparkles className="h-5 w-5" />
                                <span className="font-bold">AI Assistant</span>
                            </div>
                            <button
                                onClick={() => setIsOpen(false)}
                                className="p-1 hover:bg-white/20 rounded-full transition-colors"
                            >
                                <ChevronDown className="h-5 w-5" />
                            </button>
                        </div>

                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50" ref={scrollRef}>
                            {messages.map((msg) => (
                                <div
                                    key={msg.id}
                                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} `}
                                >
                                    <div
                                        className={`max - w - [80 %] p - 3 rounded - 2xl text - sm ${msg.role === 'user'
                                            ? 'bg-violet-600 text-white rounded-tr-none'
                                            : 'bg-white border border-slate-200 text-slate-700 rounded-tl-none shadow-sm'
                                            } `}
                                    >
                                        {msg.image && (
                                            <img src={msg.image} alt="Upload" className="mb-2 rounded-lg max-h-32 object-cover" />
                                        )}
                                        <p>{msg.text}</p>

                                        {/* Display Vision Result if available */}
                                        {msg.visionResult && (
                                            <div className="mt-2 bg-slate-50 rounded p-2 border border-slate-100 text-slate-800">
                                                <div className="flex justify-between items-center mb-1">
                                                    <strong>{msg.visionResult.issue}</strong>
                                                    <span className={`text - xs px - 1.5 py - 0.5 rounded ${msg.visionResult.severity === 'CRITICAL' ? 'bg-rose-100 text-rose-700' : 'bg-emerald-100 text-emerald-700'} `}>
                                                        {msg.visionResult.severity}
                                                    </span>
                                                </div>
                                                <div className="text-xs text-slate-500">
                                                    Confidence: {(msg.visionResult.confidence * 100).toFixed(0)}%
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {(mutation.isPending || visionMutation.isPending) && (
                                <div className="flex justify-start">
                                    <div className="bg-white border border-slate-200 p-3 rounded-2xl rounded-tl-none shadow-sm">
                                        <div className="flex gap-1">
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-100"></span>
                                            <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce delay-200"></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <div className="p-3 bg-white border-t border-slate-100 flex gap-2">
                            <input
                                type="file"
                                ref={fileInputRef}
                                className="hidden"
                                accept="image/*"
                                onChange={handleFileUpload}
                            />
                            <Button
                                variant="outline"
                                size="sm"
                                className="px-2"
                                title="Upload Image"
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <Camera className="h-4 w-4 text-slate-500" />
                            </Button>
                            <input
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                placeholder="Ask something..."
                                className="flex-1 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500/20 focus:border-violet-500 transition-all"
                            />
                            <Button
                                onClick={handleSend}
                                disabled={!input.trim() || mutation.isPending}
                                size="sm"
                                className={`rounded - xl px - 3 ${!input.trim() ? 'bg-slate-200 text-slate-400' : 'bg-violet-600 hover:bg-violet-700'} `}
                            >
                                <Send className="h-4 w-4" />
                            </Button>
                        </div>
                    </motion.div>
                ) : (
                    <motion.button
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => setIsOpen(true)}
                        className="fixed bottom-6 right-6 z-40 h-14 w-14 bg-gradient-to-tr from-violet-600 to-indigo-600 rounded-full shadow-lg shadow-violet-500/30 flex items-center justify-center text-white"
                    >
                        <Bot className="h-7 w-7" />
                        <span className="absolute -top-1 -right-1 flex h-3 w-3">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                            <span className="relative inline-flex rounded-full h-3 w-3 bg-indigo-500"></span>
                        </span>
                    </motion.button>
                )}
            </AnimatePresence>

            <SchedulerModal
                isOpen={isSchedulerOpen}
                onClose={() => setIsSchedulerOpen(false)}
            />
        </>
    );
}
