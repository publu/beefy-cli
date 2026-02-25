# Beefy CLI

Browse [Beefy Finance](https://beefy.finance) vaults across 35+ chains. APY breakdowns, TVL, fees, token search, protocol stats — with rich terminal UI.

Agent skill for [cryptoskills.sh](https://cryptoskills.sh/skill/beefy-cli).

## Install

```bash
curl -sL https://raw.githubusercontent.com/publu/beefy-cli/master/beefy_check.py -o /tmp/beefy_check.py
```

## Commands

```
vault <id>            Detailed vault info — APY breakdown, fees, TVL, risk, contracts
vaults <chain>        List all active vaults on a chain
top [n] [chain]       Top N vaults by APY (default 10, filters >$1k TVL)
search <token> [chain] Find vaults by token, platform, or ID
stats [chain]          Protocol overview
chains                 List supported chains with vault counts
```

## Examples

```bash
# Detailed vault view with rich box UI
python3 /tmp/beefy_check.py vault morpho-base-steakhouse-high-yield-usdc

# Browse all vaults on Base
python3 /tmp/beefy_check.py vaults base

# Top 10 vaults by APY
python3 /tmp/beefy_check.py top 10

# Search for USDC vaults on Base
python3 /tmp/beefy_check.py search USDC base

# Protocol stats
python3 /tmp/beefy_check.py stats

# List all chains
python3 /tmp/beefy_check.py chains
```

## Screenshot

```
  $ beefy-cli
  ✓ Connected to Beefy Finance

  ██████╗ ███████╗███████╗███████╗██╗   ██╗
  ██╔══██╗██╔════╝██╔════╝██╔════╝╚██╗ ██╔╝
  ██████╔╝█████╗  █████╗  █████╗   ╚████╔╝
  ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝    ╚██╔╝
  ██████╔╝███████╗███████╗██║        ██║
  ╚═════╝ ╚══════╝╚══════╝╚═╝        ╚═╝
                   Multichain Yield Optimizer

  beefy> vault morpho-base-steakhouse-high-yield-usdc

  ┌── morpho-base-steakhouse-high-yield-usdc ──────────┐
  │                                                     │
  │ Chain:           Base (8453)                         │
  │ Token:           USDC                                │
  │ Platform:        Morpho                              │
  │ TVL:             $156,432                            │
  │ Status:          ● Active                            │
  │                                                     │
  ├─────────────────────────────────────────────────────┤
  │                                                     │
  │ APY BREAKDOWN                                       │
  │                                                     │
  │ └─ Lending/trading:                        3.58%    │
  │                                                     │
  │ Compounds:       2190/yr (~6.0/day)                 │
  │ Total APY:       3.58%                              │
  │                                                     │
  ├─────────────────────────────────────────────────────┤
  │                                                     │
  │ Curator:         Steakhouse                         │
  │ Beefy fee:       9.50%                              │
  │ Risk:            ▓▓▓▓▓░░░ Medium                    │
  │                                                     │
  └─────────────────────────────────────────────────────┘
```

## Data Sources

All data from the [Beefy Finance API](https://api.beefy.finance) — no API keys needed.

- `/vaults/{chain}` — vault metadata
- `/apy/breakdown` — APY components
- `/tvl` — TVL by chain
- `/fees` — fee structure

## Requirements

Python 3.6+ — no external dependencies.
