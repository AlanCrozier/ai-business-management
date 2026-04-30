import { motion } from 'motion/react';
import { Menu, X } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { LumonLogo, LumonText } from './LumonBrand';

export const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();

  if (
    location.pathname.includes('/dashboard') || 
    location.pathname.includes('/login') || 
    location.pathname.includes('/signup')
  ) {
    return null;
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 px-6 py-6">
      <div className="max-w-7xl mx-auto glass-light rounded-2xl px-8 py-4 flex items-center justify-between shadow-lg ring-1 ring-black/5">
        <Link to="/" className="flex items-center gap-3 group">
          <LumonLogo className="w-10 h-10 text-natural-sage group-hover:scale-105 transition-transform" />
          <LumonText className="text-2xl" textClass="text-natural-charcoal" dotClass="fill-natural-charcoal" />
        </Link>

        {/* Desktop Links */}
        <div className="hidden md:flex items-center gap-10 text-sm font-medium text-natural-charcoal/70">
          <a href="#platform" className="hover:text-natural-sage transition-colors">Platform</a>
          <a href="#features" className="hover:text-natural-sage transition-colors">Features</a>
        </div>

        <div className="hidden md:flex items-center gap-6">
          <Link to="/login" className="text-sm font-semibold text-natural-charcoal hover:text-natural-sage transition-colors">Sign In</Link>
          <Link to="/signup" className="px-6 py-2.5 bg-natural-charcoal text-white rounded-full text-sm font-semibold hover:bg-natural-sage transition-all shadow-md active:scale-95">
            Get Started
          </Link>
        </div>

        {/* Mobile Toggle */}
        <button className="md:hidden text-natural-charcoal" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? <X /> : <Menu />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="md:hidden absolute top-24 left-6 right-6 glass-light rounded-2xl p-8 flex flex-col gap-6 items-center text-center z-50 shadow-2xl border border-white"
        >
          <a href="#platform" className="text-lg font-medium text-natural-charcoal" onClick={() => setIsMenuOpen(false)}>Platform</a>
          <a href="#features" className="text-lg font-medium text-natural-charcoal" onClick={() => setIsMenuOpen(false)}>Features</a>
          <div className="w-full h-[1px] bg-natural-charcoal/5" />
          <Link to="/login" className="text-lg font-medium text-natural-charcoal" onClick={() => setIsMenuOpen(false)}>Sign In</Link>
          <Link to="/signup" className="w-full py-4 bg-natural-sage text-white rounded-xl font-bold shadow-lg" onClick={() => setIsMenuOpen(false)}>
            Get Started
          </Link>
        </motion.div>
      )}
    </nav>
  );
};
