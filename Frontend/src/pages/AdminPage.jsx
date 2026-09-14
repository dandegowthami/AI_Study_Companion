import { useState } from 'react';
import Navbar from '../components/Navbar';
import AdminOverviewTab from '../components/admin/AdminOverviewTab';
import AdminUsersTab from '../components/admin/AdminUsersTab';
import AdminSpacesProjectsTab from '../components/admin/AdminSpacesProjectsTab';
import AdminLearningAnalyticsTab from '../components/admin/AdminLearningAnalyticsTab';
import AdminAIUsageTab from '../components/admin/AdminAIUsageTab';

const TABS = [
  { key: 'overview', label: 'Overview', Component: AdminOverviewTab },
  { key: 'users', label: 'Users', Component: AdminUsersTab },
  { key: 'spaces-projects', label: 'Spaces & Projects', Component: AdminSpacesProjectsTab },
  { key: 'analytics', label: 'Learning Analytics', Component: AdminLearningAnalyticsTab },
  { key: 'ai-usage', label: 'AI Usage & Evaluation', Component: AdminAIUsageTab },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState('overview');
  const ActiveComponent = TABS.find((t) => t.key === activeTab)?.Component ?? AdminOverviewTab;

  return (
    <>
      <Navbar />
      <div className="container mt-4">
        <h2>Admin Dashboard</h2>

        <ul className="nav nav-tabs mb-3 flex-nowrap overflow-auto">
          {TABS.map((tab) => (
            <li className="nav-item" key={tab.key}>
              <button
                className={`nav-link text-nowrap ${activeTab === tab.key ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.key)}
              >
                {tab.label}
              </button>
            </li>
          ))}
        </ul>

        <ActiveComponent />
      </div>
    </>
  );
}
