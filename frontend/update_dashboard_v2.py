import os

file_path = r"c:\Users\Алексей\Desktop\обучение\predictive-maintenance\frontend\src\pages\Dashboard.tsx"

content = """import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Header } from '../components/layout/Header';
import { RULChart } from '../components/charts/RULChart';
import { 
    fetchLogs, 
    predictRUL, 
    fetchApiKeys, 
    generateApiKey, 
    updateApiKey,
    uploadLogs, 
    fetchMachines, 
    createMachine,
    deleteMachine
} from '../services/api';
import type { MachineLog } from '../types';
import { 
    AlertCircle, 
    CheckCircle2, 
    Upload, 
    Key, 
    Cpu, 
    Plus, 
    Copy, 
    Activity, 
    X, 
    Loader2, 
    FileArchive,
    Shield,
    Trash2,
    RefreshCw,
    Database,
    Zap
} from 'lucide-react';

export const Dashboard: React.FC = () => {
    const [logs, setLogs] = useState<MachineLog[]>([]);
    const [machines, setMachines] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedMachine, setSelectedMachine] = useState<string>('');
    const [apiKeys, setApiKeys] = useState<any[]>([]);
    
    // Modal states
    const [isAddModalOpen, setIsAddModalOpen] = useState(false);
    const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
    const [newMachineName, setNewMachineName] = useState('');
    const [isCreating, setIsCreating] = useState(false);
    const [uploadStatus, setUploadStatus] = useState('');
    const [selectedFile, setSelectedFile] = useState<File | null>(null);

    const loadData = async () => {
        try {
            const machineObj = machines.find(m => m.name === selectedMachine);
            const [logsData, keysData, machinesData] = await Promise.all([
                fetchLogs(selectedMachine || undefined),
                fetchApiKeys(machineObj?.id),
                fetchMachines()
            ]);
            setLogs(logsData);
            setApiKeys(keysData);
            setMachines(machinesData);
            
            if (machinesData.length > 0 && !selectedMachine) {
                setSelectedMachine(machinesData[0].name);
            }
            setLoading(false);
        } catch (error) {
            console.error(error);
        }
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 5000);
        return () => clearInterval(interval);
    }, [selectedMachine]);

    const simulateReading = async () => {
        if (!selectedMachine) return;
        await predictRUL({
            machine_id: selectedMachine,
            sensor_1: Math.random() * 2 - 1,
            sensor_2: Math.random() * 2 - 1,
            sensor_3: Math.random() * 2 - 1,
            sensor_4: Math.random() * 2 - 1,
            is_dataset: false
        });
        loadData();
    };

    const handleAddMachine = async () => {
        if (!newMachineName.trim()) return;
        setIsCreating(true);
        try {
            await createMachine(newMachineName);
            await loadData();
            setSelectedMachine(newMachineName);
            setIsAddModalOpen(false);
            setNewMachineName('');
        } catch (err) {
            alert('Ошибка при создании станка');
        } finally {
            setIsCreating(false);
        }
    };

    const handleUploadLogs = async () => {
        if (!selectedFile || !selectedMachine) return;
        setIsCreating(true);
        setUploadStatus('Загрузка...');
        try {
            await uploadLogs(selectedMachine, selectedFile, false);
            setUploadStatus('Успешно!');
            setTimeout(() => {
                setIsUploadModalOpen(false);
                setSelectedFile(null);
                setUploadStatus('');
            }, 1500);
            await loadData();
        } catch (err) {
            setUploadStatus('Ошибка загрузки');
        } finally {
            setIsCreating(false);
        }
    };

    const handleDeleteMachine = async (id: number, name: string) => {
        if (!confirm(`Вы уверены, что хотите удалить станок "${name}" и все его логи?`)) return;
        try {
            await deleteMachine(id);
            if (selectedMachine === name) {
                setSelectedMachine('');
            }
            await loadData();
        } catch (err) {
            alert('Ошибка при удалении станка');
        }
    };

    const handleCreateKey = async () => {
        const machineObj = machines.find(m => m.name === selectedMachine);
        if (!machineObj) return;
        await generateApiKey('analysis', machineObj.id);
        loadData();
    };

    const handleToggleKeyMode = async (id: number, currentMode: string) => {
        const newMode = currentMode === 'analysis' ? 'dataset' : 'analysis';
        await updateApiKey(id, newMode);
        loadData();
    };

    const latestLog = logs.find(l => l.machine_id === selectedMachine) || logs[0];
    const selectedMachineId = machines.find(m => m.name === selectedMachine)?.id;

    const getStatusColor = (status?: string) => {
        if (status === 'Critical') return 'text-warning';
        if (status === 'Warning') return 'text-[#FFB800]';
        return 'text-electric';
    };

    const getStatusLabel = (status?: string) => {
        if (status === 'Critical') return 'Критический';
        if (status === 'Warning') return 'Предупреждение';
        if (status === 'Normal') return 'Норма';
        return status;
    };

    if (loading) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center gap-4 text-center">
                <Loader2 className="w-8 h-8 text-electric animate-spin" />
                <p className="text-white/50 font-mono text-sm tracking-widest animate-pulse uppercase">Загрузка конфигурации...</p>
            </div>
        );
    }

    return (
        <div className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto relative">
            <Header />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Column - Machine Selection & API Keys */}
                <div className="lg:col-span-1 flex flex-col gap-6">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="glass-panel p-6"
                    >
                        <div className="flex justify-between items-center mb-6">
                            <h2 className="text-sm font-mono text-white/50 tracking-wider flex items-center gap-2">
                                <Cpu className="w-4 h-4" /> Список станков
                            </h2>
                            <button 
                                onClick={() => setIsAddModalOpen(true)}
                                className="flex items-center gap-1 text-[10px] font-mono text-electric hover:text-white transition-colors bg-electric/10 px-2 py-1 rounded border border-electric/20"
                            >
                                <Plus className="w-3 h-3" /> Добавить
                            </button>
                        </div>
                        
                        <div className="flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                            {machines.map(m => (
                                <div key={m.id} className="group relative flex items-center gap-2">
                                    <button
                                        onClick={() => setSelectedMachine(m.name)}
                                        className={`flex-1 px-4 py-3 rounded-lg border font-mono text-left transition-all flex justify-between items-center ${
                                            selectedMachine === m.name
                                            ? 'bg-electric/20 border-electric text-electric shadow-[0_0_15px_rgba(0,240,255,0.2)]' 
                                            : 'bg-white/5 border-white/10 text-white/50 hover:bg-white/10'
                                        }`}
                                    >
                                        <span>{m.name}</span>
                                        {selectedMachine === m.name && <Activity className="w-3 h-3 animate-pulse" />}
                                    </button>
                                    <button 
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleDeleteMachine(m.id, m.name);
                                        }}
                                        className="p-3 text-white/20 hover:text-warning hover:bg-warning/10 rounded-lg transition-all opacity-0 group-hover:opacity-100 border border-transparent hover:border-warning/20"
                                    >
                                        <Trash2 className="w-4 h-4" />
                                    </button>
                                </div>
                            ))}
                            {machines.length === 0 && (
                                <p className="text-xs text-white/20 text-center py-4 italic font-mono uppercase">Список пуст</p>
                            )}
                        </div>

                        <div className="h-px bg-white/10 my-6" />

                        <div className="flex flex-col gap-3">
                            <button
                                onClick={simulateReading}
                                disabled={!selectedMachine}
                                className="w-full bg-electric/10 hover:bg-electric/20 disabled:opacity-30 border border-electric/30 text-electric font-mono text-xs py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                            >
                                <Zap className="w-3 h-3" /> Снять показания
                            </button>
                            <button
                                onClick={() => setIsUploadModalOpen(true)}
                                disabled={!selectedMachine}
                                className="w-full bg-white/5 hover:bg-white/10 disabled:opacity-30 border border-white/10 text-white/60 font-mono text-xs py-3 rounded-lg transition-all flex items-center justify-center gap-2"
                            >
                                <Upload className="w-3 h-3" /> Анализ логов
                            </button>
                        </div>
                    </motion.div>

                    {/* API Keys Panel */}
                    <AnimatePresence>
                        {selectedMachine && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: 20 }}
                                transition={{ delay: 0.1 }}
                                className="glass-panel p-6"
                            >
                                <div className="flex justify-between items-center mb-6">
                                    <div>
                                        <h2 className="text-sm font-mono text-white/50 tracking-wider flex items-center gap-2">
                                            <Key className="w-4 h-4" /> API Ключи
                                        </h2>
                                        <p className="text-[10px] font-mono text-white/20 uppercase mt-1">Для: {selectedMachine}</p>
                                    </div>
                                    <button 
                                        onClick={handleCreateKey}
                                        className="text-[10px] font-mono text-electric hover:text-white transition-colors"
                                    >
                                        + Новый
                                    </button>
                                </div>

                                <div className="flex flex-col gap-3">
                                    {apiKeys.map(k => (
                                        <div key={k.id} className="bg-white/5 border border-white/5 rounded-lg p-3 flex flex-col gap-2 group">
                                            <div className="flex justify-between items-center">
                                                <button
                                                    onClick={() => handleToggleKeyMode(k.id, k.mode)}
                                                    className={`text-[10px] font-mono px-2 py-0.5 rounded border flex items-center gap-1 transition-all ${
                                                        k.mode === 'dataset' 
                                                        ? 'bg-[#FF00E5]/10 border-[#FF00E5]/30 text-[#FF00E5] hover:bg-[#FF00E5]/20' 
                                                        : 'bg-electric/10 border-electric/30 text-electric hover:bg-electric/20'
                                                    }`}
                                                >
                                                    <RefreshCw className="w-2.5 h-2.5" />
                                                    {k.mode.toUpperCase()}
                                                </button>
                                                <button 
                                                    onClick={() => {
                                                        navigator.clipboard.writeText(k.key);
                                                        alert('Ключ скопирован!');
                                                    }}
                                                    className="text-white/30 hover:text-white transition-opacity"
                                                >
                                                    <Copy className="w-3 h-3" />
                                                </button>
                                            </div>
                                            <code className="text-[10px] text-white/40 truncate bg-black/40 p-1 rounded font-mono group-hover:text-white/60 transition-colors">
                                                {k.key}
                                            </code>
                                        </div>
                                    ))}
                                    {apiKeys.length === 0 && (
                                        <p className="text-[10px] text-white/20 text-center py-2 font-mono italic">Ключей не создано</p>
                                    )}
                                </div>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </div>

                {/* Right Column - Status & Log */}
                <div className="lg:col-span-2 flex flex-col gap-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="glass-panel p-6"
                        >
                            <div className="flex justify-between items-start mb-4">
                                <h2 className="text-sm font-mono text-white/50 tracking-wider uppercase">Остаточный ресурс RUL</h2>
                                <span className="text-[10px] font-mono text-white/20 px-2 py-0.5 border border-white/10 rounded-full">{selectedMachine}</span>
                            </div>
                            {latestLog ? (
                                <div>
                                    <div className={`text-6xl font-bold font-mono tracking-tighter ${getStatusColor(latestLog.status)}`}>
                                        {latestLog.rul_prediction.toFixed(1)}<span className="text-2xl text-white/50 ml-2 font-light">ч</span>
                                    </div>
                                    <div className="flex flex-col gap-2 mt-4">
                                        <div className="flex items-center gap-2 text-sm font-mono bg-white/5 p-3 rounded-lg border border-white/10">
                                            {latestLog.status === 'Critical' ? (
                                                <AlertCircle className="w-4 h-4 text-warning" />
                                            ) : (
                                                <CheckCircle2 className="w-4 h-4 text-electric" />
                                            )}
                                            <span className={getStatusColor(latestLog.status)}>{getStatusLabel(latestLog.status)}</span>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-8 text-white/30 animate-pulse font-mono text-xs uppercase flex flex-col gap-2">
                                    Нет данных: снимите показания
                                </div>
                            )}
                        </motion.div>

                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.2 }}
                            className="glass-panel p-6"
                        >
                            <h2 className="text-sm font-mono text-white/50 tracking-wider mb-6 uppercase">Прогноз деградации</h2>
                            <RULChart data={logs.filter(l => l.machine_id === selectedMachine).slice(0, 15)} />
                        </motion.div>
                    </div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.3 }}
                        className="glass-panel p-6 flex-1"
                    >
                        <h2 className="text-sm font-mono text-white/50 tracking-wider mb-4 uppercase">Последние логи</h2>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs font-mono text-white/30 uppercase bg-black/20">
                                    <tr>
                                        <th className="px-4 py-3 rounded-tl-lg font-medium">Время</th>
                                        <th className="px-4 py-3 font-medium">ID Станка</th>
                                        <th className="px-4 py-3 font-medium">RUL</th>
                                        <th className="px-4 py-3 rounded-tr-lg font-medium">Статус</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {logs.filter(l => !selectedMachine || l.machine_id === selectedMachine).slice(0, 8).map((log) => (
                                        <tr key={log.id} className="border-b border-white/5 hover:bg-white/5 transition-colors group">
                                            <td className="px-4 py-3 font-mono text-white/50">{new Date(log.timestamp).toLocaleTimeString()}</td>
                                            <td className="px-4 py-3 font-mono text-white/80">{log.machine_id}</td>
                                            <td className="px-4 py-3 font-mono text-electric">{log.rul_prediction.toFixed(2)}</td>
                                            <td className="px-4 py-3">
                                                <span className={`px-2 py-1 rounded text-[10px] font-mono ${log.status === 'Critical' ? 'bg-warning/10 text-warning border border-warning/20' :
                                                        log.status === 'Warning' ? 'bg-[#FFB800]/10 text-[#FFB800] border border-[#FFB800]/20' :
                                                            'bg-electric/10 text-electric border border-electric/20'
                                                    }`}>
                                                    {getStatusLabel(log.status)}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                    {logs.length === 0 && (
                                        <tr>
                                            <td colSpan={4} className="px-4 py-12 text-center text-white/20 font-mono italic uppercase tracking-widest">Нет данных</td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Modal: Add Machine */}
            <AnimatePresence>
                {isAddModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsAddModalOpen(false)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="bg-[#0A0A0B] border border-white/10 rounded-2xl w-full max-w-lg p-8 relative z-10 shadow-2xl overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-electric to-transparent opacity-50" />
                            
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                                        <Plus className="w-5 h-5 text-electric" /> Добавить станок
                                    </h3>
                                    <p className="text-xs font-mono text-white/40 uppercase tracking-widest">Конфигурация узла</p>
                                </div>
                                <button onClick={() => setIsAddModalOpen(false)} className="text-white/20 hover:text-white transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="space-y-6">
                                {/* Name Input */}
                                <div>
                                    <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">Название (ID)</label>
                                    <input 
                                        type="text" 
                                        value={newMachineName}
                                        onChange={(e) => setNewMachineName(e.target.value)}
                                        placeholder="Напр., M04"
                                        className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white font-mono focus:border-electric/50 focus:bg-white/10 outline-none transition-all placeholder:text-white/10"
                                    />
                                    
                                    <div className="flex flex-wrap gap-2 mt-3">
                                        {['Apex-3000', 'Titan-X', 'Precision-7'].map(preset => (
                                            <button
                                                key={preset}
                                                type="button"
                                                onClick={() => setNewMachineName(preset)}
                                                className={`px-3 py-1.5 rounded-lg border text-[10px] font-mono transition-all ${
                                                    newMachineName === preset 
                                                    ? 'bg-electric/20 border-electric text-electric shadow-[0_0_10px_rgba(0,240,255,0.1)]' 
                                                    : 'bg-white/5 border-white/10 text-white/40 hover:border-white/20'
                                                }`}
                                            >
                                                {preset}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="pt-4 flex flex-col gap-3">
                                    <button 
                                        onClick={handleAddMachine}
                                        disabled={!newMachineName || isCreating}
                                        className="w-full bg-electric text-black font-bold py-4 rounded-xl hover:bg-[#00f0ff] disabled:opacity-30 disabled:hover:bg-electric transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] flex items-center justify-center gap-2"
                                    >
                                        {isCreating ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Создание...
                                            </>
                                        ) : (
                                            'Добавить в систему'
                                        )}
                                    </button>
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>

            {/* Modal: Upload Logs / Analysis */}
            <AnimatePresence>
                {isUploadModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            onClick={() => setIsUploadModalOpen(false)}
                            className="absolute inset-0 bg-black/80 backdrop-blur-sm"
                        />
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="bg-[#0A0A0B] border border-white/10 rounded-2xl w-full max-w-lg p-8 relative z-10 shadow-2xl overflow-hidden"
                        >
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-electric to-transparent opacity-50" />
                            
                            <div className="flex justify-between items-start mb-8">
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-2 flex items-center gap-2">
                                        <Database className="w-5 h-5 text-electric" /> Загрузка данных анализа
                                    </h3>
                                    <p className="text-xs font-mono text-white/40 uppercase tracking-widest">Станок: {selectedMachine}</p>
                                </div>
                                <button onClick={() => setIsUploadModalOpen(false)} className="text-white/20 hover:text-white transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="space-y-6">
                                <div>
                                    <label className="text-[10px] font-mono text-white/30 uppercase tracking-widest mb-2 block">Файл данных (CSV / .zip / .h5)</label>
                                    <div className="relative">
                                        <input 
                                            type="file" 
                                            id="modal-upload-analysis"
                                            className="hidden"
                                            accept=".zip,.h5,.csv"
                                            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                                        />
                                        <label 
                                            htmlFor="modal-upload-analysis"
                                            className={`w-full border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center gap-3 cursor-pointer transition-all ${
                                                selectedFile 
                                                ? 'bg-electric/5 border-electric/40 text-electric' 
                                                : 'bg-white/5 border-white/10 text-white/30 hover:bg-white/10 hover:border-white/20'
                                            }`}
                                        >
                                            {selectedFile ? (
                                                <>
                                                    <FileArchive className="w-10 h-10" />
                                                    <span className="text-sm font-mono truncate max-w-[250px]">{selectedFile.name}</span>
                                                </>
                                            ) : (
                                                <>
                                                    <Upload className="w-10 h-10 opacity-50" />
                                                    <span className="text-xs font-mono">Перетащите архив или выберите файл</span>
                                                </>
                                            )}
                                        </label>
                                    </div>
                                </div>

                                <div className="bg-electric/5 border border-electric/10 rounded-xl p-4 flex gap-4">
                                    <Shield className="w-5 h-5 text-electric shrink-0 mt-0.5" />
                                    <div>
                                        <h4 className="text-xs font-bold text-electric mb-1 uppercase tracking-tight">Обработка ML</h4>
                                        <p className="text-[10px] text-white/40 leading-relaxed font-mono">
                                            Система автоматически проанализирует вибрационные сигналы и обновит график прогноза RUL для выбранного станка.
                                        </p>
                                    </div>
                                </div>

                                <div className="pt-4 flex flex-col gap-3">
                                    <button 
                                        onClick={handleUploadLogs}
                                        disabled={!selectedFile || isCreating}
                                        className="w-full bg-electric text-black font-bold py-4 rounded-xl hover:bg-[#00f0ff] disabled:opacity-30 disabled:hover:bg-electric transition-all shadow-[0_0_20px_rgba(0,240,255,0.2)] flex items-center justify-center gap-2"
                                    >
                                        {isCreating ? (
                                            <>
                                                <Loader2 className="w-5 h-5 animate-spin" />
                                                Загрузка...
                                            </>
                                        ) : (
                                            'Запустить анализ'
                                        )}
                                    </button>
                                    {uploadStatus && (
                                        <p className="text-[10px] text-center font-mono text-electric animate-pulse">{uploadStatus}</p>
                                    )}
                                </div>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </div>
    );
};
"""

with open(file_path, "w", encoding="utf-8-sig") as f:
    f.write(content)

print("Successfully updated Dashboard.tsx with new features")
