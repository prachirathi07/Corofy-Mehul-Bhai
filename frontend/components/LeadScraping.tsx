'use client';

import { useState } from 'react';
import { leadsApi } from '@/lib/api';

export default function LeadScraping() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  
  const [formData, setFormData] = useState({
    source: 'apify', // 'apollo' or 'apify'
    countries: '',
    c_suites: '',
    employee_size_min: '',
    employee_size_max: '',
    industry: '',
    total_leads_wanted: '10',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params: any = {
        source: formData.source,
        total_leads_wanted: parseInt(formData.total_leads_wanted) || 10,
      };

      if (formData.countries) {
        params.countries = formData.countries.split(',').map(c => c.trim()).filter(c => c);
      }
      if (formData.c_suites) {
        params.c_suites = formData.c_suites.split(',').map(c => c.trim()).filter(c => c);
      }
      if (formData.employee_size_min) {
        params.employee_size_min = parseInt(formData.employee_size_min);
      }
      if (formData.employee_size_max) {
        params.employee_size_max = parseInt(formData.employee_size_max);
      }
      if (formData.industry) {
        params.industry = formData.industry;
      }

      const data = await leadsApi.scrape(params);
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to scrape leads');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Scrape Leads</h2>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Data Source</label>
          <select
            value={formData.source}
            onChange={(e) => setFormData({ ...formData, source: e.target.value })}
            style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ddd', width: '100%' }}
          >
            <option value="apollo">Apollo</option>
            <option value="apify">Apify</option>
          </select>
        </div>

        <div className="form-group">
          <label>Countries (comma-separated, e.g., India, United States)</label>
          <input
            type="text"
            value={formData.countries}
            onChange={(e) => setFormData({ ...formData, countries: e.target.value })}
            placeholder="India, United States"
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>C-Suites (comma-separated, e.g., CEO,COO)</label>
            <input
              type="text"
              value={formData.c_suites}
              onChange={(e) => setFormData({ ...formData, c_suites: e.target.value })}
              placeholder="CEO, COO, Director"
            />
          </div>
          <div className="form-group">
            <label>Industry</label>
            <input
              type="text"
              value={formData.industry}
              onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
              placeholder="Technology"
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Employee Size Min</label>
            <input
              type="number"
              value={formData.employee_size_min}
              onChange={(e) => setFormData({ ...formData, employee_size_min: e.target.value })}
              placeholder="1"
            />
          </div>
          <div className="form-group">
            <label>Employee Size Max</label>
            <input
              type="number"
              value={formData.employee_size_max}
              onChange={(e) => setFormData({ ...formData, employee_size_max: e.target.value })}
              placeholder="500"
            />
          </div>
        </div>

        <div className="form-group">
          <label>Total Leads Wanted</label>
          <input
            type="number"
            value={formData.total_leads_wanted}
            onChange={(e) => setFormData({ ...formData, total_leads_wanted: e.target.value })}
            required
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Leads'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div className="success" style={{ marginTop: '20px' }}>
          <h3>Scraping Complete!</h3>
          <p><strong>Search ID:</strong> {result.search_id}</p>
          <p><strong>Total Leads Found:</strong> {result.total_leads_found}</p>
          <p><strong>Target Leads:</strong> {result.target_leads}</p>
          
          <div style={{ 
            marginTop: '15px', 
            padding: '12px', 
            background: '#e7f3ff', 
            borderRadius: '4px',
            border: '1px solid #b3d9ff'
          }}>
            <strong>🔄 Automatic Processing Started:</strong>
            <ul style={{ marginTop: '8px', paddingLeft: '20px', marginBottom: '0' }}>
              <li>Website scraping in progress for each company</li>
              <li>Email generation in progress using OpenAI</li>
              <li>Emails will be stored automatically</li>
            </ul>
            <p style={{ marginTop: '10px', marginBottom: '0', fontSize: '13px', color: '#666' }}>
              Check "View & Send Email" tab in a few minutes to see generated emails
            </p>
          </div>
          
          {result.leads && result.leads.length > 0 && (
            <div style={{ marginTop: '15px' }}>
              <strong>Sample Leads:</strong>
              <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
                {result.leads.slice(0, 5).map((lead: any, idx: number) => (
                  <li key={idx} style={{ marginBottom: '5px' }}>
                    {lead.first_name} {lead.last_name} - {lead.email} ({lead.company_name})
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

