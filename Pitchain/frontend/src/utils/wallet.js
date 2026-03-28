import { ethers } from 'ethers'

export const BASE_SEPOLIA_CHAIN_ID = 84532
export const BASE_SEPOLIA_HEX = '0x14A34'

export const BASE_SEPOLIA_CONFIG = {
  chainId: BASE_SEPOLIA_HEX,
  chainName: 'Base Sepolia Testnet',
  nativeCurrency: { name: 'Ethereum', symbol: 'ETH', decimals: 18 },
  rpcUrls: ['https://sepolia.base.org'],
  blockExplorerUrls: ['https://sepolia-explorer.base.org'],
}

/**
 * Finds the MetaMask EIP-1193 provider, even when Phantom (or other wallets)
 * is also installed and has overridden window.ethereum as the default.
 *
 * When multiple wallets coexist, EIP-5749 populates window.ethereum.providers[].
 * We specifically look for isMetaMask=true and exclude isPhantom=true.
 */
export function getMetaMaskProvider() {
  if (!window.ethereum) return null

  // Multiple wallets installed — pick MetaMask from the providers array
  if (window.ethereum.providers?.length) {
    return window.ethereum.providers.find((p) => p.isMetaMask && !p.isPhantom) ?? null
  }

  // Single wallet — make sure it's MetaMask, not Phantom in EVM mode
  if (window.ethereum.isMetaMask && !window.ethereum.isPhantom) {
    return window.ethereum
  }

  return null
}

/**
 * Connect MetaMask and switch to Base Sepolia.
 * Returns { provider, signer, address }
 * Throws a descriptive error if MetaMask is not found.
 */
export async function connectMetaMask() {
  const rawProvider = getMetaMaskProvider()
  if (!rawProvider) {
    throw new Error(
      'MetaMask not found.\n' +
      'If Phantom is your default wallet, go to Phantom → Settings → Default App Wallet → Always Ask, then refresh.\n' +
      'Or install MetaMask from https://metamask.io'
    )
  }

  const accounts = await rawProvider.request({ method: 'eth_requestAccounts' })
  const address = accounts[0]

  // Ensure Base Sepolia
  const chainId = await rawProvider.request({ method: 'eth_chainId' })
  if (chainId !== BASE_SEPOLIA_HEX) {
    try {
      await rawProvider.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: BASE_SEPOLIA_HEX }],
      })
    } catch (err) {
      if (err.code === 4902) {
        await rawProvider.request({
          method: 'wallet_addEthereumChain',
          params: [BASE_SEPOLIA_CONFIG],
        })
      } else throw err
    }
  }

  const provider = new ethers.BrowserProvider(rawProvider)
  const signer = await provider.getSigner()
  return { provider, signer, address }
}

export function shortAddress(addr) {
  return addr ? `${addr.slice(0, 6)}...${addr.slice(-4)}` : ''
}
