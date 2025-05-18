import numpy as np
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from process import ProcessData  # Importa tu clase de procesamiento

class ProcessWindow(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesamiento de Señales")
        self.datos_original = datos  # Diccionario original
        self.datos_procesados = datos.copy()  # Para no modificar el original hasta guardar
        self.parent = parent  # Referencia a la ventana principal para actualizar datos
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Figura única para los espectros
        self.figure = Figure(figsize=(6, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(QLabel("Espectro de Fourier (amplitud vs frecuencia)"))
        layout.addWidget(self.canvas)

        # Botones de procesamiento
        btn_layout = QHBoxLayout()

        btn_fourier = QPushButton("Mostrar espectro de Fourier")
        btn_fourier.clicked.connect(self.plot_fourier)
        btn_layout.addWidget(btn_fourier)

        btn_filter = QPushButton("Filtrar señal")
        btn_filter.clicked.connect(self.filter_signal)
        btn_layout.addWidget(btn_filter)

        btn_reject = QPushButton("Rechazar ventana de tiempo")
        btn_reject.clicked.connect(self.reject_window)
        btn_layout.addWidget(btn_reject)

        btn_save = QPushButton("Guardar cambios")
        btn_save.clicked.connect(self.save_and_close)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)

        # Campos para parámetros de filtrado y rechazo
        self.lowcut_edit = QLineEdit()
        self.lowcut_edit.setPlaceholderText("Frec. mínima (Hz)")
        self.highcut_edit = QLineEdit()
        self.highcut_edit.setPlaceholderText("Frec. máxima (Hz)")
        layout.addWidget(self.lowcut_edit)
        layout.addWidget(self.highcut_edit)

        self.reject_start = QLineEdit()
        self.reject_start.setPlaceholderText("Inicio ventana a rechazar (s)")
        self.reject_end = QLineEdit()
        self.reject_end.setPlaceholderText("Fin ventana a rechazar (s)")
        layout.addWidget(self.reject_start)
        layout.addWidget(self.reject_end)

    def plot_fourier(self):

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        componentes = ['z', 'n', 'e']
        nombres = ['Vertical (Z)', 'Norte (N)', 'Este (E)']
        colores = ['black', 'blue', 'red']

        for comp, nombre, color in zip(componentes, nombres, colores):
            data = self.datos_procesados[comp]['data']
            sr = self.datos_procesados[comp]['sampling_rate']
            N = len(data)
            freqs = np.fft.rfftfreq(N, d=1/sr)
            spectrum = np.abs(np.fft.rfft(data))
            ax.plot(freqs, spectrum, color=color, label=nombre)
        ax.set_xlabel("Frecuencia (Hz)")
        ax.set_ylabel("Amplitud")
        ax.set_title("Espectros de Fourier")
        ax.set_xscale('log')
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.5)
        self.figure.tight_layout()
        self.canvas.draw()

    def filter_signal(self):
        try:
            lowcut = float(self.lowcut_edit.text())
            highcut = float(self.highcut_edit.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Introduce frecuencias válidas para el filtro.")
            return

        # Prepara los datos para filtrar
        data_dict = {comp: self.datos_procesados[comp]['data'] for comp in ['z', 'n', 'e']}
        sr = self.datos_procesados['z']['sampling_rate']
        processor = ProcessData(data_dict, sr)
        filtered = processor.bandpass_filter(lowcut, highcut)

        # Actualiza los datos procesados
        for comp in ['z', 'n', 'e']:
            self.datos_procesados[comp]['data'] = filtered[comp]
        self.plot_fourier()

    def reject_window(self):
        try:
            t_ini = float(self.reject_start.text())
            t_fin = float(self.reject_end.text())
        except ValueError:
            QMessageBox.warning(self, "Error", "Introduce tiempos válidos para rechazar la ventana.")
            return

        data_dict = {comp: self.datos_procesados[comp]['data'] for comp in ['z', 'n', 'e']}
        times_dict = {comp: self.datos_procesados[comp]['times'] for comp in ['z', 'n', 'e']}
        sr = self.datos_procesados['z']['sampling_rate']
        processor = ProcessData(data_dict, sr)
        processor.reject_time_windows([(t_ini, t_fin)], times_dict)

        # Actualiza los datos procesados y los tiempos
        for comp in ['z', 'n', 'e']:
            self.datos_procesados[comp]['data'] = processor.data[comp]
            self.datos_procesados[comp]['times'] = times_dict[comp]

    def save_and_close(self):
        # Actualiza los datos en la ventana principal
        if self.parent is not None:
            self.parent.datos = self.datos_procesados
            # Si quieres actualizar el plot principal:
            from plot_data import DataPlotter
            plotter = DataPlotter(self.parent.figure_datos)
            plotter.plot_triple_component(self.parent.datos)
            self.parent.canvas_datos.draw()
        self.accept()