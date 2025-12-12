import api from './axios';
import type { Item } from './items';

export interface Vendor {
    id: number;
    name: string;
    items_count: number;
    failed_count?: number;
    // Optional/Mapped fields
    vendor_code?: string;
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
    address?: string;
    warranty_months?: number;
    notes?: string;
    created_at: string;
    is_active: boolean;
    components_supplied?: string[];
}

export interface VendorCreate {
    name: string;
    vendor_code: string;
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
    address?: string;
    warranty_months?: number;
    notes?: string;
}

export interface VendorUpdate {
    name?: string;
    vendor_code?: string;
    contact_name?: string;
    contact_email?: string;
    contact_phone?: string;
    address?: string;
    warranty_months?: number;
    notes?: string;
    is_active?: boolean;
}

export interface VendorListParams {
    q?: string;
    page?: number;
    page_size?: number;
}

export const listVendors = async (params: any = {}) => {
    // Note: params can include 'id' now
    const response = await api.get<Vendor[]>('/vendors/', { params });
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

export const listVendorItems = async (id: number) => {
    const response = await api.get<Item[]>(`/vendors/${id}/items`);
    return response.data;
};
