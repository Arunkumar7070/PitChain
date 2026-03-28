import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import Contests from './pages/Contests'
import TeamBuilder from './pages/TeamBuilder'
import Leaderboard from './pages/Leaderboard'
import Profile from './pages/Profile'

function App() {
  return (
    <div className="min-h-screen bg-pitchain-dark">
      <Navbar />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/contests" element={<Contests />} />
          <Route path="/team-builder/:contestId" element={<TeamBuilder />} />
          <Route path="/leaderboard/:contestId" element={<Leaderboard />} />
          <Route path="/profile" element={<Profile />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
