# Batch Cropper

### Image Cropper Tool

A simple and efficient application for batch cropping images.

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Overview

Image Cropper Tool is a desktop application that allows you to quickly crop multiple images to a fixed size. It's particularly useful for:

-  Batch processing images for consistent dimensions
-  Creating thumbnails or profile pictures
-  Extracting regions of interest from larger images

![demo](/assets/batchcropper-demo.gif)

## Features

-  **Batch Processing**: Load and crop multiple images at once
-  **Visual Interface**: See all your images with crop boxes overlaid
-  **Interactive Cropping**: Click to reposition or drag to move crop boxes
-  **Adjustable Crop Size**: Set custom dimensions with fine-grained control (8-pixel increments)
-  **Optional Resizing**: Resize cropped images to specific dimensions after cropping
-  **Smart Output**: Automatically creates organized output directories

## Requirements

-  Python 3.7 or higher
-  PyQt5 5.15.0 or higher
-  Pillow 9.0.0 or higher

## Installation

Option 1: Install from source code

```bash
# Clone the repository
git clone https://github.com/wflore19/BatchCropper.git
cd BatchCropper

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m src\app.py
```

Option 2: Download executable file for Windows

Step 1. Go to the latest version in 'Releases'  
Step 2. Download BatchCropper.exe  
Step 3. Run BatchCropper.exe on Windows

\*\*\* You may get a warning message when running because the app does not have a digital signature for Windows, you can just click 'More Info' then 'Run Anyways'

## Usage

1. **Launch the application**:

   ```bash
   python -m src\app.py
   ```

2. **Load images**:

   -  Click "Select Image Directory"
   -  Choose a folder containing your images
   -  All supported images will be displayed in a scrollable list

3. **Adjust crop areas**:

   -  Click anywhere on an image to center the crop box at that position
   -  Drag inside the red box to move it around
   -  Use the "Crop Size" spinner to change dimensions (default: 512x512)

4. **Process images**:
   -  Optionally set "Resize to" value for post-crop resizing
   -  Click "Crop All Images" to process the entire batch
   -  Find your cropped images in the `cropped/` subdirectory

## Supported Image Formats

-  PNG (.png)
-  JPEG (.jpg, .jpeg)
-  BMP (.bmp)
-  GIF (.gif)

## Keyboard Shortcuts & Controls

| Action           | Control                                  |
| ---------------- | ---------------------------------------- |
| Center crop box  | Left-click outside the box               |
| Move crop box    | Left-click and drag inside the box       |
| Adjust crop size | Use the spinner control (8px increments) |
| Process all      | Click "Crop All Images" button           |

## Output Structure

```
your-image-directory/
├── image1.jpg
├── image2.png
└── cropped/
    ├── cropped_image1.jpg
    └── cropped_image2.png
```

## Examples

### Basic Usage

```bash
# Run the tool
python -m src\app.py

# Select your image directory
# Adjust crop boxes as needed
# Click "Crop All Images"
```

### With Custom Settings

-  Set crop size to 256x256 pixels
-  Enable resize to 128x128 after cropping
-  Process all images in one click

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Known Issues

-  Very large images (>4K) may display slowly
-  GIF animations are not preserved (only first frame is used)

## Future Enhancements

-  [ ] Support for custom aspect ratios (not just square crops)
-  [ ] Batch export with different formats
-  [ ] Keyboard shortcuts for faster navigation
-  [ ] Undo/redo functionality
-  [ ] Save/load crop configurations

## License

This project is open source and available under the [MIT License](LICENSE).

## Acknowledgments

-  Built with PyQt5 for the GUI framework
-  Uses Pillow for image processing
