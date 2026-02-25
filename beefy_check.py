#!/usr/bin/env python3
"""Beefy Finance CLI — multichain yield optimizer dashboard with rich terminal UI."""

import json
import sys
import urllib.request

# ── Beefy API ──────────────────────────────────────────────
API = "https://api.beefy.finance"

# Chain slug → numeric chain ID (for TVL lookups)
CHAIN_IDS = {
    "ethereum": 1, "polygon": 137, "bsc": 56, "avalanche": 43114, "fantom": 250,
    "arbitrum": 42161, "optimism": 10, "base": 8453, "sonic": 146, "moonbeam": 1284,
    "moonriver": 1285, "linea": 59144, "cronos": 25, "mantle": 5000, "fraxtal": 252,
    "gnosis": 100, "scroll": 534352, "zksync": 324, "zkevm": 1101, "mode": 34443,
    "lisk": 1135, "berachain": 80094, "monad": 143, "kava": 2222, "canto": 7700,
    "metis": 1088, "fuse": 122, "aurora": 1313161554, "one": 1666600000, "celo": 42220,
    "heco": 128, "emerald": 42262, "real": 111188, "rootstock": 30, "sei": 1329,
    "plasma": 7765, "hyperevm": 999,
}

# Reverse: chain ID → slug
ID_TO_CHAIN = {v: k for k, v in CHAIN_IDS.items()}

# ── ANSI Colors ────────────────────────────────────────────
GREEN = "\033[38;2;0;255;65m"
DIM_GREEN = "\033[38;2;0;160;40m"
ORANGE = "\033[38;2;255;165;0m"
YELLOW = "\033[38;2;255;255;0m"
WHITE = "\033[97m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"
BG = "\033[48;2;10;20;10m"

def g(s): return f"{GREEN}{s}{RESET}"
def dg(s): return f"{DIM_GREEN}{s}{RESET}"
def o(s): return f"{ORANGE}{s}{RESET}"
def w(s): return f"{WHITE}{BOLD}{s}{RESET}"
def y(s): return f"{YELLOW}{s}{RESET}"
def dim(s): return f"{DIM}{s}{RESET}"

# ── Box Drawing ────────────────────────────────────────────
BOX_TL = "┌"
BOX_TR = "┐"
BOX_BL = "└"
BOX_BR = "┘"
BOX_H  = "─"
BOX_V  = "│"
BOX_LT = "├"
BOX_RT = "┤"

def box_top(width, title=""):
    if title:
        inner = f" {title} "
        line = BOX_H * 2 + inner + BOX_H * (width - 4 - len(title))
    else:
        line = BOX_H * (width - 2)
    return dg(f"  {BOX_TL}{line}{BOX_TR}")

def box_mid(width):
    return dg(f"  {BOX_LT}{BOX_H * (width - 2)}{BOX_RT}")

def box_bottom(width):
    return dg(f"  {BOX_BL}{BOX_H * (width - 2)}{BOX_BR}")

def box_row(label, value, width, color_fn=g):
    pad = width - 6 - len(label) - len(str(value))
    return f"  {dg(BOX_V)} {dg(label + ':')}{' ' * max(pad, 1)}{color_fn(value)} {dg(BOX_V)}"

def box_empty(width):
    return f"  {dg(BOX_V)}{' ' * (width - 2)}{dg(BOX_V)}"

def box_text(text, width, color_fn=g):
    pad = width - 4 - len(text)
    return f"  {dg(BOX_V)} {color_fn(text)}{' ' * max(pad, 0)} {dg(BOX_V)}"

def box_kv(label, value, width, val_color=g):
    """Key-value row with aligned columns."""
    col1 = 16  # label column width
    l = f"{label}:"
    l_padded = l.ljust(col1)
    val_str = str(value)
    remaining = width - 4 - col1 - len(val_str)
    return f"  {dg(BOX_V)} {dg(l_padded)}{val_color(val_str)}{' ' * max(remaining, 0)} {dg(BOX_V)}"

