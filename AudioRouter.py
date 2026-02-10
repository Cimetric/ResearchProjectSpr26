import os
import sys
import time
import signal
import subprocess

DEVICE_NAME = "raspberrypi"
USB_AUDIO_DEVICE = "Razer Kraken Kitty V2"  # Set to "default" to use the default audio device
DISCOVERABLE = True
PAIRABLE = True


import dbus
import dbus.mainloop.glib
from gi.repository import GLib

class BTAudioRouter:
    def __init__(self):
        self.mainloop = None
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def signal_handler(self, signum, frame):
        print("Exiting the D-Bus service...")
        self.stop()
        sys.exit(0)

    def run_command(self, cmd): 
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def setup_BT(self):
        print("Setting up Bluetooth audio routing...")

        try:
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            bus = dbus.SystemBus()

            manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")

            adapter_path = None
            for path, interfaces in manager.GetManagedObjects().items():
                if "org.bluez.Adapter1" in interfaces:
                    adapter_path = path
                    break
            if not adapter_path:
                print("ERROR: No Bluetooth adapter found.")
                return False
            adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.freedesktop.DBus.Properties")

            adapter.Set("org.bluez.Adapter1", "Powered", dbus.Boolean(True))
            adapter.Set("org.bluez.Adapter1", "Alias", dbus.String(DEVICE_NAME))
            adapter.Set("org.bluez.Adapter1", "Discoverable", dbus.Boolean(DISCOVERABLE))
            adapter.Set("org.bluez.Adapter1", "Pairable", dbus.Boolean(PAIRABLE))

            print(f"Bluetooth adapter configured successfully. Configured as: '{DEVICE_NAME}'")
            return True
        except Exception as e:
            print(f"ERROR: Failed to set up Bluetooth audio routing: {e}")
            return False

    def setup_audio(self):
        
        print("Setting up audio routing...")

        print("   Restarting PulseAudio to apply changes...")
        subprocess.run(['pulseaudio', '-k'], capture_output=True)
        time.sleep(1)
        subprocess.run(['pulseaudio', '--start'], capture_output=True)
        time.sleep(2)

        print("   Loading Bluetooth audio modules...")
        self.run_command(['pactl', 'load-module', 'module-bluetooth-discover'])
        self.run_command(['pactl', 'load-module', 'module-bluetooth-policy'])
        self.run_command(['pactl', 'load-module', 'module-switch-on-connect'])

        if USB_AUDIO_DEVICE != "default":
            if self.run_command(['pactl', 'set-default-sink', USB_AUDIO_DEVICE]):
                print(f"Audio routing configured successfully. Default sink set to: '{USB_AUDIO_DEVICE}'")
            else:
                print(f"ERROR: Failed to set default audio sink to '{USB_AUDIO_DEVICE}'. Check if the device exists.")
        else:
            print("Using default audio sink.")
        
        print("\n Available audio devices:")
        result = subprocess.run(['aplay', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith("card"):
                    print(f"   {line}")

    def start(self):

        print("=" * 60)
        print("Bluetooth Audio Router for Raspberry Pi 5")
        print("=" * 60)
        print()

        if os.getuid() != 0:
            print("ERROR: This script must be run as root. Please run with sudo.")
            sys.exit(1)

        if not self.setup_BT():
            print("ERROR: Bluetooth setup failed. Exiting.")
            sys.exit(1)
            
        print()
        print("=" * 60)
        print("Bluetooth Audio Router is RUNNING")
        print("=" * 60)
        print()
        print("Instructions:")
        print(f"1. On your phone, go to Bluetooth Settings")
        print(f"2. Look for '{DEVICE_NAME}'")
        print(f"3. Tap to connect")
        print(f"4. Play audio on your phone - it will stream to USB device!")
        print()
        print("Press Ctrl+C to stop the service.")
        print()

        try:
            self.mainloop = GLib.MainLoop()
            self.mainloop.run()
        except KeyboardInterrupt:
            print("Exiting the D-Bus service...")
            self.stop()
            sys.exit(0)
        
    def stop(self):
        if self.mainloop:
            self.mainloop.quit()
        print("Bluetooth Audio Router stopped.")