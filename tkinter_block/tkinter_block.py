import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import requests
import json
import numpy as np

def start_tinker():
    def set_data(name, input_field):
        val = input_field.get()
        data = {
            "room": name,
            "status": val
        }
        requests.post('http://127.0.0.1:5000/updateData', json=data)

    def get_data():
        try:
            res = requests.get('http://127.0.0.1:5000/GetTemperatures')
            data = res.json()

            min_temp = data[-1].get('min', 0)
            max_temp = data[-1].get('max', 0)

            min_input.delete(0, tk.END)
            min_input.insert(0, str(min_temp))

            max_input.delete(0, tk.END)
            max_input.insert(0, str(max_temp))

            update_graph(data)

        except requests.RequestException as e:
            print(f"Failed to fetch data: {e}")

        root.after(5000, get_data)

    def update_graph(data):
        figure.clear()
        ax = figure.add_subplot(111)
        ax.plot(np.array(range(len(data))), [d.get('max', 0) for d in data], label="Max")
        ax.plot(np.array(range(len(data))), [d.get('min', 0) for d in data], label="Min")
        ax.plot(np.array(range(len(data))), [d.get('value', 0) for d in data], label="Value")
        ax.legend()
        canvas.draw()

    root = tk.Tk()
    root.geometry("800x600")
    root.title("Керування розумним будинком")

    figure = Figure(figsize=(5, 4), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    max_label = tk.Label(root, text="Max")
    max_label.pack()

    max_input = tk.Entry(root)
    max_input.pack()

    max_button = tk.Button(root, text="Send", command=lambda: set_data("max", max_input))
    max_button.pack()

    min_label = tk.Label(root, text="Min")
    min_label.pack()

    min_input = tk.Entry(root)
    min_input.pack()

    min_button = tk.Button(root, text="Send", command=lambda: set_data("min", min_input))
    min_button.pack()

    get_data()

    root.mainloop()