# ── ASCII Art ──────────────────────────────────────────────
LOGO = r"""
 ██████╗ ███████╗███████╗███████╗██╗   ██╗
 ██╔══██╗██╔════╝██╔════╝██╔════╝╚██╗ ██╔╝
 ██████╔╝█████╗  █████╗  █████╗   ╚████╔╝
 ██╔══██╗██╔══╝  ██╔══╝  ██╔══╝    ╚██╔╝
 ██████╔╝███████╗███████╗██║        ██║
 ╚═════╝ ╚══════╝╚══════╝╚═╝        ╚═╝"""

def print_header(cmd_text=""):
    print()
    print(f"  {g('$')} {w('beefy-cli')}")
    print(f"  {g('✓')} {dg('Connected to Beefy Finance')}")
    for line in LOGO.strip().split("\n"):
        print(f"  {GREEN}{line}{RESET}")
    print(f"  {DIM_GREEN}{'Multichain Yield Optimizer':>43}{RESET}")
    if cmd_text:
        print()
        print(f"  {dg('beefy>')} {w(cmd_text)}")
    print()

# ── API Helpers ────────────────────────────────────────────
def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "beefy-cli/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())

def fetch_vaults(chain=None):
    url = f"{API}/vaults/{chain}" if chain else f"{API}/vaults"
    return fetch(url)

def fetch_apy_breakdown():
    return fetch(f"{API}/apy/breakdown")

def fetch_tvl():
    return fetch(f"{API}/tvl")

def fetch_fees(vault_id):
    try:
        data = fetch(f"{API}/fees")
        return data.get(vault_id)
    except Exception:
        return None

def fmt_usd(val):
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:,.2f}B"
    elif val >= 1_000_000:
        return f"${val / 1_000_000:,.2f}M"
    elif val >= 1_000:
        return f"${val:,.0f}"
    elif val >= 1:
        return f"${val:,.2f}"
    else:
        return f"${val:.2f}"

def fmt_pct(val):
    if val is None:
        return "—"
    return f"{val * 100:.2f}%" if abs(val) < 1 else f"{val:.2f}%"

def get_tvl_for_vault(tvl_data, chain_slug, vault_id):
    chain_id = CHAIN_IDS.get(chain_slug)
    if chain_id is None:
        return 0
    chain_tvl = tvl_data.get(str(chain_id), {})
    return chain_tvl.get(vault_id, 0)

def risk_label(vault):
    risks = vault.get("risks", [])
    # risks can be a list of strings or an object
    if isinstance(risks, dict):
        if risks.get("COMPLEXITY_LOW") or risks.get("BATTLE_TESTED") or risks.get("AUDIT"):
            return "Low", "▓▓▓▓░░░░"
        elif risks.get("COMPLEXITY_HIGH") or risks.get("NO_AUDIT"):
            return "High", "▓▓▓▓▓▓▓░"
        return "Medium", "▓▓▓▓▓░░░"
    if isinstance(risks, list):
        risk_set = set(risks)
        if "COMPLEXITY_LOW" in risk_set and "BATTLE_TESTED" in risk_set:
            return "Low", "▓▓░░░░░░"
        elif "COMPLEXITY_HIGH" in risk_set or "NO_AUDIT" in risk_set:
            return "High", "▓▓▓▓▓▓▓░"
        return "Medium", "▓▓▓▓▓░░░"
    return "Unknown", "░░░░░░░░"

# ── Commands ───────────────────────────────────────────────

