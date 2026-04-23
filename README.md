# SubSink

******************************************************************************************************
|  ATTENTION: IF YOU ARE SEEING THIS MESSAGE IT MEANS THAT THE PROJECT IS NOT FULLY COMPLETE.        |
|  WHILE THE BASE FUNCTIONALITY IS UP THERE IS SOME CLEANING THAT IS REQUIRED BEFORE IT IS DISTRIBUTABLE.  |
******************************************************************************************************

This project is a collection of Python scripts and utilities for audio device management, capture, and debugging on Linux systems (with a focus on PipeWire and related audio frameworks). It is a work in progress and is being developed as part of an independent study research project.

## Project Structure

- **audio_utils.py**: Core utility functions for audio device management and interaction.
- **AudioSwitch.py**: Script for switching audio devices or profiles (details TBD).
- **capture.py**: Audio capture script, likely for recording or monitoring audio streams.
- **debug_audio.py**: Tools for debugging audio routing, device status, or troubleshooting audio issues.
- **docs/ApplicationFlow.md**: Short high-level walkthrough of startup, routing, switching, and cleanup.
- **docs/class-reference/**: Detailed notes for the main controller and routing classes.

## Features (Planned & In Progress)
- List and manage audio devices (input/output)
- Switch between audio devices or profiles
- Capture audio streams for analysis or recording
- Debug and visualize audio routing and device status
- CLI tools for scripting and automation

## Getting Started

### Prerequisites
- Python 3.8+
- Linux system (PipeWire recommended)
- Required Python packages (see below)

### Installation
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd ResearchProjectSpr26
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
   *(If requirements.txt is not present, install any needed packages manually as you encounter ImportErrors.)*

### Usage
Each script can be run independently. Example:
```sh
python audio_utils.py
```

Refer to the source code for available functions and usage patterns. More detailed documentation and CLI examples will be added as the project matures.

For a quick runtime overview, see [docs/ApplicationFlow.md](docs/ApplicationFlow.md).

## Contributing
This project is currently under active development and not ready for external contributions. If you have suggestions or want to collaborate, please open an issue or contact the maintainer.

## License
[MIT License](LICENSE) *(To be added)*

## Acknowledgments
- PipeWire and Linux audio community
- CSU Independent Study Program

---
*This README will be updated as the project evolves. Stay tuned for more features and documentation!*
