import api from './axios';

export interface SchedulePreview {
    id: string; // generated ID from backend
    status: string;
    preview: any[]; // List of scheduled items/routes
    created_at?: string;
}

export interface GenerateScheduleParams {
    lots: string[];
    name: string;
    date: string;
}

export const generateSchedule = async (params: GenerateScheduleParams): Promise<SchedulePreview> => {
    const response = await api.post<SchedulePreview>('/schedule/generate', params);
    return response.data;
};

export const applySchedule = async (id: string): Promise<{ status: string }> => {
    const response = await api.post<{ status: string }>(`/schedule/${id}/apply`);
    return response.data;
};
