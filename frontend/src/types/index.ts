export interface MachineLog {
    id: number;
    machine_id: string;
    timestamp: string;
    rul_prediction: number;
    status: 'Normal' | 'Warning' | 'Critical';
    ai_log: string;
    is_dataset: boolean;
}

export interface PredictionRequest {
    machine_id: string;
    sensor_1: number;
    sensor_2: number;
    sensor_3: number;
    sensor_4: number;
    is_dataset: boolean;
}
