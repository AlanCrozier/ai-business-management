import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { 
  LayoutDashboard, TrendingUp, Users, Zap, 
  Database, Settings, Bell, Search, Menu, 
  LogOut, ChevronDown, Loader2, Briefcase
} from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { cn } from '../lib/utils';
import { auth } from '../lib/firebase';
import { onAuthStateChanged, signOut, User } from 'firebase/auth';

import OverviewTab from '../components/tabs/OverviewTab';
import SalesTab from '../components/tabs/SalesTab';
import CustomersTab from '../components/tabs/CustomersTab';
import EmployeesTab from '../components/tabs/EmployeesTab';
import AIEngineTab from '../components/tabs/AIEngineTab';
import { LumonLogo, LumonText } from '../components/LumonBrand';
import DataSourcesTab from '../components/tabs/DataSourcesTab';
import SettingsTab from '../components/tabs/SettingsTab';

const SidebarItem = ({ icon: Icon, label, active, onClick }: { icon: any, label: string, active?: boolean, onClick?: () => void }) => (
  <button onClick={onClick} className={cn(
    "w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all font-medium text-sm",
    active ? "bg-natural-sage text-white shadow-md shadow-natural-sage/20" : "text-natural-charcoal/60 hover:bg-natural-charcoal/5 hover:text-natural-charcoal"
  )}>
    <Icon className="w-5 h-5" />
    {label}
  </button>
);

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState<User | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const GAS_URL_KEY = 'saas_gas_url';
  const [appUrl, setAppUrl] = useState(localStorage.getItem(GAS_URL_KEY) || '');
  const [apiData, setApiData] = useState<any>(null);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      if (!currentUser) {
        navigate('/login');
      } else {
        setUser(currentUser);
        fetchData(currentUser);
        // Polling increased to 30s to prevent Google Sheets 429 Rate Limit Errors
        interval = setInterval(() => fetchData(currentUser), 30000);
      }
    });

    return () => {
      unsubscribe();
      if (interval) clearInterval(interval);
    };
  }, [navigate, appUrl]);

  const fetchData = async (currentUser: User) => {
    if (!appUrl) {
      setIsLoading(false);
      return;
    }
    try {
      const response = await fetch('http://127.0.0.1:8000/api/sheets/dashboard', { 
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ uid: currentUser.uid, sheet_url: appUrl })
      });
      const result = await response.json();
      if (result.success) {
        setApiData(result.data);
      }
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    await signOut(auth);
  };

  // User details
  const displayName = user?.displayName || user?.email?.split('@')[0] || "Executive";
  const displayInitials = displayName.substring(0, 2).toUpperCase();

  return (
    <div className="min-h-screen bg-[#F8F9FA] flex overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {isSidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 260, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="flex-shrink-0 bg-white border-r border-slate-200 h-screen sticky top-0 flex flex-col z-20"
          >
            <div className="h-20 flex items-center px-6 border-b border-slate-100">
              <Link to="/" className="flex items-center gap-3">
                <LumonLogo className="w-8 h-8 text-natural-sage" />
                <LumonText className="text-xl" textClass="text-natural-charcoal" dotClass="fill-natural-charcoal" />
              </Link>
            </div>

            <div className="flex-1 overflow-y-auto py-6 px-4 space-y-2">
              <div className="text-xs font-semibold text-natural-charcoal/40 uppercase tracking-wider mb-4 px-4">Overview</div>
              <SidebarItem icon={LayoutDashboard} label="Dashboard" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
              <SidebarItem icon={TrendingUp} label="Sales HQ" active={activeTab === 'sales'} onClick={() => setActiveTab('sales')} />
              <SidebarItem icon={Users} label="Customers" active={activeTab === 'customers'} onClick={() => setActiveTab('customers')} />
              <SidebarItem icon={Briefcase} label="Employees" active={activeTab === 'employees'} onClick={() => setActiveTab('employees')} />
              
              <div className="mt-8 mb-4">
                <div className="text-xs font-semibold text-natural-charcoal/40 uppercase tracking-wider px-4">Intelligence</div>
              </div>
              <SidebarItem icon={Zap} label="AI Engine" active={activeTab === 'ai'} onClick={() => setActiveTab('ai')} />
              <SidebarItem icon={Database} label="Data Sources" active={activeTab === 'datasources'} onClick={() => setActiveTab('datasources')} />
              
              <div className="mt-8 mb-4">
                <div className="text-xs font-semibold text-natural-charcoal/40 uppercase tracking-wider px-4">System</div>
              </div>
              <SidebarItem icon={Settings} label="Settings" active={activeTab === 'settings'} onClick={() => setActiveTab('settings')} />
            </div>

            <div className="p-4 border-t border-slate-100">
              <div className="flex items-center gap-3 p-3 rounded-xl hover:bg-slate-50 transition-colors cursor-pointer">
                <div className="w-10 h-10 rounded-full bg-slate-200 flex-shrink-0 flex items-center justify-center text-slate-500 font-medium">
                  {displayInitials}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-semibold text-natural-charcoal truncate">{displayName}</div>
                  <div className="text-xs text-natural-charcoal/50 truncate">{user?.email}</div>
                </div>
                <button onClick={handleLogout} className="p-1 hover:bg-slate-200 rounded">
                  <LogOut className="w-4 h-4 text-natural-charcoal/40" />
                </button>
              </div>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Header */}
        <header className="h-20 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-6 sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="p-2 rounded-lg hover:bg-slate-100 text-natural-charcoal/60 transition-colors"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-100/50 rounded-lg w-64 border border-slate-200/50 focus-within:border-natural-sage/30 focus-within:bg-white transition-all">
              <Search className="w-4 h-4 text-slate-400" />
              <input type="text" placeholder="Search insights..." className="bg-transparent border-none focus:outline-none text-sm w-full" />
            </div>
          </div>
          <div className="flex items-center gap-4">
            {/* Live Sync Status */}
            <div className="flex items-center gap-2 text-sm font-medium">
                <span className="relative flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-emerald-500"></span>
                </span>
                <span className="text-natural-charcoal/60">Live Sync</span>
            </div>
            <button className="relative p-2 rounded-lg hover:bg-slate-100 text-natural-charcoal/60 transition-colors">
              <Bell className="w-5 h-5" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border-2 border-white" />
            </button>
            <div className="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg hover:bg-slate-100 transition-colors">
              <div className="w-8 h-8 rounded-full bg-natural-sage/20 text-natural-sage flex items-center justify-center font-semibold text-sm">
                {displayInitials}
              </div>
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </div>
          </div>
        </header>

        {/* Dashboard Scroll Area */}
        <div className="flex-1 overflow-y-auto p-6 md:p-8">
          {isLoading ? (
            <div className="flex-1 h-full flex items-center justify-center">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="w-8 h-8 animate-spin text-natural-sage" />
                <span className="text-sm font-medium text-slate-500">Compiling executive insights...</span>
              </div>
            </div>
          ) : !appUrl && activeTab !== 'settings' ? (
             <div className="flex-1 h-full flex flex-col items-center justify-center gap-4">
                 <p className="text-natural-charcoal font-medium">Please configure your API Web App URL in Settings.</p>
                 <button onClick={() => setActiveTab('settings')} className="btn-primary">Go to Settings</button>
             </div>
          ) : (
            <AnimatePresence mode="wait">
              {activeTab === 'dashboard' && <OverviewTab key="dashboard" apiData={apiData} />}
              {activeTab === 'sales' && <SalesTab key="sales" apiData={apiData} appUrl={appUrl} user={user} />}
              {activeTab === 'customers' && <CustomersTab key="customers" apiData={apiData} appUrl={appUrl} user={user} />}
              {activeTab === 'employees' && <EmployeesTab key="employees" apiData={apiData} appUrl={appUrl} user={user} />}
              {activeTab === 'ai' && <AIEngineTab key="ai" apiData={apiData} />}
              {activeTab === 'datasources' && <DataSourcesTab key="datasources" apiData={apiData} appUrl={appUrl} user={user} />}
              {activeTab === 'settings' && <SettingsTab key="settings" appUrl={appUrl} setAppUrl={setAppUrl} user={user} />}
            </AnimatePresence>
          )}
        </div>
      </main>
    </div>
  );
}
