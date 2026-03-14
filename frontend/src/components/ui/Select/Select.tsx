import React, { useState, useMemo, useRef, useEffect, useId } from 'react';
import { ChevronDown, Search, X } from 'lucide-react';
import { classNames } from '@utils/classNames';
import './Select.css';

export interface SelectOption {
  value: string;
  label: string;
  group?: string;
}

export interface SelectProps {
  options: SelectOption[];
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  searchPlaceholder?: string;
  label?: string;
  error?: string;
  disabled?: boolean;
  className?: string;
  id?: string;
}

export const Select: React.FC<SelectProps> = ({
  options,
  value,
  onChange,
  placeholder = 'Sélectionner...',
  searchPlaceholder = 'Rechercher...',
  label,
  error,
  disabled = false,
  className,
  id: providedId,
}) => {
  const generatedId = useId();
  const id = providedId ?? generatedId;
  const labelId = `${id}-label`;
  const listboxId = `${id}-listbox`;
  
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');
  const [highlightedIndex, setHighlightedIndex] = useState(0);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const listRef = useRef<HTMLUListElement>(null);
  const searchInputRef = useRef<HTMLInputElement>(null);

  const selectedOption = useMemo(() => 
    options.find(opt => opt.value === value), 
  [options, value]);

  const filteredOptions = useMemo(() => {
    const term = search.toLowerCase().trim();
    if (!term) return options;
    return options.filter(opt => 
      opt.label.toLowerCase().includes(term) || 
      opt.value.toLowerCase().includes(term)
    );
  }, [options, search]);

  useEffect(() => {
    setHighlightedIndex(0);
  }, [filteredOptions]);

  useEffect(() => {
    if (isOpen && searchInputRef.current) {
      searchInputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && listRef.current) {
      const highlighted = listRef.current.querySelector(`[data-index="${highlightedIndex}"]`);
      if (highlighted && typeof highlighted.scrollIntoView === 'function') {
        highlighted.scrollIntoView({ block: 'nearest' });
      }
    }
  }, [highlightedIndex, isOpen]);

  const handleToggle = () => {
    if (disabled) return;
    setIsOpen(!isOpen);
    setSearch('');
  };

  const handleSelect = (optionValue: string) => {
    onChange(optionValue);
    setIsOpen(false);
    setSearch('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (disabled) return;

    if (!isOpen) {
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        setIsOpen(true);
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => Math.min(prev + 1, filteredOptions.length - 1));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => Math.max(prev - 1, 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (filteredOptions[highlightedIndex]) {
          handleSelect(filteredOptions[highlightedIndex].value);
        }
        break;
      case 'Escape':
        e.preventDefault();
        setIsOpen(false);
        break;
      case 'Tab':
        setIsOpen(false);
        break;
    }
  };

  // Group options if needed
  const groupedOptions = useMemo(() => {
    const groups: { name: string | undefined; items: { option: SelectOption; index: number }[] }[] = [];
    let currentIndex = 0;

    filteredOptions.forEach((option) => {
      const groupName = option.group;
      let group = groups.find(g => g.name === groupName);
      if (!group) {
        group = { name: groupName, items: [] };
        groups.push(group);
      }
      group.items.push({ option, index: currentIndex });
      currentIndex++;
    });

    return groups;
  }, [filteredOptions]);

  return (
    <div 
      className={classNames('select', className, disabled && 'select--disabled', error && 'select--error')}
      ref={containerRef}
      onKeyDown={handleKeyDown}
    >
      {label && <label id={labelId} className="select__label">{label}</label>}
      
      <div className="select__wrapper">
        <button
          id={id}
          type="button"
          className="select__trigger"
          onClick={handleToggle}
          disabled={disabled}
          aria-haspopup="listbox"
          aria-expanded={isOpen}
          aria-labelledby={label ? labelId : undefined}
          aria-invalid={!!error}
        >
          <span className={classNames('select__value', !selectedOption && 'select__value--placeholder')}>
            {selectedOption ? selectedOption.label : placeholder}
          </span>
          <ChevronDown className={classNames('select__chevron', isOpen && 'select__chevron--open')} size={20} />
        </button>

        {isOpen && (
          <div className="select__dropdown">
            <div className="select__search-wrapper">
              <Search className="select__search-icon" size={16} />
              <input
                ref={searchInputRef}
                type="text"
                className="select__search-input"
                placeholder={searchPlaceholder}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                autoComplete="off"
              />
              {search && (
                <button 
                  type="button" 
                  className="select__search-clear" 
                  onClick={() => setSearch('')}
                  aria-label="Effacer la recherche"
                >
                  <X size={14} />
                </button>
              )}
            </div>

            <ul 
              ref={listRef}
              className="select__options" 
              role="listbox" 
              id={listboxId}
              aria-label={label ?? placeholder}
            >
              {filteredOptions.length === 0 ? (
                <li className="select__no-results">Aucun résultat trouvé</li>
              ) : (
                groupedOptions.map((group, gIndex) => (
                  <React.Fragment key={group.name ?? `group-${gIndex}`}>
                    {group.name && <li className="select__group-label" role="presentation">{group.name}</li>}
                    {group.items.map(({ option, index }) => (
                      <li
                        key={option.value}
                        className={classNames(
                          'select__option',
                          index === highlightedIndex && 'select__option--highlighted',
                          option.value === value && 'select__option--selected'
                        )}
                        role="option"
                        aria-selected={option.value === value}
                        data-index={index}
                        onClick={() => handleSelect(option.value)}
                        onMouseEnter={() => setHighlightedIndex(index)}
                      >
                        {option.label}
                      </li>
                    ))}
                  </React.Fragment>
                ))
              )}
            </ul>
          </div>
        )}
      </div>

      {error && <span className="select__error">{error}</span>}
    </div>
  );
};

