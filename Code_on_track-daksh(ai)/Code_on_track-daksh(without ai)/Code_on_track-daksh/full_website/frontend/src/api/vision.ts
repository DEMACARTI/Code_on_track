import api from './axios';

export interface InspectionReport {
    report_id?: number | string;
    issue: string;
    confidence: number;
    severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
    recommended_action: string;
    bbox: number[];
    created_at?: string;
}

export const inspectComponent = async (file: File, uid: string, lot_no?: string): Promise<InspectionReport> => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('uid', uid);
    if (lot_no) formData.append('lot_no', lot_no);

    const response = await api.post<InspectionReport>('/vision/inspect', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getInspectionHistory = async (uid: string): Promise<InspectionReport[]> => {
    const response = await api.get<InspectionReport[]>(`/vision/history/${uid}`);
    return response.data;
};
