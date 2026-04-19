"""
Force A2DP profile on all Bluetooth audio cards.

Can be run standalone or imported and called from other modules.
Monitors for new BlueZ cards and switches them from audio-gateway
(HSP/HFP) to a2dp-sink or a2dp-source when available.

Usage:
    sudo python3 force_a2dp.py              # one-shot: force now
    sudo python3 force_a2dp.py --watch      # watch for new devices and force continuously
"""

import subprocess
import re
import time
import argparse
import sys


A2DP_PROFILES = ["a2dp-sink", "a2dp_sink", "a2dp-source", "a2dp_source"]
UNWANTED_PROFILES = ["audio-gateway", "headset-head-unit", "headset_head_unit"]


def _pactl(*args):
    result = subprocess.run(
        ["pactl"] + list(args),
        capture_output=True, text=True
    )
    return result


def get_bluez_cards():
    """Return list of dicts for each bluez card with name, active profile, and available profiles."""
    result = _pactl("list", "cards")
    if result.returncode != 0:
        print(f"ERROR: pactl list cards failed: {result.stderr.strip()}")
        return []

    cards = []
    current = None
    in_profiles = False
    in_active = False

    for line in result.stdout.splitlines():
        stripped = line.strip()

        if stripped.startswith("Card #"):
            if current:
                cards.append(current)
            current = {
                "index": stripped.split("#")[1],
                "name": "",
                "active_profile": "",
                "profiles": []
            }
            in_profiles = False
            in_active = False

        elif current is not None:
            if stripped.startswith("Name:"):
                current["name"] = stripped.split(":", 1)[1].strip()
            elif stripped.startswith("Profiles:"):
                in_profiles = True
                in_active = False
            elif stripped.startswith("Active Profile:"):
                current["active_profile"] = stripped.split(":", 1)[1].strip()
                in_profiles = False
                in_active = False
            elif in_profiles:
                if stripped and not stripped.startswith("Properties:") and not stripped.startswith("Ports:"):
                    # Profile lines look like: "a2dp-sink: ... (sinks: 1, sources: 0, ...)"
                    match = re.match(r"^(\S+):", stripped)
                    if match:
                        current["profiles"].append(match.group(1))
                else:
                    in_profiles = False

    if current:
        cards.append(current)

    # Filter to only bluez cards
    return [c for c in cards if "bluez_card" in c.get("name", "")]


def force_a2dp_on_card(card):
    """Attempt to switch a single card to an A2DP profile. Returns True if switched."""
    name = card["name"]
    active = card["active_profile"]
    profiles = card["profiles"]

    # Already on A2DP?
    for p in A2DP_PROFILES:
        if p == active:
            print(f"  {name}: already on A2DP profile '{active}'")
            return True

    # Find an A2DP profile to switch to
    target = None
    for p in A2DP_PROFILES:
        if p in profiles:
            target = p
            break

    if target is None:
        print(f"  {name}: NO A2DP profile available. Profiles: {profiles}")
        print(f"    Active: {active}")
        print(f"    This likely means the SPA bluetooth plugin is missing or")
        print(f"    the device doesn't support A2DP from the Pi's perspective.")
        return False

    print(f"  {name}: switching {active} -> {target} ...")
    result = _pactl("set-card-profile", name, target)
    if result.returncode == 0:
        print(f"  {name}: successfully switched to '{target}'")
        return True
    else:
        print(f"  {name}: FAILED to switch: {result.stderr.strip()}")
        return False


def force_a2dp_all():
    """Force A2DP on all currently connected Bluetooth cards."""
    cards = get_bluez_cards()
    if not cards:
        print("No Bluetooth audio cards found.")
        return 0

    print(f"Found {len(cards)} Bluetooth card(s):")
    switched = 0
    for card in cards:
        if force_a2dp_on_card(card):
            switched += 1
    return switched


def watch_and_force(interval=3):
    """Continuously monitor for Bluetooth cards and force A2DP."""
    print(f"Watching for Bluetooth devices (checking every {interval}s)...")
    print("Press Ctrl+C to stop.\n")
    seen = set()
    try:
        while True:
            cards = get_bluez_cards()
            for card in cards:
                name = card["name"]
                active = card["active_profile"]
                is_a2dp = any(p == active for p in A2DP_PROFILES)

                if name not in seen:
                    seen.add(name)
                    print(f"\n[new] Detected: {name} (profile: {active})")
                    if not is_a2dp:
                        force_a2dp_on_card(card)
                elif not is_a2dp and any(p in active for p in UNWANTED_PROFILES):
                    print(f"\n[drift] {name} drifted to '{active}', re-forcing A2DP...")
                    force_a2dp_on_card(card)

            # Remove cards that disappeared
            current_names = {c["name"] for c in cards}
            gone = seen - current_names
            for g in gone:
                print(f"\n[gone] {g} disconnected")
                seen.discard(g)

            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nStopped watching.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Force A2DP profile on Bluetooth cards")
    parser.add_argument("--watch", action="store_true",
                        help="Continuously watch and force A2DP on new connections")
    parser.add_argument("--interval", type=int, default=3,
                        help="Seconds between checks in watch mode (default: 3)")
    args = parser.parse_args()

    if args.watch:
        watch_and_force(interval=args.interval)
    else:
        force_a2dp_all()
