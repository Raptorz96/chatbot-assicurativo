// 🎨 TEST PAGE - Design System Demo & Components Showcase
import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Button, 
  PrimaryButton, 
  SecondaryButton, 
  GhostButton, 
  DangerButton,
  SuccessButton 
} from '@/components/ui/Button'

// Icons
import { 
  PaperAirplaneIcon,
  CogIcon,
  TrashIcon,
  CheckIcon,
  ArrowRightIcon,
  HeartIcon
} from '@heroicons/react/24/outline'

// 🎭 ANIMATION VARIANTS
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
}

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 }
}

export const TestPage: React.FC = () => {
  const [loading, setLoading] = useState(false)
  const [counter, setCounter] = useState(0)

  // 🔄 Simula loading
  const handleLoadingTest = () => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
      setCounter(prev => prev + 1)
    }, 2000)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-primary-50/30 to-accent-50/20 p-8">
      <motion.div
        className="max-w-6xl mx-auto"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* 🎯 HEADER */}
        <motion.div variants={itemVariants} className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gradient-primary mb-4">
            Chatbot Assicurativo UI 2025
          </h1>
          <p className="text-xl text-neutral-600 max-w-2xl mx-auto">
            Sistema di design enterprise con glassmorphism, micro-animations e TypeScript
          </p>
        </motion.div>

        {/* 🔘 BUTTON SHOWCASE */}
        <motion.section variants={itemVariants} className="glass-card mb-8">
          <h2 className="text-2xl font-semibold mb-6 text-neutral-900">
            Button System
          </h2>
          
          {/* Variants */}
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-3 text-neutral-700">Variants</h3>
              <div className="flex flex-wrap gap-4">
                <PrimaryButton 
                  onClick={() => console.log('Primary clicked')}
                  icon={<PaperAirplaneIcon className="w-4 h-4" />}
                >
                  Primary
                </PrimaryButton>
                
                <SecondaryButton 
                  icon={<CogIcon className="w-4 h-4" />}
                  iconPosition="right"
                >
                  Secondary
                </SecondaryButton>
                
                <GhostButton onClick={() => setCounter(prev => prev + 1)}>
                  Ghost ({counter})
                </GhostButton>
                
                <SuccessButton 
                  icon={<CheckIcon className="w-4 h-4" />}
                >
                  Success
                </SuccessButton>
                
                <DangerButton 
                  icon={<TrashIcon className="w-4 h-4" />}
                >
                  Danger
                </DangerButton>
              </div>
            </div>

            {/* Sizes */}
            <div>
              <h3 className="text-lg font-medium mb-3 text-neutral-700">Sizes</h3>
              <div className="flex flex-wrap items-end gap-4">
                <PrimaryButton size="sm">Small</PrimaryButton>
                <PrimaryButton size="md">Medium</PrimaryButton>
                <PrimaryButton size="lg">Large</PrimaryButton>
                <PrimaryButton size="xl">Extra Large</PrimaryButton>
              </div>
            </div>

            {/* States */}
            <div>
              <h3 className="text-lg font-medium mb-3 text-neutral-700">States</h3>
              <div className="flex flex-wrap gap-4">
                <PrimaryButton 
                  loading={loading} 
                  onClick={handleLoadingTest}
                >
                  {loading ? 'Caricamento...' : 'Test Loading'}
                </PrimaryButton>
                
                <SecondaryButton disabled>
                  Disabled
                </SecondaryButton>
                
                <SuccessButton 
                  fullWidth 
                  className="max-w-xs"
                  icon={<HeartIcon className="w-4 h-4" />}
                >
                  Full Width
                </SuccessButton>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 🌟 GLASSMORPHISM SHOWCASE */}
        <motion.section variants={itemVariants} className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {/* Glass Card 1 */}
          <div className="glass-card hover:shadow-lg transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
                <PaperAirplaneIcon className="w-5 h-5 text-primary-600" />
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">Messaggi Oggi</h3>
                <p className="text-2xl font-bold text-primary-600">1,234</p>
              </div>
            </div>
            <p className="text-sm text-neutral-600">
              +12% rispetto a ieri
            </p>
          </div>

          {/* Glass Card 2 */}
          <div className="glass-card hover:shadow-lg transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-accent-100 rounded-lg flex items-center justify-center mr-3">
                <CheckIcon className="w-5 h-5 text-accent-600" />
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">Risposte RAG</h3>
                <p className="text-2xl font-bold text-accent-600">89%</p>
              </div>
            </div>
            <p className="text-sm text-neutral-600">
              Accuracy rate
            </p>
          </div>

          {/* Glass Card 3 */}
          <div className="glass-card hover:shadow-lg transition-all duration-300">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-warning-100 rounded-lg flex items-center justify-center mr-3">
                <CogIcon className="w-5 h-5 text-warning-600" />
              </div>
              <div>
                <h3 className="font-semibold text-neutral-900">Uptime</h3>
                <p className="text-2xl font-bold text-warning-600">99.9%</p>
              </div>
            </div>
            <p className="text-sm text-neutral-600">
              Sistema stabile
            </p>
          </div>
        </motion.section>

        {/* 🎨 COLOR PALETTE */}
        <motion.section variants={itemVariants} className="glass-card mb-8">
          <h2 className="text-2xl font-semibold mb-6 text-neutral-900">
            Color Palette
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {/* Primary Colors */}
            <div>
              <h3 className="font-medium mb-3 text-neutral-700">Primary</h3>
              <div className="space-y-2">
                <div className="h-8 bg-primary-100 rounded flex items-center px-3 text-primary-900 text-sm">100</div>
                <div className="h-8 bg-primary-300 rounded flex items-center px-3 text-primary-900 text-sm">300</div>
                <div className="h-8 bg-primary-500 rounded flex items-center px-3 text-white text-sm">500</div>
                <div className="h-8 bg-primary-700 rounded flex items-center px-3 text-white text-sm">700</div>
                <div className="h-8 bg-primary-900 rounded flex items-center px-3 text-white text-sm">900</div>
              </div>
            </div>

            {/* Accent Colors */}
            <div>
              <h3 className="font-medium mb-3 text-neutral-700">Accent</h3>
              <div className="space-y-2">
                <div className="h-8 bg-accent-100 rounded flex items-center px-3 text-accent-900 text-sm">100</div>
                <div className="h-8 bg-accent-300 rounded flex items-center px-3 text-accent-900 text-sm">300</div>
                <div className="h-8 bg-accent-500 rounded flex items-center px-3 text-white text-sm">500</div>
                <div className="h-8 bg-accent-700 rounded flex items-center px-3 text-white text-sm">700</div>
                <div className="h-8 bg-accent-900 rounded flex items-center px-3 text-white text-sm">900</div>
              </div>
            </div>

            {/* Warning Colors */}
            <div>
              <h3 className="font-medium mb-3 text-neutral-700">Warning</h3>
              <div className="space-y-2">
                <div className="h-8 bg-warning-100 rounded flex items-center px-3 text-warning-900 text-sm">100</div>
                <div className="h-8 bg-warning-300 rounded flex items-center px-3 text-warning-900 text-sm">300</div>
                <div className="h-8 bg-warning-500 rounded flex items-center px-3 text-white text-sm">500</div>
                <div className="h-8 bg-warning-700 rounded flex items-center px-3 text-white text-sm">700</div>
                <div className="h-8 bg-warning-900 rounded flex items-center px-3 text-white text-sm">900</div>
              </div>
            </div>

            {/* Neutral Colors */}
            <div>
              <h3 className="font-medium mb-3 text-neutral-700">Neutral</h3>
              <div className="space-y-2">
                <div className="h-8 bg-neutral-100 rounded flex items-center px-3 text-neutral-900 text-sm">100</div>
                <div className="h-8 bg-neutral-300 rounded flex items-center px-3 text-neutral-900 text-sm">300</div>
                <div className="h-8 bg-neutral-500 rounded flex items-center px-3 text-white text-sm">500</div>
                <div className="h-8 bg-neutral-700 rounded flex items-center px-3 text-white text-sm">700</div>
                <div className="h-8 bg-neutral-900 rounded flex items-center px-3 text-white text-sm">900</div>
              </div>
            </div>
          </div>
        </motion.section>

        {/* 🎭 ANIMATION EXAMPLES */}
        <motion.section variants={itemVariants} className="glass-card">
          <h2 className="text-2xl font-semibold mb-6 text-neutral-900">
            Animation Examples
          </h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            {/* Hover Lift */}
            <motion.div 
              className="p-6 bg-white rounded-xl shadow-soft cursor-pointer hover-lift"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              <h3 className="font-medium mb-2">Hover Lift</h3>
              <p className="text-sm text-neutral-600">
                Passa il mouse sopra per vedere l'effetto
              </p>
            </motion.div>

            {/* Scale Animation */}
            <motion.div 
              className="p-6 bg-gradient-primary text-white rounded-xl cursor-pointer"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <h3 className="font-medium mb-2">Scale</h3>
              <p className="text-sm opacity-90">
                Click per vedere scale animation
              </p>
            </motion.div>

            {/* Glow Effect */}
            <motion.div 
              className="p-6 bg-accent-500 text-white rounded-xl cursor-pointer hover-glow"
              whileHover={{ boxShadow: "0 0 30px rgba(34, 197, 94, 0.4)" }}
            >
              <h3 className="font-medium mb-2">Glow Effect</h3>
              <p className="text-sm opacity-90">
                Effetto glow su hover
              </p>
            </motion.div>
          </div>
        </motion.section>

        {/* 📱 Footer */}
        <motion.footer variants={itemVariants} className="text-center mt-12 py-8">
          <p className="text-neutral-600">
            🚀 Chatbot Assicurativo - Enterprise UI System 2025
          </p>
          <p className="text-sm text-neutral-500 mt-2">
            Built with React + TypeScript + Tailwind CSS + Framer Motion
          </p>
        </motion.footer>
      </motion.div>
    </div>
  )
}