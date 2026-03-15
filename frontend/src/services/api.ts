import { API_BASE_URL } from '../config/api';
import Cookies from 'js-cookie';
import type { MachineLog, PredictionRequest } from '../types';

export const fetchLogs = async (machineId?: string): Promise<MachineLog[]> => {
    try {
        const url = machineId 
            ? `${API_BASE_URL}/logs?machine_id=${machineId}` 
            : `${API_BASE_URL}/logs`;
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch logs');
        return response.json();
    } catch (error) {
        console.error('API Error:', error);
        return [];
    }
};

export const predictRUL = async (data: PredictionRequest): Promise<MachineLog> => {
    const response = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to predict RUL');
    return response.json();
};

const withUserHeader = (init?: RequestInit): RequestInit => {
    const username = Cookies.get('username');
    const headers: Record<string, string> = {
        ...((init?.headers as Record<string, string>) || {}),
    };
    if (username) {
        headers['X-User'] = username;
    }
    return { ...init, headers };
};

export const fetchMachines = async (): Promise<any[]> => {
    const response = await fetch(`${API_BASE_URL}/machines`, withUserHeader());
    if (!response.ok) throw new Error('Failed to fetch machines');
    return response.json();
};

export const createMachine = async (name: string): Promise<any> => {
    const response = await fetch(
        `${API_BASE_URL}/machines`,
        withUserHeader({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name }),
        }),
    );
    if (!response.ok) throw new Error('Failed to create machine');
    return response.json();
};

export const deleteMachine = async (id: number): Promise<void> => {
    const response = await fetch(
        `${API_BASE_URL}/machines/${id}`,
        withUserHeader({
            method: 'DELETE',
        }),
    );
    if (!response.ok) throw new Error('Failed to delete machine');
};

export const fetchApiKeys = async (machineId?: number): Promise<any[]> => {
    const url = machineId 
        ? `${API_BASE_URL}/apikeys?machine_id=${machineId}` 
        : `${API_BASE_URL}/apikeys`;
    const response = await fetch(url, withUserHeader());
    if (!response.ok) throw new Error('Failed to fetch API keys');
    return response.json();
};

export const generateApiKey = async (mode: 'dataset' | 'analysis', machineId?: number): Promise<any> => {
    const response = await fetch(
        `${API_BASE_URL}/apikeys/generate`,
        withUserHeader({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode, machine_id: machineId }),
        }),
    );
    if (!response.ok) throw new Error('Failed to generate API key');
    return response.json();
};

export const updateApiKey = async (id: number, mode: 'dataset' | 'analysis'): Promise<any> => {
    const response = await fetch(
        `${API_BASE_URL}/apikeys/${id}`,
        withUserHeader({
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mode }),
        }),
    );
    if (!response.ok) throw new Error('Failed to update API key');
    return response.json();
};

export const uploadLogs = async (machineId: string, file: File, isDataset: boolean): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${API_BASE_URL}/upload-logs?machine_id=${machineId}&is_dataset=${isDataset}`, {
        method: 'POST',
        body: formData,
    });
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to upload logs');
    }
    return response.json();
};
