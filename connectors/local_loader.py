import os

def load_files(folder_path):
    files = []
    for file in os.listdir(folder_path):
        if file.endswith(".pdf") or file.endswith(".docx"):
            files.append(os.path.join(folder_path, file))
    return files