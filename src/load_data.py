from obspy import read

class DataLoader:
    """
    Clase para cargar y manejar tres componentes sísmicas (Z, N, E) de cualquier formato soportado por ObsPy.
    """

    @staticmethod
    def _load_trace(ruta):
        """Carga un solo archivo sísmico y retorna el primer Trace."""
        return read(ruta)[0]

    @staticmethod
    def _trace_to_dict(trace):
        """Convierte un Trace de ObsPy a un diccionario estándar."""
        return {
            'data': trace.data,
            'sampling_rate': trace.stats.sampling_rate,
            'times': trace.times()
        }

    @classmethod
    def load_triple(cls, ruta_z, ruta_n, ruta_e):
        """
        Carga tres archivos sísmicos (Z, N, E) y retorna un diccionario con los datos.
        """
        componentes = {}
        for comp, ruta in zip(['z', 'n', 'e'], [ruta_z, ruta_n, ruta_e]):
            trace = cls._load_trace(ruta)
            componentes[comp] = cls._trace_to_dict(trace)
        return componentes