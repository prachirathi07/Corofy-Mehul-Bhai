'use client';

import { useState } from 'react';
import { websitesApi } from '@/lib/api';

export default function WebsiteScraping() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [companyDomain, setCompanyDomain] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await websitesApi.scrape(
        companyDomain,
        companyWebsite || undefined
      );
      setResult(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to scrape website');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Scrape Company Website (Optional)</h2>
      <p style={{ color: '#666', marginBottom: '20px', fontSize: '14px' }}>
        <strong>Note:</strong> Websites are automatically scraped when leads are scraped. 
        Use this only if you want to manually scrape a specific website.
      </p>
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Company Domain (e.g., example.com or https://example.com)</label>
          <input
            type="text"
            value={companyDomain}
            onChange={(e) => setCompanyDomain(e.target.value)}
            placeholder="example.com"
            required
          />
        </div>

        <div className="form-group">
          <label>Company Website URL (optional)</label>
          <input
            type="text"
            value={companyWebsite}
            onChange={(e) => setCompanyWebsite(e.target.value)}
            placeholder="https://example.com"
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Scraping...' : 'Scrape Website'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}
      
      {result && (
        <div style={{ marginTop: '20px' }}>
          {result.success ? (
            <div className="success">
              <h3>Website Scraped Successfully!</h3>
              <p><strong>Domain:</strong> {result.domain}</p>
              <p><strong>URL:</strong> {result.url}</p>
              <p><strong>From Cache:</strong> {result.from_cache ? 'Yes' : 'No'}</p>
              <p><strong>Content Length:</strong> {result.markdown?.length || 0} characters</p>
              {result.markdown && (
                <div style={{ marginTop: '15px' }}>
                  <strong>Content Preview:</strong>
                  <div style={{ 
                    marginTop: '10px', 
                    padding: '10px', 
                    background: '#f8f9fa', 
                    borderRadius: '4px',
                    maxHeight: '300px',
                    overflow: 'auto',
                    fontSize: '12px'
                  }}>
                    {result.markdown.substring(0, 1000)}...
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="error">
              <h3>Scraping Failed</h3>
              <p>{result.error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

