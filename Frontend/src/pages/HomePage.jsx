import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';

export default function HomePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/home').then((res) => {
      setData(res.data);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="container mt-4">Loading...</div>;

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <h2>Welcome back</h2>

        {data.continue_learning && (
          <div className="card p-3 mb-3 bg-light">
            <h5>Continue Learning</h5>
            <p className="mb-1">{data.continue_learning.name}</p>
            <Link
              className="btn btn-primary btn-sm"
              to={`/projects/${data.continue_learning._id}`}
            >
              Resume
            </Link>
          </div>
        )}

        <div className="row mb-3">
          <div className="col">
            <div className="card p-3 text-center">
              <h6>Overall Progress</h6>
              <h3>{data.overall_progress}%</h3>
            </div>
          </div>
          <div className="col">
            <div className="card p-3 text-center">
              <h6>Total Spaces</h6>
              <h3>{data.total_spaces}</h3>
            </div>
          </div>
          <div className="col">
            <div className="card p-3 text-center">
              <h6>Total Projects</h6>
              <h3>{data.total_projects}</h3>
            </div>
          </div>
        </div>

        {data.recommended_next_step && (
          <div className="alert alert-info">
            <strong>Recommended next step:</strong> {data.recommended_next_step}
          </div>
        )}

        <h5 className="mt-4">Areas to Improve</h5>
        {data.areas_to_improve.length === 0 ? (
          <p className="text-muted">No weak areas yet — keep learning!</p>
        ) : (
          <ul className="list-group mb-3">
            {data.areas_to_improve.map((c) => (
              <li key={c._id} className="list-group-item d-flex justify-content-between">
                {c.concept}
                <span className="badge bg-warning text-dark">{c.mastery_pct}%</span>
              </li>
            ))}
          </ul>
        )}

        <h5 className="mt-4">Recent Projects</h5>
        <div className="list-group">
          {data.recent_projects.map((p) => (
            <Link
              key={p._id}
              to={`/projects/${p._id}`}
              className="list-group-item list-group-item-action"
            >
              {p.name}
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}