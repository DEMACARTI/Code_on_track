import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Lock, ArrowRight, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '../components/ui/Button';
import api from '../api/axios';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [rememberMe, setRememberMe] = useState(false);
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    // Load saved credentials on mount
    React.useEffect(() => {
        // Clear any stale access token to ensure fresh login
        localStorage.removeItem('access_token');

        const savedUsername = localStorage.getItem('savedUsername');
        const savedPassword = localStorage.getItem('savedPassword');
        const wasRemembered = localStorage.getItem('rememberMe') === 'true';

        if (wasRemembered && savedUsername && savedPassword) {
            setUsername(savedUsername);
            setPassword(savedPassword);
            setRememberMe(true);
        }
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            const response = await api.post('/auth/login', { username, password });
            const { access_token } = response.data;

            if (rememberMe) {
                localStorage.setItem('savedUsername', username);
                localStorage.setItem('savedPassword', password);
                localStorage.setItem('rememberMe', 'true');
            } else {
                localStorage.removeItem('savedUsername');
                localStorage.removeItem('savedPassword');
                localStorage.removeItem('rememberMe');
            }

            login(access_token);
            navigate('/dashboard');
        } catch (err: any) {
            console.error('Login failed', err);
            console.error('Login failed', err);
            setError(err.response?.data?.detail || err.message || 'Login failed');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-50 bg-hero-pattern p-4">
            {/* Dynamic Background */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <motion.div
                    animate={{
                        scale: [1, 1.2, 1],
                        rotate: [0, 90, 0],
                        opacity: [0.3, 0.5, 0.3]
                    }}
                    transition={{
                        duration: 20,
                        repeat: Infinity,
                        ease: "linear"
                    }}
                    className="absolute -left-[10%] -top-[10%] h-[60%] w-[60%] rounded-full bg-brand-400/20 blur-[120px]"
                />
                <motion.div
                    animate={{
                        scale: [1, 1.1, 1],
                        rotate: [0, -60, 0],
                        opacity: [0.2, 0.4, 0.2]
                    }}
                    transition={{
                        duration: 15,
                        repeat: Infinity,
                        ease: "linear",
                        delay: 2
                    }}
                    className="absolute -bottom-[10%] -right-[10%] h-[60%] w-[60%] rounded-full bg-accent-400/20 blur-[120px]"
                />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, ease: "easeOut" }}
                className="relative z-10 w-full max-w-md"
            >
                <div className="mb-8 text-center">
                    <motion.div
                        initial={{ scale: 0.5, opacity: 0, y: -20 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
                        className="mx-auto mb-6 flex flex-col items-center justify-center gap-4"
                    >
                        <img
                            src="/logo.png"
                            alt="RailChinh Logo"
                            className="h-32 w-auto object-contain drop-shadow-xl"
                        />
                        <span className="text-4xl font-extrabold tracking-tight text-slate-900 bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent">
                            RailChinh
                        </span>
                    </motion.div>
                    <h1 className="text-3xl font-bold tracking-tight text-slate-900">Welcome back</h1>
                    <p className="mt-2 text-slate-500">Sign in to access your dashboard</p>
                </div>

                <div className="overflow-hidden rounded-3xl border border-white/50 bg-white/70 p-8 shadow-2xl shadow-slate-200/50 backdrop-blur-xl">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                className="flex items-center gap-3 rounded-xl bg-rose-50 p-4 text-sm text-rose-600 border border-rose-100"
                            >
                                <AlertCircle className="h-5 w-5 flex-shrink-0 text-rose-500" />
                                <p className="font-medium">{error}</p>
                            </motion.div>
                        )}

                        <div className="space-y-4">
                            <div className="group">
                                <label className="mb-1.5 block text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Username</label>
                                <div className="relative">
                                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 group-focus-within:text-brand-500 transition-colors">
                                        <User className="h-5 w-5" />
                                    </div>
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        required
                                        className="block w-full rounded-xl border border-slate-200 bg-white/50 py-3.5 pl-11 pr-4 text-slate-900 placeholder-slate-400 shadow-sm transition-all focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/10 sm:text-sm"
                                        placeholder="Enter your username"
                                    />
                                </div>
                            </div>

                            <div className="group">
                                <label className="mb-1.5 block text-xs font-bold text-slate-400 uppercase tracking-wider ml-1">Password</label>
                                <div className="relative">
                                    <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-4 text-slate-400 group-focus-within:text-brand-500 transition-colors">
                                        <Lock className="h-5 w-5" />
                                    </div>
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        required
                                        className="block w-full rounded-xl border border-slate-200 bg-white/50 py-3.5 pl-11 pr-4 text-slate-900 placeholder-slate-400 shadow-sm transition-all focus:border-brand-500 focus:bg-white focus:outline-none focus:ring-4 focus:ring-brand-500/10 sm:text-sm"
                                        placeholder="Enter your password"
                                    />
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between">
                            <label className="flex items-center gap-3 cursor-pointer group">
                                <div className="relative flex items-center">
                                    <input
                                        type="checkbox"
                                        checked={rememberMe}
                                        onChange={(e) => setRememberMe(e.target.checked)}
                                        className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-slate-300 bg-white transition-all checked:border-brand-500 checked:bg-brand-500 hover:border-brand-500/50"
                                    />
                                    <CheckCircle2 className="pointer-events-none absolute left-1/2 top-1/2 h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 text-white opacity-0 transition-opacity peer-checked:opacity-100" />
                                </div>
                                <span className="text-sm text-slate-500 transition-colors group-hover:text-slate-700">Remember me</span>
                            </label>
                            <a href="#" className="text-sm font-medium text-brand-600 hover:text-brand-700 transition-colors">
                                Forgot password?
                            </a>
                        </div>

                        <Button
                            type="submit"
                            className="w-full bg-gradient-to-r from-brand-600 to-brand-500 py-6 text-base font-semibold shadow-lg shadow-brand-500/25 hover:shadow-brand-500/40 hover:from-brand-500 hover:to-brand-400 border-none text-white"
                            size="lg"
                            isLoading={isLoading}
                            rightIcon={!isLoading && <ArrowRight className="h-5 w-5" />}
                        >
                            Sign In
                        </Button>
                    </form>
                </div>

                <p className="mt-8 text-center text-xs text-slate-400">
                    &copy; {new Date().getFullYear()} IRF QR Tracking System. All rights reserved.
                </p>
            </motion.div>
        </div>
    );
};
