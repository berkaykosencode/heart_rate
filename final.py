import asyncio
import time
import matplotlib.pyplot as plt
from bleak import BleakClient, BleakScanner

# --- CONFIGURATION ---
# Your specific device UUID
DEVICE_ADDRESS = "6611AB28-70AF-1EA8-6837-7309EC530F3E"
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


async def run_heart_rate_monitor(duration_seconds):
    print("Scanning for device...")

    # 1. Find device first to ensure connection
    device = await BleakScanner.find_device_by_address(DEVICE_ADDRESS, timeout=20.0)

    if not device:
        print(f"Could not find device {DEVICE_ADDRESS}.")
        print("Check: Is phone Bluetooth OFF? Is strap on your chest?")
        return

    print(f"Found {device.name}! Connecting...")

    # 2. Connect
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
    if not heart_rates:
        print("No data to plot.")
        return

    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, heart_rates, label="Heart Rate", color="#d62728")
    plt.title("Heart Rate Session")
    plt.xlabel("Seconds")
    plt.ylabel("BPM")
    plt.grid(True)

    # Show average
    avg_hr = sum(heart_rates) / len(heart_rates)
    plt.axhline(y=avg_hr, color='#1f77b4', linestyle='--', label=f'Avg: {int(avg_hr)} BPM')

    plt.legend()
    plt.show()


if __name__ == "__main__":
    try:
        # --- NEW: Ask for user input ---
        user_input = input("Enter recording duration in minutes (e.g. 5 or 0.5): ")

        # Convert minutes to seconds
        duration_in_seconds = int(float(user_input) * 60)

        # Run the monitor with the custom duration
        asyncio.run(run_heart_rate_monitor(duration_in_seconds))

        # Plot the results
        plot_data()

    except ValueError:
        print("Invalid input! Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")