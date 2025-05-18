import numpy as np
from scipy.signal import butter, filtfilt

class ProcessData:
    def __init__(self, data, sampling_rate):
        """
        data: array (o dict de arrays) con la señal original.
        sampling_rate: frecuencia de muestreo en Hz.
        """
        self.data = data  # Puede ser un array o un dict {'z':..., 'n':..., 'e':...}
        self.sampling_rate = sampling_rate

    def bandpass_filter(self, lowcut, highcut, order=4):
        """
        Aplica un filtro pasa bandas Butterworth a la señal.
        lowcut, highcut en Hz.
        """
        b, a = butter(order, [lowcut, highcut], btype='band', fs=self.sampling_rate)
        if isinstance(self.data, dict):
            filtered = {}
            for comp in self.data:
                filtered[comp] = filtfilt(b, a, self.data[comp])
            return filtered
        else:
            return filtfilt(b, a, self.data)

    def reject_time_windows(self, start_end_list, times_dict):
        """
        Elimina segmentos de tiempo de la señal usando el vector de tiempos.
        start_end_list: lista de tuplas [(t_ini, t_fin), ...] en segundos.
        times_dict: dict con los vectores de tiempo para cada componente.
        """
        if isinstance(self.data, dict):
            for comp in self.data:
                self.data[comp], times_dict[comp] = self._reject_windows_array(
                    self.data[comp], times_dict[comp], start_end_list
                )
        else:
            self.data, times_dict = self._reject_windows_array(self.data, times_dict, start_end_list)

    def _reject_windows_array(self, array, times, start_end_list):
        mask = np.ones_like(array, dtype=bool)
        for t_ini, t_fin in start_end_list:
            mask &= ~((times >= t_ini) & (times <= t_fin))
        new_array = array[mask]
        # Recalcula el vector de tiempos para que sea continuo desde cero
        dt = times[1] - times[0] if len(times) > 1 else 0
        new_times = np.arange(len(new_array)) * dt
        return new_array, new_times