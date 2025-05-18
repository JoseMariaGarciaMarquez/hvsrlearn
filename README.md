# hvsrlearn
![icono](https://github.com/JoseMariaGarciaMarquez/hvsrlearn/assets/30852961/4e47c871-a680-43f7-88ba-3e3525a29638)


## Overview

"hvsrlearn" is a Python application designed for the calculation and analysis of the Horizontal-to-Vertical Spectral Ratio (HVSR) from seismic data in three components (Z, N, E). The application features a graphical user interface built using Tkinter, providing an intuitive and interactive platform for users to analyze and visualize seismic data.

## Key Features

- **User-Friendly Interface:** The application offers an intuitive graphical interface with organized controls for easy interaction.
- **Real-time Results Visualization:** Users can visualize the HVSR spectrum and relevant parameters in real-time as they adjust settings, enhancing the analysis process.
- **Customizable Analysis Process:** Users can load seismic data files for Z, N, and E components, and customize parameters such as oversampling, window width, overlap, HVSR method, and more.
- **Results Saving Capability:** The application allows users to save generated results, including graphs and relevant data, for further reference.
- **Compatibility with Various HVSR Calculation Methods:** Users can choose from multiple recognized methods for HVSR spectrum calculation, providing flexibility in the analysis approach.
- **Console Monitoring:** An integrated console displays detailed process and result information, enabling users to monitor the analysis progress closely.
- **File Management:** Functionalities for searching and loading seismic data files enhance accessibility and ease of use.

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

1. Launch the application using the provided installation instructions.
2. Load seismic data files for Z, N, and E components.
3. Customize analysis parameters such as oversampling, window width, overlap, HVSR method, etc.
4. Visualize real-time results and monitor the analysis process through the integrated console.
5. Save generated results for further analysis or reference.

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

**Note:** Replace "your-username" with your GitHub username in the installation instructions.


