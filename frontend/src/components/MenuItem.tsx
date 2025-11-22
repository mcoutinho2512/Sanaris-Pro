'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronDown } from 'lucide-react';

interface MenuItemProps {
  item: {
    id: string;
    name: string;
    icon: any;
    path?: string;
    children?: any[];
  };
}

export default function MenuItem({ item }: MenuItemProps) {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const Icon = item.icon;

  const isActive = item.path === pathname || 
    (item.children && item.children.some(child => child.path === pathname));

  if (item.children && item.children.length > 0) {
    return (
      <div className="mb-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`w-full flex items-center justify-between px-4 py-2.5 rounded-lg transition-all duration-200 ${
            isActive
              ? 'bg-blue-50 text-blue-600'
              : 'text-gray-700 hover:bg-gray-100'
          }`}
        >
          <div className="flex items-center gap-3">
            <Icon className="w-5 h-5" />
            <span className="font-medium">{item.name}</span>
          </div>
          <ChevronDown 
            className={`w-4 h-4 transition-transform duration-200 ${
              isOpen ? 'rotate-180' : ''
            }`}
          />
        </button>
        
        <div 
          className={`overflow-hidden transition-all duration-200 ${
            isOpen ? 'max-h-96 opacity-100 mt-1' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="ml-4 pl-4 border-l-2 border-gray-200 space-y-1">
            {item.children.map((child) => {
              const ChildIcon = child.icon;
              const isChildActive = pathname === child.path;
              
              return (
                <Link
                  key={child.id}
                  href={child.path}
                  className={`flex items-center gap-3 px-4 py-2 rounded-lg text-sm transition-all duration-200 ${
                    isChildActive
                      ? 'bg-blue-50 text-blue-600 font-medium'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <ChildIcon className="w-4 h-4" />
                  <span>{child.name}</span>
                </Link>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  return (
    <Link
      href={item.path || '#'}
      className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 mb-1 ${
        isActive
          ? 'bg-blue-50 text-blue-600 font-medium'
          : 'text-gray-700 hover:bg-gray-100'
      }`}
    >
      <Icon className="w-5 h-5" />
      <span>{item.name}</span>
    </Link>
  );
}
