import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { Save, Link as LinkIcon, Shield, Upload, CheckCircle, XCircle, Trash2, Loader2, KeyRound } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function SettingsTab({ appUrl, setAppUrl, user }: any) {
  const [url, setUrl] = useState(appUrl);
  const [saved, setSaved] = useState(false);

  // SA Upload state
  const [saStatus, setSaStatus] = useState<any>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [statusLoading, setStatusLoading] = useState(true);

  // Fetch SA status on mount
  useEffect(() => {
    if (!user?.uid) return;
    setStatusLoading(true);
    fetch(`${API}/api/accounts/status/${user.uid}`)
      .then(r => r.json())
      .then(data => setSaStatus(data))
      .catch(() => setSaStatus(null))
      .finally(() => setStatusLoading(false));
  }, [user?.uid]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();

    // 1. Save to localStorage immediately
    localStorage.setItem('saas_gas_url', url);

    // 2. Show visual feedback right away
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);

    // 3. Persist to backend (non-blocking)
    if (user?.uid) {
      try {
        await fetch(`${API}/api/accounts/sheet-url`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: user.uid, sheet_url: url })
        });
      } catch (err) {
        console.warn('Failed to persist sheet URL to backend:', err);
      }
    }

    // 4. Update parent state last (triggers dashboard data fetch)
    setTimeout(() => setAppUrl(url), 500);
  };

  const handleSAUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user?.uid) return;

    try {
      const text = await file.text();
      const saJson = JSON.parse(text);

      // Client-side validation
      if (saJson.type !== 'service_account') {
        alert('Invalid file: must be a Google Cloud Service Account JSON (type: "service_account").');
        return;
      }
      if (!saJson.private_key || !saJson.client_email) {
        alert('Invalid file: missing private_key or client_email fields.');
        return;
      }

      setIsUploading(true);

      const res = await fetch(`${API}/api/accounts/upload-sa`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          uid: user.uid,
          email: user.email,
          display_name: user.displayName,
          service_account_json: saJson,
        })
      });
      const result = await res.json();

      if (res.ok && result.success) {
        setSaStatus({
          ...saStatus,
          sa_configured: true,
          sa_project_id: result.sa_project_id,
          sa_client_email: result.sa_client_email,
        });
      } else {
        alert(result.detail || 'Upload failed.');
      }
    } catch (err) {
      alert('Failed to read or upload the file. Ensure it is a valid JSON file.');
    } finally {
      setIsUploading(false);
      // Reset file input
      e.target.value = '';
    }
  };

  const handleSADelete = async () => {
    if (!user?.uid) return;
    if (!confirm('Remove your service account? The backend will no longer be able to access your Google Sheets.')) return;

    setIsDeleting(true);
    try {
      await fetch(`${API}/api/accounts/${user.uid}`, { method: 'DELETE' });
      setSaStatus({ ...saStatus, sa_configured: false, sa_project_id: null, sa_client_email: null });
    } catch (err) {
      alert('Failed to remove service account.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">System Settings</h1>
        <p className="text-sm text-slate-500">Configure your platform integration endpoints, service account, and view profile information.</p>
      </div>

      {/* ── Service Account Upload ─────────────────────────────────────── */}
      <div className="card-3d rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-slate-100">
          <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center text-amber-600">
            <KeyRound className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-natural-charcoal">Service Account</h2>
            <p className="text-sm text-slate-500">Upload your Google Cloud service account JSON to enable Sheets integration.</p>
          </div>
        </div>

        {statusLoading ? (
          <div className="flex items-center gap-2 text-sm text-slate-400">
            <Loader2 className="w-4 h-4 animate-spin" /> Checking status...
          </div>
        ) : saStatus?.sa_configured ? (
          <div className="space-y-4">
            {/* Status: Configured */}
            <div className="flex items-center gap-3 p-4 bg-emerald-50 rounded-xl border border-emerald-200">
              <CheckCircle className="w-5 h-5 text-emerald-600 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-emerald-800">Service Account Configured</p>
                <p className="text-xs text-emerald-600 truncate mt-0.5">
                  {saStatus.sa_client_email || 'Encrypted & stored securely'}
                </p>
                {saStatus.sa_project_id && (
                  <p className="text-xs text-emerald-500 mt-0.5">
                    Project: {saStatus.sa_project_id}
                  </p>
                )}
              </div>
              <button
                onClick={handleSADelete}
                disabled={isDeleting}
                className="p-2 text-red-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                title="Remove service account"
              >
                {isDeleting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              </button>
            </div>

            {/* Replace SA */}
            <div className="flex items-center gap-3">
              <label className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-slate-600 border border-slate-200 rounded-xl cursor-pointer hover:bg-slate-50 transition-colors">
                <Upload className="w-4 h-4" />
                Replace Service Account
                <input type="file" accept=".json" onChange={handleSAUpload} className="hidden" />
              </label>
              {isUploading && <Loader2 className="w-4 h-4 animate-spin text-natural-sage" />}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {/* Status: Not Configured */}
            <div className="flex items-center gap-3 p-4 bg-amber-50 rounded-xl border border-amber-200">
              <XCircle className="w-5 h-5 text-amber-600 flex-shrink-0" />
              <div>
                <p className="text-sm font-semibold text-amber-800">No Service Account Configured</p>
                <p className="text-xs text-amber-600 mt-0.5">Upload your Google Cloud service account JSON to enable Sheets sync.</p>
              </div>
            </div>

            <label className={`
              flex flex-col items-center justify-center gap-3 p-8 rounded-xl border-2 border-dashed
              border-slate-200 hover:border-natural-sage/50 hover:bg-natural-sage/5
              cursor-pointer transition-all group
            `}>
              <div className="w-14 h-14 rounded-2xl bg-slate-100 group-hover:bg-natural-sage/10 flex items-center justify-center transition-colors">
                <Upload className="w-6 h-6 text-slate-400 group-hover:text-natural-sage transition-colors" />
              </div>
              <div className="text-center">
                <p className="text-sm font-medium text-natural-charcoal">
                  {isUploading ? 'Uploading...' : 'Click to upload service_account.json'}
                </p>
                <p className="text-xs text-slate-400 mt-1">Your private key is encrypted before storage</p>
              </div>
              <input type="file" accept=".json" onChange={handleSAUpload} className="hidden" disabled={isUploading} />
            </label>
          </div>
        )}
      </div>

      {/* ── Backend Configuration (Sheet URL) ─────────────────────────── */}
      <div className="card-3d rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6 pb-6 border-b border-slate-100">
          <div className="w-10 h-10 rounded-lg bg-natural-sage/10 flex items-center justify-center text-natural-sage">
            <LinkIcon className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-natural-charcoal">Backend Configuration</h2>
            <p className="text-sm text-slate-500">Link your central Google Sheet URL to power the dashboard.</p>
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
            {saStatus?.sa_client_email && (
              <p className="text-xs text-slate-400 mt-2">
                ⚠️ Make sure this sheet is shared with: <span className="font-mono text-natural-sage">{saStatus.sa_client_email}</span>
              </p>
            )}
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

      {/* ── Security Identity ─────────────────────────────────────────── */}
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
