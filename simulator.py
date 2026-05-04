import pyautogui
import pytesseract
import pygetwindow as gw
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import json
import sys
import ctypes

# Set the tesseract executable path dynamically based on OS
if sys.platform == "win32":
    if hasattr(sys, '_MEIPASS'):
        tess_path = os.path.join(sys._MEIPASS, "tesseract_bin", "tesseract.exe")
    else:
        tess_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tesseract_bin", "tesseract.exe")
        
    if os.path.exists(tess_path):
        pytesseract.pytesseract.tesseract_cmd = tess_path
        os.environ["TESSDATA_PREFIX"] = os.path.join(os.path.dirname(tess_path), "tessdata")
    else:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
elif sys.platform == "darwin":
    pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract' # Typical Mac Homebrew path
else:
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # Typical Linux apt path
TIMER = 5

import cv2
import numpy as np
import time

def activate_window(window_keyword):
    """
    Finds a window by keyword and brings it to the foreground.
    Returns a tuple: (window_found: bool, region: tuple or None)
    """
    if sys.platform != "win32":
        print(f"Warning: Window activation via pygetwindow is currently only fully supported on Windows. Assuming '{window_keyword}' is already focused.")
        return True, None
        
    try:
        # Find all windows containing the keyword (case-insensitive)
        windows = gw.getWindowsWithTitle(window_keyword)
        active_window = gw.getActiveWindow()
        if active_window and window_keyword.lower() in active_window.title.lower():
            print(f"'{window_keyword}' is already the active window: '{active_window.title}'")
            return True, (active_window.left, active_window.top, active_window.width, active_window.height)
    except Exception:
        pass # getActiveWindow can sometimes fail if no window is active
        
    print(f"Looking for a window containing '{window_keyword}'...")
    matching_windows = [w for w in gw.getAllWindows() if window_keyword.lower() in w.title.lower() and w.visible]
    
    if not matching_windows:
        print(f"Could not find any open windows containing '{window_keyword}'!")
        return False, None
        
    target_window = matching_windows[0]
    print(f"Activating window: '{target_window.title}'")
    try:
        if target_window.isMinimized:
            target_window.restore()
        target_window.activate()
        time.sleep(1.5) # Wait a moment for it to come to the foreground
        return True, (target_window.left, target_window.top, target_window.width, target_window.height)
    except Exception as e:
        print(f"Failed to activate window: {e}")
        return True, None # We assume it might still be visible

