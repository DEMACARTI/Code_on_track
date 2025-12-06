import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import Items from '../pages/Items';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

vi.mock('axios');

describe('Items', () => {
    it('renders items table', async () => {
        (axios.get as any).mockResolvedValue({
            data: [
                { uid: 'ITEM-001', component_type: 'Resistor', status: 'In Stock' },
                { uid: 'ITEM-002', component_type: 'Capacitor', status: 'Deployed' }
            ]
        });

        render(
            <BrowserRouter>
                <Items />
            </BrowserRouter>
        );

        await waitFor(() => {
            expect(screen.getByText('ITEM-001')).toBeInTheDocument();
            expect(screen.getByText('Resistor')).toBeInTheDocument();
            expect(screen.getByText('ITEM-002')).toBeInTheDocument();
        });
    });
});
