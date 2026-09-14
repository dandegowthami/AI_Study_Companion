import { useEffect, useState } from 'react';
import api from '../../services/api';

const PAGE_SIZE = 25;

export default function AdminActivityTab() {
  const [events, setEvents] = useState([]);
  const [eventTypes, setEventTypes] = useState([]);
  const [total, setTotal] = useState(0);
  const [eventType, setEventType] = useState('');
  const [skip, setSkip] = useState(0);
  const [loading, setLoading] = useState(true);

  const load = (currentSkip, currentEventType) => {
    setLoading(true);
    const params = { limit: PAGE_SIZE, skip: currentSkip };
    if (currentEventType) params.event_type = currentEventType;

    api.get('/admin/activity', { params }).then((res) => {
      setEvents(res.data.events);
      setTotal(res.data.total);
      setEventTypes(res.data.event_types);
      setLoading(false);
    });
  };

  useEffect(() => {
    load(0, eventType);
    setSkip(0);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [eventType]);

  const goPrev = () => {
    const newSkip = Math.max(0, skip - PAGE_SIZE);
    setSkip(newSkip);
    load(newSkip, eventType);
  };

  const goNext = () => {
    const newSkip = skip + PAGE_SIZE;
    setSkip(newSkip);
    load(newSkip, eventType);
  };

  return (
    <div>
      <div className="d-flex align-items-center gap-2 mb-3">
        <select className="form-select form-select-sm w-auto" value={eventType} onChange={(e) => setEventType(e.target.value)}>
          <option value="">All event types</option>
          {eventTypes.map((t) => (
            <option key={t} value={t}>{t}</option>
          ))}
        </select>
        <small className="text-muted">{total} total event(s)</small>
      </div>

      {loading ? (
        <p>Loading activity...</p>
      ) : (
        <>
          <ul className="list-group mb-3">
            {events.length === 0 && <li className="list-group-item text-muted small">No activity found.</li>}
            {events.map((e) => (
              <li key={e._id} className="list-group-item d-flex justify-content-between small">
                <span>
                  <span className="badge bg-secondary me-2">{e.event_type}</span>
                  {e.user_name} ({e.user_email})
                </span>
                <span className="text-muted">{new Date(e.timestamp).toLocaleString()}</span>
              </li>
            ))}
          </ul>

          <div className="d-flex justify-content-between">
            <button className="btn btn-sm btn-outline-secondary" onClick={goPrev} disabled={skip === 0}>
              Previous
            </button>
            <button className="btn btn-sm btn-outline-secondary" onClick={goNext} disabled={skip + PAGE_SIZE >= total}>
              Next
            </button>
          </div>
        </>
      )}
    </div>
  );
}
