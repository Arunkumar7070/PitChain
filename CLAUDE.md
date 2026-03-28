# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PitChain is a decentralized Web3 fantasy cricket platform for IPL. Users connect MetaMask, pay Base Sepolia ETH entry fees, select 11 players, and winners receive prizes via smart contract automatically.

**Stack:** Django 4.2 + DRF + MySQL (backend) · React 18 + Vite + Tailwind (frontend) · Solidity on Base Sepolia (contracts)

---

## Development Commands

### Backend (Django)

```bash
cd Pitchain/backend
source venv/bin/activate

python manage.py runserver              # Start dev server on :8000
python manage.py makemigrations <app>   # Generate migrations for a specific app
python manage.py migrate                # Apply migrations
python manage.py test <app>             # Run tests for an app
python manage.py test accounts.tests.SpecificTestCase  # Run a single test
```

**Environment:** Settings are split — `base.py` + `development.py`. The active settings module is set via `DJANGO_SETTINGS_MODULE`. All secrets come from `.env` via `python-decouple`.

**Database:** MySQL. Requires `pitchain_db` to exist. Create it with:
```bash
mysql -u root -p<password> -e "CREATE DATABASE pitchain_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

**API Docs (Swagger):** `http://127.0.0.1:8000/api/docs/` — authenticate using a JWT `access` token from `/api/auth/token/`, paste the raw token (no "Bearer" prefix) into the Swagger auth dialog.

### Frontend (React + Vite)

```bash
cd Pitchain/frontend
npm install
npm run dev     # Start dev server on :3000 (proxies /api → :8000)
npm run build   # Production build
npm run lint    # ESLint
```

### Smart Contracts

Contracts live in `Pitchain/contracts/`. Compiled ABIs are in `Pitchain/contracts/artifacts/`. Deployed on Base Sepolia (chain ID: 84532). Contract address is set in `.env` as `CONTRACT_ADDRESS`.

---

## Architecture

### Backend App Structure

Each Django app follows the standard pattern: `models.py → serializers.py → views.py → urls.py`.

| App | Responsibility |
|-----|---------------|
| `accounts` | Custom `User` model with `wallet_address`; ECDSA wallet-based login; JWT issuance |
| `contests` | `Match`, `Contest`, `UserEntry`, `PrizeDistribution`, `AdminEarnings` models; contest lifecycle |
| `players` | `IPLTeam`, `Player`, `PlayerMatchStats`; fantasy scoring engine lives in `PlayerMatchStats.calculate_fantasy_points()` |
| `scores` | `PlayerScore`, `UserTeam`, `UserTeamPlayer`; captain ×2 / vice-captain ×1.5 point multipliers |
| `admin_panel` | Stub — placeholder for future admin endpoints |

**Key backend relationships:**
- `Match` → `Contest` (one match has many contests)
- `Contest` + `User` → `UserEntry` (unique per pair; stores JSON list of 11 player IDs)
- `Contest` + `Player` → `PlayerScore` (real performance stats used to score teams)
- `UserTeam` → `UserTeamPlayer` (11 rows per team; captain/VC flags drive multipliers)

**AUTH_USER_MODEL** is `accounts.User` with `db_table = 'users'`. Always run `makemigrations accounts` before other apps when setting up fresh.

### Frontend Structure

```
src/
  App.jsx          # All routes defined here
  utils/
    wallet.js      # MetaMask connect, Base Sepolia chain switching, getMetaMaskProvider()
    api.js         # Axios instance; auto-attaches JWT; handles 401 → token refresh → logout
  components/
    Navbar.jsx     # Wallet connect button, navigation
  pages/           # Home done; Contests/TeamBuilder/Leaderboard/Profile are stubs (TODO)
  context/         # Empty — add React context here when needed
  hooks/           # Empty — add custom hooks here
```

The Vite dev server proxies all `/api/*` requests to `http://localhost:8000`, so the frontend always uses relative `/api/` paths.

### Smart Contract

`PitchainContest.sol` handles:
- `createContest()` — admin creates contest on-chain
- `joinContest(contestId, teamHash)` — user pays entry fee; `teamHash` is the hashed team selection
- `distributePrizes()` — admin triggers; 5% fee goes to owner, remainder to winners

### Blockchain Integration

- **Frontend:** ethers.js v6 (`wallet.js`) for MetaMask and contract calls
- **Backend:** web3.py for reading contract state and verifying on-chain data
- Chain: Base Sepolia (chain ID 84532, RPC `https://sepolia.base.org`)
- Contract address configured via `CONTRACT_ADDRESS` in `.env` / `PITCHAIN_CONTRACT_ADDRESS` in settings

### API Endpoints

```
POST /api/accounts/wallet-login/          → ECDSA sign → JWT tokens
GET  /api/accounts/profile/               → Authenticated user profile

GET  /api/contests/                       → List contests (filter: ?status=)
GET  /api/contests/{id}/my_entry/         → Current user's entry for a contest
POST /api/contests/entries/               → Submit 11-player team + tx_hash

GET  /api/players/teams/                  → IPL teams
GET  /api/players/                        → Players (filter: ?team=, ?role=; search: ?search=)

GET  /api/scores/                         → Player scores (filter: ?contest=, ?player=)

GET  /api/docs/                           → Swagger UI
```

### Tailwind Custom Colors

| Token | Value | Use |
|-------|-------|-----|
| `pitchain-primary` | `#6366f1` | Primary actions, highlights |
| `pitchain-secondary` | `#f59e0b` | Accent, CTAs |
| `pitchain-dark` | `#0f172a` | Page background |
| `pitchain-card` | `#1e293b` | Card backgrounds |
| `pitchain-border` | `#334155` | Borders, dividers |

Shared utility classes: `.btn-primary`, `.btn-secondary`, `.input`, `.card` (defined in `index.css`).
