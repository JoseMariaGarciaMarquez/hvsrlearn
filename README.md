# hvsrlearn
![icono](https://github.com/JoseMariaGarciaMarquez/hvsrlearn/assets/30852961/4e47c871-a680-43f7-88ba-3e3525a29638)

## Overview

**hvsrlearn** is a Python application for the calculation and analysis of the Horizontal-to-Vertical Spectral Ratio (HVSR) from seismic data in three components (Z, N, E). The application features a modern graphical user interface built with PyQt5, providing an intuitive and interactive platform for seismic data analysis and visualization.

## Key Features

- **User-Friendly Interface:** An intuitive GUI with organized controls for easy interaction.
- **Simultaneous Multi-File Loading:** Now supports loading the three seismic components (Z, N, E) at once, streamlining the workflow.
- **Dedicated Processing Window:** Includes a dedicated window for signal processing, allowing bandpass filtering and rejection of unwanted time windows, with immediate visualization of the effects.
- **Customizable HVSR Calculation:** A dedicated HVSR calculation window lets users select the method, window type, and other parameters, with simplified controls for fixed parameters (e.g., oversampling and confidence).
- **Real-Time Results Visualization:** HVSR spectrum and relevant parameters are visualized in real time, both in the calculation window and in the main interface.
- **Results Saving and Export:** Results, including graphs and key data, can be saved for further reference. The HVSR figure can be exported as PNG or PDF.
- **Compatibility with Various HVSR Methods:** Multiple recognized methods for HVSR spectrum calculation are available.
- **Console Monitoring:** An integrated console displays detailed process and result information for close monitoring.
- **Robust Validations:** Improved error handling and user feedback for a smoother experience.

## Installation

To run "hvsrlearn," follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/JoseMariaGarciaMarquez/hvsrlearn.git
    cd hvsrlearn
    ```

2. Create the conda environment:

    ```bash
    conda env create -f conda/hvsrlearn.yaml
    ```

3. Run the application:

    ```bash
    python src/hvsrlearn.py
    ```

## Usage

1. Launch the application using the installation instructions above.
2. Load seismic data files for Z, N, and E components (now possible in a single step).
3. Use the processing window to apply bandpass filters or reject unwanted time windows, visualizing the results instantly.
4. Open the HVSR calculation window to select the method and parameters, and calculate the HVSR spectrum.
5. Visualize results in real time and monitor the process through the integrated console.
6. Save or export results and figures as needed.

### Screenshots

![gui](https://github.com/user-attachments/assets/c2fd37e6-1ec0-4156-a811-81b0590da4d5)
*Main graphical user interface (GUI) showing the loaded seismic data components.*

![verinfo](https://github.com/user-attachments/assets/08fdf6d5-f2ad-4a70-9583-64ccae6cacde)
*Detailed information about the seismic data being displayed.*

![verdatos](https://github.com/user-attachments/assets/ac8e0d60-6971-4c18-885d-2f296228a8e9)
*Graphical display of the three seismic components (Z, N, E).*

![calculatehvsr](https://github.com/user-attachments/assets/4206705b-b95b-487c-b1e3-f4c479ed5ae1)
*HVSR spectrum calculated from the loaded seismic data.*

## Contributing

Contributions are welcome! If you have ideas for improvements or encounter issues, please open an [issue](https://github.com/JoseMariaGarciaMarquez/hvsrlearn/issues) or submit a [pull request](https://github.com/JoseMariaGarciaMarquez/hvsrlearn/pulls).

## License

This project is licensed under the [MIT License](LICENSE). Feel free to use and modify the code for your purposes.

---

**Note:** Replace "your-username" with your GitHub username in the installation instructions if needed.