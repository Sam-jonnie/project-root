import React, { useState } from 'react';
import axios from 'axios';
import './Login.css';

export default function Login({ onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState({ email: '', password: '' });

  const validateField = (name, value) => {
    let errorMsg = '';
    if (name === 'email') {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (value && !emailRegex.test(value)) {
        errorMsg = '⚠️ Standard structural email expression required (e.g. name@domain.com)';
      }
    }
    if (name === 'password') {
      if (value && value.length < 6) {
        errorMsg = '⚠️ Encryption key parameter must be at least 6 characters long';
      }
    }
    setErrors(prev => ({ ...prev, [name]: errorMsg }));
  };

  const submit = async (e) => {
    e.preventDefault();
    if (errors.email || errors.password || !email || !password) return;

    setIsSubmitting(true);
    const data = new URLSearchParams();
    data.append('username', email);
    data.append('password', password);

    try {
      const res = await axios.post('http://localhost:8000/auth/login', data);
      onLoginSuccess(res.data.access_token, res.data.role);
    } catch (err) {
      alert('Authentication failure. System rejected the provided validation keys.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-row-container">
      
      {/* LEFT COLUMN: Visual Branding Node Area */}
      <div className="login-side-visual">
        <div className="blur-orb orb-1"></div>
        <div className="blur-orb orb-2"></div>
        <div className="visual-message-context">
          <div className="brand-logo-large">⚡</div>
          <h1>Project Management<br/>Matrix Board</h1>
          <p>Manage projects and tasks with RBAC.</p>
        </div>
      </div>

      {/* RIGHT COLUMN: Interactive Input Form Area */}
      <div className="login-side-form">
        <div className="form-inner-wrapper">
          <div className="form-brand-header">
            <h2>Establish Connection</h2>
            <p>Input your authorized session access keys</p>
          </div>

          <form onSubmit={submit} className="modern-form">
            <div className={`input-group-modern ${errors.email ? 'has-error' : ''}`}>
              <input 
                type="email" 
                id="email"
                value={email}
                placeholder=" " 
                onChange={e => {
                  setEmail(e.target.value);
                  validateField('email', e.target.value);
                }} 
                required 
              />
              <label htmlFor="email">Email</label>
              <span className="input-bar"></span>
              {errors.email && <div className="error-text-alert">{errors.email}</div>}
            </div>

            <div className={`input-group-modern password-group-modern ${errors.password ? 'has-error' : ''}`}>
              <input 
                type={showPassword ? 'text' : 'password'} 
                id="password"
                value={password}
                placeholder=" " 
                onChange={e => {
                  setPassword(e.target.value);
                  validateField('password', e.target.value);
                }} 
                required 
              />
              <label htmlFor="password">Password</label>
              
              <button 
                type="button" 
                className="password-toggle-btn"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
              
              <span className="input-bar"></span>
              {errors.password && <div className="error-text-alert">{errors.password}</div>}
            </div>

            <button 
              type="submit" 
              className="submit-btn-modern" 
              disabled={isSubmitting || !!errors.email || !!errors.password}
            >
              {isSubmitting ? 'Please wait...' : 'Login'}
            </button>
          </form>

          <footer className="form-footer-modern">
            <span>© created by Samuel Jonathan.</span>
          </footer>
        </div>
      </div>

    </div>
  );
}
