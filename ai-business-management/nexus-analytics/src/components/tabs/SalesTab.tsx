import React, { useState } from 'react';
import { motion } from 'motion/react';
import { TrendingUp, Package, Loader2 } from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { KPICard } from '../KPICard';

export default function SalesTab({ apiData, appUrl, user }: any) {
  const [formData, setFormData] = useState({ product_id: '', region: 'North', units_sold: '', revenue: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const sales = apiData?.sales || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!appUrl || !user) return;
    setIsSubmitting(true);
    try {
      // 1. Try to get Real ML Prediction
      let mlData = null;
      try {
        const mlRes = await fetch('http://127.0.0.1:8000/api/predict/revenue', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            product_id: formData.product_id,
            region: formData.region,
            units_sold: parseInt(formData.units_sold),
            revenue: parseFloat(formData.revenue)
          })
        });
        const mlResJson = await mlRes.json();
        if (mlResJson.success) mlData = mlResJson.data;
      } catch (err) {
        console.warn("FastAPI ML backend unavailable. Falling back to GAS Mock AI.");
      }

      // 2. Save to Central DB (GAS)
      const payload = {
          uid: user.uid,
          sheet_url: appUrl,
          module_type: 'sales',
          data: {
              product_id: formData.product_id,
              region: formData.region,
              units_sold: parseInt(formData.units_sold),
              revenue: parseFloat(formData.revenue),
              ...(mlData && { 
                 predicted_revenue: mlData.predicted_revenue || mlData.predicted_value, 
                 predicted_profit: mlData.predicted_profit || (mlData.predicted_value * 0.35), 
                 anomaly_flag: mlData.anomaly_flag || 1 
              })
          }
      };
      await fetch('http://127.0.0.1:8000/api/sheets/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setFormData({ product_id: '', region: 'North', units_sold: '', revenue: '' });
    } catch (err) {
      console.error("Failed to submit", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalRev = sales.reduce((sum: number, s: any) => sum + parseFloat(s.revenue || 0), 0);
  const totalUnits = sales.reduce((sum: number, s: any) => sum + parseInt(s.units_sold || 0), 0);

  const revByDate: Record<string, number> = {};
  const revByRegion: Record<string, number> = {};
  const unitsByProd: Record<string, number> = {};

  const sortedSales = [...sales].sort((a: any, b: any) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  
  sortedSales.forEach((s: any) => {
    const d = new Date(s.timestamp).toLocaleDateString();
    const r = parseFloat(s.revenue || 0);
    const u = parseInt(s.units_sold || 0);
    revByDate[d] = (revByDate[d] || 0) + r;
    revByRegion[s.region] = (revByRegion[s.region] || 0) + r;
    unitsByProd[s.product_id] = (unitsByProd[s.product_id] || 0) + u;
  });

  const lineData = {
    labels: Object.keys(revByDate),
    datasets: [{ label: 'Revenue ($)', data: Object.values(revByDate), borderColor: '#8B9D83', backgroundColor: 'rgba(139, 157, 131, 0.1)', fill: true, tension: 0.4 }]
  };
  
  const regionData = {
    labels: Object.keys(revByRegion),
    datasets: [{ label: 'Revenue', data: Object.values(revByRegion), backgroundColor: '#2D3436', borderRadius: 4 }]
  };

  const productData = {
    labels: Object.keys(unitsByProd).slice(0, 10),
    datasets: [{ label: 'Units Sold', data: Object.values(unitsByProd).slice(0, 10), backgroundColor: '#C4A484', borderRadius: 4 }]
  };

  const pieData = {
    labels: Object.keys(revByRegion),
    datasets: [{ data: Object.values(revByRegion), backgroundColor: ['#8B9D83', '#C4A484', '#2D3436', '#A3B19B', '#D3C4B3'], borderWidth: 0 }]
  };

  const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.03)' } } } };
  const doughnutOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, cutout: '75%' };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">Sales HQ</h1>
        <p className="text-sm text-slate-500">Track regional performance, product output, and revenue streams.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <KPICard title="Total Tracked Revenue" value={totalRev.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})} hideChange icon={TrendingUp} unit="$" />
        <KPICard title="Total Units Sold" value={totalUnits.toLocaleString()} hideChange icon={Package} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Revenue Trend</h2>
          <div className="h-[250px]"><Line data={lineData} options={chartOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Revenue by Region</h2>
          <div className="h-[250px]"><Bar data={regionData} options={chartOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Top Products (Units)</h2>
          <div className="h-[250px]"><Bar data={productData} options={chartOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Sales Distribution</h2>
          <div className="h-[250px] flex justify-center"><Doughnut data={pieData} options={doughnutOptions} /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Record New Sale</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" placeholder="Product ID / Name" required value={formData.product_id} onChange={e=>setFormData({...formData, product_id: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <select required value={formData.region} onChange={e=>setFormData({...formData, region: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage">
              <option value="North">North</option><option value="South">South</option><option value="East">East</option><option value="West">West</option>
            </select>
            <input type="number" placeholder="Units Sold" required min="1" value={formData.units_sold} onChange={e=>setFormData({...formData, units_sold: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="number" placeholder="Total Revenue" required min="0" step="0.01" value={formData.revenue} onChange={e=>setFormData({...formData, revenue: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <button type="submit" disabled={isSubmitting} className="w-full py-2 bg-natural-sage text-white rounded-lg hover:bg-natural-sage/90 transition flex justify-center">
              {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Process Sale'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 card-3d rounded-2xl p-6 h-[400px] overflow-y-auto">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Recent Sales</h2>
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0">
              <tr>
                <th className="px-4 py-3">Date</th><th className="px-4 py-3">Product</th>
                <th className="px-4 py-3">Region</th><th className="px-4 py-3">Units</th>
                <th className="px-4 py-3">Revenue</th>
              </tr>
            </thead>
            <tbody>
              {sortedSales.reverse().slice(0, 50).map((s: any, i: number) => (
                <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3">{new Date(s.timestamp).toLocaleDateString()}</td>
                  <td className="px-4 py-3 font-medium">{s.product_id}</td>
                  <td className="px-4 py-3">{s.region}</td>
                  <td className="px-4 py-3">{s.units_sold}</td>
                  <td className="px-4 py-3">${parseFloat(s.revenue||0).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
