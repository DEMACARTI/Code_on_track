import { useEffect, useState } from 'react';
import axios from 'axios';

const Dashboard = () => {
    const [stats, setStats] = useState({ items: 0, vendors: 0 });

    useEffect(() => {
        // Mock API call or real one if backend existed
        // For now, we'll just simulate fetching if we were using real API
        // But the test will mock axios.get
        const fetchStats = async () => {
            try {
                const res = await axios.get('/reports/summary');
                setStats(res.data);
            } catch (e) {
                console.error(e);
            }
        };
        fetchStats();
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-2xl mb-4">Dashboard</h1>
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-white p-4 rounded shadow" data-testid="kpi-items">
                    <h3 className="text-gray-500">Total Items</h3>
                    <p className="text-3xl font-bold">{stats.items}</p>
                </div>
                <div className="bg-white p-4 rounded shadow" data-testid="kpi-vendors">
                    <h3 className="text-gray-500">Total Vendors</h3>
                    <p className="text-3xl font-bold">{stats.vendors}</p>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
