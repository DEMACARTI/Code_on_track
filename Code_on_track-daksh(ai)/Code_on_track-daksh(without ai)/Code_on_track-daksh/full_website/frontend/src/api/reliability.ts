import axios from './axios';

export interface VendorReliability {
    vendor_id: number;
    vendor_name: string;
    otr: number;
    qr: number;
    fr: number;
    rts: number;
    ccr: number;
    reliability_score: number;
}

export const getVendorReliability = async (sort?: string): Promise<VendorReliability[]> => {
    const params = sort ? { sort } : {};
    const response = await axios.get<VendorReliability[]>('/vendors/reliability', { params });
    return response.data;
};
