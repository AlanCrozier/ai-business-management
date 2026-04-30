import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Database, Link as LinkIcon, CheckCircle, AlertCircle, Loader2, RefreshCw } from 'lucide-react';


export default function DataSourcesTab({ apiData, appUrl, user }: any) {
  const [sheetUrl, setSheetUrl] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);

  const handleConnect = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sheetUrl || !appUrl || !user) return;
    setIsConnecting(true);
    try {
      await fetch('http://127.0.0.1:8000/api/sheets/connect', { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: user.uid, sheet_url: sheetUrl })
      });
      setSheetUrl('');
    } catch(err) {
      console.error(err);
    } finally {
      setIsConnecting(false);
    }
  };

  const ext = apiData?.external;
  const isConnected = ext?.status === 'connected';
  const isError = ext?.status === 'error';

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">Data Sources</h1>
        <p className="text-sm text-slate-500">Connect external integrations like Google Sheets to pipe data directly into the AI engine.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center text-emerald-600">
                <Database className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-semibold text-natural-charcoal">Google Sheets Integration</h2>
            </div>
            {isConnected && <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-md flex items-center gap-1"><CheckCircle className="w-3 h-3"/> Active</span>}
            {isError && <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-md flex items-center gap-1"><AlertCircle className="w-3 h-3"/> Error</span>}
            {!isConnected && !isError && <span className="px-2 py-1 bg-slate-100 text-slate-500 text-xs font-semibold rounded-md">Not Connected</span>}
          </div>

          <form onSubmit={handleConnect} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-natural-charcoal mb-2">Public Sheet URL</label>
              <input 
                type="url" 
                value={sheetUrl} 
                onChange={(e) => setSheetUrl(e.target.value)} 
                placeholder="https://docs.google.com/spreadsheets/d/..."
                required
                className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage transition-all bg-slate-50/50"
              />
              <p className="text-xs text-slate-400 mt-2">Ensure the sheet has "Anyone with link" viewer access.</p>
            </div>
            <button 
              type="submit" 
              disabled={isConnecting}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-natural-sage text-white rounded-xl hover:bg-natural-sage/90 transition-all font-medium disabled:opacity-50"
            >
              {isConnecting ? <Loader2 className="w-4 h-4 animate-spin" /> : <LinkIcon className="w-4 h-4" />}
              {isConnecting ? "Connecting..." : "Sync Sheet"}
            </button>
          </form>
        </div>

        {ext && ext.status !== 'not_connected' && (
          <div className="card-3d rounded-2xl p-6 flex flex-col justify-center">
            <h3 className="text-sm font-medium text-slate-500 mb-4">Current Sync Status</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Source Name</span>
                <span className="font-medium text-natural-charcoal">{ext.sheet_name || (isError ? ext.error : 'Loading...')}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Rows Ingested</span>
                <span className="font-medium text-natural-charcoal">{ext.total_rows || 0}</span>
              </div>
              <div className="flex justify-between items-center py-2 border-b border-slate-100">
                <span className="text-sm text-slate-500">Computed Revenue</span>
                <span className="font-medium text-natural-sage">${(ext.computed_external_revenue || 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between items-center py-2">
                <span className="text-sm text-slate-500">Last Synced</span>
                <span className="font-medium text-natural-charcoal flex items-center gap-1">
                  <RefreshCw className="w-3 h-3 text-emerald-500" /> Real-time
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
