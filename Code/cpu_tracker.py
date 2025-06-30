import psutil
import matplotlib.pyplot as plt

class CPUTracker:
    def __init__(self):
        self.usage = []

    def track(self):
        cpu = psutil.cpu_percent(interval=None)  # keine Pause
        self.usage.append(cpu)

    def summary(self):
        if not self.usage:
            return "Keine CPU-Daten aufgezeichnet."
        avg = sum(self.usage) / len(self.usage)
        return f"\nCPU-Statistik:\nDurchschnitt: {avg:.2f}%\nMax: {max(self.usage):.2f}%\nMin: {min(self.usage):.2f}%"

    def plot(self):
        if not self.usage:
            print("Keine CPU-Daten zum Plotten.")
            return
        plt.plot(self.usage, label="CPU %")
        plt.xlabel("Messpunkt")
        plt.ylabel("CPU-Auslastung (%)")
        plt.title("CPU-Auslastung über Zeit")
        plt.legend()
        plt.grid(True)
        plt.show()
