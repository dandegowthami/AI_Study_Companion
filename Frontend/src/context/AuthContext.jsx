import { createContext, useContext, useState } from 'react';
import api from '../services/api';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem('user');
    return stored ? JSON.parse(stored) : null;
  });

  const login = async (email, password) => {
    const res = await api.post('/auth/login', { email, password });
    const { token, user_id, name, role } = res.data;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify({ user_id, name, role }));
    setUser({ user_id, name, role });
    return { user_id, name, role };
  };

  const signup = async (name, email, password) => {
    const res = await api.post('/auth/signup', { name, email, password });
    const { token, user_id, name: userName, role } = res.data;
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify({ user_id, name: userName, role }));
    setUser({ user_id, name: userName, role });
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}