import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import '../styles/Login.css';

interface LoginResponse {
  token: string;
  expires_at: string;
  user: {
    id: string;
    username: string;
    email: string;
  };
}

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await axios.post<LoginResponse>(
        `${import.meta.env.VITE_API_URL}/auth/login`,
        { username, password },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      // Save token to localStorage
      localStorage.setItem('access_token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      localStorage.setItem('expires_at', response.data.expires_at);

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      setError(
        err.response?.data?.error || 'Failed to login. Please try again.'
      );
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <div className="login-header">
          <h1>AgroVision</h1>
          <p>Sistema de Gerenciamento de Gado</p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Usuário</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Digite seu usuário"
              required
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Digite sua senha"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className="submit-button"
          >
            {loading ? 'Autenticando...' : 'Entrar'}
          </button>
        </form>

        <div className="login-footer">
          <p>Credenciais de teste:</p>
          <p>Usuário: <code>admin</code></p>
          <p>Senha: <code>password123</code></p>
        </div>
      </div>
    </div>
  );
};
