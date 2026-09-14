import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';

export default function SpaceDetailPage() {
  const { spaceId } = useParams();
  const [data, setData] = useState(null);
  const [name, setName] = useState('');
  const [goal, setGoal] = useState('');
  const [loading, setLoading] = useState(true);

  const loadSpace = () => {
    api.get(`/spaces/${spaceId}`).then((res) => {
      setData(res.data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadSpace();
  }, [spaceId]);

  const handleCreateProject = async (e) => {
    e.preventDefault();
    await api.post('/projects', { space_id: spaceId, name, goal });
    setName('');
    setGoal('');
    loadSpace();
  };

  if (loading) return <div className="container mt-4">Loading...</div>;

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <h2>{data.space.name}</h2>
        <p className="text-muted">{data.space.description}</p>

        <form onSubmit={handleCreateProject} className="card p-3 mb-4">
          <h6>Create a new Project</h6>
          <div className="row g-2">
            <div className="col-md-4">
              <input
                className="form-control"
                placeholder="Project name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>
            <div className="col-md-6">
              <input
                className="form-control"
                placeholder="Learning goal"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                required
              />
            </div>
            <div className="col-md-2">
              <button className="btn btn-primary w-100" type="submit">Create</button>
            </div>
          </div>
        </form>

        <div className="row">
          {data.projects.map((p) => (
            <div className="col-md-4 mb-3" key={p._id}>
              <div className="card p-3">
                <h5>{p.name}</h5>
                <p className="text-muted small">{p.goal}</p>
                <Link to={`/projects/${p._id}`} className="btn btn-outline-primary btn-sm">
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