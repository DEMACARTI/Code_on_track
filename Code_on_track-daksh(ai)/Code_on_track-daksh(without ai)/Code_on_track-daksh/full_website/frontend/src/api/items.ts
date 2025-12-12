export interface Item {
    uid: string;
    component_type: string;
    status: string;
    current_status?: string;
    lot_number?: string;
    vendor_id?: number;
    vendor?: {
        id: number;
        name: string;
        warranty_years?: number;
    };
    quantity?: number;
    warranty_years?: number;
    manufacture_date?: string;
    qr_image_url?: string;
    metadata?: any;
    created_at?: string;
    updated_at?: string;
}
