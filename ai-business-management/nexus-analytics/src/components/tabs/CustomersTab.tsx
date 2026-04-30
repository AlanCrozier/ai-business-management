import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Users, DollarSign, Loader2 } from 'lucide-react';
import { Bar, Doughnut } from 'react-chartjs-2';
import { KPICard } from '../KPICard';

export default function CustomersTab({ apiData, appUrl, user }: any) {
  const [formData, setFormData] = useState({ customer_id: '', age: '', city: '', membership_level: 'Standard', lifetime_value: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const customers = apiData?.customer || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!appUrl || !user) return;
    setIsSubmitting(true);
    try {
      // 1. Try to get Real ML Prediction
      let mlData = null;
      try {
        const mlRes = await fetch('http://127.0.0.1:8000/api/predict/clv', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            customer_id: formData.customer_id,
            age: parseInt(formData.age),
            city: formData.city,
            membership_level: formData.membership_level,
            lifetime_value: parseFloat(formData.lifetime_value)
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
          module_type: 'customer',
          data: {
              customer_id: formData.customer_id,
              age: parseInt(formData.age),
              city: formData.city,
              membership_level: formData.membership_level,
              lifetime_value: parseFloat(formData.lifetime_value),
              ...(mlData && { 
                 predicted_revenue: mlData.predicted_clv || mlData.predicted_value, 
                 predicted_profit: mlData.predicted_profit || (mlData.predicted_clv * 0.4), 
                 anomaly_flag: mlData.anomaly_flag || 1 
              })
          }
      };
      await fetch('http://127.0.0.1:8000/api/sheets/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setFormData({ customer_id: '', age: '', city: '', membership_level: 'Standard', lifetime_value: '' });
    } catch (err) {
      console.error("Failed to submit", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalCust = customers.length;
  const avgLtv = totalCust > 0 ? customers.reduce((sum: number, c: any) => sum + parseFloat(c.lifetime_value || 0), 0) / totalCust : 0;

  // Age Bins
  const ageBins: Record<string, number> = { "<20": 0, "20-30": 0, "31-40": 0, "41-50": 0, ">50": 0 };
  const memCounts: Record<string, number> = {};
  const cityCounts: Record<string, number> = {};

  customers.forEach((c: any) => {
    const age = parseInt(c.age || 0);
    if (age < 20) ageBins["<20"]++;
    else if (age <= 30) ageBins["20-30"]++;
    else if (age <= 40) ageBins["31-40"]++;
    else if (age <= 50) ageBins["41-50"]++;
    else ageBins[">50"]++;

    memCounts[c.membership_level] = (memCounts[c.membership_level] || 0) + 1;
    cityCounts[c.city] = (cityCounts[c.city] || 0) + 1;
  });

  const ageData = {
    labels: Object.keys(ageBins),
    datasets: [{ label: 'Customers', data: Object.values(ageBins), backgroundColor: '#8B9D83', borderRadius: 4 }]
  };

  const memData = {
    labels: Object.keys(memCounts),
    datasets: [{ data: Object.values(memCounts), backgroundColor: ['#C4A484', '#2D3436', '#A3B19B', '#D3C4B3'], borderWidth: 0 }]
  };

  const cityData = {
    labels: Object.keys(cityCounts).slice(0, 10),
    datasets: [{ label: 'Customers', data: Object.values(cityCounts).slice(0, 10), backgroundColor: '#2D3436', borderRadius: 4 }]
  };

  const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.03)' } } } };
  const doughnutOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, cutout: '75%' };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">Customers</h1>
        <p className="text-sm text-slate-500">Analyze demographics and lifetime value.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <KPICard title="Total Customers" value={totalCust} hideChange icon={Users} />
        <KPICard title="Avg Lifetime Value" value={avgLtv.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})} hideChange icon={DollarSign} unit="$" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Age Distribution</h2>
          <div className="h-[250px]"><Bar data={ageData} options={chartOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Membership Breakdown</h2>
          <div className="h-[250px] flex justify-center"><Doughnut data={memData} options={doughnutOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Customers by City</h2>
          <div className="h-[250px]"><Bar data={cityData} options={chartOptions} /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Add Customer Details</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" placeholder="Customer ID / Name" required value={formData.customer_id} onChange={e=>setFormData({...formData, customer_id: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="number" placeholder="Age" required min="1" value={formData.age} onChange={e=>setFormData({...formData, age: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="text" placeholder="City" required value={formData.city} onChange={e=>setFormData({...formData, city: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <select required value={formData.membership_level} onChange={e=>setFormData({...formData, membership_level: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage">
              <option value="Standard">Standard</option>
              <option value="Silver">Silver</option>
              <option value="Gold">Gold</option>
              <option value="Platinum">Platinum</option>
              <option value="VIP">VIP</option>
            </select>
            <input type="number" placeholder="Lifetime Spend ($)" required min="0" step="0.01" value={formData.lifetime_value} onChange={e=>setFormData({...formData, lifetime_value: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <button type="submit" disabled={isSubmitting} className="w-full py-2 bg-natural-sage text-white rounded-lg hover:bg-natural-sage/90 transition flex justify-center">
              {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Save Profile'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 card-3d rounded-2xl p-6 h-[400px] overflow-y-auto">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">High Value Customers</h2>
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">LTV</th>
                <th className="px-4 py-3">Level</th>
              </tr>
            </thead>
            <tbody>
              {[...customers].sort((a: any, b: any)=> parseFloat(b.lifetime_value||0) - parseFloat(a.lifetime_value||0)).slice(0, 20).map((c: any, i: number) => (
                <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{c.customer_id}</td>
                  <td className="px-4 py-3">${parseFloat(c.lifetime_value||0).toLocaleString()}</td>
                  <td className="px-4 py-3"><span className="px-2 py-1 bg-slate-100 rounded text-xs">{c.membership_level}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
