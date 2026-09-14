import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar navbar-expand navbar-dark bg-dark px-3">
      <Link className="navbar-brand" to={user?.role === 'admin' ? '/admin' : '/home'}>AI Study Companion</Link>
      <div className="navbar-nav">
        {user?.role !== 'admin' && (
        <>
        <Link className="nav-link text-white" to="/home">Home</Link>
        <Link className="nav-link text-white" to="/spaces">Spaces</Link>
        </>
        )}
         {user?.role === 'admin' && (
        <Link className="nav-link text-white" to="/admin">Admin</Link>
        )}
      </div>
      <div className="ms-auto d-flex align-items-center">
        <span className="text-white me-3">Hi, {user?.name}</span>
        <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>Logout</button>
      </div>
    </nav>
  );
}