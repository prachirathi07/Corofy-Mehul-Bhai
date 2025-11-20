'use client';

import { useState, useEffect } from 'react';
import { emailsApi } from '@/lib/api';

export default function SentEmails() {
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadEmails();
  }, []);

  const loadEmails = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await emailsApi.getSent(0, 50);
      setEmails(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to load emails');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2>Sent Emails</h2>
        <button onClick={loadEmails} className="btn btn-secondary">Refresh</button>
      </div>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">Loading emails...</div>
      ) : emails.length === 0 ? (
        <div className="loading">No emails sent yet</div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>To</th>
                <th>Subject</th>
                <th>Type</th>
                <th>Sent At</th>
                <th>Personalized</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {emails.map((email) => (
                <tr key={email.id}>
                  <td>{email.email_to}</td>
                  <td>{email.email_subject}</td>
                  <td>{email.email_type}</td>
                  <td>{new Date(email.sent_at).toLocaleString()}</td>
                  <td>{email.is_personalized ? 'Yes' : 'No'}</td>
                  <td>
                    <span className={`badge badge-${email.status === 'replied' ? 'success' : 'info'}`}>
                      {email.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

