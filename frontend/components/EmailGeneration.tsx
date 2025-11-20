'use client';

import { useState, useEffect } from 'react';
import { emailsApi, leadsApi } from '@/lib/api';

export default function EmailGeneration() {
  const [leads, setLeads] = useState<any[]>([]);
  const [selectedLeadId, setSelectedLeadId] = useState('');
  const [emailType, setEmailType] = useState('initial');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadLeads();
  }, []);

  const loadLeads = async () => {
    try {
      const data = await leadsApi.getAll(0, 100);
      setLeads(data);
    } catch (err) {
      console.error('Failed to load leads:', err);
    }
  };

  const handleViewEmail = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedLeadId) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // Check if email was already generated (from automatic process)
      // Check both "generated" and "sent" status emails
      const sentEmails = await emailsApi.getSent(0, 10, selectedLeadId);
      if (sentEmails && sentEmails.length > 0) {
        // Find email matching the type
        const email = sentEmails.find((e: any) => e.email_type === emailType) || sentEmails[0];
        setResult({
          subject: email.email_subject,
          body: email.email_body,
          is_personalized: email.is_personalized,
          company_website_used: email.company_website_used,
          from_cache: true,
          status: email.status
        });
      } else {
        // Generate new email if not found
        const data = await emailsApi.generate(selectedLeadId, emailType, false);
        setResult(data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to get email');
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!selectedLeadId) return;

    setLoading(true);
    setError(null);

    try {
      const data = await emailsApi.send(selectedLeadId, emailType);
      setResult({ ...result, sendResult: data });
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to send email');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>View & Send Email</h2>
      <p style={{ color: '#666', marginBottom: '20px', fontSize: '14px' }}>
        <strong>Note:</strong> Emails are automatically generated when leads are scraped. 
        You can view and send them here.
      </p>
      
      <form onSubmit={handleViewEmail}>
        <div className="form-group">
          <label>Select Lead</label>
          <select
            value={selectedLeadId}
            onChange={(e) => setSelectedLeadId(e.target.value)}
            required
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="">-- Select a lead --</option>
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>
                {lead.first_name} {lead.last_name} - {lead.email} ({lead.company_name})
              </option>
            ))}
          </select>
        </div>

        <div className="form-group">
          <label>Email Type</label>
          <select
            value={emailType}
            onChange={(e) => setEmailType(e.target.value)}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd' }}
          >
            <option value="initial">Initial</option>
            <option value="followup_5day">5-Day Follow-up</option>
            <option value="followup_10day">10-Day Follow-up</option>
          </select>
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading || !selectedLeadId}>
          {loading ? 'Loading...' : 'View Email'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div style={{ marginTop: '20px' }}>
          <div className="success">
            <h3>Email {result.from_cache ? '(Auto-generated)' : 'Generated!'}</h3>
            <p><strong>Personalized:</strong> {result.is_personalized ? 'Yes' : 'No'}</p>
            <p><strong>Website Used:</strong> {result.company_website_used ? 'Yes' : 'No'}</p>
            
            <div style={{ marginTop: '15px' }}>
              <strong>Subject:</strong>
              <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '4px', marginTop: '5px' }}>
                {result.subject}
              </div>
            </div>

            <div style={{ marginTop: '15px' }}>
              <strong>Body:</strong>
              <div style={{ 
                padding: '10px', 
                background: '#f8f9fa', 
                borderRadius: '4px', 
                marginTop: '5px',
                whiteSpace: 'pre-wrap',
                maxHeight: '400px',
                overflow: 'auto'
              }}>
                {result.body}
              </div>
            </div>

            {!result.sendResult && result.status !== 'sent' && (
              <button 
                onClick={handleSend} 
                className="btn btn-success" 
                style={{ marginTop: '15px' }}
                disabled={loading}
              >
                {loading ? 'Sending...' : result.status === 'generated' ? 'Send Email' : 'Send Email'}
              </button>
            )}
            
            {result.status === 'sent' && !result.sendResult && (
              <div style={{ marginTop: '15px', padding: '10px', background: '#d4edda', borderRadius: '4px' }}>
                <strong>Email Already Sent</strong>
              </div>
            )}

            {result.sendResult && (
              <div style={{ marginTop: '15px', padding: '10px', background: '#d4edda', borderRadius: '4px' }}>
                <strong>Email Sent!</strong>
                <p>Message ID: {result.sendResult.message_id}</p>
                {result.sendResult.scheduled && (
                  <p>Scheduled for: {result.sendResult.scheduled_time}</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

