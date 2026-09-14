import { useEffect, useState } from 'react';
import api from '../../services/api';

function StatusBadge({ healthy }) {
  return <span className={`badge ${healthy ? 'bg-success' : 'bg-danger'}`}>{healthy ? 'Healthy' : 'Down'}</span>;
}

export default function AdminSystemHealthTab() {
  const [health, setHealth] = useState(null);

  const load = () => api.get('/admin/system-health').then((res) => setHealth(res.data));

  useEffect(() => {
    load();
  }, []);

  if (!health) return <p>Loading system health...</p>;

  return (
    <div>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h5 className="mb-0">System Health</h5>
        <button className="btn btn-sm btn-outline-secondary" onClick={load}>Refresh</button>
      </div>

      <div className="row g-3 mb-4">
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Database</small>
            <div className="mt-1"><StatusBadge healthy={health.database.healthy} /></div>
            <small className="text-muted">{health.database.latency_ms ?? '—'}ms</small>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Vector Store</small>
            <div className="mt-1"><StatusBadge healthy={health.vector_store.healthy} /></div>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">AI Provider Error Rate (recent)</small>
            <h5 className="mb-0">{health.ai_provider.recent_error_rate_pct}%</h5>
            <small className="text-muted">n={health.ai_provider.sample_size}</small>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">AI Avg Latency (recent)</small>
            <h5 className="mb-0">{health.ai_provider.recent_avg_latency_ms}ms</h5>
          </div>
        </div>
      </div>

      <h6>Background Processing (Materials)</h6>
      <div className="row g-3 mb-3">
        {Object.entries(health.background_processing.material_status_counts).map(([status, count]) => (
          <div className="col-md-3 col-sm-6" key={status}>
            <div className="card p-2 text-center">
              <small className="text-muted text-capitalize">{status}</small>
              <h5 className="mb-0">{count}</h5>
            </div>
          </div>
        ))}
      </div>

      {health.background_processing.stuck_materials_count > 0 && (
        <div className="alert alert-warning">
          <strong>{health.background_processing.stuck_materials_count} material(s) stuck</strong> in queued/processing
          for longer than expected:
          <ul className="mb-0 mt-2 small">
            {health.background_processing.stuck_materials.map((m) => (
              <li key={m._id}>{m.name} — {m.status} since {new Date(m.uploaded_at).toLocaleString()}</li>
            ))}
          </ul>
        </div>
      )}

      <h6>Recent AI Failures</h6>
      <ul className="list-group">
        {health.recent_ai_failures.length === 0 && (
          <li className="list-group-item small text-muted">No recent AI failures.</li>
        )}
        {health.recent_ai_failures.map((f, i) => (
          <li key={i} className="list-group-item small">
            <div className="d-flex justify-content-between">
              <span className="badge bg-secondary">{f.feature}</span>
              <span className="text-muted">{new Date(f.timestamp).toLocaleString()}</span>
            </div>
            <div className="text-danger">{f.error}</div>
          </li>
        ))}
      </ul>
    </div>
  );
}
