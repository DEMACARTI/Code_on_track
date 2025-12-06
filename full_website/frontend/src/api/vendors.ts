import api from './axios';

export interface Vendor {
    id: number;
    name: string;
    contact_info: Record<string, any> | null;
    metadata: Record<string, any> | null;
    created_at: string;
    is_active: boolean;
    items_count: number;
}

export interface VendorCreate {
    name: string;
    contact_info?: Record<string, any>;
    metadata?: Record<string, any>;
}

export interface VendorUpdate {
    name?: string;
    contact_info?: Record<string, any>;
    metadata?: Record<string, any>;
    is_active?: boolean;
}

export interface VendorListParams {
    q?: string;
    page?: number;
    page_size?: number;
}

export const listVendors = async (params: VendorListParams = {}) => {
    const response = await api.get<Vendor[]>('/vendors', { params });
    return response.data;
};

export const getVendor = async (id: number) => {
    const response = await api.get<Vendor>(`/vendors/${id}`);
    return response.data;
};

export const createVendor = async (data: VendorCreate) => {
    const response = await api.post<Vendor>('/vendors', data);
    return response.data;
};

export const updateVendor = async (id: number, data: VendorUpdate) => {
    const response = await api.put<Vendor>(`/vendors/${id}`, data);
    return response.data;
};

export const deleteVendor = async (id: number) => {
    await api.delete(`/vendors/${id}`);
};
