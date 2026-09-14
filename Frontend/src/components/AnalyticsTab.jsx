import { useEffect, useState } from 'react';
import api from '../services/api';

export default function AnalyticsTab({ projectId }) {
  const [overview, setOverview] = useState(null);
  const [growth, setGrowth] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  const loadAnalytics = async () => {
    const [overviewRes, growthRes, recRes] = await Promise.all([
      api.get(`/analytics/${projectId}/overview`),
      api.get(`/analytics/${projectId}/growth`),
      api.get(`/analytics/${projectId}/recommendation`),
    ]);
    setOverview(overviewRes.data);
    setGrowth(growthRes.data.trends);
    setRecommendation(recRes.data.recommendation);
    setLoading(false);
  };

  useEffect(() => {
    loadAnalytics();
  }, [projectId]);

  const handleGenerateRecommendation = async () => {
    setGenerating(true);
    const res = await api.post(`/analytics/${projectId}/recommendation`);
    setRecommendation(res.data.recommendation);
    setGenerating(false);
  };

  if (loading) return <p>Loading analytics...</p>;

  const trendBadge = (trend) => {
    if (trend === 'Improving') return 'bg-success';
    if (trend === 'Needs Attention') return 'bg-danger';
    if (trend === 'Stable') return 'bg-secondary';
    return 'bg-light text-dark';
  };

  return (
    <div>
      <div className="row mb-3">
        <div className="col-md-3">
          <div className="card p-2 text-center">
            <small>Tutor Questions</small>
            <h5>{overview.activity.tutor_questions}</h5>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card p-2 text-center">
            <small>Quiz Accuracy</small>
            <h5>{overview.performance.quiz_accuracy_pct}%</h5>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card p-2 text-center">
            <small>Concepts Mastered</small>
            <h5>{overview.performance.concepts_mastered}</h5>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card p-2 text-center">
            <small>AI Requests</small>
            <h5>{overview.ai_activity.total_ai_calls}</h5>
          </div>
        </div>
      </div>

      <div className="card p-3 mb-3">
        <div className="d-flex justify-content-between align-items-center mb-2">
          <h6 className="mb-0">Recommended Next Step</h6>
          <button className="btn btn-sm btn-outline-primary" onClick={handleGenerateRecommendation} disabled={generating}>
            {generating ? 'Generating...' : 'Refresh'}
          </button>
        </div>
        <p className="mb-0">{recommendation || 'No recommendation yet.'}</p>
      </div>

      <h6>Growth by Concept</h6>
      <ul className="list-group">
        {growth.map((t, i) => (
          <li key={i} className="list-group-item d-flex justify-content-between align-items-center">
            <span>{t.concept}</span>
            <span>
              {t.previous_mastery}% → {t.current_mastery}%{' '}
              <span className={`badge ${trendBadge(t.trend)}`}>{t.trend}</span>
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}