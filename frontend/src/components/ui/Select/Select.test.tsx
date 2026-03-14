import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Select } from './Select';

const mockOptions = [
  { value: '1', label: 'Option 1', group: 'Group A' },
  { value: '2', label: 'Option 2', group: 'Group A' },
  { value: '3', label: 'Option 3', group: 'Group B' },
];

describe('Select', () => {
  it('renders with placeholder and opens on click', () => {
    render(<Select options={mockOptions} value="" onChange={() => {}} placeholder="Select an option" />);
    
    const trigger = screen.getByRole('button');
    expect(screen.getByText('Select an option')).toBeInTheDocument();
    
    fireEvent.click(trigger);
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Rechercher...')).toBeInTheDocument();
  });

  it('filters options based on search input', () => {
    render(<Select options={mockOptions} value="" onChange={() => {}} />);
    
    fireEvent.click(screen.getByRole('button'));
    const searchInput = screen.getByPlaceholderText('Rechercher...');
    
    fireEvent.change(searchInput, { target: { value: 'Option 3' } });
    
    expect(screen.getByText('Option 3')).toBeInTheDocument();
    expect(screen.queryByText('Option 1')).not.toBeInTheDocument();
  });

  it('calls onChange and closes when an option is selected', () => {
    const handleChange = vi.fn();
    render(<Select options={mockOptions} value="" onChange={handleChange} />);
    
    fireEvent.click(screen.getByRole('button'));
    fireEvent.click(screen.getByText('Option 2'));
    
    expect(handleChange).toHaveBeenCalledWith('2');
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('supports keyboard navigation (ArrowDown, ArrowUp, Enter)', () => {
    const handleChange = vi.fn();
    const { container } = render(<Select options={mockOptions} value="" onChange={handleChange} />);
    
    const trigger = screen.getByRole('button');
    fireEvent.keyDown(trigger, { key: 'ArrowDown' }); // Opens
    
    const listbox = screen.getByRole('listbox');
    expect(listbox).toBeInTheDocument();
    
    const selectContainer = container.firstChild as HTMLElement;
    
    fireEvent.keyDown(selectContainer, { key: 'ArrowDown' }); // Move to index 1 (Option 2)
    fireEvent.keyDown(selectContainer, { key: 'Enter' });
    
    expect(handleChange).toHaveBeenCalledWith('2');
  });

  it('closes on Escape key', () => {
    const { container } = render(<Select options={mockOptions} value="" onChange={() => {}} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByRole('listbox')).toBeInTheDocument();
    
    const selectContainer = container.firstChild as HTMLElement;
    fireEvent.keyDown(selectContainer, { key: 'Escape' });
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('renders group labels', () => {
    render(<Select options={mockOptions} value="" onChange={() => {}} />);
    
    fireEvent.click(screen.getByRole('button'));
    expect(screen.getByText('Group A')).toBeInTheDocument();
    expect(screen.getByText('Group B')).toBeInTheDocument();
  });

  it('shows no results message when search matches nothing', () => {
    render(<Select options={mockOptions} value="" onChange={() => {}} />);
    
    fireEvent.click(screen.getByRole('button'));
    fireEvent.change(screen.getByPlaceholderText('Rechercher...'), { target: { value: 'nonexistent' } });
    
    expect(screen.getByText('Aucun résultat trouvé')).toBeInTheDocument();
  });
});
