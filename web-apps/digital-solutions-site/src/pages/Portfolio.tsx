import { motion } from 'framer-motion';

const projects = [
  { title: "E-Commerce", cat: "Web", desc: "Shopping platform", icon: "🛒" },
  { title: "HealthApp", cat: "Mobile", desc: "Telemedicine", icon: "🏥" },
  { title: "FinDash", cat: "Analytics", desc: "Trading dashboard", icon: "💹" },
  { title: "Vault", cat: "Security", desc: "Secrets manager", icon: "🔐" }
];

export default function Portfolio() {
  return (
    <div className="min-h-screen bg-[#e0e5ec] text-gray-700 py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-700 mb-4">Portfolio</h1>
          <p className="text-xl text-gray-500">Selected works</p>
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {projects.map((p, i) => (
            <motion.div
              key={i}
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.15 }}
              className="rounded-3xl bg-[#e0e5ec] shadow-[20px_20px_60px_#bebebe,-20px_-20px_60px_#ffffff] overflow-hidden"
            >
              <div className="h-64 bg-[#e0e5ec] shadow-[inset_10px_10px_20px_#bebebe,inset_-10px_-10px_20px_#ffffff] flex items-center justify-center m-6 rounded-2xl">
                <span className="text-8xl text-gray-400">{p.icon}</span>
              </div>
              <div className="px-8 pb-8">
                <span className="text-blue-500 text-sm font-semibold mb-2 block">{p.cat}</span>
                <h3 className="text-2xl font-bold text-gray-700 mb-1">{p.title}</h3>
                <p className="text-gray-500">{p.desc}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}