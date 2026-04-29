import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Save, Link as LinkIcon, Shield } from 'lucide-react';

export default function SettingsTab({ appUrl, setAppUrl, user }: any) {
  const [url, setUrl] = useState(appUrl);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('saas_gas_url', url);
    setAppUrl(url);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">System Settings</h1>
        <p className="text-sm text-slate-500">Configure your platform integration endpoints and view profile information.</p>
      </div>

      <div className="card-3d rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-slate-100">
          <div className="w-10 h-10 rounded-lg bg-natural-sage/10 flex items-center justify-center text-natural-sage">
            <LinkIcon className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-natural-charcoal">Backend Configuration</h2>
            <p className="text-sm text-slate-500">Link your central Google Sheet URL to power the dashboard via the backend service account.</p>
          </div>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-natural-charcoal mb-2">Google Sheet URL</label>
            <input 
              type="url" 
              value={url} 
              onChange={(e) => setUrl(e.target.value)} 
              placeholder="https://docs.google.com/spreadsheets/d/..."
              required
              className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage transition-all bg-slate-50/50"
            />
          </div>
          <button 
            type="submit" 
            className="flex items-center gap-2 px-6 py-3 bg-natural-sage text-white rounded-xl hover:bg-natural-sage/90 transition-all font-medium"
          >
            <Save className="w-4 h-4" />
            {saved ? "Saved Successfully" : "Save Configuration"}
          </button>
        </form>
      </div>

      <div className="card-3d rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-slate-100">
          <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center text-blue-600">
            <Shield className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-natural-charcoal">Security Identity</h2>
            <p className="text-sm text-slate-500">Your Firebase Authentication identity used for data isolation.</p>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-natural-charcoal mb-2">Display Email</label>
            <input 
              type="text" 
              value={user?.email || ''} 
              disabled
              className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 cursor-not-allowed"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-natural-charcoal mb-2">Unique Identifier (UID)</label>
            <input 
              type="text" 
              value={user?.uid || ''} 
              disabled
              className="w-full px-4 py-3 rounded-xl border border-slate-200 bg-slate-100 text-slate-500 cursor-not-allowed font-mono text-sm"
            />
            <p className="text-xs text-slate-400 mt-2">This UID secures your data on the backend. Only rows tagged with this UID are returned.</p>
          </div>
        </div>
      </div>
    </motion.div>
  );
}
