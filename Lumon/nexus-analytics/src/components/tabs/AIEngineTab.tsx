
import { motion } from 'motion/react';
import { Zap, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Line } from 'react-chartjs-2';

export default function AIEngineTab({ apiData }: any) {
  const preds = apiData?.predictions || [];
  const sales = apiData?.sales || [];
  
  const pDates = preds.map((p: any) => new Date(p.timestamp).toLocaleDateString());
  
  const revByDate: Record<string, number> = {};
  sales.forEach((s: any) => {
    const d = new Date(s.timestamp).toLocaleDateString();
    revByDate[d] = (revByDate[d] || 0) + parseFloat(s.revenue || 0);
  });
  const actualRevData = Object.values(revByDate).slice(0, pDates.length);

  const dualLineData = {
    labels: pDates,
    datasets: [
        { label: 'Predicted Rev ($)', data: preds.map((p:any) => parseFloat(p.predicted_revenue||0)), borderColor:'#8B5CF6', tension:0, borderWidth: 2 },
        { label: 'Actual Revenue Trend', data: actualRevData, borderColor:'#2563EB', borderDash: [5, 5], tension:0, borderWidth: 2 }
    ]
  };

  const profitTrendData = {
    labels: pDates,
    datasets: [
        { label: 'Predicted Profit', data: preds.map((p:any) => parseFloat(p.predicted_profit||0)), borderColor:'#10B981', fill:true, backgroundColor:'rgba(16,185,129,0.1)', tension:0.4, borderWidth: 2 }
    ]
  };

  const chartOptions = { 
      responsive: true, 
      maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' as const } },
      scales: {
          x: { grid: { display: false } },
          y: { grid: { color: 'rgba(0,0,0,0.05)' } }
      }
  };

  const anomalies = preds.filter((p:any) => parseInt(p.anomaly_flag) === -1).reverse().slice(0, 10);

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="max-w-7xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-natural-charcoal mb-1">AI Intelligence Engine</h1>
        <p className="text-sm text-slate-500">View real-time predictions, forecasts, and anomaly detections across all business modules.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
            <div className="card-3d rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Actual vs Predicted Revenue</h2>
              <div className="h-[300px]">
                <Line data={dualLineData} options={chartOptions} />
              </div>
            </div>

            <div className="card-3d rounded-2xl p-6">
              <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Profitability Forecast</h2>
              <div className="h-[250px]">
                <Line data={profitTrendData} options={chartOptions} />
              </div>
            </div>
        </div>

        <div className="space-y-6">
            <div className="card-3d rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                  <Zap className="w-5 h-5 text-purple-500" />
                  <h2 className="text-lg font-semibold text-natural-charcoal">Anomaly Detection</h2>
              </div>
              
              {anomalies.length === 0 ? (
                  <div className="flex flex-col items-center justify-center p-8 text-center bg-emerald-50 rounded-xl border border-emerald-100">
                      <ShieldCheck className="w-8 h-8 text-emerald-500 mb-2" />
                      <p className="text-emerald-700 font-medium">System Optimal</p>
                      <p className="text-xs text-emerald-600/70 mt-1">No anomalies detected across any business metrics.</p>
                  </div>
              ) : (
                  <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                      {anomalies.map((a: any, i: number) => (
                          <div key={i} className="p-4 rounded-xl bg-red-50 border border-red-100">
                              <div className="flex items-center gap-2 mb-1">
                                  <AlertTriangle className="w-4 h-4 text-red-500" />
                                  <span className="font-semibold text-red-700 text-sm">{a.module_type.toUpperCase()} Error Flag</span>
                              </div>
                              <p className="text-xs text-red-600/70 mb-2">{new Date(a.timestamp).toLocaleString()}</p>
                              <p className="text-sm text-red-800">Deviance detected across metrics. Manual review recommended.</p>
                          </div>
                      ))}
                  </div>
              )}
            </div>
        </div>
      </div>

      <div className="card-3d rounded-2xl p-6 overflow-hidden">
          <h2 className="text-lg font-semibold text-natural-charcoal mb-4">Prediction Log</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
                <thead className="text-xs text-slate-500 uppercase bg-slate-50">
                <tr>
                    <th className="px-4 py-3">Timestamp</th>
                    <th className="px-4 py-3">Module</th>
                    <th className="px-4 py-3">Pred. Revenue</th>
                    <th className="px-4 py-3">Pred. Profit</th>
                    <th className="px-4 py-3">Status</th>
                </tr>
                </thead>
                <tbody>
                {preds.reverse().slice(0, 20).map((p: any, i: number) => {
                    const isAnomaly = parseInt(p.anomaly_flag) === -1;
                    return (
                        <tr key={i} className="border-b border-slate-100 hover:bg-slate-50">
                            <td className="px-4 py-3">{new Date(p.timestamp).toLocaleString()}</td>
                            <td className="px-4 py-3 font-medium">{p.module_type.toUpperCase()}</td>
                            <td className="px-4 py-3">${parseFloat(p.predicted_revenue||0).toLocaleString()}</td>
                            <td className="px-4 py-3">${parseFloat(p.predicted_profit||0).toLocaleString()}</td>
                            <td className="px-4 py-3">
                                {isAnomaly ? (
                                    <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-md">Anomaly</span>
                                ) : (
                                    <span className="px-2 py-1 bg-emerald-100 text-emerald-700 text-xs font-semibold rounded-md">Normal</span>
                                )}
                            </td>
                        </tr>
                    );
                })}
                </tbody>
            </table>
          </div>
      </div>

    </motion.div>
  );
}
