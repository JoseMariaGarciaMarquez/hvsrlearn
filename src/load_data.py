import numpy as np
import matplotlib.pyplot as plt

from obspy import read
from scipy import signal
from obspy.signal.konnoohmachismoothing import konno_ohmachi_smoothing as konno_ohmachi

def load_sac_triple(ruta_z, ruta_n, ruta_e):
    """
    Carga tres archivos SAC (Z, N, E) y retorna los datos, sampling rate y tiempos de cada uno.

    Returns:
        dict con claves 'z', 'n', 'e', cada una con un subdiccionario:
            {
                'data': array de datos,
                'sampling_rate': float,
                'times': array de tiempos (en segundos desde el inicio)
            }
    """
    z = read(ruta_z)[0]
    n = read(ruta_n)[0]
    e = read(ruta_e)[0]

    return {
        'z': {
            'data': z.data,
            'sampling_rate': z.stats.sampling_rate,
            'times': z.times()
        },
        'n': {
            'data': n.data,
            'sampling_rate': n.stats.sampling_rate,
            'times': n.times()
        },
        'e': {
            'data': e.data,
            'sampling_rate': e.stats.sampling_rate,
            'times': e.times()
        }
    }

# Ejemplo de uso:
if __name__ == "__main__":
    ruta_z = r"C:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\hvsrlearn\data\stationA\A04_staA.z.sac"
    ruta_n = r"C:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\hvsrlearn\data\stationA\A04_staA.n.sac"
    ruta_e = r"C:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\repositorios\hvsrlearn\data\stationA\A04_staA.e.sac"

    datos = load_sac_triple(ruta_z, ruta_n, ruta_e)
    print(datos['z']['data'])
    print(datos['z']['sampling_rate'])
    print(datos['z']['times'])