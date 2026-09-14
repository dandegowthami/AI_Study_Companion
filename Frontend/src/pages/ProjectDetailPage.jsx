import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../services/api';
import Navbar from '../components/Navbar';
import Materialtab from '../components/Materialtab';
import TutorTab from '../components/TutorTab';
import AnalyticsTab from '../components/AnalyticsTab';
import QuizTab from '../components/QuizTab';

export default function ProjectDetailPage() {
  const { projectId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('materials');

  const loadProject = () => {
    api.get(`/projects/${projectId}`).then((res) => {
      setData(res.data);
      setLoading(false);
    });
  };

  useEffect(() => {
    loadProject();
  }, [projectId]);

  if (loading) return <div className="container mt-4">Loading...</div>;

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <h2>{data.project.name}</h2>
        <p className="text-muted">{data.project.goal}</p>

        <div className="d-flex gap-3 mb-3">
          <div className="card p-2 px-3 text-center">
            <small>Overall Mastery</small>
            <h5>{data.overall_mastery}%</h5>
          </div>
        </div>

        <ul className="nav nav-tabs mb-3">
          {['materials', 'tutor', 'quiz', 'analytics'].map((tab) => (
            <li className="nav-item" key={tab}>
              <button
                className={`nav-link ${activeTab === tab ? 'active' : ''}`}
                onClick={() => setActiveTab(tab)}
              >
                {tab.charAt(0).toUpperCase() + tab.slice(1)}
              </button>
            </li>
          ))}
        </ul>

        {activeTab === 'materials' && (
          <Materialtab projectId={projectId} materials={data.materials} onUploaded={loadProject} />
        )}
        {activeTab === 'tutor' && <TutorTab projectId={projectId} />}
        {activeTab === 'quiz' && <QuizTab projectId={projectId} onAnswered={loadProject} />}
        {activeTab === 'analytics' && <AnalyticsTab projectId={projectId} />}
      </div>
    </>
  );
}