import axios from './axios';

export interface BreakdownItem {
    lot_no: string;
    count: number;
    components?: string;
}

export interface NotificationMetadata {
    by_lot?: BreakdownItem[];
    total_items?: number;
    date_range?: {
        start_date?: string;
        end_date?: string;
    };
    [key: string]: any;
}

export interface Notification {
    id: number;
    type: string;
    title: string;
    message: string;
    severity: 'info' | 'warning' | 'danger' | 'success';
    is_read: boolean;
    created_at: string;
    metadata?: NotificationMetadata;
}

export const getNotifications = async (): Promise<Notification[]> => {
    const response = await axios.get<Notification[]>('/notifications');
    return Array.isArray(response.data) ? response.data : [];
};

export const getUnreadCount = async (): Promise<number> => {
    try {
        const response = await axios.get<Notification[]>('/notifications?unread_only=true');
        const data = Array.isArray(response.data) ? response.data : [];
        return data.length;
    } catch (error) {
        return 0;
    }
};

export const markNotificationsRead = async (id: number): Promise<void> => {
    await axios.patch(`/notifications/${id}/read`);
};

