import asyncio
import time
import matplotlib.pyplot as plt
from bleak import BleakClient, BleakScanner

# --- CONFIGURATION ---
HR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

# --- DATA STORAGE ---
timestamps = []
heart_rates = []
start_time = None


def notification_handler(sender, data):
    global start_time
    flags = data[0]
    hr_format_bit = flags & 0x01

    if hr_format_bit == 0:
        hr_val = data[1]
    else:
        hr_val = int.from_bytes(data[1:3], byteorder='little')

    current_time = time.time()
    if start_time is None:
        start_time = current_time

    elapsed = current_time - start_time
    timestamps.append(elapsed)
    heart_rates.append(hr_val)
    print(f"Time: {elapsed:.1f}s | Heart Rate: {hr_val} bpm")


async def find_hr50_device():
    """Scan for and find the HR50 device automatically."""
    print("Scanning for HR50 device... (Wear your strap!)")
    devices = await BleakScanner.discover(timeout=20.0)
    
    # Look for devices with HR50 or iGPSPORT in the name
    for device in devices:
        if device.name:
            name_upper = device.name.upper()
            if "HR50" in name_upper or "IGPSPORT" in name_upper:
                print(f"Found HR50 device: {device.name} - {device.address}")
                return device
    
    print("HR50 device not found. Make sure:")
    print("- The device is turned on")
    print("- The device is nearby")
    print("- Bluetooth is enabled on your computer")
    return None


async def run_heart_rate_monitor(duration_seconds):
    """Find and connect to HR50 device, then record heart rate data."""
    # Find the device automatically
    device = await find_hr50_device()
    
    if not device:
        return

    # Ask user for confirmation before starting recording
    user_response = input(f"Start recording with {device.name}? (y/n): ").strip().lower()
    if user_response not in ['y', 'yes']:
        print("Recording cancelled.")
        return

    print(f"Connecting to {device.name}...")

    # Connect and monitor
    async with BleakClient(device) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected! Waiting for data...")
        await client.start_notify(HR_UUID, notification_handler)

        print(f"Recording for {duration_seconds} seconds ({duration_seconds / 60:.1f} minutes)...")

        # Wait for the user-specified duration
        await asyncio.sleep(duration_seconds)

        await client.stop_notify(HR_UUID)
        print("Recording finished.")


def plot_data():
    """Plot the recorded heart rate data."""
    if not heart_rates:
        print("No data to plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, heart_rates, label="Heart Rate", color="#d62728")
    plt.title("Heart Rate Session")
    plt.xlabel("Seconds")
    plt.ylabel("BPM")
    plt.grid(True)

    # Calculate average
    avg_hr = sum(heart_rates) / len(heart_rates)
    plt.axhline(y=avg_hr, color='#1f77b4', linestyle='--', label=f'Avg: {int(avg_hr)} BPM')

    # Calculate trimmed mean
    max_hr = max(heart_rates)
    min_hr = min(heart_rates)
    trimmed_mean = (sum(heart_rates) - max_hr - min_hr) / (len(heart_rates) - 2)
    plt.axhline(y=trimmed_mean, color='#2ca02c', linestyle='--', label=f'Trimmed Mean: {int(trimmed_mean)} BPM')
    
    print(f"\nStatistics:")
    print(f"Average: {int(avg_hr)} BPM")
    print(f"Trimmed Mean: {int(trimmed_mean)} BPM (Max: {max_hr}, Min: {min_hr})")

    plt.legend()
    plt.show()


if __name__ == "__main__":
    try:
        # Ask for user input
        user_input = input("Enter recording duration in seconds (e.g. 300 for 5 minutes): ")

        # Get duration in seconds
        duration_in_seconds = int(float(user_input))

        # Run the monitor with the custom duration
        asyncio.run(run_heart_rate_monitor(duration_in_seconds))

        # Plot the results
        plot_data()

    except ValueError:
        print("Invalid input! Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")