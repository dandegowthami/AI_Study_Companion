import { useEffect, useState } from 'react';
import api from '../../services/api';

export default function AdminAIUsageTab() {
  const [usage, setUsage] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [snapshotting, setSnapshotting] = useState(false);

  const loadEvaluation = () => api.get('/admin/evaluation').then((res) => setEvaluation(res.data));

  useEffect(() => {
    api.get('/admin/ai-usage').then((res) => setUsage(res.data));
    loadEvaluation();
  }, []);

  const takeSnapshot = async () => {
    setSnapshotting(true);
    await api.post('/admin/evaluation/snapshot');
    await loadEvaluation();
    setSnapshotting(false);
  };

  if (!usage || !evaluation) return <p>Loading AI usage &amp; evaluation...</p>;

  const evalCurrent = evaluation.current;

  return (
    <div>
      <h5>AI Usage</h5>
      <div className="row g-3 mb-3">
        <div className="col-md-3 col-sm-6">
          <div className="card p-2 text-center"><small>Total Requests</small><h5>{usage.total_requests}</h5></div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-2 text-center"><small>Avg Latency</small><h5>{usage.avg_latency_ms}ms</h5></div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-2 text-center"><small>Total Tokens</small><h5>{usage.total_input_tokens + usage.total_output_tokens}</h5></div>
        </div>
        <div className="col-md-3 col-sm-6">
          <div className="card p-2 text-center">
            <small>Est. Cost</small>
            <h5>${usage.estimated_cost_usd}</h5>
          </div>
        </div>
      </div>
      <p className="small text-muted">{usage.cost_note}</p>

      <h6>Usage by Feature</h6>
      <table className="table table-sm">
        <thead>
          <tr><th>Feature</th><th>Requests</th><th>Failures</th><th>Total Tokens</th></tr>
        </thead>
        <tbody>
          {Object.entries(usage.by_feature).map(([feature, stats]) => (
            <tr key={feature}>
              <td>{feature}</td>
              <td>{stats.count}</td>
              <td className={stats.failures > 0 ? 'text-danger' : ''}>{stats.failures}</td>
              <td>{stats.total_tokens}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <hr className="my-4" />

      <div className="d-flex justify-content-between align-items-center mb-2">
        <h5 className="mb-0">AI Evaluation</h5>
        <button className="btn btn-sm btn-outline-primary" onClick={takeSnapshot} disabled={snapshotting}>
          {snapshotting ? 'Saving...' : 'Save Snapshot'}
        </button>
      </div>

      <div className="row g-3 mb-3">
        <div className="col-md-6">
          <div className="card p-3 h-100">
            <h6>Tutor</h6>
            <p className="small mb-1">Total answers: {evalCurrent.tutor.total_answers}</p>
            <p className="small mb-1">Groundedness rate: {evalCurrent.tutor.groundedness_rate_pct}%</p>
            <p className="small mb-1">Unsupported-question handling rate: {evalCurrent.tutor.unsupported_handling_rate_pct}%</p>
            <p className="small mb-1">Avg sources per answer: {evalCurrent.tutor.avg_sources_per_answer}</p>
            <p className="small text-muted mb-0">{evalCurrent.tutor.note}</p>
          </div>
        </div>
        <div className="col-md-6">
          <div className="card p-3 h-100">
            <h6>Assessment &amp; Recommendations</h6>
            <p className="small mb-1">Quiz attempts started: {evalCurrent.assessment.quiz_attempts_started}</p>
            <p className="small mb-1">Quiz attempts completed: {evalCurrent.assessment.quiz_attempts_completed}</p>
            <p className="small mb-1">
              Quiz generation failure rate: {evalCurrent.assessment.quiz_generation_failure_rate_pct ?? 'N/A'}%
            </p>
            <p className="small mb-1">
              Quiz grading failure rate: {evalCurrent.assessment.quiz_grading_failure_rate_pct ?? 'N/A'}%
            </p>
            <p className="small mb-1">Recommendations generated: {evalCurrent.recommendations.recommendations_generated}</p>
            <p className="small mb-0">
              Recommendation failure rate: {evalCurrent.recommendations.recommendation_failure_rate_pct ?? 'N/A'}%
            </p>
          </div>
        </div>
      </div>

      <h6>Snapshot History (regression tracking)</h6>
      {evaluation.history.length === 0 ? (
        <p className="small text-muted">No snapshots saved yet. Use "Save Snapshot" to record a baseline.</p>
      ) : (
        <table className="table table-sm">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Groundedness</th>
              <th>Unsupported Handling</th>
              <th>Quiz Grading Failures</th>
            </tr>
          </thead>
          <tbody>
            {evaluation.history.map((h) => (
              <tr key={h._id}>
                <td className="small">{new Date(h.timestamp).toLocaleString()}</td>
                <td>{h.tutor.groundedness_rate_pct}%</td>
                <td>{h.tutor.unsupported_handling_rate_pct}%</td>
                <td>{h.assessment.quiz_grading_failure_rate_pct ?? 'N/A'}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
