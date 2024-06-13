# TTools for ComfyUI

Enhance your ComfyUI environment with TTools, a powerful suite designed for effective manipulation of text and JSON data, alongside optimization of resolution calculations.

## Features
- **Text Randomization and Formatting**: Simplifies string manipulation by altering and randomizing the sequence.
- **JSON Extraction and Processing**: Allows for robust extraction and manipulation of JSON embedded within strings.
- **SD3 Resolution Solver**: Computes optimal image resolutions to achieve near 1 megapixel clarity under set constraints.

### Installation Steps

1. Navigate to your `/ComfyUI/custom_nodes/` directory.
2. Clone the repository:
   ```bash
   git clone https://github.com/toxicwind/TTools.git
   ```
3. Change to the cloned directory:
   ```bash
   cd TTools
   ```
4. Depending on your setup, install dependencies:
   - **Portable/Venv**:
     ```bash
     path/to/ComfyUI/python_embedded/python.exe -s -m pip install -r requirements.txt
     ```
   - **System Python**:
     ```bash
     pip install -r requirements.txt
     ```

## Contributing

Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
```

This README template now includes specific installation steps tailored to different setups and clarifies how to set up and use `TTools` quickly and efficiently.