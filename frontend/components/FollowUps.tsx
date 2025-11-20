'use client';

import { useState, useEffect } from 'react';
import { followupsApi } from '@/lib/api';

export default function FollowUps() {
  const [followups, setFollowups] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processResult, setProcessResult] = useState<any>(null);

  useEffect(() => {
    loadFollowups();
  }, []);

  const loadFollowups = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await followupsApi.getAll();
      setFollowups(data.followups || []);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load follow-ups');
    } finally {
      setLoading(false);
    }
  };

  const handleProcess = async () => {
    setProcessing(true);
    setError(null);
    setProcessResult(null);
    try {
      const result = await followupsApi.process();
      setProcessResult(result);
      await loadFollowups(); // Refresh
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to process follow-ups');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Follow-ups</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={loadFollowups} className="btn btn-secondary">Refresh</button>
          <button onClick={handleProcess} className="btn btn-primary" disabled={processing}>
            {processing ? 'Processing...' : 'Process Due Follow-ups'}
          </button>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {processResult && (
        <div className="success">
          <strong>Follow-ups Processed!</strong>
          <p>Processed: {processResult.processed}, Failed: {processResult.failed}, Total: {processResult.total}</p>
        </div>
      )}

      {loading ? (
        <div className="loading">Loading follow-ups...</div>
      ) : followups.length === 0 ? (
        <div className="loading">No follow-ups scheduled</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Scheduled Date</th>
                <th>Status</th>
                <th>Lead ID</th>
              </tr>
            </thead>
            <tbody>
              {followups.map((followup) => (
                <tr key={followup.id}>
                  <td>{followup.followup_type}</td>
                  <td>{new Date(followup.scheduled_date).toLocaleDateString()}</td>
                  <td>
                    <span className={`badge badge-${
                      followup.status === 'sent' ? 'success' : 
                      followup.status === 'replied' ? 'info' : 
                      followup.status === 'failed' ? 'danger' : 
                      'warning'
                    }`}>
                      {followup.status}
                    </span>
                  </td>
                  <td>{followup.lead_id}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

