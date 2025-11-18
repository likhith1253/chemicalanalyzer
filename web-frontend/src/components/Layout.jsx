import React, { useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { getCurrentUser, authAPI } from '../api/client';
import './Layout.css';

const Layout = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = getCurrentUser();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
      navigate('/login');
    }
  };

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/history', label: 'History', icon: '📚' },
    { path: '/visualizations', label: 'Visualizations', icon: '📈' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
    { path: '/help', label: 'Help', icon: '❓' },
  ];

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <span className="sidebar-icon">⚗️</span>
            {sidebarOpen && <span className="sidebar-name">ChemViz</span>}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`sidebar-link ${location.pathname === item.path ? 'active' : ''}`}
              title={item.label}
            >
              <span className="sidebar-link-icon">{item.icon}</span>
              {sidebarOpen && <span className="sidebar-link-label">{item.label}</span>}
            </Link>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <div className="main-wrapper">
        {/* Top Navbar */}
        <header className="top-navbar">
          <div className="navbar-content">
            <div className="navbar-left">
              <h1 className="navbar-title">Chemical Equipment Visualizer</h1>
            </div>
            <div className="navbar-right">
              {user && (
                <div className="user-menu">
                  <span className="user-greeting">Welcome, {user.username || 'User'}</span>
                  <button className="logout-button" onClick={handleLogout}>
                    🚪 Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="main-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
