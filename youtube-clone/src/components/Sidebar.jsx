import React from 'react';
import { Link } from 'react-router-dom';

export default function Sidebar() {
  const menuItems = [
    { name: 'Home', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
    { name: 'Explore', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
    { name: 'Subscriptions', icon: 'M12 12h.01M12 6h.01M12 18h.01M6.343 12.657a9 9 0 1111.314 0' },
    { name: 'Library', icon: 'M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2h14' },
    { name: 'Settings', icon: 'M10.344 1.656a.75.75 0 010 1.06l-7.5 7.5a.75.75 0 01-1.06 0l-3.5-3.5a.75.75 0 011.06-1.06l3.5 3.5 7.5-7.5a.75.75 0 011.06 0zM13.688 8.944a.75.75 0 010 1.06l-7.5 7.5a.75.75 0 01-1.06 0l-3.5-3.5a.75.75 0 011.06-1.06l3.5 3.5 7.5-7.5a.75.75 0 011.06 0z' },
  ];

  return (
    <aside className="w-64 bg-white shadow-sm hidden md:block">
      <div className="p-4">
        {menuItems.map((item, index) => (
          <Link key={index} to={item.name === 'Home' ? '/' : `/${item.name.toLowerCase()}`} className="flex items-center p-2 mb-2 rounded-lg hover:bg-gray-100">
            <svg className="w-6 h-6 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={item.icon} />
            </svg>
            <span className="text-sm">{item.name}</span>
          </Link>
        ))}
      </div>
    </aside>
  );
}