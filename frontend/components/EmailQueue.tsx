'use client';

import { useState, useEffect } from 'react';
import { emailsApi } from '@/lib/api';

export default function EmailQueue() {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processResult, setProcessResult] = useState<any>(null);

  useEffect(() => {
    loadQueue();
  }, []);

  const loadQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await emailsApi.getQueue();
      setQueue(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load queue');
    } finally {
      setLoading(false);
    }
  };

  const handleProcessQueue = async () => {
    setProcessing(true);
    setError(null);
    setProcessResult(null);
    try {
      const result = await emailsApi.processQueue();
      setProcessResult(result);
      await loadQueue(); // Refresh queue
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to process queue');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Email Queue</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={loadQueue} className="btn btn-secondary">Refresh</button>
          <button onClick={handleProcessQueue} className="btn btn-primary" disabled={processing}>
            {processing ? 'Processing...' : 'Process Queue'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {processResult && (
        <div className="success">
          <strong>Queue Processed!</strong>
          <p>Processed: {processResult.processed}, Failed: {processResult.failed}, Total: {processResult.total}</p>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading queue...</div>
      ) : queue.length === 0 ? (
        <div className="loading">No emails in queue</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>To</th>
                <th>Subject</th>
                <th>Scheduled Time</th>
                <th>Status</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {queue.map((item) => (
                <tr key={item.id}>
                  <td>{item.email_to}</td>
                  <td>{item.email_subject}</td>
                  <td>{new Date(item.scheduled_time).toLocaleString()}</td>
                  <td>
                    <span className={`badge badge-${item.status === 'sent' ? 'success' : item.status === 'failed' ? 'danger' : 'warning'}`}>
                      {item.status}
                    </span>
                  </td>
                  <td>{item.email_type}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

