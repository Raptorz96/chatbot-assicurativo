// Test minimal per debug layout
export const TestMinimal = () => {
  return (
    <div className="h-screen bg-slate-900 overflow-hidden">
      <div className="flex h-full max-w-7xl mx-auto">
        
        {/* LEFT PANEL */}
        <div className="w-1/2 h-full bg-blue-500/20 p-4">
          <div className="bg-white/10 p-4 rounded">
            <h1 className="text-white">LEFT PANEL</h1>
            <p className="text-white/60">Questo è il pannello sinistro</p>
          </div>
        </div>

        {/* RIGHT PANEL */}
        <div className="w-1/2 h-full bg-green-500/20 p-4">
          <div className="bg-white/10 p-4 rounded h-full">
            <h1 className="text-white">RIGHT PANEL</h1>
            <p className="text-white/60">Questo è il pannello destro</p>
            
            {/* Empty state message */}
            <div className="text-center mt-20">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-white text-lg font-bold mb-2">
                Test Layout Minimal
              </h3>
              <p className="text-white/60 text-sm">
                Se questo layout è stabile, il problema è in Framer Motion
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}