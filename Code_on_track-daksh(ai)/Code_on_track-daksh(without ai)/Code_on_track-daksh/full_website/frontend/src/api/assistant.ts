import api from './axios';

export interface AssistantAction {
    type: 'open_bucket' | 'open_scheduler' | 'open_optimized_scheduler' | 'open_inspection_history' | 'navigate';
    bucket?: string;
    params?: any;
    data?: any;
}

export interface AssistantResponse {
    answer: string;
    actions?: AssistantAction[];
}

export const queryAssistant = async (query: string): Promise<AssistantResponse> => {
    const response = await api.post<AssistantResponse>('/assistant/query', { query });
    return response.data;
};
