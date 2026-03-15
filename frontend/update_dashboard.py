import os
import re

file_path = r"c:\Users\Алексей\Desktop\обучение\predictive-maintenance\frontend\src\pages\Dashboard.tsx"

with open(file_path, "rb") as f:
    content = f.read().decode("utf-8", errors="ignore")

# 1. Update imports
content = content.replace(
    "    createMachine \n} from '../services/api';",
    "    createMachine,\n    deleteMachine\n} from '../services/api';"
)
content = content.replace(
    "    Shield\n} from 'lucide-react';",
    "    Shield,\n    Trash2\n} from 'lucide-react';"
)

# 2. Update loadData to handle machine filtering
content = content.replace(
    "fetchLogs(),",
    "fetchLogs(selectedMachine || undefined),"
)

# 3. Add handleDeleteMachine
delete_method = """    const handleDeleteMachine = async (id: number, name: string) => {
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

    const handleCreateKey = """

content = content.replace("    const handleCreateKey = ", delete_method)

# 4. Update machines mapping to include delete button
machines_section = """                        <div className="flex flex-col gap-2 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
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
                        </div>"""

# Using regex to find the machines section because of unknown chars
content = re.sub(
    r'<div className="flex flex-col gap-2 max-h-\[300px\].*?\{machines\.length === 0 && \(.*?<\/p>.*?\)\}.*?<\/div>',
    machines_section,
    content,
    flags=re.DOTALL
)

# 5. Add Presets to modal
presets_section = """                            <div className="space-y-6">
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
                                </div>"""

content = re.sub(
    r'<div className="space-y-6">.*?{/\* Name Input \*/}.*?<label.*?>(.*?)<\/label>.*?<input.*?\/?>.*?<\/div>',
    presets_section,
    content,
    flags=re.DOTALL
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Successfully updated Dashboard.tsx")
