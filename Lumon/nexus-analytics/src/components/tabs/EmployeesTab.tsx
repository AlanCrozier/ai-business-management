import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Briefcase, Activity, Loader2 } from 'lucide-react';
import { Bar, Scatter } from 'react-chartjs-2';
import { KPICard } from '../KPICard';

export default function EmployeesTab({ apiData, appUrl, user, chartOptions }: any) {
  const [formData, setFormData] = useState({ employee_id: '', role: '', years_worked: '', attendance_percent: '', performance_score: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const employees = apiData?.employee || [];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!appUrl || !user) return;
    setIsSubmitting(true);
    try {
      // 1. Try to get Real ML Prediction
      let mlData = null;
      try {
        const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
        const mlRes = await fetch(`${API}/api/predict/employee`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            employee_id: formData.employee_id,
            role: formData.role,
            years_worked: parseInt(formData.years_worked),
            attendance_percent: parseFloat(formData.attendance_percent),
            performance_score: parseFloat(formData.performance_score)
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
          module_type: 'employee',
          data: {
              employee_id: formData.employee_id,
              role: formData.role,
              years_worked: parseInt(formData.years_worked),
              attendance_percent: parseFloat(formData.attendance_percent),
              performance_score: parseFloat(formData.performance_score),
              ...(mlData && { 
                 predicted_revenue: mlData.predicted_impact || mlData.predicted_value, 
                 predicted_profit: mlData.predicted_profit || (mlData.predicted_impact * 0.2), 
                 anomaly_flag: mlData.anomaly_flag || 1 
              })
          }
      };
      const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
      await fetch(`${API}/api/sheets/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      setFormData({ employee_id: '', role: '', years_worked: '', attendance_percent: '', performance_score: '' });
    } catch (err) {
      console.error("Failed to submit", err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const totalEmp = employees.length;
  const avgPerf = totalEmp > 0 ? employees.reduce((sum: number, e: any) => sum + parseFloat(e.performance_score || 0), 0) / totalEmp : 0;
  const avgAtt = totalEmp > 0 ? employees.reduce((sum: number, e: any) => sum + parseFloat(e.attendance_percent || 0), 0) / totalEmp : 0;

  const roleAtt: Record<string, number[]> = {};
  const rolePerf: Record<string, number[]> = {};

  employees.forEach((e: any) => {
    const role = e.job_level || e.role || "General";
    if (!roleAtt[role]) roleAtt[role] = [];
    if (!rolePerf[role]) rolePerf[role] = [];
    
    roleAtt[role].push(parseFloat(e.attendance_percent || 0));
    rolePerf[role].push(parseFloat(e.performance_score || 0));
  });

  const avgRoleAtt = Object.keys(roleAtt).reduce((acc, role) => {
    acc[role] = roleAtt[role].reduce((a,b)=>a+b,0) / roleAtt[role].length;
    return acc;
  }, {} as Record<string, number>);

  const avgRolePerf = Object.keys(rolePerf).reduce((acc, role) => {
    acc[role] = rolePerf[role].reduce((a,b)=>a+b,0) / rolePerf[role].length;
    return acc;
  }, {} as Record<string, number>);

  const attendanceData = {
    labels: Object.keys(avgRoleAtt),
    datasets: [{ label: 'Avg Attendance (%)', data: Object.values(avgRoleAtt), backgroundColor: '#C4A484', borderRadius: 4 }]
  };

  const perfRoleData = {
    labels: Object.keys(avgRolePerf),
    datasets: [{ label: 'Avg Performance', data: Object.values(avgRolePerf), backgroundColor: '#8B9D83', borderRadius: 4 }]
  };

  const scatterData = {
    datasets: [{
      label: 'Performance vs Years',
      data: employees.map((e: any) => ({ x: parseFloat(e.years_worked || 0), y: parseFloat(e.performance_score || 0) })),
      backgroundColor: '#2D3436',
      pointRadius: 4
    }]
  };

  const localChartOptions = chartOptions || { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { x: { grid: { display: false } }, y: { grid: { color: 'rgba(0,0,0,0.03)' } } } };

  const scatterOptions = {
    ...localChartOptions,
    scales: {
      x: { title: { display: true, text: 'Years Worked' }, grid: { display: false } },
      y: { title: { display: true, text: 'Performance Score' }, grid: { color: 'rgba(0,0,0,0.03)' } }
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">Employees</h1>
        <p className="text-sm text-slate-500">Track performance, attendance, and role analytics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <KPICard title="Avg Performance Score" value={avgPerf.toFixed(1)} hideChange icon={Briefcase} unit="%" />
        <KPICard title="Avg Attendance" value={avgAtt.toFixed(1)} hideChange icon={Activity} unit="%" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Attendance Analysis</h2>
          <div className="h-[250px]"><Bar data={attendanceData} options={localChartOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Performance vs Experience</h2>
          <div className="h-[250px]"><Scatter data={scatterData} options={scatterOptions} /></div>
        </div>
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Role-wise Performance</h2>
          <div className="h-[250px]"><Bar data={perfRoleData} options={localChartOptions} /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card-3d rounded-2xl p-6">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Employee Metrics</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <input type="text" placeholder="Employee ID" required value={formData.employee_id} onChange={e=>setFormData({...formData, employee_id: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="text" placeholder="Role (e.g., Senior)" required value={formData.role} onChange={e=>setFormData({...formData, role: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="number" placeholder="Years Worked" required min="0" value={formData.years_worked} onChange={e=>setFormData({...formData, years_worked: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="number" placeholder="Attendance (%)" required min="0" max="100" value={formData.attendance_percent} onChange={e=>setFormData({...formData, attendance_percent: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <input type="number" placeholder="Performance Score (0-100)" required min="0" max="100" value={formData.performance_score} onChange={e=>setFormData({...formData, performance_score: e.target.value})} className="w-full px-4 py-2 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-natural-sage" />
            <button type="submit" disabled={isSubmitting} className="w-full py-2 bg-natural-sage text-white rounded-lg hover:bg-natural-sage/90 transition flex justify-center">
              {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Update Metric'}
            </button>
          </form>
        </div>

        <div className="lg:col-span-2 card-3d rounded-2xl p-6 h-[400px] overflow-y-auto">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Top Employees</h2>
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-slate-500 uppercase bg-slate-50 sticky top-0">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Performance</th>
              </tr>
            </thead>
            <tbody>
              {[...employees].sort((a: any, b: any)=> parseFloat(b.performance_score||0) - parseFloat(a.performance_score||0)).slice(0, 20).map((e: any, i: number) => (
                <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium">{e.employee_id}</td>
                  <td className="px-4 py-3">{e.job_level || e.role}</td>
                  <td className="px-4 py-3"><span className="px-2 py-1 bg-slate-100 rounded text-xs">{Number(e.performance_score||0).toFixed(1)}%</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  );
}
