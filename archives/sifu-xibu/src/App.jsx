import { motion } from 'framer-motion';
import { Terminal, Shield, Code, Cpu, Bug, Zap } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen bg-black text-gray-200 font-mono overflow-x-hidden">
      {/* Matrix/Grid Background */}
      <div className="fixed inset-0 bg-[linear-gradient(rgba(0,255,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,0,0.03)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none" />
      
      {/* Navbar */}
      <nav className="fixed top-0 w-full z-50 bg-black/80 backdrop-blur-md border-b border-green-900/30">
        <div className="container mx-auto px-4 py-4 flex justify-between items-center">
          <div className="text-2xl font-bold text-green-500 tracking-widest flex items-center gap-2">
            <Terminal size={24} /> SIFU_XIBU
          </div>
          <div className="hidden md:flex gap-8">
            {['Home', 'Services', 'Portfolio', 'Contact'].map((item) => (
              <a key={item} href={`#${item.toLowerCase()}`} className="hover:text-green-400 transition-colors uppercase text-sm tracking-widest">
                {item}
              </a>
            ))}
          </div>
          <a href="https://fiverr.com/sifuxibu" target="_blank" className="bg-green-600 text-black px-6 py-2 rounded font-bold hover:bg-green-400 transition-all transform hover:scale-105">
            HIRE ME
          </a>
        </div>
      </nav>

      {/* Hero Section */}
      <section id="home" className="pt-32 pb-20 px-4 container mx-auto text-center relative">
        <motion.div 
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          className="max-w-4xl mx-auto"
        >
          <div className="inline-block border border-green-500/50 px-4 py-1 rounded-full text-green-400 text-sm mb-6 bg-green-900/10">
            SYSTEM_STATUS: ONLINE_
          </div>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-white">
            I FIX WHAT <span className="text-green-500 text-shadow-glow">OTHERS CAN'T</span>
          </h1>
          <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
            Elite debugging, security patching, and high-performance optimization. 
            Your code is broken. I am the fix.
          </p>
          <div className="flex justify-center gap-4">
            <button className="border border-green-500 text-green-500 px-8 py-3 rounded hover:bg-green-500 hover:text-black transition-all font-bold">
              VIEW_PROTOCOLS
            </button>
            <a href="https://fiverr.com/sifuxibu" className="bg-green-600 text-black px-8 py-3 rounded font-bold hover:bg-green-400 transition-all">
              EXECUTE_HIRE()
            </a>
          </div>
        </motion.div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-20 bg-zinc-950 border-y border-green-900/20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-16 text-green-500">ACTIVE_PROTOCOLS</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: <Bug size={40} />, title: "Debugging", desc: "Complex error resolution in React, Python, JS." },
              { icon: <Shield size={40} />, title: "Security Audit", desc: "Patching vulnerabilities & hardening systems." },
              { icon: <Zap size={40} />, title: "Optimization", desc: "Improving load times & database queries." },
              { icon: <Code size={40} />, title: "Refactoring", desc: "Cleaning messy legacy code." },
              { icon: <Cpu size={40} />, title: "Automation", desc: "Scripts to do your boring work automatically." },
              { icon: <Terminal size={40} />, title: "Server Mgmt", desc: "Linux, Nginx, and deployment fixes." }
            ].map((s, i) => (
              <motion.div 
                key={i}
                whileHover={{ y: -10 }}
                className="bg-black p-8 rounded border border-green-900/30 hover:border-green-500 transition-all group"
              >
                <div className="text-green-500 mb-4 group-hover:text-white transition-colors">{s.icon}</div>
                <h3 className="text-xl font-bold text-white mb-2">{s.title}</h3>
                <p className="text-gray-500">{s.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-10 text-center text-gray-600 text-sm border-t border-green-900/20">
        <p>// SIFU XIBU // EST. 2026 //</p>
        <p className="mt-2">All systems operational.</p>
      </footer>
    </div>
  );
}

export default App;