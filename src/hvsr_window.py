from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from hvsr_calculator import calculate_hvsr_helper

class HVSRWindow(QDialog):
    def __init__(self, datos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cálculo de Cocientes Espectrales (HVSR)")
        self.datos = datos
        self.parent = parent
        self.hvsr_results = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        param_layout = QHBoxLayout()

        self.method_box = QComboBox()
        self.method_box.addItems([
            "Luendei and Albarello N",
            "Luendei and Albarello E",
            "Picozzi",
            "Lunedei and Malischewsky",
            "Nakamura",
            "Nuevo"
        ])
        self.method_box.setCurrentText("Nakamura")
        param_layout.addWidget(QLabel("Método:"))
        param_layout.addWidget(self.method_box)

        self.window_box = QComboBox()
        self.window_box.addItems(["hann", "hamming", "blackman"])
        self.window_box.setCurrentText("hamming")
        param_layout.addWidget(QLabel("Ventana:"))
        param_layout.addWidget(self.window_box)

        self.ancho_edit = QLineEdit("82.02")
        param_layout.addWidget(QLabel("Ancho (s):"))
        param_layout.addWidget(self.ancho_edit)

        self.overlap_edit = QLineEdit("5")
        param_layout.addWidget(QLabel("Overlap (%):"))
        param_layout.addWidget(self.overlap_edit)

        self.sm_edit = QLineEdit("1")
        self.sm_edit.setDisabled(True)
        param_layout.addWidget(QLabel("sm:"))
        param_layout.addWidget(self.sm_edit)

        self.detrend_box = QComboBox()
        self.detrend_box.addItems(["constant", "linear"])
        self.detrend_box.setCurrentText("linear")
        param_layout.addWidget(QLabel("Detrend:"))
        param_layout.addWidget(self.detrend_box)

        self.confianza_edit = QLineEdit("100")
        self.confianza_edit.setDisabled(True)
        param_layout.addWidget(QLabel("Confianza (%):"))
        param_layout.addWidget(self.confianza_edit)

        self.b_edit = QLineEdit("188.5")
        param_layout.addWidget(QLabel("Konno-Ohmachi b:"))
        param_layout.addWidget(self.b_edit)

        layout.addLayout(param_layout)

        self.figure = Figure(figsize=(7, 4))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(QLabel("Cociente espectral H/V"))
        layout.addWidget(self.canvas)

        btn_layout = QHBoxLayout()
        btn_calc = QPushButton("Calcular HVSR")
        btn_calc.clicked.connect(self.calculate_hvsr)
        btn_layout.addWidget(btn_calc)

        btn_save = QPushButton("Guardar resultados")
        btn_save.clicked.connect(self.save_results)
        btn_layout.addWidget(btn_save)

        btn_export = QPushButton("Guardar figura")
        btn_export.clicked.connect(self.save_figure)
        btn_layout.addWidget(btn_export)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def calculate_hvsr(self):
        try:
            method = self.method_box.currentText()
            window = self.window_box.currentText()
            ancho = float(self.ancho_edit.text())
            overlap = float(self.overlap_edit.text())
            sm = 1  # Fijo
            detr = self.detrend_box.currentText()
            confianza = 100.0  # Fijo
            b = float(self.b_edit.text())
        except Exception:
            return

        z = self.datos['z']['data']
        n = self.datos['n']['data']
        e = self.datos['e']['data']
        samples = self.datos['z']['sampling_rate']

        nperseg = int(ancho * samples)
        if nperseg > len(z) or nperseg > len(n) or nperseg > len(e):
            QMessageBox.warning(self, "Error", "El ancho de ventana es mayor que la longitud de la señal.")
            return

        nfft = sm * nperseg
        if nfft < nperseg:
            QMessageBox.warning(self, "Error", "nfft debe ser mayor o igual que nperseg.")
            return

        f, HV, sd_moving, f_rejected, rejected_data, frecuencia_sitio, HV_f, pos = calculate_hvsr_helper(
            z, n, e, sm, method, window, ancho, overlap, detr, confianza, b, samples
        )

        self.hvsr_results = {
            "frecuencia_sitio": frecuencia_sitio,
            "HVSR": HV,
            "frecuencias": f,
            "sd_moving": sd_moving,
            "HV_f": HV_f,
            "pos": pos,
            "params": {
                "method": method,
                "window": window,
                "ancho": ancho,
                "overlap": overlap,
                "sm": sm,
                "detr": detr,
                "confianza": confianza,
                "b": b,
                "sampling_rate": samples
            }
        }

        self.figure.clear()
        ax = self.figure.add_subplot(1, 1, 1)
        ax.set_title(f'HVSR - Método: {method}')
        ax.plot(f, HV - sd_moving, '--', lw=0.5, c='black')
        ax.plot(f, HV + sd_moving, '--', lw=0.5, c='black')
        ax.fill_between(f, HV - sd_moving, HV + sd_moving, color='gray', alpha=0.5)
        ax.plot(f, HV, label='HVSR', color='purple')
        if len(HV_f) > 0:
            ax.scatter(frecuencia_sitio, HV_f[pos], s=100, marker='*', c='violet', label='Pico')
            ax.axvline(frecuencia_sitio, c='red', label='Frecuencia del sitio')
        ax.set_xlim(0.1, 20)
        ax.set_ylim(0, max(HV) * 1.1)
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.set_xlabel('Frecuencia (Hz)', fontsize=12)
        ax.set_ylabel('HVSR', fontsize=12)
        ax.legend()
        ax.set_xscale('log')
        self.figure.tight_layout()
        self.canvas.draw()

    def save_results(self):
        if self.hvsr_results is None:
            QMessageBox.warning(self, "Error", "Primero calcula el HVSR.")
            return
        if self.parent is not None:
            self.parent.hvsr_results = self.hvsr_results
            if hasattr(self.parent, "show_hvsr_results"):
                self.parent.show_hvsr_results()
            if hasattr(self.parent, "tabs") and hasattr(self.parent, "tab_hvsr"):
                self.parent.tabs.setCurrentWidget(self.parent.tab_hvsr)
        QMessageBox.information(self, "Guardado", "Resultados HVSR guardados y mostrados en la ventana principal.")
        self.accept()

    def save_figure(self):
        if self.hvsr_results is None:
            QMessageBox.warning(self, "Error", "Primero calcula el HVSR.")
            return
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar figura como", "", "PNG Files (*.png);;PDF Files (*.pdf)", options=options)
        if filename:
            self.figure.savefig(filename)
            QMessageBox.information(self, "Guardado", f"Figura guardada en:\n{filename}")