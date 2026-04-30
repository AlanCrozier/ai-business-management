import React, { useState, useEffect } from 'react';
import { motion } from 'motion/react';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { auth } from '../lib/firebase';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  updateProfile,
  onAuthStateChanged
} from 'firebase/auth';
import { LumonText } from '../components/LumonBrand';

const AuthPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const isSignup = location.pathname.includes('/signup');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  // Form states
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  useEffect(() => {
    // If user is already logged in, redirect to dashboard
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) navigate('/dashboard');
    });
    return unsubscribe;
  }, [navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');

    try {
      if (isSignup) {
        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
        await updateProfile(userCredential.user, { displayName: name });
        // Redirect handled by onAuthStateChanged
      } else {
        await signInWithEmailAndPassword(auth, email, password);
        // Redirect handled by onAuthStateChanged
      }
    } catch (error: any) {
      setErrorMsg(error.message.replace('Firebase: ', ''));
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* LEFT: Branding/Quote */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.6 }}
        className="hidden lg:flex lg:w-1/2 bg-natural-charcoal relative p-12 flex-col justify-between"
      >
        <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1497366216548-37526070297c?q=80&w=2069&auto=format&fit=crop')] bg-cover bg-center opacity-10 mix-blend-overlay" />
        
        <div className="relative z-10 flex justify-between items-center">
          <Link to="/" className="text-white flex items-center gap-2 hover:opacity-80 transition-opacity">
            <ArrowLeft className="w-5 h-5" />
            <span className="text-sm font-medium">Return Home</span>
          </Link>
          <LumonText className="text-3xl" textClass="text-white" dotClass="fill-white" />
        </div>

        <div className="relative z-10 max-w-md">
          <motion.blockquote 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-3xl font-display text-white leading-tight mb-6"
          >
            "Data is not just an asset; it's the very foundation of strategic foresight."
          </motion.blockquote>
        </div>
      </motion.div>

      {/* RIGHT: Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 bg-natural-bg">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <div className="mb-10 text-center lg:text-left">
            <h2 className="text-3xl font-display font-medium text-natural-charcoal mb-2">
              {isSignup ? 'Begin Your Journey' : 'Welcome Back'}
            </h2>
            <p className="text-natural-charcoal/60 text-sm">
              {isSignup ? 'Enter your details to architect your analytics suite.' : 'Enter your credentials to access your insights.'}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            {errorMsg && (
              <div className="p-3 text-sm text-red-600 bg-red-50 border border-red-200 rounded-xl">
                {errorMsg}
              </div>
            )}

            {isSignup && (
              <div className="space-y-1.5">
                <label className="text-sm font-medium text-natural-charcoal/80">Full Name</label>
                <input 
                  type="text" 
                  required 
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl border border-black/10 bg-white/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-natural-sage/30 transition-all"
                  placeholder="John Doe"
                />
              </div>
            )}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-natural-charcoal/80">Executive Email</label>
              <input 
                type="email" 
                required 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-black/10 bg-white/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-natural-sage/30 transition-all"
                placeholder="john@company.com"
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-natural-charcoal/80">Password</label>
              <input 
                type="password" 
                required 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-black/10 bg-white/50 focus:bg-white focus:outline-none focus:ring-2 focus:ring-natural-sage/30 transition-all"
                placeholder="••••••••"
              />
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className="w-full py-3.5 bg-natural-charcoal text-white rounded-xl font-medium flex items-center justify-center gap-2 transition-all hover:bg-natural-sage disabled:opacity-70"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                isSignup ? 'Create Account' : 'Sign In'
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-natural-charcoal/60">
            {isSignup ? 'Already have an account? ' : "Don't have an account? "}
            <Link to={isSignup ? '/login' : '/signup'} className="font-medium text-natural-sage hover:underline">
              {isSignup ? 'Sign in' : 'Create one'}
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default AuthPage;
