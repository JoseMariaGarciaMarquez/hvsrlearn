class DataPlotter:
    def __init__(self, figure):
        self.figure = figure

    def plot_triple_component(self, datos):
        """
        Plotea las tres componentes (Z, N, E) en subplots usando la Figure asociada.
        """
        self.figure.clear()
        componentes = ['z', 'n', 'e']
        nombres = ['Vertical (Z)', 'Norte (N)', 'Este (E)']
        colores = ['black', 'blue', 'red']

        axes = []
        for i, comp in enumerate(componentes):
            ax = self.figure.add_subplot(3, 1, i+1)
            ax.plot(datos[comp]['times'], datos[comp]['data'], color=colores[i], label=nombres[i])
            ax.set_ylabel(nombres[i])
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend(loc='upper right', fontsize='small', frameon=False)
            if i < 2:
                ax.tick_params(labelbottom=False)
            else:
                ax.set_xlabel("Tiempo (s)")
            axes.append(ax)
        self.figure.suptitle("Datos cargados", fontsize=14, y=0.98)
        self.figure.tight_layout(rect=[0, 0, 1, 0.96])