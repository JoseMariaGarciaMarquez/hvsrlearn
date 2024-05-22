import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import psutil
import numpy as np
from obspy import read
from scipy import signal
import matplotlib.pyplot as plt
from obspy.signal.konnoohmachismoothing import konno_ohmachi_smoothing


def browse_file(entry_var):
    file_path = filedialog.askopenfilename(filetypes=[('SAC Files', '*.sac')])
    entry_var.set(file_path)


def calculate_hvsr(z, n, e, ventana, ventaneo, overlap):
    """
    Calculate the Horizontal-to-Vertical Spectral Ratio (HVSR) for seismic data.
    Args:
        z (str): Path to the Z component data file.
        n (str): Path to the N component data file.
        e (str): Path to the E component data file.
        ventana (int): Number of samples in the window.
        ventaneo (str): Type of window.
        overlap (float): Overlapping percentage.
    """
    ventana = int(ventana)
    overlap = int(overlap)

    # Cargar datos con Obspy
    st_z = read(z)
    st_n = read(n)
    st_e = read(e)

    muestreo=st_z[0].stats.sampling_rate

    #ventana_segs = ventana / st_z[0].stats.sampling_rate

    # Obtener los arreglos de las trazas en NumPy
    z = st_z[0].data
    n = st_n[0].data
    e = st_e[0].data

    # Cálculo del traslape
    overlapping = (overlap / 100) * ventana

    # Remueve la tendencia lineal de los datos
    z = signal.detrend(z, type='linear')
    n = signal.detrend(n, type='linear')
    e = signal.detrend(e, type='linear')

    # Calcula la Transformada de Fourier mediante la función signal.welch
    fz, Pz = signal.welch(z, fs=st_z[0].stats.sampling_rate, window=ventaneo, nperseg=ventana, noverlap=overlapping, scaling='spectrum')
    fn, Pn = signal.welch(n, fs=st_n[0].stats.sampling_rate, window=ventaneo, nperseg=ventana, noverlap=overlapping, scaling='spectrum')
    fe, Pe = signal.welch(e, fs=st_e[0].stats.sampling_rate, window=ventaneo, nperseg=ventana, noverlap=overlapping, scaling='spectrum')


    # https://github.com/arkottke/pykooh/blob/main/example.ipynb
    # Implementación de suavizamiento a partir del enlace anterior
    b = 188.5
    ko_Pz = konno_ohmachi_smoothing(Pz, fz, b, normalize=True)
    ko_Pn = konno_ohmachi_smoothing(Pn, fn, b, normalize=True)
    ko_Pe = konno_ohmachi_smoothing(Pe, fe, b, normalize=True)

    
    Nakamura = (np.sqrt(Pn**2 + Pe**2)) / Pz  # Nakamura

    # Este promedio de frecuencias no tiene sentido, pues los vectores son los mismos
    f = (fn + fe) / 2

    # Extrae frecuencias mayores que 0.1 Hz
    mask = f >= 0.1
    f_filtered = f[mask]

    Nakamura_filtered = Nakamura[mask]

    # Calculo d ela frecuencia fundamental o periodo característico del sitio
    pos = np.argmax(Nakamura_filtered)
    frecuencia_sitio = f_filtered[pos]
    periodo_sitio = 1 / frecuencia_sitio


    # Plot the HVSR
    title = input('Título de la gráfica\n')
    fig, ax = plt.subplots(figsize=(7, 5), dpi=300)
    ax.axvline(frecuencia_sitio, c='lightgrey', linewidth=10)
    ax.plot(f_filtered, Nakamura_filtered, label='HVSR')
    ax.axvline(frecuencia_sitio, c='black', linestyle='--', label='Frecuencia del sitio')
    ax.set_xlabel('Frecuencia (Hz)')
    ax.set_ylabel('HVSR')
    ax.set_title(title)
    ax.set_xscale('log')
    ax.set_xlim(0.1, 40)
    ax.legend()
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)

    # Save the figure
    nombre = input('Nombre de la figura\n')
    plt.savefig('{}.png'.format(nombre), bbox_inches='tight')

    plt.show()

    return frecuencia_sitio


def main_window():
    window_options = ['boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop', 'parzen', 'bohmann', 'blackmanharris', 'nuttall', 'barthan', 'cosine', 'exponential', 'tukey', 'taylor', 'lanczos']
    ventana_size = [1024, 2048, 4096, 8202]
    overlap_values = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

    window = tk.Tk()
    window.title('HVSR(中村)')

    # Sección para la entrada o lectura de las trazas
    sacz_var = tk.StringVar()
    sacn_var = tk.StringVar()
    sace_var = tk.StringVar()

    # Define the layout
    layout = [
        [tk.Label(text='Cargar componentes', font=('Helvetica', 14, 'bold'))],
        [tk.Label(text='Componente Z'), tk.Entry(textvariable=sacz_var), tk.Button(text='Browse', command=lambda: browse_file(sacz_var))],
        [tk.Label(text='Componente N'), tk.Entry(textvariable=sacn_var), tk.Button(text='Browse', command=lambda: browse_file(sacn_var))],
        [tk.Label(text='Componente E'), tk.Entry(textvariable=sace_var), tk.Button(text='Browse', command=lambda: browse_file(sace_var))],
        [tk.Label(text='Procesamiento',font=('Helvetica', 14, 'bold'))],
        [tk.Label(text='Ventana'), ttk.Combobox(values=ventana_size)],
        [tk.Label(text='Taper'), ttk.Combobox(values=window_options)],
        [tk.Label(text='Overlap by'), ttk.Combobox(values=overlap_values), tk.Label(text='%')],
        [tk.Button(text='Calculate HVSR', command=lambda: calculate_hvsr(sacz_var.get(), sacn_var.get(), sace_var.get(), ventana_combobox.get(), ventaneo_combobox.get(), overlap_combobox.get()))],
        [tk.Button(text='Visualize data', command=lambda: plotear(sacz_var.get(), sacn_var.get(), sace_var.get(), ventana_combobox.get(), ventaneo_combobox.get(), overlap_combobox.get()))],
        [tk.Button(text="Exit", command=lambda: exit())],
    ]

    # Populate the layout
    for row in layout:
        if row:
            for idx in range(len(row)):
                row[idx].grid(row=layout.index(row), column=idx, padx=5, pady=5)

    ventana_combobox = layout[5][1]
    ventaneo_combobox = layout[6][1]
    overlap_combobox = layout[7][1]

    # Run the main loop
    window.mainloop()

if __name__ == '__main__':
    main_window()
