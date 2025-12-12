import { Fragment } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, AlertTriangle, AlertCircle, Info, Check } from 'lucide-react';
import { Menu, Transition } from '@headlessui/react';
import {
    getNotifications,
    markNotificationsRead,
    type Notification
} from '../api/notifications';

export const NotificationBell = () => {
    const queryClient = useQueryClient();

    const { data: notificationData } = useQuery({
        queryKey: ['notifications', 'list'],
        queryFn: getNotifications,
        refetchInterval: 30000,
    });

    const notifications = Array.isArray(notificationData) ? notificationData : [];
    const unreadCount = notifications.filter(n => !n.is_read).length;

    const markReadMutation = useMutation({
        mutationFn: markNotificationsRead,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['notifications'] });
        },
    });

    const handleNotificationClick = (notification: Notification) => {
        if (!notification.is_read) {
            markReadMutation.mutate(notification.id);
        }
    };

    const getIcon = (severity: string) => {
        switch (severity) {
            case 'danger': return <AlertCircle className="h-5 w-5 text-rose-500" />;
            case 'warning': return <AlertTriangle className="h-5 w-5 text-amber-500" />;
            case 'success': return <Check className="h-5 w-5 text-emerald-500" />;
            default: return <Info className="h-5 w-5 text-blue-500" />;
        }
    };

    return (
        <Menu as="div" className="relative">
            <Menu.Button className="relative flex h-9 w-9 items-center justify-center rounded-full text-slate-500 hover:bg-brand-50 hover:text-brand-600 transition-colors">
                <Bell className="h-5 w-5" />
                {unreadCount > 0 && (
                    <span className="absolute top-0 right-0 h-4 w-4 rounded-full bg-rose-500 text-[10px] font-bold text-white flex items-center justify-center ring-2 ring-white">
                        {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                )}
            </Menu.Button>

            <Transition
                as={Fragment}
                enter="transition ease-out duration-100"
                enterFrom="transform opacity-0 scale-95"
                enterTo="transform opacity-100 scale-100"
                leave="transition ease-in duration-75"
                leaveFrom="transform opacity-100 scale-100"
                leaveTo="transform opacity-0 scale-95"
            >
                <Menu.Items className="absolute right-0 mt-2 w-96 origin-top-right divide-y divide-slate-100 rounded-xl bg-white shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none z-50 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 bg-slate-50/50">
                        <h3 className="font-semibold text-slate-900">Notifications</h3>
                    </div>

                    <div className="max-h-[70vh] overflow-y-auto">
                        {notifications.length === 0 ? (
                            <div className="px-4 py-8 text-center text-slate-500 text-sm">
                                <div className="mx-auto w-10 h-10 bg-slate-100 rounded-full flex items-center justify-center mb-2">
                                    <Bell className="h-5 w-5 text-slate-400" />
                                </div>
                                No notifications
                            </div>
                        ) : (
                            notifications.map((notification) => (
                                <Menu.Item key={notification.id}>
                                    {({ active }) => (
                                        <div
                                            className={`relative px-4 py-3 cursor-pointer transition-colors ${active ? 'bg-slate-50' : ''
                                                } ${!notification.is_read ? 'bg-blue-50/50' : ''}`}
                                            onClick={() => handleNotificationClick(notification)}
                                        >
                                            <div className="flex gap-3">
                                                <div className={`mt-0.5 h-8 w-8 rounded-full flex items-center justify-center flex-shrink-0 ${!notification.is_read ? 'bg-white shadow-sm ring-1 ring-slate-100' : 'bg-slate-100'
                                                    }`}>
                                                    {getIcon(notification.severity)}
                                                </div>
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-start justify-between gap-2">
                                                        <p className={`text-sm font-medium ${!notification.is_read ? 'text-slate-900' : 'text-slate-600'}`}>
                                                            {notification.title}
                                                        </p>
                                                        <span className="text-[10px] text-slate-400 whitespace-nowrap">
                                                            {notification.created_at ? new Date(notification.created_at).toLocaleDateString() : ''}
                                                        </span>
                                                    </div>
                                                    <p className="text-sm text-slate-500 mt-0.5 line-clamp-2">
                                                        {notification.message}
                                                    </p>
                                                </div>
                                            </div>
                                        </div>
                                    )}
                                </Menu.Item>
                            ))
                        )}
                    </div>
                </Menu.Items>
            </Transition>
        </Menu>
    );
};
