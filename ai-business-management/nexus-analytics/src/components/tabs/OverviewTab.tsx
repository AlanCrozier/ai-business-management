
import { motion } from 'motion/react';
import { Activity, Users, Target, Zap } from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { KPICard } from '../KPICard';

export default function OverviewTab({ apiData }: any) {
  if (!apiData || !apiData.dashboardSummary) return null;
  const summary = apiData.dashboardSummary;

  // Compute Revenue Trajectory
  const sales = apiData.sales || [];
  const revByDate: Record<string, number> = {};
  
  // Sort sales by date ascending
  const sortedSales = [...sales].sort((a: any, b: any) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime());
  
  sortedSales.forEach((s: any) => {
    const d = new Date(s.timestamp).toLocaleDateString();
    revByDate[d] = (revByDate[d] || 0) + parseFloat(s.revenue || 0);
  });
  
  const lineChartData = {
    labels: Object.keys(revByDate),
    datasets: [{
      label: 'Revenue Trajectory',
      data: Object.values(revByDate),
      borderColor: '#8B9D83',
      backgroundColor: 'rgba(139, 157, 131, 0.1)',
      fill: true,
      tension: 0.4,
      borderWidth: 2,
      pointRadius: 0
    }]
  };

  // Compute Customer Distribution
  const custs = apiData.customer || [];
  let p = 0, g = 0, s = 0;
  custs.forEach((c: any) => {
      if (c.membership_level === 'Platinum') p++;
      else if (c.membership_level === 'Gold') g++;
      else if (c.membership_level === 'Silver') s++;
  });
  const doughnutData = {
    labels: ['Platinum', 'Gold', 'Silver'],
    datasets: [{
      data: [p, g, s],
      backgroundColor: ['#8B9D83', '#C4A484', '#2D3436'],
      borderWidth: 0
    }]
  };
  const totalCusts = p + g + s;

  // Compute Quarterly Sales
  let q1=0, q2=0, q3=0, q4=0;
  sales.forEach((sale: any) => {
      const month = new Date(sale.timestamp).getMonth();
      const rev = parseFloat(sale.revenue || 0);
      if (month < 3) q1 += rev;
      else if (month < 6) q2 += rev;
      else if (month < 9) q3 += rev;
      else q4 += rev;
  });
  const barChartData = {
    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
    datasets: [{
      label: 'Sales HQ (Quarterly)',
      data: [q1, q2, q3, q4],
      backgroundColor: '#2D3436',
      borderRadius: 6
    }]
  };

  const chartOptions = { 
    responsive: true, 
    maintainAspectRatio: false, 
    plugins: { legend: { display: false } }, 
    scales: { 
      x: { grid: { display: false } }, 
      y: { grid: { color: 'rgba(0,0,0,0.03)' }, border: { display: false } } 
    } 
  };
  
  const doughnutOptions = { 
    responsive: true, 
    maintainAspectRatio: false, 
    plugins: { legend: { display: false } }, 
    cutout: '75%' 
  };

  // Internal vs External Revenue combination
  let internalRev = parseFloat(summary.totalRevenue || 0);
  let externalRev = apiData.external && apiData.external.status === 'connected' ? parseFloat(apiData.external.computed_external_revenue || 0) : 0;
  const grandTotalRev = internalRev + externalRev;
  const totalProfit = grandTotalRev * 0.35; // Simulated profit

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="max-w-7xl mx-auto space-y-8"
    >
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">Executive Dashboard</h1>
        <p className="text-sm text-slate-500">Welcome back. Overall Health Score: <span className="font-semibold text-natural-sage">92/100</span></p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard 
          title="Total Global Revenue"
          value={grandTotalRev.toLocaleString(undefined, { maximumFractionDigits: 0 })} 
          change={12.4} 
          isPositive={true} 
          icon={Activity} 
          unit="$"
        />
        <KPICard 
          title="Total Customers"
          value={totalCusts.toLocaleString()} 
          change={5.2} 
          isPositive={true} 
          icon={Users} 
          unit=""
        />
        <KPICard 
          title="Avg Employee Perf"
          value="4.2" 
          change={1.1} 
          isPositive={true} 
          icon={Target} 
          unit="/5"
        />
        <KPICard 
          title="Projected Profit"
          value={totalProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })} 
          change={8.9} 
          isPositive={true} 
          icon={Zap} 
          unit="$"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 card-3d rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-natural-charcoal">Revenue Trajectory</h2>
            <select className="text-sm border-none bg-slate-50 rounded-md px-3 py-1.5 focus:ring-0 cursor-pointer outline-none">
              <option>This Year</option>
            </select>
          </div>
          <div className="h-[300px]">
            <Line data={lineChartData} options={chartOptions} />
          </div>
        </div>

        <div className="card-3d rounded-2xl p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-natural-charcoal">Client Distribution</h2>
          </div>
          <div className="h-[240px] flex items-center justify-center relative">
            <Doughnut data={doughnutData} options={doughnutOptions} />
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-3xl font-bold text-natural-charcoal">
                {totalCusts}
              </span>
              <span className="text-xs text-slate-400 font-medium">Total</span>
            </div>
          </div>
          <div className="mt-6 space-y-3">
            {doughnutData.labels.map((label: string, i: number) => {
              const percent = totalCusts > 0 ? Math.round((doughnutData.datasets[0].data[i] / totalCusts) * 100) : 0;
              return (
                <div key={label} className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: doughnutData.datasets[0].backgroundColor[i] }} />
                    <span className="text-slate-600 font-medium">{label}</span>
                  </div>
                  <span className="font-semibold text-natural-charcoal">{percent}%</span>
                </div>
              )
            })}
          </div>
        </div>

        <div className="lg:col-span-3 card-3d rounded-2xl p-6">
           <div className="flex justify-between items-center mb-6">
            <h2 className="text-lg font-semibold text-natural-charcoal">Quarterly Sales HQ Output</h2>
          </div>
          <div className="h-[300px]">
            <Bar data={barChartData} options={chartOptions} />
          </div>
        </div>
      </div>
    </motion.div>
  );
}