def cmd_vault(args):
    """Show detailed info for a specific vault."""
    if not args:
        print(f"  {o('Usage:')} beefy_check.py vault <vault_id>")
        print(f"  {dim('Example: beefy_check.py vault morpho-base-steakhouse-high-yield-usdc')}")
        return

    query = args[0].lower()
    print_header(f"vault {args[0]}")

    # Fetch data
    vaults = fetch_vaults()
    apy_data = fetch_apy_breakdown()
    tvl_data = fetch_tvl()

    # Find vault — exact match first, then partial
    vault = None
    for v in vaults:
        if v["id"].lower() == query:
            vault = v
            break
    if not vault:
        matches = [v for v in vaults if query in v["id"].lower() and v.get("status") == "active"]
        if len(matches) == 1:
            vault = matches[0]
        elif len(matches) > 1:
            print(f"  {o('Multiple matches:')}")
            for m in matches[:10]:
                print(f"    {g('•')} {m['id']}")
            if len(matches) > 10:
                print(f"    {dim(f'... and {len(matches) - 10} more')}")
            return
        else:
            # try inactive too
            for v in vaults:
                if query in v["id"].lower():
                    vault = v
                    break

    if not vault:
        print(f"  {o('✗')} No vault found matching '{args[0]}'")
        return

    vid = vault["id"]
    chain = vault.get("chain", "?")
    chain_id = CHAIN_IDS.get(chain, "?")
    token = vault.get("token", "?")
    status = vault.get("status", "?")
    platform = vault.get("platformId", "?")
    strategy_type = vault.get("strategyTypeId", "?")
    earned_token = vault.get("earnedToken", "?")
    vault_addr = vault.get("earnContractAddress", "?")
    strategy_addr = vault.get("strategy", "?")
    token_addr = vault.get("tokenAddress", "?")
    curator = vault.get("curatorId", vault.get("curator", "—"))
    ppfs = vault.get("pricePerFullShare", "?")

    tvl = get_tvl_for_vault(tvl_data, chain, vid)
    apy_info = apy_data.get(vid, {})
    total_apy = apy_info.get("totalApy", 0) or 0
    vault_apr = apy_info.get("vaultApr", 0) or 0
    trading_apr = apy_info.get("tradingApr", 0) or 0
    lsd_apr = apy_info.get("liquidStakingApr", 0) or 0
    compounds = apy_info.get("compoundingsPerYear", 0) or 0
    beefy_fee = apy_info.get("beefyPerformanceFee", 0) or 0

    risk_text, risk_bar = risk_label(vault)

    print(f"  {g('✓')} {dg(earned_token)}")
    print()

    W = 52

    # Main info box
    print(box_top(W, vid))
    print(box_empty(W))
    print(box_kv("Chain", f"{chain.title()} ({chain_id})", W))
    print(box_kv("Token", token, W))
    print(box_kv("Platform", platform.title(), W))
    print(box_kv("Strategy", strategy_type, W))
    print(box_kv("TVL", fmt_usd(tvl), W, val_color=w))
    print(box_kv("Status", "● Active" if status == "active" else "○ EOL", W,
                  val_color=g if status == "active" else o))
    print(box_empty(W))
    print(box_mid(W))

    # APY Breakdown section
    print(box_empty(W))
    print(box_text("APY BREAKDOWN", W, color_fn=o))
    print(box_empty(W))

    # Show component APRs with tree branches
    components = []
    if vault_apr > 0:
        components.append(("Base vault", vault_apr))
    if trading_apr > 0:
        components.append(("Lending/trading", trading_apr))
    if lsd_apr > 0:
        components.append(("Liquid staking", lsd_apr))

    for i, (label, apr) in enumerate(components):
        is_last = (i == len(components) - 1)
        branch = "└" if is_last else "├"
        line = f"{branch}─ {label}:"
        val = fmt_pct(apr)
        pad = W - 6 - len(line) - len(val)
        print(f"  {dg(BOX_V)} {o(line)}{' ' * max(pad, 1)}{o(val)} {dg(BOX_V)}")

    if not components:
        line = "└─ Yield:"
        val = fmt_pct(total_apy)
        pad = W - 6 - len(line) - len(val)
        print(f"  {dg(BOX_V)} {o(line)}{' ' * max(pad, 1)}{o(val)} {dg(BOX_V)}")

    print(box_empty(W))

    # Autocompound info
    if compounds > 0:
        daily = compounds / 365
        comp_text = f"{int(compounds)}/yr (~{daily:.1f}/day)"
        print(box_kv("Compounds", comp_text, W))

    print(box_kv("Total APY", fmt_pct(total_apy), W, val_color=y))
    print(box_empty(W))
    print(box_mid(W))

    # Curator / Risk / Fees
    print(box_empty(W))
    if curator and curator != "—":
        print(box_kv("Curator", curator.replace("-", " ").title(), W))
    print(box_kv("Beefy fee", fmt_pct(beefy_fee), W))
    risk_display = f"{risk_bar} {risk_text}"
    print(box_kv("Risk", risk_display, W, val_color=g if risk_text == "Low" else o))
    print(box_empty(W))
    print(box_bottom(W))

    # Contract addresses (below box, dimmed)
    print()
    print(f"  {dim('Vault:    ' + str(vault_addr))}")
    print(f"  {dim('Strategy: ' + str(strategy_addr))}")
    print(f"  {dim('Token:    ' + str(token_addr))}")
    print()


