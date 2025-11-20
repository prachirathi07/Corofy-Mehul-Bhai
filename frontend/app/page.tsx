'use client';

import { useState } from 'react';
import LeadScraping from '@/components/LeadScraping';
import LeadsList from '@/components/LeadsList';
import WebsiteScraping from '@/components/WebsiteScraping';
import EmailGeneration from '@/components/EmailGeneration';
import EmailQueue from '@/components/EmailQueue';
import SentEmails from '@/components/SentEmails';
import FollowUps from '@/components/FollowUps';

export default function Home() {
  const [activeTab, setActiveTab] = useState('scrape');

  const tabs = [
    { id: 'scrape', label: 'Scrape Leads' },
    { id: 'leads', label: 'View Leads' },
    { id: 'websites', label: 'Scrape Websites (Optional)' },
    { id: 'emails', label: 'View & Send Emails' },
    { id: 'queue', label: 'Email Queue' },
    { id: 'sent', label: 'Sent Emails' },
    { id: 'followups', label: 'Follow-ups' },
  ];

  return (
    <div className="container">
      <header style={{ marginBottom: '30px', padding: '20px 0', borderBottom: '2px solid #0070f3' }}>
        <h1 style={{ fontSize: '32px', color: '#0070f3', marginBottom: '10px' }}>
          Lead Automation System
        </h1>
        <p style={{ color: '#666' }}>Test your lead scraping and email automation system</p>
      </header>

      <div className="tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      <div>
        {activeTab === 'scrape' && <LeadScraping />}
        {activeTab === 'leads' && <LeadsList />}
        {activeTab === 'websites' && <WebsiteScraping />}
        {activeTab === 'emails' && <EmailGeneration />}
        {activeTab === 'queue' && <EmailQueue />}
        {activeTab === 'sent' && <SentEmails />}
        {activeTab === 'followups' && <FollowUps />}
      </div>
    </div>
  );
}

