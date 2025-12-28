# Heart Rate Monitor

A simple Python script that connects to a Bluetooth heart rate monitor, records your heart rate data, and displays it in a graph.

## What You Need

- Python 3.7 or higher
- A Bluetooth-enabled computer
- A compatible heart rate monitor device
- The device must be paired and nearby

## Installation

1. Install the required Python packages:

```bash
pip install bleak matplotlib
```

## How to Run

1. Make sure your heart rate monitor is turned on and nearby
2. Run the script:

```bash
python final.py
```

3. When prompted, enter how long you want to record (in minutes):
   - For example: `5` for 5 minutes, or `0.5` for 30 seconds
4. The script will:
   - Search for your heart rate device
   - Connect to it
   - Record heart rate data for the specified duration
   - Display a graph with your heart rate over time

## Configuration

If you need to change the device address, edit the `DEVICE_ADDRESS` variable in `final.py`:

```python
DEVICE_ADDRESS = "6611AB28-70AF-1EA8-6837-7309EC530F3E"
```

## Troubleshooting

- **"Could not find device"**: Make sure your heart rate monitor is turned on, nearby, and Bluetooth is enabled on your computer
- **Connection issues**: Try turning Bluetooth off and on again, or move the device closer
- **No data**: Ensure the heart rate monitor is properly positioned (usually on your chest or wrist)

## Output

The script will:
- Print real-time heart rate readings to the console
- Display a graph showing your heart rate over time with an average line

