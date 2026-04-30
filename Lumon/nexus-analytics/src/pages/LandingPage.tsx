import { motion } from 'motion/react';
import { ArrowRight, Play, BarChart3, PieChart, TrendingUp } from 'lucide-react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  return (
    <div className="relative min-h-screen overflow-hidden pt-32 pb-20">
      {/* Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-natural-sage/20 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-[20%] right-[-10%] w-[30%] h-[50%] bg-natural-gold/10 rounded-full blur-[100px] pointer-events-none" />
      <div className="absolute bottom-[-10%] left-[20%] w-[50%] h-[30%] bg-natural-sand/50 rounded-full blur-[100px] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center max-w-4xl mx-auto mb-16">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-7xl font-display font-medium text-natural-charcoal leading-tight mb-8"
          >
            Architecting Resilient <br className="hidden md:block" />
            <span className="italic text-natural-sage">Business Strategies</span> with AI
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg md:text-xl text-natural-charcoal/70 mb-12 max-w-2xl mx-auto"
          >
            Transform raw data into executive clarity. Our premium predictive analytics engine models complex market dynamics to optimize your operational resilience.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <Link to="/signup" className="w-full sm:w-auto button-natural flex items-center justify-center gap-2 group">
              Begin Exploration
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </Link>
          </motion.div>
        </div>

        {/* 3D Dashboard Mock UI */}
        <motion.div
          id="platform"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.5 }}
          className="relative mx-auto max-w-5xl aspect-[16/9] rounded-[2rem] overflow-hidden glass-light border border-white/40 shadow-2xl p-2 mt-12"
          style={{ transform: "perspective(1000px) rotateX(5deg)", scrollMarginTop: "120px" }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-natural-bg/80 via-transparent to-transparent z-10 pointer-events-none" />
          <div className="w-full h-full bg-white rounded-[1.5rem] overflow-hidden shadow-inner flex flex-col">
            {/* Mock Header */}
            <div className="h-14 border-b border-slate-100 flex items-center px-6 gap-4">
              <div className="flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-400" />
                <div className="w-3 h-3 rounded-full bg-amber-400" />
                <div className="w-3 h-3 rounded-full bg-green-400" />
              </div>
              <div className="flex-1 max-w-md bg-slate-50 border border-slate-200 h-8 rounded-md flex items-center px-3 text-xs text-slate-400">
                Search insights...
              </div>
              <div className="flex-1" />
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-xs font-medium text-slate-600">Live Sync</span>
              </div>
              <div className="w-8 h-8 rounded-full bg-natural-sage/20 text-natural-sage font-bold text-xs flex items-center justify-center">EJ</div>
            </div>
            {/* Mock Content */}
            <div className="flex-1 flex p-6 gap-6 bg-slate-50/50">
              {/* Mock Sidebar */}
              <div className="w-48 flex flex-col gap-2">
                <div className="px-3 py-2 bg-white rounded-lg border border-slate-100 shadow-sm text-sm font-semibold text-natural-sage flex items-center gap-2">
                  Dashboard
                </div>
                <div className="px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 transition-colors flex items-center gap-2">
                  Sales HQ
                </div>
                <div className="px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 transition-colors flex items-center gap-2">
                  Customers
                </div>
                <div className="px-3 py-2 rounded-lg text-sm font-medium text-slate-500 hover:bg-slate-100 transition-colors flex items-center gap-2">
                  Employees
                </div>
                <div className="mt-4 px-3 py-2 bg-natural-sage text-white rounded-lg shadow-md text-sm font-semibold flex items-center gap-2">
                  AI Engine
                </div>
              </div>
              {/* Mock Main */}
              <div className="flex-1 flex flex-col gap-6">
                <div className="flex gap-4">
                  <div className="flex-1 h-24 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center p-4 gap-4">
                    <div className="w-12 h-12 bg-emerald-50 rounded-lg flex items-center justify-center"><TrendingUp className="text-emerald-500 w-6 h-6" /></div>
                    <div className="flex-1">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Total Revenue</div>
                      <div className="text-xl font-bold text-natural-charcoal">$12,450,890</div>
                    </div>
                  </div>
                  <div className="flex-1 h-24 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center p-4 gap-4">
                    <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center"><BarChart3 className="text-blue-500 w-6 h-6" /></div>
                    <div className="flex-1">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">Active Customers</div>
                      <div className="text-xl font-bold text-natural-charcoal">4,892 <span className="text-xs text-emerald-500 font-medium ml-1">+12%</span></div>
                    </div>
                  </div>
                  <div className="flex-1 h-24 bg-white rounded-xl shadow-sm border border-slate-100 flex items-center p-4 gap-4">
                    <div className="w-12 h-12 bg-amber-50 rounded-lg flex items-center justify-center"><PieChart className="text-amber-500 w-6 h-6" /></div>
                    <div className="flex-1">
                      <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-1">AI Profit Forecast</div>
                      <div className="text-xl font-bold text-natural-charcoal">+24.5% <span className="text-xs text-emerald-500 font-medium ml-1">Surge</span></div>
                    </div>
                  </div>
                </div>
                <div className="flex-1 bg-white rounded-xl shadow-sm border border-slate-100 p-6 flex flex-col gap-4 relative overflow-hidden">
                   <div className="text-sm font-bold text-natural-charcoal mb-4">Revenue Trajectory (Next 30 Days)</div>
                   <div className="absolute top-6 right-6 text-xs font-semibold text-natural-sage bg-natural-sage/10 px-2 py-1 rounded-md">ML Model Active</div>
                   <div className="flex-1 flex items-end gap-2">
                     {[40, 70, 45, 90, 65, 85, 55, 100, 75, 60, 80].map((h, i) => (
                       <motion.div key={i} className="flex-1 bg-gradient-to-t from-natural-sage/40 to-natural-sage/20 rounded-t-sm" initial={{ height: 0 }} animate={{ height: `${h}%` }} transition={{ duration: 1, delay: 0.5 + i * 0.05 }} />
                     ))}
                   </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Scroll-Triggered Features Section */}
        <div id="features" className="mt-40 mb-32 relative z-10" style={{ scrollMarginTop: "120px" }}>
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.7 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-display font-medium text-natural-charcoal mb-4">Unprecedented Operational Clarity</h2>
            <p className="text-lg text-natural-charcoal/60 max-w-2xl mx-auto">Leverage state-of-the-art machine learning models to anticipate market shifts and optimize enterprise performance.</p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              { icon: TrendingUp, title: "Predictive Forecasting", desc: "Our machine learning models analyze historical trajectories to predict future revenue and profit margins with high accuracy." },
              { icon: PieChart, title: "Enterprise Data Isolation", desc: "Military-grade multi-tenant architecture ensures your data is completely isolated via Google Cloud Service Accounts." },
              { icon: BarChart3, title: "Automated Data Pipelines", desc: "No manual data entry required. Your dashboard synchronizes directly with secure, auto-provisioned Google Sheets." }
            ].map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 40 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-50px" }}
                transition={{ duration: 0.6, delay: idx * 0.2 }}
                className="glass-light p-10 rounded-[2rem] border border-white/60 shadow-xl hover:shadow-2xl hover:-translate-y-2 transition-all duration-300 group"
              >
                <div className="w-16 h-16 bg-natural-sage/10 rounded-2xl flex items-center justify-center mb-8 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-8 h-8 text-natural-sage" />
                </div>
                <h3 className="text-2xl font-semibold text-natural-charcoal mb-4">{feature.title}</h3>
                <p className="text-natural-charcoal/70 leading-relaxed text-lg">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>

        {/* CTA Section */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="mb-20 glass-light rounded-[3rem] p-16 text-center border border-white/40 shadow-2xl relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-natural-charcoal" />
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop')] bg-cover bg-center opacity-20 mix-blend-overlay" />
          <div className="relative z-10">
            <h2 className="text-4xl md:text-5xl font-display font-medium text-white mb-6">Ready to Architect Your Future?</h2>
            <p className="text-white/80 text-xl max-w-2xl mx-auto mb-10">Join elite enterprises leveraging Lumon to transform raw data into strategic foresight.</p>
            <Link to="/signup" className="inline-flex items-center gap-2 px-8 py-4 bg-white text-natural-charcoal rounded-full font-bold transition-transform hover:scale-105 shadow-xl">
              Start Your Journey
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;
