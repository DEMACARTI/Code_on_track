import React from 'react';
import { Search } from 'lucide-react';
import { Input } from './Input';

interface SearchInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
    value: string;
    onChange: (value: string) => void;
}

export const SearchInput: React.FC<SearchInputProps> = ({ value, onChange, placeholder = "Search...", className, ...props }) => {
    return (
        <Input
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder={placeholder}
            leftIcon={<Search className="h-4 w-4" />}
            className={className}
            {...props}
        />
    );
};
