import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, UserPlus, LogOut } from 'lucide-react';
import Cookies from 'js-cookie';

export const Header: React.FC = () => {
    const navigate = useNavigate();
    const isAuthenticated = !!Cookies.get('auth_token');

    const handleLogout = () => {
        Cookies.remove('auth_token');
        navigate('/register');
    };

    return (
        <header className="glass-panel mb-8 p-4 flex items-center justify-between sticky top-4 z-50">
            <div className="flex items-center gap-3">
                <div className="p-2 bg-electric/10 rounded-lg">
                    <Activity className="text-electric w-6 h-6 animate-pulse-slow" />
                </div>
                <div>
                    <h1 className="text-xl font-bold tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-white to-white/70 uppercase">
                        NEXUS <span className="text-electric">ПРЕДИКТИВ</span>
                    </h1>
                    <p className="text-xs text-electric/70 uppercase tracking-widest font-mono">
                        Интеллект ЧПУ Станков
                    </p>
                </div>
            </div>

            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    <span className="relative flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-electric opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-electric"></span>
                    </span>
                    <span className="text-sm font-mono text-white/70">Система в сети</span>
                </div>
                {isAuthenticated ? (
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-2 px-3 py-1.5 bg-warning/10 hover:bg-warning/20 border border-warning/30 text-warning font-mono text-xs rounded-lg transition-all"
                    >
                        <LogOut className="w-4 h-4" />
                        ВЫХОД
                    </button>
                ) : (
                    <button
                        onClick={() => navigate('/register')}
                        className="flex items-center gap-2 px-3 py-1.5 bg-electric/10 hover:bg-electric/20 border border-electric/30 text-electric font-mono text-xs rounded-lg transition-all"
                    >
                        <UserPlus className="w-4 h-4" />
                        РЕГИСТРАЦИЯ
                    </button>
                )}
            </div>
        </header>
    );
};
