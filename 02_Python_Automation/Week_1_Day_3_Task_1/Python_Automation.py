
import pyautogui
import time

# Safety: move mouse to top-left corner to stop automation
pyautogui.FAILSAFE = True

# Step 1: Open Chrome
print("Opening Google Chrome...")

pyautogui.hotkey("win", "r")
time.sleep(2)

pyautogui.write("chrome", interval=0.1)
pyautogui.press("enter")

time.sleep(5)

# Step 2: Open NSE Nifty 50 live data page
print("Opening NSE Nifty 50 page...")

pyautogui.hotkey("ctrl", "l")

pyautogui.write(
    "https://www.nseindia.com/market-data/live-equity-market?symbol=NIFTY%2050",
    interval=0.02
)

pyautogui.press("enter")

# Allow the webpage to load
time.sleep(12)

# Step 3: Copy webpage data
print("Copying NSE data...")

pyautogui.hotkey("ctrl", "a")
time.sleep(1)

pyautogui.hotkey("ctrl", "c")
time.sleep(2)

# Step 4: Open Notepad
print("Opening Notepad...")

pyautogui.hotkey("win", "r")
time.sleep(2)

pyautogui.write("notepad", interval=0.1)
pyautogui.press("enter")

time.sleep(3)

# Step 5: Paste copied data
print("Pasting NSE data into Notepad...")

pyautogui.hotkey("ctrl", "v")

time.sleep(2)

print("SUCCESS: NSE data copied into Notepad!")
