import React, { useMemo } from 'react';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    Area,
    AreaChart,
} from 'recharts';
import type { MachineLog } from '../../types';

interface Props {
    data: MachineLog[];
}

export const RULChart: React.FC<Props> = ({ data }) => {
    const chartData = useMemo(() => {
        return data.slice().reverse().map(log => ({
            time: new Date(log.timestamp).toLocaleTimeString(),
            rul: log.rul_prediction,
        }));
    }, [data]);

    return (
        <div className="w-full h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorRul" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#00F0FF" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#00F0FF" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <XAxis dataKey="time" stroke="#ffffff50" tick={{ fill: '#ffffff50', fontSize: 12 }} />
                    <YAxis stroke="#ffffff50" tick={{ fill: '#ffffff50', fontSize: 12 }} />
                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" vertical={false} />
                    <Tooltip
                        contentStyle={{ backgroundColor: 'rgba(5, 5, 17, 0.9)', border: '1px solid rgba(0, 240, 255, 0.2)', borderRadius: '8px' }}
                        itemStyle={{ color: '#00F0FF' }}
                    />
                    <Area type="monotone" dataKey="rul" stroke="#00F0FF" fillOpacity={1} fill="url(#colorRul)" />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
};
