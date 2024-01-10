import sys
import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
import subprocess

from tkinter import filedialog
from PIL import Image, ImageTk
from obspy import read
from scipy import signal
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class HvsrCalculator:
    def __init__(self, master):
        self.master = master
        master.title("hvsrlearn")

        # Cargar la imagen como ícono
        icon_image = Image.open("/images/icono.png")
        icon_image = icon_image.resize((150, 150), Image.BICUBIC)
        self.icon_image = ImageTk.PhotoImage(icon_image)

        master.tk.call('wm', 'iconphoto', master._w, self.icon_image)

        self.create_widgets()

    def create_widgets(self):

        self.image_label = tk.Label(self.master, image=self.icon_image)
        self.image_label.grid(row=10 , column=2, rowspan=2, padx=10, pady=10)

        self.terminal_text = tk.Text(self.master, wrap='word', height=10, width=85)
        self.terminal_text.grid(row=10, column=3, rowspan=10, padx=10, pady=10)
        sys.stdout = TextRedirector(self.terminal_text, "stdout")

        # Widget de canvas para mostrar el gráfico
        self.plot_canvas = FigureCanvasTkAgg(plt.Figure(figsize=(6, 5), dpi=100))
        self.plot_canvas_widget = self.plot_canvas.get_tk_widget()
        self.plot_canvas_widget.grid(row=0, column=3, rowspan=10, padx=10, pady=10)

        # Botón para guardar imagen
        self.save_image_button = tk.Button(self.master, text="Guardar Imagen", command=self.save_image)
        self.save_image_button.grid(row=7, column=2 , padx=10, pady=10)

        # Botón para cambiar el eje y a escala logarítmica
        self.log_y_button = tk.Button(self.master, text="Eje Y Log", command=self.toggle_log_y)
        self.log_y_button.grid(row=8, column=2, padx=10, pady=5)

        # Variable de control para el estado del eje y logarítmico
        self.log_y_state = tk.BooleanVar(value=False)

        # Componentes
        self.label_z = tk.Label(self.master, text="Componente Z")
        self.label_z.grid(row=0, column=0)
        self.entry_z = tk.Entry(self.master)
        self.entry_z.grid(row=0, column=1)
        self.button_z = tk.Button(self.master, text="Buscar", command=self.browse_z)
        self.button_z.grid(row=0, column=2)

        self.label_n = tk.Label(self.master, text="Componente N")
        self.label_n.grid(row=1, column=0)
        self.entry_n = tk.Entry(self.master)
        self.entry_n.grid(row=1, column=1)
        self.button_n = tk.Button(self.master, text="Buscar", command=self.browse_n)
        self.button_n.grid(row=1, column=2)

        self.label_e = tk.Label(self.master, text="Componente E")
        self.label_e.grid(row=2, column=0)
        self.entry_e = tk.Entry(self.master)
        self.entry_e.grid(row=2, column=1)
        self.button_e = tk.Button(self.master, text="Buscar", command=self.browse_e)
        self.button_e.grid(row=2, column=2)

        # Procesamiento
        self.label_smooth = tk.Label(self.master, text="Sobre-muestreo")
        self.label_smooth.grid(row=3, column=0)
        self.entry_smooth = tk.Entry(self.master)
        self.entry_smooth.grid(row=3, column=1)

        self.label_len = tk.Label(self.master, text="Ancho de ventana [s]")
        self.label_len.grid(row=4, column=0)
        self.entry_len = tk.Entry(self.master)
        self.entry_len.grid(row=4, column=1)

        self.label_overlap = tk.Label(self.master, text="Solapamiento [%]")
        self.label_overlap.grid(row=5, column=0)
        self.entry_overlap = tk.Entry(self.master)
        self.entry_overlap.grid(row=5, column=1)

        self.label_sd = tk.Label(self.master, text="Desviación estándar [%]")
        self.label_sd.grid(row=6, column=0)
        self.entry_sd = tk.Entry(self.master)
        self.entry_sd.grid(row=6, column=1)

        self.label_hvs = tk.Label(self.master, text="Método HVSR")
        self.label_hvs.grid(row=7, column=0)
        self.hvs_var = tk.StringVar(self.master)
        self.hvs_var.set('Nakamura')
        self.hvs_combo = tk.OptionMenu(self.master, self.hvs_var, 'Luendei and Albarello N', 'Luendei and Albarello E', 'Picozzi', 'Lunedei and Malischewsky', 'Nakamura')
        self.hvs_combo.grid(row=7, column=1)

        self.label_window = tk.Label(self.master, text="Ventaneo")
        self.label_window.grid(row=8, column=0)
        self.window_var = tk.StringVar(self.master)
        self.window_var.set('hann')
        self.window_combo = tk.OptionMenu(self.master, self.window_var, 'boxcar', 'triang', 'blackman', 'hamming', 'hann', 'bartlett', 'flattop')
        self.window_combo.grid(row=8, column=1)

        self.label_detrend = tk.Label(self.master, text="Detrend")
        self.label_detrend.grid(row=9, column=0)
        self.detrend_var = tk.StringVar(self.master)
        self.detrend_var.set('linear')
        self.detrend_combo = tk.OptionMenu(self.master, self.detrend_var, 'linear', 'constant')
        self.detrend_combo.grid(row=9, column=1)



        self.calculate_button = tk.Button(self.master, text="Calcular", command=self.calculate_hvsr)
        self.calculate_button.grid(row=10, column=0, columnspan=2)

        self.exit_button = tk.Button(self.master, text="Salir", command=self.master.destroy)
        self.exit_button.grid(row=11, column=0, columnspan=2)

    def toggle_log_y(self):
        # Función para cambiar el estado del eje y a escala logarítmica
        self.log_y_state.set(not self.log_y_state.get())
        self.update_plot()

    def update_plot(self):
        # Función para actualizar el gráfico con el estado actual del eje y
        if hasattr(self, 'current_figure'):
            ax = self.current_figure.axes[0]  # Obtener el objeto Axes
            ax.set_yscale('log' if self.log_y_state.get() else 'linear')
            self.plot_canvas.draw()

    def browse_z(self):
        filename = filedialog.askopenfilename()
        self.entry_z.delete(0, tk.END)
        self.entry_z.insert(0, filename)

    def browse_n(self):
        filename = filedialog.askopenfilename()
        self.entry_n.delete(0, tk.END)
        self.entry_n.insert(0, filename)

    def browse_e(self):
        filename = filedialog.askopenfilename()
        self.entry_e.delete(0, tk.END)
        self.entry_e.insert(0, filename)

    def calculate_hvsr(self):
        z = self.entry_z.get()
        n = self.entry_n.get()
        e = self.entry_e.get()
        sm = float(self.entry_smooth.get())
        method = self.hvs_var.get()
        window = self.window_var.get()
        ancho = float(self.entry_len.get())
        overlap = float(self.entry_overlap.get())
        detr = self.detrend_var.get()
        confianza = float(self.entry_sd.get())

        # Llamar a la función de cálculo de HVSR
        self.calculate_hvsr_helper(z, n, e, sm, method, window, ancho, overlap, detr, confianza)



    def calculate_hvsr_helper(self, z, n, e, sm, method, window, ancho, overlap, detr, confianza):

        """
        Esta función calcula el espectro de razón espectral horizontal-vertical (HVSR) a partir de datos sísmicos en tres componentes.

        Parámetros:
        - z, n, e: Rutas de los archivos de datos sísmicos en las componentes Z, N y E respectivamente.
        - sm: Factor de sobre-muestreo para el cálculo del espectro.
        - method: Método de cálculo del HVSR. Puede ser 'Luendei and Albarello N', 'Luendei and Albarello E', 'Picozzi', 'Lunedei and Malischewsky', 'Nakamura' o 'Nuevo'.
        - window: Ventana utilizada para el cálculo del espectro (por ejemplo, 'hann', 'hamming', etc.).
        - ancho: Ancho de la ventana en segundos.
        - overlap: Porcentaje de superposición entre ventanas.
        - detr: Tipo de tendencia a eliminar de los datos ('linear', 'constant', etc.).
        - confianza: Nivel de confianza para el umbral de la desviación estándar móvil.

        Salida:
        - Muestra un gráfico del HVSR con información adicional, incluyendo la frecuencia del sitio y datos rechazados.
        """

        # Cargar datos con ObsPy
        st_z = read(z)
        st_n = read(n)
        st_e = read(e)
        
        nperseg = ancho*st_z[0].stats.sampling_rate

        # Obtener arreglos NumPy de los datos sísmicos
        z = st_z[0].data
        n = st_n[0].data
        e = st_e[0].data
        

        # Overlapping calculation
        overlapping = (overlap / 100) * nperseg

        # Linear detrend the data
        z = signal.detrend(z, type='linear')
        n = signal.detrend(n, type='linear')
        e = signal.detrend(e, type='linear')
        overlapping = (5 / 100) * 8202
        samples = st_z[0].stats.sampling_rate
        
        f, Pz = signal.welch(z, fs=samples, 
                         window=window, 
                         nperseg=nperseg, 
                         noverlap=overlapping,
                         nfft=sm*nperseg,detrend=detr,
                         scaling='spectrum', average='median')
        _, Pn = signal.welch(n, fs=samples, 
                         window=window, 
                         nperseg=nperseg, 
                         noverlap=overlapping,
                         nfft=sm*nperseg, detrend=detr,
                         scaling='spectrum', average='median')
        _, Pe = signal.welch(e, fs=samples, 
                         window=window, 
                         nperseg=nperseg, detrend=detr,
                         noverlap=overlapping,
                         nfft=sm*nperseg,
                         scaling='spectrum', average='median')
        
        if method == 'Luendei and Albarello N':
            HV = Pn / Pz  # Lunedei and Albarello N
            
        if method == 'Luendei and Albarello E':
            HV = Pe / Pz  # Lunedei and Albarello E
        
        if method == 'Picozzi':
            HV = (np.sqrt(Pn * Pe)) / Pz  # Picozzi
            
        if method == 'Lunedei and Malischewsky':
            HV = np.sqrt((Pn + Pe) / Pz)  # Lunedei and Malischewsky
        
        if method == 'Nakamura':
            HV = (np.sqrt(Pn**2 + Pe**2)) / Pz  # Nakamura
            
        if method == 'Nuevo':
            HV = (Pn + Pe) / Pz
            
        """
        Sección para proponer un cálculo
        """    
        # Calcular la desviación estándar móvil
        window_size=100
        sd = np.std(HV[:window_size])
        sd_moving = np.zeros_like(HV)
        for i in range(window_size, len(HV)):
            sd_moving[i-window_size:i] = sd
            sd = np.std(HV[i-window_size+1:i+1])
            
        # Definir un umbral para la desviación estándar
        sd_threshold = confianza * (max(sd_moving)/100)  # Ajusta este valor según tus necesidades

        # Crear la máscara con la condición de la desviación estándar
        mask = sd_moving < sd_threshold

        # Crear un arreglo para los datos rechazados
        rejected_data = HV[~mask]
        f_rejected = f[~mask]

        f_f = f[mask]
        HV_f = HV[mask]

        pos = np.argmax(HV_f)
        frecuencia_sitio = f_f[pos]

        
        print('----------------------------------------------------------\n'
            'Estación: {}\n'
            'Método usado: {}\n'
            'Muestras por ventana: {}\n'
            'frecuencia del sitio: {} Hz\n'
            'Amplitud del sitio: {} m\n'
            'Comentarios:\n'.format(st_z[0].stats.station, method, nperseg, frecuencia_sitio, 1/frecuencia_sitio))
        
        
        figure = plt.Figure(figsize=(6, 5), dpi=100)
        ax = figure.add_subplot(1, 1, 1)
        ax.set_title('Station {}'.format(st_z[0].stats.station))
        ax.plot(f, HV - sd_moving, '--', lw=0.5, c='black')
        ax.plot(f, HV + sd_moving, '--', lw=0.5, c='black')
        ax.plot(f, HV, label=method)
        ax.plot(f, sd_moving, label='SD')
        ax.axvline(frecuencia_sitio, c='red', linestyle='--', label='Frecuencia del sitio')
        ax.axhline(sd_threshold, c='pink', linestyle='--')
        ax.fill_between(f, HV - sd_moving, HV + sd_moving, color='gray', alpha=0.5)
        ax.scatter(f_rejected, rejected_data, s=20, marker='*', c='gold', label='Rejected')
        ax.scatter(frecuencia_sitio, HV_f[pos], s=100, marker='*', c='violet')
        ax.set_ylim(0, max(HV))
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_xlabel('Frecuencia', fontsize=15)
        ax.set_ylabel('HVSR', fontsize=15)
        ax.legend()
        ax.set_xscale('log')


        # Actualizar el canvas con el nuevo gráfico
        self.plot_canvas.figure = figure
        self.plot_canvas.draw()
                # Asignar la figura al objeto para que esté disponible para guardarla
        self.current_figure = figure

    def save_image(self):
        # Función para guardar la imagen actual del gráfico
        if hasattr(self, 'current_figure'):
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                       filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
                                                       title="Guardar Imagen")
            if file_path:
                self.current_figure.savefig(file_path)


class TextRedirector:
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.insert(tk.END, str, (self.tag,))
        self.widget.see(tk.END)

    def flush(self):
        pass


def main():
    root = tk.Tk()
    app = HvsrCalculator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
