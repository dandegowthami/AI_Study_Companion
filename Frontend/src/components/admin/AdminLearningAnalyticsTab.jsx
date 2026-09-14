import { useEffect, useState } from 'react';
import api from '../../services/api';

function Bar({ pct, colorClass = 'bg-primary' }) {
  return (
    <div className="progress" style={{ height: 8 }}>
      <div className={`progress-bar ${colorClass}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

export default function AdminLearningAnalyticsTab() {
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get('/admin/learning-analytics').then((res) => setData(res.data));
  }, []);

  if (!data) return <p>Loading learning analytics...</p>;

  const maxDailyCount = Math.max(1, ...data.learning_activity.daily_trend.map((d) => d.count));
  const maxFeatureCount = Math.max(1, ...data.frequently_used_features.map((f) => f.count));

  return (
    <div>
      <div className="row g-3 mb-4">
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Active Users (7d)</small>
            <h4 className="mb-0">{data.user_engagement.active_users_7d}</h4>
            <small className="text-muted">of {data.user_engagement.total_users} total</small>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Avg Quiz Accuracy</small>
            <h4 className="mb-0">{data.assessment_performance.avg_quiz_accuracy_pct}%</h4>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Average Mastery</small>
            <h4 className="mb-0">{data.average_mastery_pct}%</h4>
          </div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-3 text-center h-100">
            <small className="text-muted">Active Projects (7d)</small>
            <h4 className="mb-0">{data.active_projects.active_last_7_days}</h4>
            <small className="text-muted">of {data.active_projects.total} total</small>
          </div>
        </div>
      </div>

      <div className="row">
        <div className="col-md-6 mb-4">
          <h6>Learning Activity (last 14 days)</h6>
          <div className="card p-3">
            {data.learning_activity.daily_trend.length === 0 && (
              <p className="small text-muted mb-0">No activity recorded yet.</p>
            )}
            {data.learning_activity.daily_trend.map((d) => (
              <div key={d.date} className="mb-2">
                <div className="d-flex justify-content-between small">
                  <span>{d.date}</span>
                  <span>{d.count}</span>
                </div>
                <Bar pct={(d.count / maxDailyCount) * 100} />
              </div>
            ))}
          </div>
        </div>

        <div className="col-md-6 mb-4">
          <h6>Frequently Used Features</h6>
          <div className="card p-3">
            {data.frequently_used_features.length === 0 && (
              <p className="small text-muted mb-0">No activity recorded yet.</p>
            )}
            {data.frequently_used_features.map((f) => (
              <div key={f.event_type} className="mb-2">
                <div className="d-flex justify-content-between small">
                  <span>{f.event_type}</span>
                  <span>{f.count}</span>
                </div>
                <Bar pct={(f.count / maxFeatureCount) * 100} colorClass="bg-info" />
              </div>
            ))}
          </div>
        </div>
      </div>

      <h6>Concepts Learners Commonly Struggle With</h6>
      <ul className="list-group">
        {data.struggling_concepts.length === 0 && (
          <li className="list-group-item small text-muted">No struggling concepts detected yet.</li>
        )}
        {data.struggling_concepts.map((c) => (
          <li key={c.concept} className="list-group-item d-flex justify-content-between small">
            <span>{c.concept}</span>
            <span className="badge bg-danger">{c.learners_struggling} learner record(s) below 50%</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
