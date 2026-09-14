import { useEffect, useState } from 'react';
import api from '../../services/api';

export default function AdminSpacesProjectsTab() {
  const [view, setView] = useState('projects'); // 'spaces' | 'projects'
  const [spaces, setSpaces] = useState([]);
  const [projects, setProjects] = useState([]);
  const [detail, setDetail] = useState(null);
  const [detailType, setDetailType] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.get('/admin/spaces'), api.get('/admin/projects')]).then(([sRes, pRes]) => {
      setSpaces(sRes.data);
      setProjects(pRes.data);
      setLoading(false);
    });
  }, []);

  const viewSpace = async (spaceId) => {
    const res = await api.get(`/admin/spaces/${spaceId}`);
    setDetail(res.data);
    setDetailType('space');
  };

  const viewProject = async (projectId) => {
    const res = await api.get(`/admin/projects/${projectId}`);
    setDetail(res.data);
    setDetailType('project');
  };

  if (loading) return <p>Loading spaces &amp; projects...</p>;

  return (
    <div className="row">
      <div className="col-md-6">
        <div className="btn-group mb-3">
          <button
            className={`btn btn-sm ${view === 'spaces' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setView('spaces')}
          >
            Spaces ({spaces.length})
          </button>
          <button
            className={`btn btn-sm ${view === 'projects' ? 'btn-primary' : 'btn-outline-primary'}`}
            onClick={() => setView('projects')}
          >
            Projects ({projects.length})
          </button>
        </div>

        {view === 'spaces' && (
          <ul className="list-group" style={{ maxHeight: 500, overflowY: 'auto' }}>
            {spaces.map((s) => (
              <li
                key={s._id}
                className="list-group-item list-group-item-action"
                style={{ cursor: 'pointer' }}
                onClick={() => viewSpace(s._id)}
              >
                <div className="d-flex justify-content-between">
                  <strong>{s.name}</strong>
                  <span className="badge bg-secondary">{s.project_count} project(s)</span>
                </div>
                <small className="text-muted">
                  Owner: {s.owner.name} ({s.owner.email})
                </small>
                <br />
                <small className="text-muted">Last activity: {new Date(s.last_activity).toLocaleString()}</small>
              </li>
            ))}
          </ul>
        )}

        {view === 'projects' && (
          <ul className="list-group" style={{ maxHeight: 500, overflowY: 'auto' }}>
            {projects.map((p) => (
              <li
                key={p._id}
                className="list-group-item list-group-item-action"
                style={{ cursor: 'pointer' }}
                onClick={() => viewProject(p._id)}
              >
                <div className="d-flex justify-content-between">
                  <strong>{p.name}</strong>
                  <span className="badge bg-info text-dark">{p.overall_mastery_pct}% mastery</span>
                </div>
                <small className="text-muted">
                  Owner: {p.owner.name} · Space: {p.space_name}
                </small>
                <br />
                <small className="text-muted">
                  {p.material_count} material(s) · {p.tutor_questions} tutor question(s) · {p.quiz_attempts} quiz attempt(s)
                </small>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="col-md-6">
        <h5>Detail</h5>
        {!detail && <p className="text-muted">Select a space or project to view details.</p>}

        {detail && detailType === 'space' && (
          <div className="card p-3">
            <h6>{detail.space.name}</h6>
            <p className="small text-muted">{detail.space.description}</p>
            <p className="small">Owner: {detail.owner.name} ({detail.owner.email})</p>
            <h6 className="mt-3">Projects</h6>
            <ul className="list-group">
              {detail.projects.length === 0 && <li className="list-group-item small text-muted">No projects yet.</li>}
              {detail.projects.map((p) => (
                <li key={p._id} className="list-group-item small d-flex justify-content-between">
                  <span>{p.name}</span>
                  <span>{p.material_count} material(s) · {p.overall_mastery_pct}% mastery</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {detail && detailType === 'project' && (
          <div className="card p-3">
            <h6>{detail.project.name}</h6>
            <p className="small text-muted">{detail.project.goal}</p>
            <p className="small">
              Owner: {detail.owner.name} ({detail.owner.email}) · Space: {detail.space_name}
            </p>
            <p className="small">
              Materials: {detail.materials.length} · Quiz attempts: {detail.quiz_attempts_count}
            </p>

            <h6 className="mt-3">Mastery</h6>
            <ul className="list-group mb-3">
              {detail.mastery.length === 0 && <li className="list-group-item small text-muted">No mastery data yet.</li>}
              {detail.mastery.map((m) => (
                <li key={m._id} className="list-group-item small d-flex justify-content-between">
                  <span>{m.concept}</span>
                  <span>{m.mastery_pct}%</span>
                </li>
              ))}
            </ul>

            <h6>Recent Activity</h6>
            <ul className="list-group" style={{ maxHeight: 250, overflowY: 'auto' }}>
              {detail.activity_timeline.length === 0 && (
                <li className="list-group-item small text-muted">No activity yet.</li>
              )}
              {detail.activity_timeline.map((a, i) => (
                <li key={i} className="list-group-item small d-flex justify-content-between">
                  <span>{a.event_type}</span>
                  <span className="text-muted">{new Date(a.timestamp).toLocaleString()}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
