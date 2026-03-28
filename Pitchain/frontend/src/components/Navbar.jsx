import { Link } from 'react-router-dom'
import { useState } from 'react'

/**
 * Finds the MetaMask provider even when multiple wallets (e.g. Phantom) are installed.
 * When multiple EVM wallets exist they populate window.ethereum.providers[].
 */
function getMetaMaskProvider() {
  if (!window.ethereum) return null

  // Multiple wallets installed — find MetaMask specifically
  if (window.ethereum.providers?.length) {
    return window.ethereum.providers.find((p) => p.isMetaMask && !p.isPhantom) ?? null
  }

  // Only one wallet — check it's MetaMask (not Phantom pretending to be EVM)
  if (window.ethereum.isMetaMask && !window.ethereum.isPhantom) {
    return window.ethereum
  }

  return null
}

export default function Navbar() {
  const [walletAddress, setWalletAddress] = useState(null)
  const [connecting, setConnecting] = useState(false)

  const connectWallet = async () => {
    const provider = getMetaMaskProvider()
    if (!provider) {
      alert(
        'MetaMask not found.\n\n' +
        'If you have Phantom installed, go to Phantom → Settings → Default App Wallet → Always Ask, then refresh.\n\n' +
        'Or install MetaMask from metamask.io'
      )
      return
    }
    setConnecting(true)
    try {
      // Request account access via MetaMask specifically
      const accounts = await provider.request({ method: 'eth_requestAccounts' })

      // Switch to Base Sepolia (Chain ID: 84532) via MetaMask provider
      try {
        await provider.request({
          method: 'wallet_switchEthereumChain',
          params: [{ chainId: '0x14A34' }],
        })
      } catch (switchError) {
        if (switchError.code === 4902) {
          await provider.request({
            method: 'wallet_addEthereumChain',
            params: [{
              chainId: '0x14A34',
              chainName: 'Base Sepolia Testnet',
              nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
              rpcUrls: ['https://sepolia.base.org'],
              blockExplorerUrls: ['https://sepolia-explorer.base.org'],
            }],
          })
        }
      }

      setWalletAddress(accounts[0])
    } catch (err) {
      console.error('Wallet connection failed:', err)
    } finally {
      setConnecting(false)
    }
  }

  const shortAddress = (addr) => `${addr.slice(0, 6)}...${addr.slice(-4)}`

  return (
    <nav className="bg-pitchain-card border-b border-pitchain-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl">🏏</span>
            <span className="text-xl font-bold text-white">
              Pit<span className="text-pitchain-primary">chain</span>
            </span>
          </Link>

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/contests" className="text-slate-300 hover:text-white transition-colors text-sm font-medium">
              Contests
            </Link>
            <Link to="/profile" className="text-slate-300 hover:text-white transition-colors text-sm font-medium">
              My Teams
            </Link>
          </div>

          {/* Wallet Button */}
          <button
            onClick={walletAddress ? null : connectWallet}
            disabled={connecting}
            className={walletAddress
              ? 'flex items-center gap-2 bg-pitchain-dark border border-pitchain-border px-4 py-2 rounded-lg text-sm font-mono text-pitchain-primary cursor-default'
              : 'btn-primary text-sm'
            }
          >
            {connecting ? (
              <>
                <span className="animate-spin">⟳</span> Connecting...
              </>
            ) : walletAddress ? (
              <>
                <span className="w-2 h-2 bg-green-400 rounded-full inline-block"></span>
                {shortAddress(walletAddress)}
              </>
            ) : (
              'Connect MetaMask'
            )}
          </button>
        </div>
      </div>
    </nav>
  )
}
