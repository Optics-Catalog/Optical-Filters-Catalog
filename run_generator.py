import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


try:

    subprocess.run(
        [sys.executable, "catalog_generator.py"],
        check=True
    )

    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo(
        "Catalog Generator",
        "Catalog generation finished successfully!"
    )

except subprocess.CalledProcessError:

    root = tk.Tk()
    root.withdraw()

    messagebox.showerror(
        "Catalog Generator",
        "An error occurred during generation."
    )

