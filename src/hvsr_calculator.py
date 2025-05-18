import numpy as np
from scipy import signal
from obspy.signal.konnoohmachismoothing import konno_ohmachi_smoothing

def calculate_hvsr_helper(z, n, e, sm, method, window, ancho, overlap, detr, confianza, b, samples):
    """
    Calcula el espectro HVSR a partir de tres componentes sísmicas.

    Parámetros:
    - z, n, e: arrays de datos (Z, N, E)
    - sm: factor de oversampling
    - method: método HVSR ('Luendei and Albarello N', 'Luendei and Albarello E', 'Picozzi', 'Lunedei and Malischewsky', 'Nakamura', 'Nuevo')
    - window: tipo de ventana ('hann', 'hamming', etc.)
    - ancho: ancho de ventana en segundos
    - overlap: porcentaje de solapamiento entre ventanas
    - detr: tipo de detrending ('linear', 'constant', etc.)
    - confianza: nivel de confianza para el umbral de desviación estándar
    - b: parámetro b para suavizado Konno-Ohmachi
    - samples: frecuencia de muestreo

    Retorna:
    - f: vector de frecuencias
    - HV: HVSR completo
    - sd_moving: desviación estándar móvil
    - f_rejected: frecuencias rechazadas
    - rejected_data: valores HVSR rechazados
    - frecuencia_sitio: frecuencia del pico principal
    - HV_f: HVSR filtrado
    - pos: posición del pico
    """
    nperseg = int(ancho * samples)

    z = signal.detrend(z, type='linear')
    n = signal.detrend(n, type='linear')
    e = signal.detrend(e, type='linear')

    overlapping = int((overlap / 100) * nperseg)

    f, Pz = signal.welch(z, fs=samples,
                         window=window,
                         nperseg=nperseg,
                         noverlap=overlapping,
                         nfft=sm * nperseg, detrend=detr,
                         scaling='spectrum', average='median')
    _, Pn = signal.welch(n, fs=samples,
                         window=window,
                         nperseg=nperseg,
                         noverlap=overlapping,
                         nfft=sm * nperseg, detrend=detr,
                         scaling='spectrum', average='median')
    _, Pe = signal.welch(e, fs=samples,
                         window=window,
                         nperseg=nperseg, detrend=detr,
                         noverlap=overlapping,
                         nfft=sm * nperseg,
                         scaling='spectrum', average='median')

    ko_Pz = konno_ohmachi_smoothing(Pz, f, b, normalize=True)
    ko_Pn = konno_ohmachi_smoothing(Pn, f, b, normalize=True)
    ko_Pe = konno_ohmachi_smoothing(Pe, f, b, normalize=True)

    if method == 'Luendei and Albarello N':
        HV = ko_Pn / ko_Pz
    elif method == 'Luendei and Albarello E':
        HV = ko_Pe / ko_Pz
    elif method == 'Picozzi':
        HV = (np.sqrt(ko_Pn * ko_Pe)) / ko_Pz
    elif method == 'Lunedei and Malischewsky':
        HV = np.sqrt((ko_Pn + ko_Pe) / ko_Pz)
    elif method == 'Nakamura':
        HV = (np.sqrt(ko_Pn**2 + ko_Pe**2)) / ko_Pz
    elif method == 'Nuevo':
        HV = (ko_Pn + ko_Pe) / ko_Pz
    else:
        raise ValueError("Método HVSR no reconocido.")

    window_size = 100
    sd = np.std(HV[:window_size])
    sd_moving = np.zeros_like(HV)
    for i in range(window_size, len(HV)):
        sd_moving[i - window_size:i] = sd
        sd = np.std(HV[i - window_size + 1:i + 1])

    sd_threshold = confianza * (max(sd_moving) / 100)
    mask = sd_moving < sd_threshold

    rejected_data = HV[~mask]
    f_rejected = f[~mask]

    # Filtrar para buscar el pico solo entre 0.1 y 20 Hz
    rango_mask = (f >= 0.1) & (f <= 20)
    f_f = f[mask & rango_mask]
    HV_f = HV[mask & rango_mask]

    if len(HV_f) > 0:
        pos = int(np.argmax(HV_f))
        frecuencia_sitio = f_f[pos]
    else:
        pos = 0
        frecuencia_sitio = np.nan

    return f, HV, sd_moving, f_rejected, rejected_data, frecuencia_sitio, HV_f, pos