def cmd_vaults(args):
    """List active vaults on a chain."""
    chain = args[0].lower() if args else None

    if not chain:
        print(f"  {o('Usage:')} beefy_check.py vaults <chain>")
        print(f"  {dim('Example: beefy_check.py vaults base')}")
        print(f"  {dim('Run \"beefy_check.py chains\" to see available chains')}")
        return

    print_header(f"vaults {chain}")

    vaults = fetch_vaults(chain)
    apy_data = fetch_apy_breakdown()
    tvl_data = fetch_tvl()

    active = [v for v in vaults if v.get("status") == "active"]
    active_with_data = []

    for v in active:
        vid = v["id"]
        apy_info = apy_data.get(vid, {})
        total_apy = (apy_info.get("totalApy") or 0)
        tvl = get_tvl_for_vault(tvl_data, chain, vid)
        active_with_data.append((v, total_apy, tvl))

    # Sort by TVL descending
    active_with_data.sort(key=lambda x: x[2], reverse=True)

    if not active_with_data:
        print(f"  {o('✗')} No active vaults on {chain}")
        return

    total_tvl = sum(t for _, _, t in active_with_data)

    print(f"  {g('✓')} {w(str(len(active_with_data)))} {dg('active vaults')}")
    print(f"  {dg('Total TVL:')} {w(fmt_usd(total_tvl))}")
    print()

    # Table header
    hdr = f"  {dg('Vault'):<52} {dg('Token'):<10} {dg('APY'):>10} {dg('TVL'):>14}"
    print(hdr)
    print(f"  {DIM_GREEN}{'─' * 80}{RESET}")

    shown = min(len(active_with_data), 30)
    for v, apy, tvl in active_with_data[:shown]:
        vid = v["id"]
        token = v.get("token", "?")
        name = vid[:40]
        apy_str = fmt_pct(apy) if apy > 0 else "—"
        tvl_str = fmt_usd(tvl) if tvl > 0 else "—"

        apy_color = o if apy > 0.05 else g
        print(f"  {g(name):<52} {dg(token):<10} {apy_color(apy_str):>18} {w(tvl_str):>22}")

    if len(active_with_data) > shown:
        print(f"  {dim(f'... and {len(active_with_data) - shown} more')}")
    print()


def cmd_top(args):
    """Show top vaults by APY."""
    n = 10
    chain = None

    for arg in args:
        try:
            n = int(arg)
        except ValueError:
            chain = arg.lower()

    print_header(f"top {n}" + (f" {chain}" if chain else ""))

    if chain:
        vaults = fetch_vaults(chain)
    else:
        vaults = fetch_vaults()

    apy_data = fetch_apy_breakdown()
    tvl_data = fetch_tvl()

    active = [v for v in vaults if v.get("status") == "active"]

    ranked = []
    for v in active:
        vid = v["id"]
        apy_info = apy_data.get(vid, {})
        total_apy = (apy_info.get("totalApy") or 0)
        # Filter out absurd APYs (data anomalies)
        if total_apy > 10:  # >1000% is likely bad data
            continue
        tvl = get_tvl_for_vault(tvl_data, v.get("chain", ""), vid)
        # Only show vaults with meaningful TVL
        if tvl < 1000:
            continue
        ranked.append((v, total_apy, tvl))

    ranked.sort(key=lambda x: x[1], reverse=True)
    ranked = ranked[:n]

    if not ranked:
        print(f"  {o('✗')} No vaults found")
        return

    print(f"  {g('✓')} Top {w(str(n))} {dg('vaults by APY')} {dg('(TVL > $1k)')}")
    print()

    hdr = f"  {dg('#'):<5} {dg('Vault'):<40} {dg('Chain'):<12} {dg('APY'):>10} {dg('TVL'):>14}"
    print(hdr)
    print(f"  {DIM_GREEN}{'─' * 85}{RESET}")

    for i, (v, apy, tvl) in enumerate(ranked, 1):
        vid = v["id"][:35]
        ch = v.get("chain", "?")
        apy_str = fmt_pct(apy)
        tvl_str = fmt_usd(tvl)
        num_color = o if i <= 3 else g

        print(f"  {num_color(str(i)):<13} {g(vid):<48} {dg(ch):<12} {o(apy_str):>18} {w(tvl_str):>22}")

    print()


