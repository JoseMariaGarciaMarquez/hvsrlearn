import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QPushButton, QLabel, QLineEdit, QComboBox, QMessageBox, QFileDialog, QCheckBox
)
from PyQt5.QtGui import QIcon
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
        self.resize(500, 500)  # Ajusta el tamaño inicial

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

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
        form_layout.addRow("Método:", self.method_box)

        self.window_box = QComboBox()
        self.window_box.addItems(["hann", "hamming", "blackman"])
        self.window_box.setCurrentText("hamming")
        form_layout.addRow("Ventana:", self.window_box)

        self.ancho_edit = QLineEdit("82.02")
        form_layout.addRow("Ancho (s):", self.ancho_edit)

        self.overlap_edit = QLineEdit("5")
        form_layout.addRow("Overlap (%):", self.overlap_edit)

        self.detrend_box = QComboBox()
        self.detrend_box.addItems(["constant", "linear"])
        self.detrend_box.setCurrentText("linear")
        form_layout.addRow("Detrend:", self.detrend_box)

        self.b_edit = QLineEdit("188.5")
        form_layout.addRow("Konno-Ohmachi b:", self.b_edit)

        # Frecuencia fundamental
        self.freq_edit = QLineEdit()
        self.freq_edit.setPlaceholderText("Automática")
        self.freq_edit.setToolTip("Frecuencia fundamental detectada. Puedes editarla para marcar otra frecuencia.")
        form_layout.addRow("Frecuencia fundamental (Hz):", self.freq_edit)

        # Georreferenciación
        geo_layout = QHBoxLayout()
        self.geo_checkbox = QCheckBox("Georreferenciar")
        geo_layout.addWidget(self.geo_checkbox)
        self.lat_edit = QLineEdit()
        self.lat_edit.setPlaceholderText("Latitud")
        self.lat_edit.setDisabled(True)
        geo_layout.addWidget(QLabel("Lat:"))
        geo_layout.addWidget(self.lat_edit)
        self.lon_edit = QLineEdit()
        self.lon_edit.setPlaceholderText("Longitud")
        self.lon_edit.setDisabled(True)
        geo_layout.addWidget(QLabel("Lon:"))
        geo_layout.addWidget(self.lon_edit)
        form_layout.addRow("Ubicación:", geo_layout)

        # Habilita/deshabilita los campos según el checkbox
        self.geo_checkbox.stateChanged.connect(
            lambda state: [
                self.lat_edit.setDisabled(not state),
                self.lon_edit.setDisabled(not state)
            ]
        )

        layout.addLayout(form_layout)

        self.figure = Figure(figsize=(6, 3))
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
        self.freq_edit.setText(f"{frecuencia_sitio:.3f}")
        geo_data = None
        if self.geo_checkbox.isChecked():
            try:
                lat = float(self.lat_edit.text())
                lon = float(self.lon_edit.text())
                geo_data = {"lat": lat, "lon": lon}
            except Exception:
                geo_data = None

        try:
            freq_usuario = float(self.freq_edit.text())
        except Exception:
            freq_usuario = None

        self.hvsr_results = {
            "geo": geo_data,
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
        if freq_usuario and abs(freq_usuario - frecuencia_sitio) > 1e-3:
            ax.axvline(freq_usuario, c='orange', linestyle='--', label='Frecuencia usuario')
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
        try:
            freq_usuario = float(self.freq_edit.text())
        except Exception:
            freq_usuario = None

        self.hvsr_results["frecuencia_usuario"] = freq_usuario
        if self.hvsr_results is None:
            QMessageBox.warning(self, "Error", "Primero calcula el HVSR.")
            return
        if self.parent is not None:
            self.parent.hvsr_results = self.hvsr_results
            if hasattr(self.parent, "show_hvsr_results"):
                self.parent.show_hvsr_results()
            if hasattr(self.parent, "tabs") and hasattr(self.parent, "tab_hvsr"):
                self.parent.tabs.setCurrentWidget(self.parent.tab_hvsr)

            if self.hvsr_results.get("geo") is not None:
                punto = {
                    "lat": self.hvsr_results["geo"]["lat"],
                    "lon": self.hvsr_results["geo"]["lon"],
                    "frecuencia": self.hvsr_results["frecuencia_sitio"],
                    "periodo": 1.0 / self.hvsr_results["frecuencia_sitio"] if self.hvsr_results["frecuencia_sitio"] > 0 else None
                }
                if hasattr(self.parent, "hvsr_points"):
                    self.parent.hvsr_points.append(punto)
                if hasattr(self.parent, "show_hvsr_map"):
                    self.parent.show_hvsr_map()
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