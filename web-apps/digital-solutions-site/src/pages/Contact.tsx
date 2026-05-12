import { motion } from 'framer-motion';

export default function Contact() {
  return (
    <div className="min-h-screen bg-[#e0e5ec] text-gray-700 py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h1 className="text-5xl font-bold text-gray-700 mb-4">Contact</h1>
          <p className="text-xl text-gray-500">Let's talk</p>
        </div>

        <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-12">
          <div className="p-8 rounded-3xl bg-[#e0e5ec] shadow-[20px_20px_60px_#bebebe,-20px_-20px_60px_#ffffff]">
            <h3 className="text-2xl font-bold text-gray-700 mb-6">Send Message</h3>
            <form className="space-y-6">
              <input type="text" placeholder="Name" className="w-full bg-[#e0e5ec] border-none rounded-xl p-4 text-gray-700 placeholder-gray-400 shadow-[inset_8px_8px_16px_#bebebe,inset_-8px_-8px_16px_#ffffff] focus:outline-none focus:shadow-[inset_12px_12px_24px_#bebebe,inset_-12px_-12px_24px_#ffffff] transition-all" />
              <input type="email" placeholder="Email" className="w-full bg-[#e0e5ec] border-none rounded-xl p-4 text-gray-700 placeholder-gray-400 shadow-[inset_8px_8px_16px_#bebebe,inset_-8px_-8px_16px_#ffffff] focus:outline-none focus:shadow-[inset_12px_12px_24px_#bebebe,inset_-12px_-12px_24px_#ffffff] transition-all" />
              <textarea rows={5} placeholder="Message" className="w-full bg-[#e0e5ec] border-none rounded-xl p-4 text-gray-700 placeholder-gray-400 shadow-[inset_8px_8px_16px_#bebebe,inset_-8px_-8px_16px_#ffffff] focus:outline-none focus:shadow-[inset_12px_12px_24px_#bebebe,inset_-12px_-12px_24px_#ffffff] transition-all resize-none" />
              <button className="w-full py-4 rounded-xl bg-[#e0e5ec] shadow-[10px_10px_20px_#bebebe,-10px_-10px_20px_#ffffff] text-blue-500 font-semibold hover:shadow-[inset_10px_10px_20px_#bebebe,inset_-10px_-10px_20px_#ffffff] active:shadow-[inset_12px_12px_24px_#bebebe,inset_-12px_-12px_24px_#ffffff] transition-all">
                Send Message
              </button>
            </form>
          </div>

          <div className="space-y-6">
            {[
              { icon: "📍", label: "Office", info: "Singapore" },
              { icon: "📧", label: "Email", info: "hello@numeria.com" },
              { icon: "📞", label: "Phone", info: "+65 1234 5678" }
            ].map((c, i) => (
              <motion.div
                key={i}
                initial={{ x: 30, opacity: 0 }}
                animate={{ x: 0, opacity: 1 }}
                transition={{ delay: i * 0.15 }}
                className="p-6 rounded-2xl bg-[#e0e5ec] shadow-[15px_15px_40px_#bebebe,-15px_-15px_40px_#ffffff]"
              >
                <div className="text-3xl mb-2">{c.icon}</div>
                <div className="text-gray-400 text-sm mb-1">{c.label}</div>
                <div className="text-gray-700 font-medium">{c.info}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}