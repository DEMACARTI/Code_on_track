import { render, screen, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import Dashboard from '../pages/Dashboard';
import axios from 'axios';

vi.mock('axios');

describe('Dashboard', () => {
    it('renders KPI cards with data', async () => {
        (axios.get as any).mockResolvedValue({
            data: { items: 10, vendors: 5 }
        });

        render(<Dashboard />);

        await waitFor(() => {
            expect(screen.getByTestId('kpi-items')).toHaveTextContent('10');
            expect(screen.getByTestId('kpi-vendors')).toHaveTextContent('5');
        });
    });
});
