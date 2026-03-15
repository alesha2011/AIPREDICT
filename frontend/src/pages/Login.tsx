import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, LogIn, ArrowRight } from 'lucide-react';
import Cookies from 'js-cookie';
import { API_BASE_URL } from '../config/api';

export const Login: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка входа');
            }

            const data = await response.json();
            Cookies.set('auth_token', data.token, { expires: 1 });
            Cookies.set('username', data.username, { expires: 1 });
            navigate('/');
        } catch (err: any) {
            setError(err.message === 'Incorrect username or password' ? 'Неверный логин или пароль' : err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <div className="w-full max-w-md">

                <div className="text-center mb-8">
                    <div className="inline-block p-3 bg-electric/10 rounded-2xl mb-4">
                        <Activity className="text-electric w-8 h-8 animate-pulse-slow" />
                    </div>
                    <h1 className="text-3xl font-bold tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 uppercase">
                        NEXUS <span className="text-electric">ПРЕДИКТИВ</span>
                    </h1>
                    <p className="text-sm text-electric/70 uppercase tracking-widest font-mono mt-2">
                        Вход в систему
                    </p>
                </div>

                <div className="glass-panel p-8 relative overflow-hidden">
                    <div className="absolute top-0 right-0 w-32 h-32 bg-electric/10 rounded-full blur-[50px] pointer-events-none" />
                    <div className="absolute bottom-0 left-0 w-32 h-32 bg-neon/10 rounded-full blur-[50px] pointer-events-none" />

                    <form onSubmit={handleLogin} className="flex flex-col gap-6 relative z-10">
                        {error && (
                            <div className="bg-warning/10 border border-warning/30 text-warning px-4 py-3 rounded-lg text-sm font-mono text-center">
                                {error}
                            </div>
                        )}

                        <div>
                            <label className="block text-xs font-mono text-electric mb-2 uppercase tracking-wider">Username</label>
                            <input
                                type="text"
                                required
                                value={username}
                                onChange={(e) => {
                                    const val = e.target.value;
                                    if (/[а-яё]/i.test(val)) return;
                                    setUsername(val);
                                }}
                                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-electric/50 focus:ring-1 focus:ring-electric/50 transition-all font-mono"
                                placeholder="Username"
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-mono text-electric mb-2 uppercase tracking-wider">Password</label>
                            <input
                                type="password"
                                required
                                value={password}
                                onChange={(e) => {
                                    const val = e.target.value;
                                    if (/[а-яё]/i.test(val)) return;
                                    setPassword(val);
                                }}
                                className="w-full bg-black/40 border border-white/10 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-electric/50 focus:ring-1 focus:ring-electric/50 transition-all font-mono"
                                placeholder="Password"
                            />
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full mt-2 bg-gradient-to-r from-electric/80 to-neon/80 hover:from-electric hover:to-neon text-white font-bold py-3 rounded-lg transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] hover:shadow-[0_0_30px_rgba(0,240,255,0.4)] flex justify-center items-center gap-2 group disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? (
                                <span className="animate-pulse">АВТОРИЗАЦИЯ...</span>
                            ) : (
                                <>
                                    <LogIn className="w-5 h-5" />
                                    <span>ВОЙТИ</span>
                                </>
                            )}
                        </button>
                    </form>
                </div>

                <div className="text-center mt-6">
                    <button
                        type="button"
                        onClick={() => navigate('/register')}
                        className="text-white/50 hover:text-white font-mono text-sm flex items-center gap-2 mx-auto transition-colors group"
                    >
                        Нет аккаунта? Зарегистрироваться <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>
            </div>
        </div>
    );
};