def cmd_search(args):
    """Search vaults by token name."""
    if not args:
        print(f"  {o('Usage:')} beefy_check.py search <token> [chain]")
        print(f"  {dim('Example: beefy_check.py search USDC base')}")
        return

    query = args[0].lower()
    chain = args[1].lower() if len(args) > 1 else None

    print_header(f"search {args[0]}" + (f" {chain}" if chain else ""))

    if chain:
        vaults = fetch_vaults(chain)
    else:
        vaults = fetch_vaults()

    apy_data = fetch_apy_breakdown()
    tvl_data = fetch_tvl()

    matches = []
    for v in vaults:
        if v.get("status") != "active":
            continue
        # Search in token, id, assets, name, platformId
        searchable = " ".join([
            v.get("token", ""),
            v.get("id", ""),
            v.get("name", ""),
            v.get("platformId", ""),
            " ".join(v.get("assets", [])),
        ]).lower()
        if query in searchable:
            vid = v["id"]
            apy_info = apy_data.get(vid, {})
            total_apy = (apy_info.get("totalApy") or 0)
            tvl = get_tvl_for_vault(tvl_data, v.get("chain", ""), vid)
            matches.append((v, total_apy, tvl))

    matches.sort(key=lambda x: x[2], reverse=True)

    if not matches:
        print(f"  {o('✗')} No active vaults matching '{args[0]}'")
        return

    print(f"  {g('✓')} {w(str(len(matches)))} {dg('vaults matching')} {w(args[0])}")
    print()

    hdr = f"  {dg('Vault'):<48} {dg('Chain'):<10} {dg('APY'):>10} {dg('TVL'):>14}"
    print(hdr)
    print(f"  {DIM_GREEN}{'─' * 85}{RESET}")

    shown = min(len(matches), 25)
    for v, apy, tvl in matches[:shown]:
        vid = v["id"][:40]
        ch = v.get("chain", "?")
        apy_str = fmt_pct(apy) if apy > 0 else "—"
        tvl_str = fmt_usd(tvl) if tvl > 0 else "—"

        print(f"  {g(vid):<56} {dg(ch):<10} {o(apy_str):>18} {w(tvl_str):>22}")

    if len(matches) > shown:
        print(f"  {dim(f'... and {len(matches) - shown} more')}")
    print()


