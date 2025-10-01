**Python OCR Project**

A Python-based Optical Character Recognition (OCR) program that extracts text from images and scanned documents. This project leverages Tesseract OCR with image preprocessing to improve recognition accuracy, making non-searchable documents machine-readable.

**Features:**

- Extracts text from images and scanned documents
- Image preprocessing (resize, grayscale, noise reduction) for better OCR results
- Supports multiple image formats (PNG, JPG, TIFF, etc.)
- Converts extracted text into clean, structured plain text
- Easy to extend for batch processing or integration with other tools

**Technologies Used:**

- Python 3
- pytesseract (Python wrapper for Tesseract OCR)
- Pillow for image loading and manipulation
- (Optional) OpenCV for advanced preprocessing
- (Optional) PyMuPDF / pdf2image for handling PDFs

**For Installation:**

1. Clone this repository

   Open your terminal (Command Prompt, PowerShell, or bash) and run:


```bash
git clone https://github.com/AlyssaMM/my-vscode-program.git
cd my-vscode-program
```

2. Set up a virtual environment **(recommended)**

   Keep dependencies organized:

```bash
python -m venv venv
# Activate it:
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

3. Install dependencies

  You'll want a **requirments.txt** file in your repo. Something like this:

```bash
pytesseract
Pillow
opencv-python
```

  Then users just run:

```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR engine

  Your Python code (pytesseract) is just a wrapper — users also need the actual Tesseract program installed.

  - Windows: Download the installer from [Tesseract OCR](https://github.com/tesseract-ocr/tesseract?utm_source=chatgpt.com) and add it to PATH
  - mac:
    
```bash
brew install tesseract
```

  - Linux (Debian/Ubuntu):

```bash
sudo apt install tesseract-ocr
```

5. Run your script

```bash
python ocr4.py path/to/image.png
```


🚀 **Contributing:**

Contributions, issues, and feature requests are welcome!


    




