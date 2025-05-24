from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QComboBox

class LearnWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aprende sobre HVSR y Procesamiento")
        self.resize(650, 500)
        layout = QVBoxLayout(self)

        self.topic_box = QComboBox()
        self.topic_box.addItems([
            "Ruido Sísmico Ambiental",
            "Procesamiento de Señales",
            "Dominio de Fourier",
            "Cociente Espectral H/V (HVSR)",
            "Método Nakamura"
        ])
        layout.addWidget(QLabel("Selecciona un tema:"))
        layout.addWidget(self.topic_box)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        self.topic_box.currentIndexChanged.connect(self.update_info)
        self.update_info(0)

    def update_info(self, idx):
        temas = {
            0: """
                <h2>Ruido Sísmico Ambiental</h2>
                <p>
                El ruido sísmico ambiental es generado por fuentes naturales, como el viento y el oleaje, y actividades humanas, como el tráfico y la maquinaria. Aunque tiene amplitud baja, este ruido contiene información valiosa sobre las propiedades dinámicas del subsuelo, ya que está compuesto principalmente por ondas superficiales, como ondas Rayleigh.
                </p>
                <p>
                Los métodos HVSR y SPAC aprovechan estas ondas para estimar parámetros críticos, como la frecuencia fundamental y las curvas de dispersión, sin necesidad de fuentes sísmicas activas.
                </p>
                <p>
                <b>Referencia:</b> Wathelet et al. (2020), Geopsy.
                </p>
            """,
            1: """
                <h2>Procesamiento de Señales</h2>
                <p>
                El procesamiento incluye filtrado, rechazo de ventanas contaminadas y análisis espectral. Un procesamiento adecuado mejora la calidad de los resultados HVSR.
                </p>
                <ul>
                    <li><b>Filtrado:</b> Permite eliminar frecuencias no deseadas.</li>
                    <li><b>Rechazo de ventanas:</b> Se eliminan segmentos de la señal con ruido anómalo.</li>
                    <li><b>Análisis espectral:</b> Permite estudiar la energía de la señal en el dominio de la frecuencia.</li>
                </ul>
                <h3>Autocorrelación y Crosscorrelación</h3>
                <p>
                La <b>autocorrelación</b> mide la similitud de una señal consigo misma en diferentes retardos temporales, mientras que la <b>crosscorrelación</b> compara dos señales diferentes para identificar patrones comunes. Estas herramientas son fundamentales para calcular la coherencia espacial en el método SPAC.
                </p>
                <p>
                <b>Autocorrelación discreta:</b><br>
                <code>R_x(τ) = Σ x[n] · x[n+τ]</code>
                </p>
                <p>
                <b>Crosscorrelación discreta:</b><br>
                <code>R_xy(τ) = Σ x[n] · y[n+τ]</code>
                </p>
                <p>
                En Python, puedes usar <b>SciPy</b> para calcular estas funciones.
                </p>
            """,
            2: """
                <h2>Dominio de Fourier</h2>
                <p>
                El análisis de Fourier permite descomponer una señal compleja en sus componentes de frecuencia, proporcionando información sobre la distribución de energía en el dominio de la frecuencia. La transformada de Fourier es fundamental para calcular los espectros de las componentes horizontales y verticales en HVSR, y para analizar las correlaciones de fase en SPAC.
                </p>
                <p>
                <b>Transformada de Fourier continua:</b><br>
                <code>X(f) = ∫ x(t) e<sup>-j2πft</sup> dt</code>
                </p>
                <p>
                <b>Transformada de Fourier discreta:</b><br>
                <code>X(f) = Σ x[n] e<sup>-j2πfn/N</sup></code>
                </p>
                <p>
                donde x[n] es la señal discreta, N el número de muestras y f la frecuencia.
                </p>
                <p>
                <a href="https://docs.scipy.org/doc/scipy/tutorial/fft.html">Guía de Fourier en SciPy</a>
                </p>
            """,
            3: """
                <h2>Cociente Espectral H/V (HVSR)</h2>
                <p>
                El método HVSR (Horizontal-Vertical Spectral Ratio) propuesto por Nakamura (1989) se calcula dividiendo el espectro horizontal entre el espectro vertical en función de la frecuencia:
                </p>
                <p>
                <code>HVSR(f) = EspectroHorizontal(f) / EspectroVertical(f)</code>
                </p>
                <p>
                Es común observar un pico en la relación de amplitudes, conocido como el pico de resonancia, que indica la frecuencia fundamental de vibración de la capa de suelo blando (<b>f<sub>0</sub></b>).
                </p>
                <p>
                <b>Fórmula general:</b><br>
                <code>HVSR(f) = sqrt(P_N(f) + P_E(f)) / P_Z(f)</code>
                </p>
                <p>
                donde P_N, P_E y P_Z son los espectros de potencia de las componentes Norte, Este y Vertical, respectivamente.
                </p>
                <p>
                <b>Estimación del espesor:</b><br>
                <code>f<sub>0</sub> = β / (4H)</code>
                </p>
                <p>
                donde β es la velocidad de ondas de corte y H el espesor de la capa de suelo blando.
                </p>
            """,
            4: """
                <h2>Método Nakamura</h2>
                <p>
                El método Nakamura es una técnica HVSR que utiliza el cociente espectral entre las componentes horizontales y verticales del ruido sísmico ambiental para identificar la frecuencia fundamental del sitio. Es ampliamente utilizado en estudios de microzonificación sísmica.
                </p>
                <p>
                <b>Referencia:</b> Nakamura (1989), Lermo y Chávez-García (1994).
                </p>
            """
        }
        self.text.setHtml(temas.get(idx, ""))