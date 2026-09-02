# orchtwain-lotts

MATLAB‑free implementation of the LOTTS domain‑specific language for orchestrating digital twins. This repository provides:

- A Rascal‑based DSL (in `LOTTS/`) for describing digital twin services and their interconnections.
- A Python runtime (in `src/`) that executes LOTTS models using **FMU** and **Python** backends only.

This codebase is part of the **OrchTwin** research project on digital twin orchestration and model‑driven engineering. It deliberately excludes MATLAB/Simulink so that anyone can run the code with open tools only.

## Features

- **LOTTS DSL**: Define sensors, data processes, simulation models, and connections in a compact, domain‑specific language.
- **FMU support**: Execute FMI 2.0 FMU models via `fmpy`.
- **Python models**: Wrap native Python classes as simulation or data‑processing components.
- **No MATLAB dependency**: MATLAB/Simulink is **not** supported in this repository.

## Supported simulation engines

- `FMU` – for FMI 2.0 FMU models.
- `Python` – for native Python model classes.

## Requirements

- Python 3.10+ (tested with 3.11/3.12)
- [Rascal](https://www.rascal-mpl.org/) (for language engineering work in `LOTTS/`)
- `fmpy` (for FMU support)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/<your-username>/orchtwain-lotts.git
   cd orchtwain-lotts
   ```

2. (Recommended) Create a virtual environment:

   ```bash
   python -m venv .venv
   # On Windows
   .venv\Scripts\activate
   # On macOS/Linux
   source .venv/bin/activate
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Ensure Rascal is installed and can access the `LOTTS` project (e.g., via the Rascal VS Code extension or Eclipse IDE).

## Basic usage (overview)

1. Define a digital twin service in a `.oca` file under `LOTTS/examples/` using the LOTTS syntax.
2. Use the Rascal code generator (`GenerateCode.rsc`) to produce Python orchestration code.
3. Place FMU files and/or Python model files in an appropriate directory.
4. Run the generated Python script, which uses the `src` package to instantiate and connect components.

Detailed usage examples and tutorials will be added as the implementation matures.

## Project structure

- `LOTTS/` – Rascal project defining the LOTTS language (syntax, AST, checks, code generation).
- `src/` – Python implementation of the digital twin runtime:
  - `Comm.py` – core component classes (`Source`, `Sink`, `Model`, etc.).
  - `API/` – backend wrappers:
    - `FMUAPI.py` – FMU execution via `fmpy`.
    - `PythonAPI.py` – Python model wrapping.
  - `exeMgn.py`, `exeAreas.py`, `Service.py`, `GlOb.py` – execution and service management utilities.

## License

This project is licensed under the MIT License – see the `LICENSE` file for details.

## Acknowledgements

This implementation is part of the OrchTwin project on digital twin orchestration, model‑driven engineering, and systems engineering.
