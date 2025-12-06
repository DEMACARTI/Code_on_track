import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import ImportItems from '../pages/ImportItems';
import * as importApi from '../api/import';

// Mock the API module
vi.mock('../api/import', () => ({
    previewImport: vi.fn(),
    commitImport: vi.fn(),
}));

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: false,
        },
    },
});

const renderComponent = () => {
    return render(
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <ImportItems />
            </BrowserRouter>
        </QueryClientProvider>
    );
};

describe('ImportItems Page', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('renders file input and disabled buttons initially', () => {
        renderComponent();

        expect(screen.getByText('Import Items')).toBeInTheDocument();
        expect(screen.getByLabelText(/select csv file/i)).toBeInTheDocument();

        const previewBtn = screen.getByRole('button', { name: /preview import/i });
        const commitBtn = screen.getByRole('button', { name: /commit import/i });

        expect(previewBtn).toBeDisabled();
        expect(commitBtn).toBeDisabled();
    });

    it('enables preview button when file is selected', async () => {
        renderComponent();
        const user = userEvent.setup();

        const file = new File(['uid,component_type\n1,resistor'], 'test.csv', { type: 'text/csv' });
        const input = screen.getByLabelText(/select csv file/i);

        await user.upload(input, file);

        const previewBtn = screen.getByRole('button', { name: /preview import/i });
        expect(previewBtn).toBeEnabled();
    });

    it('shows preview table with invalid rows and keeps commit disabled', async () => {
        const mockPreviewResponse = {
            total_rows: 3,
            valid_rows: 2,
            invalid_rows: [
                {
                    row_number: 2,
                    errors: ['Missing uid'],
                    row: { component_type: 'Resistor', vendor_name: 'Vendor A' }
                }
            ]
        };

        vi.mocked(importApi.previewImport).mockResolvedValue(mockPreviewResponse);

        renderComponent();
        const user = userEvent.setup();

        const file = new File(['content'], 'test.csv', { type: 'text/csv' });
        await user.upload(screen.getByLabelText(/select csv file/i), file);

        await user.click(screen.getByRole('button', { name: /preview import/i }));

        await waitFor(() => {
            expect(screen.getByText('Import Preview')).toBeInTheDocument();
        });

        expect(screen.getByText('Total Rows')).toBeInTheDocument();
        expect(screen.getByText('3')).toBeInTheDocument(); // Total
        expect(screen.getByText('1')).toBeInTheDocument(); // Invalid

        // Check table content
        expect(screen.getByText('Missing uid')).toBeInTheDocument();

        // Commit should be disabled because invalid_rows > 0
        expect(screen.getByRole('button', { name: /commit import/i })).toBeDisabled();
    });

    it('enables commit button when preview has no errors and calls commit on click', async () => {
        const mockPreviewResponse = {
            total_rows: 5,
            valid_rows: 5,
            invalid_rows: []
        };

        const mockCommitResponse = {
            created_items: ['ITEM-1', 'ITEM-2'],
            skipped_rows: 0
        };

        vi.mocked(importApi.previewImport).mockResolvedValue(mockPreviewResponse);
        vi.mocked(importApi.commitImport).mockResolvedValue(mockCommitResponse);

        renderComponent();
        const user = userEvent.setup();

        const file = new File(['content'], 'valid.csv', { type: 'text/csv' });
        await user.upload(screen.getByLabelText(/select csv file/i), file);

        // Preview
        await user.click(screen.getByRole('button', { name: /preview import/i }));

        await waitFor(() => {
            expect(screen.getByText('All rows are valid! Ready to commit.')).toBeInTheDocument();
        });

        const commitBtn = screen.getByRole('button', { name: /commit import/i });
        expect(commitBtn).toBeEnabled();

        // Commit
        await user.click(commitBtn);

        await waitFor(() => {
            expect(importApi.commitImport).toHaveBeenCalled();
            expect(screen.getByText(/successfully imported 2 items/i)).toBeInTheDocument();
        });
    });
});
