import './index.css';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { motion } from 'framer-motion';
import Home from './pages/Home';
import Services from './pages/Services';
import Portfolio from './pages/Portfolio';
import Contact from './pages/Contact';

function App() {
  return (
    <Router>
      <div className="bg-[#e0e5ec] min-h-screen text-gray-700">
        {/* Neumorphic Navbar */}
        <nav className="fixed top-4 left-1/2 -translate-x-1/2 z-50 w-[95%] max-w-5xl">
          <div className="bg-[#e0e5ec] rounded-2xl px-6 py-3 shadow-[10px_10px_20px_#bebebe,-10px_-10px_20px_#ffffff]">
            <div className="flex justify-between items-center">
              <NavLink to="/" className="flex items-center gap-3">
                <motion.div
                  whileHover={{ rotate: 360 }}
                  className="w-10 h-10 rounded-xl bg-[#e0e5ec] shadow-[inset_6px_6px_12px_#bebebe,inset_-6px_-6px_12px_#ffffff] flex items-center justify-center"
                >
                  <span className="text-lg text-gray-600">◈</span>
                </motion.div>
                <span className="font-bold text-xl tracking-wide text-gray-700">NUMERIA</span>
              </NavLink>

              <div className="flex gap-1">
                {[
                  ['/', 'Home'],
                  ['/services', 'Services'],
                  ['/portfolio', 'Work'],
                  ['/contact', 'Contact']
                ].map(([path, label]) => (
                  <NavLink
                    key={path}
                    to={path}
                    className={({ isActive }) =>
                      `px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                        isActive 
                          ? 'shadow-[inset_6px_6px_12px_#bebebe,inset_-6px_-6px_12px_#ffffff] text-blue-500' 
                          : 'text-gray-500 hover:text-gray-700'
                      }`
                    }
                  >
                    {label}
                  </NavLink>
                ))}
              </div>

              <NavLink 
                to="/contact"
                className="px-5 py-2 rounded-xl text-sm font-medium bg-[#e0e5ec] shadow-[8px_8px_16px_#bebebe,-8px_-8px_16px_#ffffff] text-blue-500 hover:shadow-[inset_6px_6px_12px_#bebebe,inset_-6px_-6px_12px_#ffffff] transition-all"
              >
                Get Started
              </NavLink>
            </div>
          </div>
        </nav>

        <div className="pt-28">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/services" element={<Services />} />
            <Route path="/portfolio" element={<Portfolio />} />
            <Route path="/contact" element={<Contact />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;