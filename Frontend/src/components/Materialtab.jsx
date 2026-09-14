import { useState } from 'react';
import api from '../services/api';

export default function Materialtab({ projectId, materials, onUploaded }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [statuses, setStatuses] = useState({});

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true);

    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('file', file);

    const res = await api.post('/materials/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });

    setUploading(false);
    setFile(null);
    pollStatus(res.data.material_id);
  };

  const pollStatus = (materialId) => {
    const interval = setInterval(async () => {
      const res = await api.get(`/materials/${materialId}/status`);
      setStatuses((prev) => ({ ...prev, [materialId]: res.data.status }));

      if (res.data.status === 'ready' || res.data.status === 'failed') {
        clearInterval(interval);
        onUploaded();
      }
    }, 2000);
  };

  return (
    <div>
      <form onSubmit={handleUpload} className="card p-3 mb-3">
        <h6>Upload Material (PDF)</h6>
        <div className="row g-2">
          <div className="col-md-8">
            <input
              type="file"
              accept="application/pdf"
              className="form-control"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>
          <div className="col-md-4">
            <button className="btn btn-primary w-100" type="submit" disabled={!file || uploading}>
              {uploading ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </div>
      </form>

      <h6>Materials</h6>
      <ul className="list-group">
        {materials.map((m) => (
          <li key={m._id} className="list-group-item d-flex justify-content-between align-items-center">
            <span>{m.name}</span>
            <span className={`badge ${
              (statuses[m._id] || m.status) === 'ready' ? 'bg-success' :
              (statuses[m._id] || m.status) === 'failed' ? 'bg-danger' : 'bg-secondary'
            }`}>
              {statuses[m._id] || m.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}