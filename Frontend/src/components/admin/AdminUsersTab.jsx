import { useEffect, useState } from 'react';
import api from '../../services/api';

export default function AdminUsersTab() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/admin/users').then((res) => {
      setUsers(res.data);
      setLoading(false);
    });
  }, []);

  const viewUser = async (userId) => {
    const res = await api.get(`/admin/users/${userId}`);
    setSelectedUser(res.data);
  };

  if (loading) return <p>Loading users...</p>;

  return (
    <div className="row">
      <div className="col-md-6">
        <h5>Users ({users.length})</h5>
        <ul className="list-group" style={{ maxHeight: 500, overflowY: 'auto' }}>
          {users.map((u) => (
            <li
              key={u._id}
              className={`list-group-item list-group-item-action ${selectedUser?.user?._id === u._id ? 'active' : ''}`}
              style={{ cursor: 'pointer' }}
              onClick={() => viewUser(u._id)}
            >
              <div className="d-flex justify-content-between">
                <span>{u.name} <small className="text-muted">({u.email})</small></span>
                <span className="badge bg-secondary">{u.role}</span>
              </div>
              <small>{u.space_count} space(s) · {u.project_count} project(s)</small>
            </li>
          ))}
        </ul>
      </div>

      <div className="col-md-6">
        <h5>User Detail</h5>
        {!selectedUser ? (
          <p className="text-muted">Select a user to view details.</p>
        ) : (
          <div className="card p-3">
            <h6>{selectedUser.user.name}</h6>
            <p className="small text-muted mb-2">{selectedUser.user.email}</p>
            <p className="mb-1">Spaces: {selectedUser.spaces_count} | Projects: {selectedUser.projects_count}</p>
            <p>Quiz Accuracy: {selectedUser.quiz_accuracy_pct}%</p>
            <h6 className="mt-3">Recent Activity</h6>
            <ul className="list-group" style={{ maxHeight: 300, overflowY: 'auto' }}>
              {selectedUser.activity_timeline.length === 0 && (
                <li className="list-group-item small text-muted">No activity yet.</li>
              )}
              {selectedUser.activity_timeline.map((a, i) => (
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
