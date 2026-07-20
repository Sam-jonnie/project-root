
import React, { useState } from 'react';
import Login from './components/Login';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [role, setRole] = useState(localStorage.getItem('role') || '');

  const handleLoginSuccess = (jwt, userRole) => {
    localStorage.setItem('token', jwt);
    localStorage.setItem('role', userRole);
    setToken(jwt);
    setRole(userRole);
  };

  const handleLogout = () => {
    localStorage.clear();
    setToken('');
    setRole('');
  };

  return (
    <div className="app-container">
      {!token ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <Dashboard token={token} role={role} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
