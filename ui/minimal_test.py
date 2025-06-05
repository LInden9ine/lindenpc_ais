# ui/minimal_test.py
import tkinter as tk

print("Minimal test: Starting...")

try:
    root = tk.Tk()
    root.title("Minimal Tkinter Test")
    label = tk.Label(root, text="Hello, Tkinter!")
    label.pack()
    print("Minimal test: Tkinter initialized")
    root.mainloop()
    print("Minimal test: Tkinter mainloop finished")
except Exception as e:
    print(f"Minimal test: An error occurred: {e}")

print("Minimal test: Exiting...")
