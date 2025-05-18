from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QToolBar, QFileDialog, QAction, QDialog, QLabel, QHBoxLayout, QTextEdit, QTabWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from process_window import ProcessWindow
from load_data import load_sac_triple
from plot_data import DataPlotter
from hvsr_window import HVSRWindow


class ProcessingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Procesamiento de Señales")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Aquí irán las opciones de filtrado, Fourier, espectros, rechazo de ventanas, etc."))

class HVSRDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cálculo de Cocientes Espectrales (HVSR)")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Aquí irán las opciones para calcular HVSR y mostrar resultados."))

class HvsrMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HVSRLearn")
        self.setGeometry(100, 100, 1200, 800)
        self.init_ui()

    def init_ui(self):
        # Barra de herramientas superior
        toolbar = QToolBar("Barra principal")
        self.addToolBar(toolbar)

        # Botón Cargar datos
        load_action = QAction("Cargar datos", self)
        load_action.triggered.connect(self.load_data)
        toolbar.addAction(load_action)

        # Botón Procesamiento
        proc_action = QAction("Procesamiento", self)
        proc_action.triggered.connect(self.open_processing_dialog)
        toolbar.addAction(proc_action)

        # Botón HVSR
        hvsr_action = QAction("Cocientes espectrales", self)
        hvsr_action.triggered.connect(self.open_hvsr_dialog)
        toolbar.addAction(hvsr_action)

        # Widget central: tabs de figuras + terminal
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Tabs para las figuras
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=4)

        # Tab 1: Datos cargados
        self.tab_datos = QWidget()
        self.tabs.addTab(self.tab_datos, "Datos cargados")
        tab1_layout = QVBoxLayout(self.tab_datos)
        self.figure_datos = Figure(figsize=(8, 6))
        self.canvas_datos = FigureCanvas(self.figure_datos)
        tab1_layout.addWidget(self.canvas_datos)

        # Tab 2: HVSR
        self.tab_hvsr = QWidget()
        self.tabs.addTab(self.tab_hvsr, "Cálculo H/V")
        tab2_layout = QVBoxLayout(self.tab_hvsr)
        self.figure_hvsr = Figure(figsize=(8, 6))
        self.canvas_hvsr = FigureCanvas(self.figure_hvsr)
        tab2_layout.addWidget(self.canvas_hvsr)

        # Resumen HVSR (debajo del gráfico)
        self.hvsr_summary = QLabel("Aquí aparecerá el resumen del cálculo HVSR.")
        self.hvsr_summary.setWordWrap(True)
        tab2_layout.addWidget(self.hvsr_summary)

        # Terminal de texto
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setFixedHeight(120)
        main_layout.addWidget(self.terminal, stretch=1)

    def load_data(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Archivos SAC (*.sac);;Todos los archivos (*)")
        if file_dialog.exec_():
            files = file_dialog.selectedFiles()
            if len(files) != 3:
                self.terminal.append("Por favor selecciona exactamente 3 archivos SAC: Z, N y E.")
                return

            # Identificar cada componente por su nombre de archivo
            rutas = {'z': None, 'n': None, 'e': None}
            for f in files:
                fname = f.lower()
                if '.z.' in fname or fname.endswith('z.sac'):
                    rutas['z'] = f
                elif '.n.' in fname or fname.endswith('n.sac'):
                    rutas['n'] = f
                elif '.e.' in fname or fname.endswith('e.sac'):
                    rutas['e'] = f

            if None in rutas.values():
                self.terminal.append("No se pudieron identificar las tres componentes (Z, N, E).")
                return

            # --- Aquí se usa load_sac_triple ---
            datos = load_sac_triple(rutas['z'], rutas['n'], rutas['e'])
            self.datos = datos 
            self.terminal.append(f"Archivos cargados:\nZ: {rutas['z']}\nN: {rutas['n']}\nE: {rutas['e']}")

            plotter = DataPlotter(self.figure_datos)
            plotter.plot_triple_component(datos)
            self.canvas_datos.draw()


    def open_processing_dialog(self):
        dlg = ProcessWindow(self.datos, self)
        dlg.exec_()
        self.terminal.append("Ventana de procesamiento abierta.")

    def open_hvsr_dialog(self):
        if not hasattr(self, 'datos') or self.datos is None:
            self.terminal.append("Primero debes cargar y procesar los datos.")
            return
        dlg = HVSRWindow(self.datos, self)
        dlg.exec_()
        self.terminal.append("Ventana de cocientes espectrales abierta.")

    def show_hvsr_results(self):
        print("Dibujando HVSR")  # Debug
        if not self.hvsr_results:
            self.hvsr_summary.setText("No hay resultados HVSR guardados.")
            self.figure_hvsr.clear()
            self.canvas_hvsr.draw()
            return

        res = self.hvsr_results
        resumen = (
            f"<b>Frecuencia del sitio:</b> {res['frecuencia_sitio']:.3f} Hz<br>"
            f"<b>Método:</b> {res['params']['method']}<br>"
            f"<b>Ventana:</b> {res['params']['window']}<br>"
            f"<b>Ancho:</b> {res['params']['ancho']} s<br>"
            f"<b>Overlap:</b> {res['params']['overlap']} %<br>"
            f"<b>Konno-Ohmachi b:</b> {res['params']['b']}<br>"
        )
        self.hvsr_summary.setText(resumen)

        self.figure_hvsr.clear()
        ax = self.figure_hvsr.add_subplot(1, 1, 1)
        f = res["frecuencias"]
        HV = res["HVSR"]
        sd_moving = res["sd_moving"]
        HV_f = res["HV_f"]
        pos = res["pos"]
        frecuencia_sitio = res["frecuencia_sitio"]

        ax.set_title(f'HVSR - Método: {res["params"]["method"]}')
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
        self.figure_hvsr.tight_layout()
        self.canvas_hvsr.draw()
        self.tabs.setCurrentWidget(self.tab_hvsr)

def save_results(self):
    if self.hvsr_results is None:
        QMessageBox.warning(self, "Error", "Primero calcula el HVSR.")
        return
    if self.parent is not None:
        self.parent.hvsr_results = self.hvsr_results
        self.parent.show_hvsr_results()
        self.parent.tabs.setCurrentWidget(self.parent.tab_hvsr)  # <-- Selecciona la pestaña HVSR
    QMessageBox.information(self, "Guardado", "Resultados HVSR guardados y mostrados en la ventana principal.")
    self.accept()

# Para pruebas rápidas:
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = HvsrMainWindow()
    window.show()
    sys.exit(app.exec_())