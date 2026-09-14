import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';

export default function SpacesPage() {
  const [spaces, setSpaces] = useState([]);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(true);

  const loadSpaces = () => {
    api.get('/spaces').then((res) => {
      setSpaces(res.data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadSpaces();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    await api.post('/spaces', { name, description });
    setName('');
    setDescription('');
    loadSpaces();
  };

  if (loading) return <div className="container mt-4">Loading...</div>;

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <h2>Your Spaces</h2>

        <form onSubmit={handleCreate} className="card p-3 mb-4">
          <h6>Create a new Space</h6>
          <div className="row g-2">
            <div className="col-md-4">
              <input
                className="form-control"
                placeholder="Space name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                placeholder="Description (optional)"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />
            </div>
            <div className="col-md-2">
              <button className="btn btn-primary w-100" type="submit">Create</button>
            </div>
          </div>
        </form>

        <div className="row">
          {spaces.map((s) => (
            <div className="col-md-4 mb-3" key={s._id}>
              <div className="card p-3">
                <h5>{s.name}</h5>
                <p className="text-muted">{s.description}</p>
                <p className="small">{s.project_count} project(s)</p>
                <Link to={`/spaces/${s._id}`} className="btn btn-outline-primary btn-sm">
                  Open
                </Link>
              </div>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}