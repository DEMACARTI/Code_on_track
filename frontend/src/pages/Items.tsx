import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

interface Item {
    uid: string;
    component_type: string;
    status: string;
}

const Items = () => {
    const [items, setItems] = useState<Item[]>([]);

    useEffect(() => {
        const fetchItems = async () => {
            try {
                const res = await axios.get('/items');
                setItems(res.data);
            } catch (e) {
                console.error(e);
            }
        };
        fetchItems();
    }, []);

    return (
        <div className="p-8">
            <h1 className="text-2xl mb-4">Items</h1>
            <table className="min-w-full bg-white">
                <thead>
                    <tr>
                        <th className="py-2 px-4 border-b">UID</th>
                        <th className="py-2 px-4 border-b">Type</th>
                        <th className="py-2 px-4 border-b">Status</th>
                        <th className="py-2 px-4 border-b">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {items.map((item) => (
                        <tr key={item.uid}>
                            <td className="py-2 px-4 border-b">{item.uid}</td>
                            <td className="py-2 px-4 border-b">{item.component_type}</td>
                            <td className="py-2 px-4 border-b">{item.status}</td>
                            <td className="py-2 px-4 border-b">
                                <Link to={`/items/${item.uid}`} className="text-blue-500">View</Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Items;
