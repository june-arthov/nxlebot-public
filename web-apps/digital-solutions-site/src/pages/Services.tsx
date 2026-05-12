import { motion } from 'framer-motion';

const services = [
  { title: "Web Dev", desc: "React & Next.js", icon: "🌐" },
  { title: "Mobile", desc: "Flutter & RN", icon: "📱" },
  { title: "Cloud", desc: "AWS & Azure", icon: "☁️" },
  { title: "AI/ML", desc: "TensorFlow", icon: "🤖" },
  { title: "Game Engine", desc: "Godot & Unity", icon: "🎮" },
  { title: "3D Animation", desc: "Blender & Cinema 4D", icon: "🎬" }
];

export default function Services() {
  return (
    <div className="min-h-screen bg-[#e0e5ec] text-gray-700 py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-700 mb-4">Services</h1>
          <p className="text-xl text-gray-500">What we do best</p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-10">
          {services.map((s, i) => (
            <motion.div
              key={i}
              initial={{ y: 30, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.1 }}
              whileHover={{ scale: 1.03 }}
              className="p-8 rounded-3xl bg-[#e0e5ec] shadow-[15px_15px_40px_#bebebe,-15px_-15px_40px_#ffffff] hover:shadow-[inset_10px_10px_20px_#bebebe,inset_-10px_-10px_20px_#ffffff] transition-all cursor-pointer"
            >
              <div className="w-16 h-16 mb-6 rounded-2xl bg-[#e0e5ec] shadow-[inset_6px_6px_12px_#bebebe,inset_-6px_-6px_12px_#ffffff] flex items-center justify-center">
                <span className="text-3xl">{s.icon}</span>
              </div>
              <h3 className="text-2xl font-bold text-gray-700 mb-2">{s.title}</h3>
              <p className="text-gray-500">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}