def cmd_stats(args):
    """Protocol-level stats."""
    chain = args[0].lower() if args else None

    print_header(f"stats" + (f" {chain}" if chain else ""))

    if chain:
        vaults = fetch_vaults(chain)
    else:
        vaults = fetch_vaults()

    apy_data = fetch_apy_breakdown()
    tvl_data = fetch_tvl()

    active = [v for v in vaults if v.get("status") == "active"]
    eol = [v for v in vaults if v.get("status") == "eol"]

    chains = set(v.get("chain", "?") for v in active)
    platforms = set(v.get("platformId", "?") for v in active)

    # Compute TVL and APY stats
    total_tvl = 0
    apys = []
    for v in active:
        vid = v["id"]
        tvl = get_tvl_for_vault(tvl_data, v.get("chain", ""), vid)
        total_tvl += tvl
        apy_info = apy_data.get(vid, {})
        total_apy = (apy_info.get("totalApy") or 0)
        if 0 < total_apy < 10:
            apys.append((total_apy, v))

    avg_apy = sum(a for a, _ in apys) / max(len(apys), 1)
    best = max(apys, key=lambda x: x[0]) if apys else None

    # Find biggest vault by TVL
    biggest_tvl = 0
    biggest_vault = None
    for v in active:
        vid = v["id"]
        tvl = get_tvl_for_vault(tvl_data, v.get("chain", ""), vid)
        if tvl > biggest_tvl:
            biggest_tvl = tvl
            biggest_vault = v

    W = 52

    print(box_top(W, "Protocol Stats"))
    print(box_empty(W))
    print(box_kv("Total TVL", fmt_usd(total_tvl), W, val_color=w))
    print(box_kv("Active vaults", str(len(active)), W))
    print(box_kv("EOL vaults", str(len(eol)), W))
    print(box_kv("Chains", str(len(chains)), W))
    print(box_kv("Protocols", str(len(platforms)), W))
    print(box_empty(W))
    print(box_mid(W))
    print(box_empty(W))
    print(box_kv("Avg APY", fmt_pct(avg_apy), W, val_color=o))

    if best:
        best_apy, best_v = best
        best_name = f"{fmt_pct(best_apy)} ({best_v['token']} on {best_v.get('chain', '?')})"
        # Manually format to fit
        label = "Best APY:"
        pad = W - 4 - len(label) - 1
        # Truncate if needed
        if len(best_name) > pad:
            best_name = best_name[:pad - 1]
        remaining = W - 4 - len(label) - len(best_name) - 1
        print(f"  {dg(BOX_V)} {dg(label)} {y(best_name)}{' ' * max(remaining, 0)} {dg(BOX_V)}")

    if biggest_vault:
        big_name = f"{fmt_usd(biggest_tvl)} ({biggest_vault['token']} on {biggest_vault.get('chain', '?')})"
        label = "Largest:"
        if len(big_name) > W - 6 - len(label):
            big_name = big_name[:W - 7 - len(label)]
        remaining = W - 4 - len(label) - len(big_name) - 1
        print(f"  {dg(BOX_V)} {dg(label)}  {w(big_name)}{' ' * max(remaining, 0)} {dg(BOX_V)}")

    print(box_empty(W))

    # Top chains by TVL
    print(box_mid(W))
    print(box_empty(W))
    print(box_text("TOP CHAINS BY TVL", W, color_fn=o))
    print(box_empty(W))

    chain_tvls = {}
    for v in active:
        ch = v.get("chain", "?")
        tvl = get_tvl_for_vault(tvl_data, ch, v["id"])
        chain_tvls[ch] = chain_tvls.get(ch, 0) + tvl

    sorted_chains = sorted(chain_tvls.items(), key=lambda x: x[1], reverse=True)[:8]
    for ch, tvl in sorted_chains:
        print(box_kv(ch.title(), fmt_usd(tvl), W))

    print(box_empty(W))
    print(box_bottom(W))
    print()


def cmd_chains(args):
    """List supported chains with vault counts."""
    print_header("chains")

    vaults = fetch_vaults()
    active = [v for v in vaults if v.get("status") == "active"]

    chain_counts = {}
    for v in active:
        ch = v.get("chain", "?")
        chain_counts[ch] = chain_counts.get(ch, 0) + 1

    sorted_chains = sorted(chain_counts.items(), key=lambda x: x[1], reverse=True)

    print(f"  {g('✓')} {w(str(len(sorted_chains)))} {dg('chains supported')}")
    print()

    W = 42

    print(box_top(W, "Chains"))
    print(box_empty(W))

    for ch, count in sorted_chains:
        chain_id = CHAIN_IDS.get(ch, "?")
        val = f"{count} vaults"
        label = f"{ch.title()} ({chain_id})"
        if len(label) > 20:
            label = label[:20]
        pad = W - 4 - len(label) - len(val) - 1
        print(f"  {dg(BOX_V)} {g(label)}{' ' * max(pad, 1)}{dg(val)} {dg(BOX_V)}")

    print(box_empty(W))
    print(box_bottom(W))
    print()


# ── CLI Entry ──────────────────────────────────────────────

COMMANDS = {
    "vault": (cmd_vault, "Detailed vault info <vault_id>"),
    "vaults": (cmd_vaults, "List active vaults <chain>"),
    "top": (cmd_top, "Top vaults by APY [n] [chain]"),
    "search": (cmd_search, "Search vaults <token> [chain]"),
    "stats": (cmd_stats, "Protocol stats [chain]"),
    "chains": (cmd_chains, "List supported chains"),
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print_header()
        print(f"  {w('Usage:')} beefy_check.py <command> [args]")
        print()
        for name, (_, desc) in COMMANDS.items():
            print(f"    {g(name):<20} {dg(desc)}")
        print()
        sys.exit(1)

    cmd = sys.argv[1]
    fn, _ = COMMANDS[cmd]
    fn(sys.argv[2:])


if __name__ == "__main__":
    main()
