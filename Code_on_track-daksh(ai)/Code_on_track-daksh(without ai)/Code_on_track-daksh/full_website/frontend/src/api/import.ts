import api from './axios';

export interface ImportPreviewResponse {
    total_rows: number;
    valid_rows: number;
    invalid_rows: Array<{
        row_number: number;
        errors: string[];
        row: Record<string, string>;
    }>;
}

export interface ImportCommitResponse {
    created_items: string[];
    skipped_rows: number;
}

export async function previewImport(formData: FormData): Promise<ImportPreviewResponse> {
    const response = await api.post<ImportPreviewResponse>('/api/import/items', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
}

export async function commitImport(formData: FormData): Promise<ImportCommitResponse> {
    // Append commit=true to the URL query params
    const response = await api.post<ImportCommitResponse>('/api/import/items', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
}
