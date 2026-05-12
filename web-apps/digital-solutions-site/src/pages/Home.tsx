import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

export default function Home() {
  return (
    <div className="min-h-screen bg-[#e0e5ec] text-gray-700 relative overflow-hidden">
      <div className="container mx-auto px-4 py-32 text-center">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="w-32 h-32 mx-auto mb-8 rounded-full bg-[#e0e5ec] shadow-[20px_20px_60px_#bebebe,-20px_-20px_60px_#ffffff] flex items-center justify-center"
        >
          <span className="text-6xl text-gray-600">◈</span>
        </motion.div>

        <motion.h1 
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-6xl font-bold text-gray-700 mb-6 tracking-tight"
        >
          NUMERIA
        </motion.h1>
        
        <p className="text-xl text-gray-500 mb-12 max-w-2xl mx-auto">
          Digital solutions crafted with precision and soft aesthetics.
        </p>

        <div className="flex gap-6 justify-center">
          <Link to="/services" className="px-8 py-4 rounded-full bg-[#e0e5ec] shadow-[10px_10px_20px_#bebebe,-10px_-10px_20px_#ffffff] text-gray-600 font-medium hover:shadow-[inset_10px_10px_20px_#bebebe,inset_-10px_-10px_20px_#ffffff] transition-all">
            Explore
          </Link>
          <Link to="/contact" className="px-8 py-4 rounded-full bg-[#e0e5ec] shadow-[10px_10px_20px_#bebebe,-10px_-10px_20px_#ffffff] text-blue-500 font-medium hover:shadow-[inset_10px_10px_20px_#bebebe,inset_-10px_-10px_20px_#ffffff] transition-all">
            Start Project
          </Link>
        </div>
      </div>

      {/* Features with Neumorphic Cards */}
      <div className="container mx-auto px-4 py-20">
        <div className="grid md:grid-cols-3 gap-10">
          {[
            { icon: "⚡", title: "Fast", desc: "Optimized performance" },
            { icon: "🎯", title: "Precise", desc: "Pixel-perfect details" },
            { icon: "🛡️", title: "Game Dev", desc: "Godot & Unity" }
          ].map((f, i) => (
            <motion.div
              key={i}
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.2 }}
              whileHover={{ scale: 1.02 }}
              className="p-8 rounded-3xl bg-[#e0e5ec] shadow-[20px_20px_60px_#bebebe,-20px_-20px_60px_#ffffff]"
            >
              <div className="w-20 h-20 mx-auto mb-6 rounded-2xl bg-[#e0e5ec] shadow-[inset_8px_8px_16px_#bebebe,inset_-8px_-8px_16px_#ffffff] flex items-center justify-center">
                <span className="text-4xl text-gray-600">{f.icon}</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-700 mb-3 text-center">{f.title}</h3>
              <p className="text-gray-500 text-center">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}