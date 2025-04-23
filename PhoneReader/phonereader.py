from ppadb.client import Client as AdbClient
# Important: make sure to install the scrcpy (https://github.com/Genymobile/scrcpy) on your system, otherwise this will not run.
# Phone needs to be connected to the computer and USB debugging enabled.

client = AdbClient(host="127.0.0.1", port=5037)
devices = client.devices()

if len(devices) == 0:
    print("No devices attached")
    quit()

device = devices[0]
print(f"Connected to {device.serial}")
# Take a screenshot and save it to a file
result = device.screencap()
with open("screen.png", "wb") as fp:
    fp.write(result)