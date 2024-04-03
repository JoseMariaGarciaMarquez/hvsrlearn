import numpy as np
import matplotlib.pyplot as plt
import obspy
from scipy import signal

class Spectrogram:
    def __init__(self, filename):
        self.filename = filename

    def hvsr(self, z, n, e, window_size, overlap_percent):
        # Cargar datos con ObsPy
        st_z = obspy.read(z)
        st_n = obspy.read(n)
        st_e = obspy.read(e)

        # Obtener arreglos NumPy de los datos sísmicos
        z = st_z[0].data
        n = st_n[0].data
        e = st_e[0].data

        # Linear detrend the data
        z = signal.detrend(z, type='linear')
        n = signal.detrend(n, type='linear')
        e = signal.detrend(e, type='linear')

        # Número de muestras en la señal
        signal_length = len(z)

        # Calcular el tamaño de solapamiento
        overlap_size = int(window_size * overlap_percent / 100)

        # Número de ventanas
        num_windows = (signal_length - window_size) // (window_size - overlap_size) + 1

        # Inicializa la matriz para almacenar los resultados de FFT de cada ventana
        Z = np.zeros((num_windows, window_size), dtype=np.complex128)
        N = np.zeros((num_windows, window_size), dtype=np.complex128)
        E = np.zeros((num_windows, window_size), dtype=np.complex128)

        # Almacena los resultados de HVSR para cada ventana
        hvsr_results = []
        
        
        plt.figure(figsize=(10, 6))

        # Aplica la transformada de Fourier por ventanas y traza todas las ventanas en una sola figura
        for i in range(num_windows):
            start = i * (window_size - overlap_size)
            end = start + window_size

            windowz = z[start:end]
            windown = n[start:end]
            windowe = e[start:end]

            Z[i, :] = np.fft.fft(windowz, norm="ortho")
            N[i, :] = np.fft.fft(windown, norm="ortho")
            E[i, :] = np.fft.fft(windowe, norm="ortho")

            self.HVSR = np.sqrt((N[i, :] + E[i, :]) / Z[i, :])

            # Almacena los resultados de HVSR
            hvsr_results.append(self.HVSR)
            
            # Trazar la transformada de la ventana actual (opcional)
            plt.plot(HVSR, linewidth=0.5)
            plt.xscale('log')

        # Calcula el promedio del HVSR
        self.avg_hvsr = np.mean(np.array(hvsr_results), axis=0)

        # Trazar el promedio del HVSR
        
        plt.plot(avg_hvsr, linewidth=2, color='red')  # Promedio del HVSR
        plt.xscale('log')

        # Etiquetas y título
        plt.title('Promedio del HVSR')
        plt.xlabel('Frecuencia')
        plt.ylabel('HVSR')
        plt.grid(True)
        plt.show()

    def plotear(self):
        figure = plt.figure(figsize=(10,4), dpi = 200)
        ax = figure.add_subplot()
        ax.xscale('log')
        ax.plot(self.avg_hvsr, linewidth=2, color='blue')
        ax.set_title('HVSR Data')
        ax.set_xlabel('Frequency')
        ax.set_ylabel('HVSR')
        ax.grid(True)
        plt.show()

    def kick_window(self):
        for hv in  range(len(self.hvsr_results)):
            
            

