'use client';

import { useState, useEffect, useRef } from 'react';
import { Search, X } from 'lucide-react';

interface Medication {
  id: string;
  commercial_name: string;
  active_ingredient: string;
  concentration: string | null;
  pharmaceutical_form: string | null;
  manufacturer: string | null;
}

interface Props {
  value: string;
  onChange: (value: string, medication?: Medication) => void;
  placeholder?: string;
  className?: string;
}

export default function MedicationAutocomplete({ value, onChange, placeholder, className }: Props) {
  const [query, setQuery] = useState(value);
  const [suggestions, setSuggestions] = useState<Medication[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Debounce search
  useEffect(() => {
    if (query.length < 2) {
      setSuggestions([]);
      setIsOpen(false);
      return;
    }

    const timer = setTimeout(async () => {
      await searchMedications(query);
    }, 300); // 300ms debounce

    return () => clearTimeout(timer);
  }, [query]);

  // Close on click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const searchMedications = async (searchTerm: string) => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `/api/v1/medications/search?q=${encodeURIComponent(searchTerm)}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setSuggestions(data);
        setIsOpen(data.length > 0);
      }
    } catch (error) {
      console.error('Erro ao buscar medicamentos:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelect = (medication: Medication) => {
    const displayValue = `${medication.commercial_name} ${medication.concentration || ''} - ${medication.pharmaceutical_form || ''}`.trim();
    setQuery(displayValue);
    onChange(displayValue, medication);
    setIsOpen(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev < suggestions.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && suggestions[selectedIndex]) {
          handleSelect(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div ref={wrapperRef} className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            onChange(e.target.value);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "Digite o nome do medicamento..."}
          className={`w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 ${className}`}
        />
        {query && (
          <button
            onClick={() => {
              setQuery('');
              onChange('');
              setSuggestions([]);
              setIsOpen(false);
            }}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {isOpen && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((medication, index) => (
            <button
              key={medication.id}
              onClick={() => handleSelect(medication)}
              className={`w-full text-left px-4 py-3 hover:bg-blue-50 border-b border-gray-100 last:border-b-0 transition-colors ${
                index === selectedIndex ? 'bg-blue-50' : ''
              }`}
            >
              <div className="font-medium text-gray-900">
                {medication.commercial_name}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                {medication.active_ingredient}
                {medication.concentration && ` • ${medication.concentration}`}
                {medication.pharmaceutical_form && ` • ${medication.pharmaceutical_form}`}
              </div>
              {medication.manufacturer && (
                <div className="text-xs text-gray-500 mt-1">
                  {medication.manufacturer}
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {isLoading && (
        <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent"></div>
        </div>
      )}
    </div>
  );
}
