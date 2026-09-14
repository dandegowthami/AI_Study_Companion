import { useEffect, useState } from 'react';
import api from '../../services/api';

export default function AdminOverviewTab() {
  const [overview, setOverview] = useState(null);

  useEffect(() => {
    api.get('/admin/overview').then((res) => setOverview(res.data));
  }, []);

  if (!overview) return <p>Loading overview...</p>;

  const stats = [
    { label: 'Total Users', value: overview.total_users },
    { label: 'Total Spaces', value: overview.total_spaces },
    { label: 'Total Projects', value: overview.total_projects },
    { label: 'Materials Uploaded', value: overview.total_materials },
    { label: 'Tutor Questions Asked', value: overview.tutor_questions_asked },
    { label: 'Quiz Attempts Started', value: overview.quiz_attempts_started },
    { label: 'Total AI Requests', value: overview.total_ai_requests },
    { label: 'AI Error Rate', value: `${overview.ai_error_rate_pct}%` },
    { label: 'Avg AI Latency', value: `${overview.avg_ai_latency_ms}ms` },
  ];

  return (
    <div className="row g-3">
      {stats.map((s) => (
        <div className="col-md-4 col-sm-6" key={s.label}>
          <div className="card p-3 text-center h-100">
            <small className="text-muted">{s.label}</small>
            <h4 className="mb-0">{s.value}</h4>
          </div>
        </div>
      ))}
    </div>
  );
}
