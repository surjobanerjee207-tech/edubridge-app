import pypdf
import os

def extract_text(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        elif ext == ".pdf":
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            return "Error: Unsupported file format."
    except Exception as e:
        return f"Error reading file: {str(e)}"
