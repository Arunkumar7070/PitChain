export default function Home() {
  return (
    <div className="text-center py-20">
      <h1 className="text-5xl font-extrabold mb-4">
        🏏 Welcome to <span className="text-pitchain-primary">Pitchain</span>
      </h1>
      <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
        The decentralised Web3 fantasy cricket platform built for IPL.
        Pay entry fees in ETH, build your squad, and win on-chain rewards — no middlemen.
      </p>
      <a href="/contests" className="btn-primary text-lg px-10 py-3 inline-block rounded-lg">
        View Contests →
      </a>
    </div>
  )
}
