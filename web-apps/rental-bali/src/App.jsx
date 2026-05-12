import { motion, useScroll, useTransform } from 'framer-motion';
import { Bike, Car, MapPin, ShieldCheck, Star, Calendar, ChevronRight, Phone, MessageCircle } from 'lucide-react';

const fleet = [
  { id: 1, name: "Vespa Sprint 150", type: "Scooter", price: "120K", rating: 4.9, img: "🛵", tag: "Best Seller" },
  { id: 2, name: "NMAX 155 ABS", type: "Maxi Scooter", price: "160K", rating: 4.8, img: "🏍️", tag: "Comfort" },
  { id: 3, name: "Honda Brio Satya", type: "City Car", price: "250K", rating: 4.7, img: "🚗", tag: "Economical" },
  { id: 4, name: "Mitsubishi Xpander", type: "MPV 7-Seater", price: "400K", rating: 5.0, img: "🚙", tag: "Family" },
];

export default function App() {
  const { scrollY } = useScroll();
  const y1 = useTransform(scrollY, [0, 500], [0, 200]);

  return (
    <div className="min-h-screen bg-stone-50 text-stone-900 overflow-hidden">
      {/* Navigation */}
      <nav className="fixed w-full z-50 transition-all duration-300 bg-white/80 backdrop-blur-md border-b border-stone-100">
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-teal-600 rounded-lg flex items-center justify-center text-white font-bold text-xl">B</div>
            <span className="text-xl font-bold tracking-tight text-stone-900">BALI<span className="text-teal-600">RIDE</span></span>
          </div>
          <div className="hidden md:flex gap-8 text-sm font-medium text-stone-600">
            {['Fleet', 'Services', 'Locations', 'Contact'].map((item) => (
              <a key={item} href="#" className="hover:text-teal-600 transition-colors">{item}</a>
            ))}
          </div>
          <button className="bg-stone-900 text-white px-5 py-2.5 rounded-full text-sm font-bold hover:bg-teal-700 transition-all">
            My Booking
          </button>
        </div>
      </nav>

      {/* Hero Section with Parallax */}
      <section className="relative pt-32 pb-40 overflow-hidden">
        <motion.div style={{ y: y1 }} className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-b from-teal-900/10 to-stone-50 z-10" />
          <div className="w-full h-full bg-stone-200 flex items-center justify-center text-stone-400">
            {/* Placeholder for high-quality Bali image */}
            <div className="text-center">
              <div className="text-9xl mb-4">🌴</div>
              <p>Imagine a stunning tropical road here</p>
            </div>
          </div>
        </motion.div>

        <div className="container mx-auto px-6 relative z-20 text-center">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
            <span className="inline-block py-1 px-3 rounded-full bg-teal-100 text-teal-800 text-xs font-bold tracking-widest mb-6 uppercase">
              Premium Rental Service
            </span>
            <h1 className="text-6xl md:text-8xl font-serif font-bold text-stone-900 mb-8 leading-tight">
              Ride the <span className="text-teal-700 italic">Island</span><br />of Gods
            </h1>
            <p className="text-xl text-stone-600 max-w-2xl mx-auto mb-10 leading-relaxed">
              Experience Bali's freedom with our meticulously maintained fleet. 
              Free delivery, zero deposit options, and 24/7 roadside assistance.
            </p>
          </motion.div>

          {/* Glass Search Bar */}
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4 }}
            className="max-w-4xl mx-auto bg-white/60 backdrop-blur-xl p-4 rounded-3xl shadow-2xl border border-white/50 flex flex-col md:flex-row gap-4 items-center"
          >
            <div className="flex-1 w-full bg-white p-4 rounded-2xl shadow-sm border border-stone-100">
              <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">Pick-up Location</label>
              <div className="flex items-center gap-2 text-stone-800 font-semibold">
                <MapPin size={18} className="text-teal-600" /> Ngurah Rai Airport
              </div>
            </div>
            <div className="flex-1 w-full bg-white p-4 rounded-2xl shadow-sm border border-stone-100">
              <label className="block text-xs font-bold text-stone-400 uppercase tracking-wider mb-1">Duration</label>
              <div className="flex items-center gap-2 text-stone-800 font-semibold">
                <Calendar size={18} className="text-teal-600" /> 3 Days - 1 Week
              </div>
            </div>
            <button className="w-full md:w-auto bg-teal-700 text-white p-4 rounded-2xl hover:bg-teal-800 transition-all shadow-lg shadow-teal-700/20">
              <ChevronRight size={24} />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Fleet Section */}
      <section className="py-24 bg-white">
        <div className="container mx-auto px-6">
          <div className="flex justify-between items-end mb-16">
            <div>
              <h2 className="text-4xl font-serif font-bold text-stone-900 mb-2">The Fleet</h2>
              <p className="text-stone-500">Choose your perfect companion for the journey.</p>
            </div>
            <a href="#" className="hidden md:flex items-center gap-2 text-teal-700 font-bold hover:gap-4 transition-all">
              View all vehicles <ChevronRight size={20} />
            </a>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {fleet.map((v, i) => (
              <motion.div 
                key={v.id}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="group bg-stone-50 rounded-3xl p-6 border border-stone-100 hover:border-teal-200 hover:shadow-xl hover:shadow-teal-900/5 transition-all duration-300"
              >
                <div className="relative h-48 bg-white rounded-2xl mb-6 flex items-center justify-center text-8xl shadow-sm group-hover:scale-105 transition-transform duration-500">
                  <span className="absolute top-4 left-4 bg-stone-900 text-white text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wider">{v.tag}</span>
                  {v.img}
                </div>
                <div className="mb-4">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="text-xl font-bold text-stone-900">{v.name}</h3>
                    <div className="flex items-center gap-1 text-xs font-bold text-stone-900">
                      <Star size={12} className="fill-yellow-400 text-yellow-400" /> {v.rating}
                    </div>
                  </div>
                  <p className="text-stone-500 text-sm">{v.type}</p>
                </div>
                <div className="flex items-center justify-between pt-4 border-t border-stone-200">
                  <div>
                    <span className="text-xs text-stone-400 block">Starting from</span>
                    <span className="text-lg font-bold text-teal-700">IDR {v.price}<span className="text-xs text-stone-500 font-normal">/day</span></span>
                  </div>
                  <button className="bg-stone-900 text-white p-3 rounded-xl hover:bg-teal-700 transition-colors">
                    <ChevronRight size={20} />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust Section */}
      <section className="py-24 bg-stone-900 text-white relative overflow-hidden">
        <div className="absolute top-0 right-0 w-1/3 h-full bg-teal-900/20 blur-3xl" />
        <div className="container mx-auto px-6 relative z-10">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            {[
              { icon: <ShieldCheck size={32} />, title: "Fully Insured", desc: "Ride without worry. Comprehensive coverage included." },
              { icon: <MessageCircle size={32} />, title: "24/7 Support", desc: "Local team ready to help via WhatsApp anytime." },
              { icon: <MapPin size={32} />, title: "Free Delivery", desc: "We bring the bike to your hotel, villa, or arrival gate." }
            ].map((f, i) => (
              <div key={i} className="p-8 rounded-3xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors">
                <div className="inline-block text-teal-400 mb-6 p-4 bg-teal-900/30 rounded-2xl">{f.icon}</div>
                <h3 className="text-2xl font-bold mb-3">{f.title}</h3>
                <p className="text-stone-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-stone-950 py-12 border-t border-stone-900 text-center">
        <div className="flex justify-center gap-6 mb-6 text-stone-400">
          <MessageCircle size={24} className="hover:text-white cursor-pointer transition-colors" />
        </div>
        <p className="text-stone-600 text-sm">© 2026 BALIRIDE. Designed by <span className="text-teal-700 font-bold">Sifu Xibu</span>.</p>
      </footer>
    </div>
  );
}