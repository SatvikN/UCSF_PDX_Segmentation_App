import React from 'react';
import { NavLink } from 'react-router-dom';
import '../styles/index.css';

const navItems = [
  { label: 'Model Selection', to: '/model' },
  { label: 'Information & Calculations', to: '/information' },
  { label: 'Images', to: '/images' },
  { label: 'Saving', to: '/saving' },
];

export default function SideBar() {
  return (
    <nav
      className="sidebar d-flex flex-column h-100 p-3 gap-3"
      style={{ width: '16rem' }}
    >
      {navItems.map(({ label, to }) => (
        <NavLink
          key={to}
          to={to}
          end
          className={({ isActive }) =>
            `btn flex-fill py-4 w-100 fs-4 d-flex align-items-center justify-content-center ${isActive ? 'btn-primary active' : 'btn-outline-primary'}`
          }
        >
          {label}
        </NavLink>
      ))}
    </nav>
  );
}