def ui_countdown_with_interrupt(parent, seconds, action_name, target_x=None, target_y=None, target_w=None, target_h=None):
    """
    Shows a UI countdown timer in the center of the screen with an Interrupt button.
    Draws a red highlight box over the target coordinates.
    """
    result = {"completed": False}
    
    top = tk.Toplevel(parent)
    top.title("Countdown")
    top.attributes("-topmost", True)
    top.overrideredirect(True) # No borders
    # Make the window completely transparent
    top.attributes("-transparentcolor", "black")
    top.config(bg="black")
    
    # Position in center
    screen_width = top.winfo_screenwidth()
    screen_height = top.winfo_screenheight()
    window_width = 450
    window_height = 400
    cx = (screen_width - window_width) // 2
    cy = (screen_height - window_height) // 2
    top.geometry(f"{window_width}x{window_height}+{cx}+{cy}")
    
    # Selection Highlight Overlay
    highlight = None
    if target_x is not None and target_y is not None and target_w is not None and target_h is not None:
        highlight = tk.Toplevel(top)
        highlight.overrideredirect(True)
        highlight.attributes("-topmost", True)
        
        # Transparent background for the overlay
        highlight.attributes("-transparentcolor", "black")
        highlight.config(bg="black")
        
        # Calculate top-left based on center coordinates
        hx = int(target_x - target_w/2)
        hy = int(target_y - target_h/2)
        w = int(target_w)
        h = int(target_h)
        
        padding = 10
        highlight.geometry(f"{w + padding*2}x{h + padding*2}+{hx - padding}+{hy - padding}")
        
        h_canvas = tk.Canvas(highlight, bg="black", highlightthickness=0)
        h_canvas.pack(fill="both", expand=True)
        h_canvas.create_rectangle(padding, padding, w + padding, h + padding, outline="red", width=3)
        
    # Main UI - Draw directly on black canvas so it's transparent
    canvas = tk.Canvas(top, width=window_width, height=window_height, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    def draw_shadow_text(x, y, text, font, fill="white", shadow="gray20", **kwargs):
        canvas.create_text(x+3, y+3, text=text, font=font, fill=shadow, **kwargs)
        return canvas.create_text(x, y, text=text, font=font, fill=fill, **kwargs)
        
    draw_shadow_text(window_width//2, 20, f"Preparing to:\n{action_name}", font=("Arial", 16, "bold"), justify="center", anchor="n")
    
    # Timer Circle
    cx_circ, cy_circ = window_width//2, 200
    r = 50
    canvas.create_oval(cx_circ-r+3, cy_circ-r+3, cx_circ+r+3, cy_circ+r+3, outline="gray20", width=5)
    canvas.create_oval(cx_circ-r, cy_circ-r, cx_circ+r, cy_circ+r, outline="white", width=5)
    
    text_item_shadow = canvas.create_text(cx_circ+3, cy_circ+3, text=str(seconds), font=("Arial", 40, "bold"), fill="gray20")
    text_item = canvas.create_text(cx_circ, cy_circ, text=str(seconds), font=("Arial", 40, "bold"), fill="white")
    
    # Interrupt Button (Custom Drawn)
    btn_y = 320
    btn_w = 160
    btn_h = 40
    # Shadow
    canvas.create_rectangle(window_width//2 - btn_w//2 + 3, btn_y - btn_h//2 + 3, window_width//2 + btn_w//2 + 3, btn_y + btn_h//2 + 3, fill="gray20", outline="")
    # Button
    btn_rect = canvas.create_rectangle(window_width//2 - btn_w//2, btn_y - btn_h//2, window_width//2 + btn_w//2, btn_y + btn_h//2, fill="white", outline="white")
    btn_text = canvas.create_text(window_width//2, btn_y, text="Interrupt", font=("Arial", 14, "bold"), fill="red")
    
    def on_interrupt(event=None):
        result["completed"] = False
        if highlight: highlight.destroy()
        top.destroy()
        
    canvas.tag_bind(btn_rect, "<Button-1>", on_interrupt)
    canvas.tag_bind(btn_text, "<Button-1>", on_interrupt)

    def tick(left):
        if left <= 0:
            result["completed"] = True
            if highlight:
                highlight.destroy()
            top.destroy()
        else:
            canvas.itemconfig(text_item, text=str(left))
            canvas.itemconfig(text_item_shadow, text=str(left))
            top.after(1000, tick, left - 1)
            
    top.after(1000, tick, seconds - 1)
    
    # Wait for the toplevel window to be destroyed
    parent.wait_window(top)
    
    return result["completed"]

def find_text_and_interact(parent, target_text, text_to_type, region=None):
    """
    Finds specific text on the screen, clicks it, types text, and presses Enter.
    """
    # 1. Take a screenshot
    print("Taking a screenshot...")
    
    # Handle regions that might be out of bounds (e.g., negative coordinates)
    if region is not None:
        x, y, w, h = region
        screen_w, screen_h = pyautogui.size()
        x = max(0, min(x, screen_w - 1))
        y = max(0, min(y, screen_h - 1))
        w = min(w, screen_w - x)
        h = min(h, screen_h - y)
        if w > 0 and h > 0:
            region = (x, y, w, h)
        else:
            region = None

    if region:
        screenshot = pyautogui.screenshot(region=region)
        region_offset_x = region[0]
        region_offset_y = region[1]
    else:
        screenshot = pyautogui.screenshot()
        region_offset_x = 0
        region_offset_y = 0
        
    # Save the screenshot for debugging/viewing
    screenshot.save('screenshot.png')
    print("Screenshot saved to 'screenshot.png'")
    
    # Calculate scale factor (crucial for Retina displays on Mac)
    if region:
        scale_x = screenshot.width / region[2]
        scale_y = screenshot.height / region[3]
    else:
        screen_width, screen_height = pyautogui.size()
        scale_x = screenshot.width / screen_width
        scale_y = screenshot.height / screen_height
    
    # Convert screenshot to OpenCV format (numpy array)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # 2. Find the text using OCR (Tesseract)
    print(f"Looking for text: '{target_text}'")
    # pytesseract returns a dictionary with bounding box information
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    target_x, target_y, target_w, target_h = None, None, None, None
    
    # Group words by line to handle phrases and spacing issues
    lines = {}
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        if not text: continue
        
        # A unique key for each line of text
        key = (data['block_num'][i], data['par_num'][i], data['line_num'][i])
        if key not in lines:
            lines[key] = {
                'text': [],
                'words': [],
                'left': data['left'][i],
                'top': data['top'][i],
                'right': data['left'][i] + data['width'][i],
                'bottom': data['top'][i] + data['height'][i]
            }
        
        lines[key]['text'].append(text)
        lines[key]['words'].append({
            'text': text,
            'left': data['left'][i],
            'top': data['top'][i],
            'right': data['left'][i] + data['width'][i],
            'bottom': data['top'][i] + data['height'][i]
        })
        # Update bounding box to encompass the whole line
        lines[key]['right'] = max(lines[key]['right'], data['left'][i] + data['width'][i])
        lines[key]['bottom'] = max(lines[key]['bottom'], data['top'][i] + data['height'][i])
        lines[key]['left'] = min(lines[key]['left'], data['left'][i])
        lines[key]['top'] = min(lines[key]['top'], data['top'][i])
        
    # Search for the target text
    target_normalized = target_text.lower().replace(" ", "")
    
    for key, line_info in lines.items():
        line_text = ' '.join(line_info['text'])
        line_normalized = line_text.lower().replace(" ", "")
        
        if target_normalized in line_normalized:
            # We found a match! Get the exact bounding box of the matching words.
            start_idx = line_normalized.find(target_normalized)
            end_idx = start_idx + len(target_normalized)
            
            match_left, match_top, match_right, match_bottom = None, None, None, None
            current_len = 0
            
            for word in line_info['words']:
                word_len = len(word['text'].lower().replace(" ", ""))
                word_start = current_len
                word_end = current_len + word_len
                
                # Check if this word overlaps with the matched target
                if word_end > start_idx and word_start < end_idx:
                    if match_left is None:
                        match_left = word['left']
                        match_top = word['top']
                        match_right = word['right']
                        match_bottom = word['bottom']
                    else:
                        match_left = min(match_left, word['left'])
                        match_top = min(match_top, word['top'])
                        match_right = max(match_right, word['right'])
                        match_bottom = max(match_bottom, word['bottom'])
                        
                current_len += word_len
                
            x = match_left
            y = match_top
            w = match_right - x
            h = match_bottom - y
            
            # Calculate the center coordinate of the matching text
            pixel_x = x + (w / 2)
            pixel_y = y + (h / 2)
            
            # Convert image pixels to screen points for pyautogui
            target_x = (pixel_x / scale_x) + region_offset_x
            target_y = (pixel_y / scale_y) + region_offset_y
            
            # Use the precise width of the matched text
            target_w = w / scale_x
            target_h = h / scale_y
            
            print(f"Matched line: '{line_text}'")
            break # Stop at the first match
            
    if target_x is not None and target_y is not None:
        print(f"Found '{target_text}' at screen coordinates ({target_x:.2f}, {target_y:.2f})")
        
        # 3. Perform a click operation
        print("Performing click operation...")
        pyautogui.click(x=target_x, y=target_y)
        
        # Wait a moment for the UI to respond (e.g., focus the input field)
        time.sleep(0.5)
        
        # 4. Perform a type operation
        if not ui_countdown_with_interrupt(parent, TIMER, f"type '{text_to_type}'", target_x, target_y, target_w, target_h):
            return False, "User manually interrupted before typing"
            
        print(f"Performing type operation: '{text_to_type}'")
        pyautogui.write(text_to_type, interval=0.05)
        
        # 5. Perform an enter operation
        if not ui_countdown_with_interrupt(parent, TIMER, "press Enter", target_x, target_y, target_w, target_h):
            return False, "User manually interrupted before pressing Enter"
            
        print("Performing enter operation...")
        pyautogui.press('enter')
        
        print("Operation completed successfully!")
        return True, ""
    else:
        print(f"Could not find the text '{target_text}' on the screen.")
        return False, f"Could not find text '{target_text}' via OCR"

class SimulatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Text Type Simulator")
        self.geometry("700x800")
        
        # Fix Windows Taskbar Icon Grouping
        try:
            myappid = 'custom.text.type.simulator.1.0'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass
            
        # Set Window Icon
        icon_path = "icon.ico"
        if getattr(sys, 'frozen', False):
            # If running as PyInstaller exe
            icon_path = os.path.join(sys._MEIPASS, "icon.ico") if hasattr(sys, '_MEIPASS') else "icon.ico"
            
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
        # Main Frame
        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title Label
        title_lbl = ctk.CTkLabel(frame, text="Automation Configuration", font=ctk.CTkFont(size=24, weight="bold"))
        title_lbl.pack(pady=(10, 20))
        
        # Input: Target Window Name
        ctk.CTkLabel(frame, text="Target Window Name:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.entry_window = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=14))
        self.entry_window.insert(0, "Zoom")
        self.entry_window.pack(fill="x", pady=(0, 15), padx=20)
        
        # Input: Search Text
        ctk.CTkLabel(frame, text="Search Text:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.entry_search = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=14))
        self.entry_search.insert(0, "Write a message to Webex space for Mohana")
        self.entry_search.pack(fill="x", pady=(0, 15), padx=20)
        
        # Input: Text to Type
        ctk.CTkLabel(frame, text="Text to Type:", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.entry_type = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=14))
        self.entry_type.insert(0, "Check")
        self.entry_type.pack(fill="x", pady=(0, 15), padx=20)
        
        # Input: Interval
        ctk.CTkLabel(frame, text="Run every X minutes (0 for single run):", font=ctk.CTkFont(size=14)).pack(anchor="w", padx=20)
        self.entry_interval = ctk.CTkEntry(frame, height=40, font=ctk.CTkFont(size=14))
        self.entry_interval.insert(0, "15")
        self.entry_interval.pack(fill="x", pady=(0, 25), padx=20)
        
        # Buttons Frame
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 20))
        
        self.btn_run = ctk.CTkButton(btn_frame, text="Perform Action", command=self.start_process, 
                                     fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(size=16, weight="bold"),
                                     width=200, height=50)
        self.btn_run.pack(side="left", padx=10)
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="Stop Autopilot", command=self.stop_process, 
                                      fg_color="#dc3545", hover_color="#c82333", font=ctk.CTkFont(size=16, weight="bold"),
                                      width=200, height=50, state="disabled")
        self.btn_stop.pack(side="left", padx=10)
        
        # Status Label
        self.lbl_status = ctk.CTkLabel(frame, text="", text_color="#007bff", font=ctk.CTkFont(size=14, weight="bold"), wraplength=600)
        self.lbl_status.pack(pady=5)
        
        # Image Label
        self.lbl_image = ctk.CTkLabel(frame, text="")
        self.lbl_image.pack(pady=10, fill="both", expand=True)
        
        self.is_recurring = False
        self.recurring_timer_id = None
        
        self.config_path = os.path.join(os.path.expanduser("~"), ".text_type_simulator_config.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                if "window_name" in config:
                    self.entry_window.delete(0, "end")
                    self.entry_window.insert(0, config["window_name"])
                if "search_text" in config:
                    self.entry_search.delete(0, "end")
                    self.entry_search.insert(0, config["search_text"])
                if "type_text" in config:
                    self.entry_type.delete(0, "end")
                    self.entry_type.insert(0, config["type_text"])
                if "interval" in config:
                    self.entry_interval.delete(0, "end")
                    self.entry_interval.insert(0, str(config["interval"]))
            except Exception as e:
                print(f"Failed to load config: {e}")

    def save_config(self):
        try:
            config = {
                "window_name": self.entry_window.get(),
                "search_text": self.entry_search.get(),
                "type_text": self.entry_type.get(),
                "interval": self.entry_interval.get()
            }
            with open(self.config_path, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def start_process(self):
        try:
            self.interval = float(self.entry_interval.get())
        except ValueError:
            self.lbl_status.configure(text="Error: Interval must be a valid number.")
            return
            
        self.save_config()
            
        self.is_recurring = self.interval > 0
        if self.is_recurring:
            self.btn_stop.configure(state="normal")
            
        if self.recurring_timer_id:
            self.after_cancel(self.recurring_timer_id)
            self.recurring_timer_id = None
            
        self.run_process()

    def stop_process(self, message="Autopilot stopped."):
        self.is_recurring = False
        if self.recurring_timer_id:
            self.after_cancel(self.recurring_timer_id)
            self.recurring_timer_id = None
        if message:
            self.lbl_status.configure(text=message)
        self.btn_stop.configure(state="disabled")

    def run_process(self):
        self.lbl_status.configure(text="Running...")
        self.withdraw() # Hide main window while working
        
        window_name = self.entry_window.get()
        search_text = self.entry_search.get()
        type_text = self.entry_type.get()
        
        # We need to run this with slight delay to ensure window withdraws properly
        self.after(500, lambda: self._execute(window_name, search_text, type_text))
        
    def _execute(self, window_name, search_text, type_text):
        success = False
        reason = ""
        try:
            window_found, region = activate_window(window_name)
            if not window_found:
                reason = f"Could not find window '{window_name}'"
                self.lbl_status.configure(text=f"Error: {reason}")
            else:
                success, reason = find_text_and_interact(self, search_text, type_text, region)
                if success:
                    self.lbl_status.configure(text="Operation completed successfully!")
                else:
                    self.lbl_status.configure(text=f"Operation failed: {reason}")
                    
            # Load and display screenshot if it exists
            if os.path.exists('screenshot.png'):
                img = Image.open('screenshot.png')
                img.thumbnail((600, 450)) # Resize to fit the UI
                ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.lbl_image.configure(image=ctk_img, text="")
                
        except Exception as e:
            reason = str(e)
            self.lbl_status.configure(text=f"Error: {reason}")
            
        self.deiconify() # Show main window again
        
        # Stop recurring if the user manually interrupted the process or it failed
        if not success and self.is_recurring:
            new_msg = self.lbl_status.cget("text") + f" | Autopilot stopped ({reason})"
            self.stop_process(message=new_msg)
            return
            
        if self.is_recurring:
            total_seconds = int(self.interval * 60)
            self._wait_for_next_run(total_seconds)
            
    def _wait_for_next_run(self, seconds_left):
        if not self.is_recurring:
            return
            
        if seconds_left <= 0:
            self.run_process()
        else:
            mins, secs = divmod(seconds_left, 60)
            self.lbl_status.configure(text=f"Next run in {mins:02d}:{secs:02d}...")
            self.recurring_timer_id = self.after(1000, self._wait_for_next_run, seconds_left - 1)

if __name__ == "__main__":
    app = SimulatorApp()
    app.mainloop()
