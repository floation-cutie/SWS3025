import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faSignOutAlt, faInfoCircle } from '@fortawesome/free-solid-svg-icons';

const UserProfileDropdown: React.FC = () => {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const handleLogout = () => {
    Cookies.remove('token');
    navigate('/login');
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="relative inline-block text-left" ref={dropdownRef}>
      <button 
        type="button" 
        className="inline-flex justify-center items-center w-full px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 rounded-md shadow-sm focus:outline-none" 
        id="menu-button" 
        aria-expanded="true" 
        aria-haspopup="true"
        onClick={() => setIsOpen(!isOpen)}
      >
        <FontAwesomeIcon icon={faUser} className="h-5 w-5 text-gray-700" />
      </button>

      {isOpen && (
        <div className="origin-top-right absolute right-0 mt-2 w-32 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none z-10" role="menu" aria-orientation="vertical" aria-labelledby="menu-button" tabIndex={-1}>
          <div className="py-1" role="none">
            <a href="/profile" className="group flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100" role="menuitem">
              <FontAwesomeIcon icon={faInfoCircle} className="mr-3 h-5 w-5 text-gray-400 group-hover:text-gray-500" />
              Profile
            </a>
            <button type="button" className="group flex items-center w-full text-left px-4 py-2 text-sm text-red-700 hover:bg-gray-100" role="menuitem" onClick={handleLogout}>
              <FontAwesomeIcon icon={faSignOutAlt} className="mr-3 h-5 w-5 text-red-700 group-hover:text-red-800" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UserProfileDropdown;
