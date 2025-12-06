import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, it, expect } from 'vitest';
import { Login } from '../pages/Login';
import { AuthProvider } from '../context/AuthContext';
import { BrowserRouter } from 'react-router-dom';
import axios from 'axios';

vi.mock('axios');

const renderWithProviders = (ui: React.ReactElement) => {
    return render(
        <AuthProvider>
            <BrowserRouter>
                {ui}
            </BrowserRouter>
        </AuthProvider>
    );
};

describe('Login', () => {
    it('renders login form and submits', async () => {
        (axios.post as any).mockResolvedValue({
            data: { access_token: 'fake-token', token_type: 'bearer' }
        });
        (axios.get as any).mockResolvedValue({
            data: { id: 1, email: 'test@example.com', role: 'admin', is_active: true }
        });

        renderWithProviders(<Login />);

        fireEvent.change(screen.getByPlaceholderText('Enter your username'), { target: { value: 'test@example.com' } });
        fireEvent.change(screen.getByPlaceholderText('Enter your password'), { target: { value: 'password' } });
        fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));

        await waitFor(() => {
            expect(axios.post).toHaveBeenCalledWith(
                '/auth/login',
                { username: 'test@example.com', password: 'password' }
            );
        });
    });
});
