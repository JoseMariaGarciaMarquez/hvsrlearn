import os
import obspy
import numpy as np
import matplotlib.pyplot as plt

from obspy import read

ruta = r'C:\Users\lenovo.DESKTOP-NGHQ1VP\OneDrive\Documentos\voladura\STA_A'
sta_a_z = r'6631z0\20140221_2200_z.gcf'
sta_a_n = r'6631n0\20140221_2200_n.gcf'
sta_a_e = r'6631e0\20140221_2200_e.gcf'


sta_a_z = os.path.join(ruta, sta_a_z)
sta_a_n = os.path.join(ruta, sta_a_n)
sta_a_e = os.path.join(ruta, sta_a_e)


# Cargar datos
staz = read(sta_a_z)
stan = read(sta_a_n)
stae = read(sta_a_e)

print(staz)
print(stan)
print(stae)