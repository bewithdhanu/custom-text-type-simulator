# Text Type Simulator

A powerful, visual-based desktop automation tool. Instead of relying on rigid screen coordinates or unreliable HTML selectors, this simulator visually "reads" your screen using Tesseract OCR, identifies the text you are looking for, and automatically performs precision mouse clicks and keyboard typing. 

It comes with a modern **CustomTkinter** Graphical User Interface (GUI), built-in visual highlighting, and a recurring "Autopilot" mode!

## 🌟 Key Features

* **Visual Screen Reading (OCR):** Uses Google's Tesseract engine to locate target text directly on your screen.
* **Modern GUI Configuration:** A sleek, fully featured desktop application that supports both Light and Dark system themes.
* **Autopilot (Recurring Mode):** Configure the tool to automatically execute your interactions every X minutes seamlessly in the background.
* **Failsafe Visual Countdown:** Before any input is sent, a transparent floating overlay appears, pinpointing exactly where the click will occur and providing an "Interrupt" button to easily cancel the operation.
* **Screenshot Verification:** Upon completion, the tool snaps a screenshot of the target application and displays it directly within your main configuration window.
* **Configuration Memory:** Automatically remembers and loads your last used Window Name, Search Text, and Type parameters for your next session.
* **Cross-Platform Support:** Ready to run natively on Windows, macOS (Intel & Apple Silicon), and Linux Ubuntu.

## 🚀 Getting Started

### Prerequisites

1. **Python 3.9+**
2. **Tesseract OCR Engine**
   - **Windows**: Install [Tesseract for Windows](https://github.com/UB-Mannheim/tesseract/wiki) and ensure it's installed at `C:\Program Files\Tesseract-OCR\tesseract.exe`.
   - **macOS**: `brew install tesseract`
   - **Linux (Ubuntu)**: `sudo apt-get install tesseract-ocr`

### Installation

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/bewithdhanu/custom-text-type-simulator.git
cd custom-text-type-simulator
pip install -r requirements.txt
```
*(Dependencies include: `pyinstaller`, `customtkinter`, `pyautogui`, `pytesseract`, `pygetwindow`, `pillow`, `opencv-python`, `numpy`)*

### Running the App

```bash
python simulator.py
```

## 🛠️ Building the Executable

You do not need Python installed to run the tool if you compile it into an executable! 

### For Windows Users
Simply double-click the included `build.bat` file in your File Explorer. It will clean up old caches and use PyInstaller to spit out a single `simulator.exe` inside the `dist` directory.

### Cross-Platform CI/CD Pipeline
This project includes a fully configured **GitHub Actions** pipeline (`.github/workflows/build.yml`). 
If you push this repository to GitHub, the Actions tab will automatically provision cloud computers and compile native executables for:
- Windows (x64, x86)
- macOS (Intel, Apple Silicon / M-Series)
- Linux Ubuntu (x64, ARM64)

## 📖 How It Works

1. **Window Targeting**: The script attempts to find a running application window matching your "Target Window Name" and brings it to the foreground.
2. **Screenshot & OCR**: A rapid screenshot is taken and processed via OpenCV and PyTesseract.
3. **Smart Matching**: It scans for your "Search Text" and calculates the precise, exact bounding box around the matched words, completely ignoring variations in spacing.
4. **Failsafe Countdown**: A floating transparent overlay highlights the targeted word in a red box and counts down from 5 seconds. You can click "Interrupt" at any point.
5. **Execution**: If uninterrupted, the script clicks the targeted location and types your specified "Text to Type", hitting `Enter` at the end.
6. **Autopilot Loop**: If a recurring interval is set, it will silently wait in the background and trigger the entire loop again when the timer expires.
