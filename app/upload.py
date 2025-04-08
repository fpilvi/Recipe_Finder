import os
from fastapi import UploadFile, File, HTTPException
from pathlib import Path
from shutil import copyfileobj

UPLOAD_FOLDER = "static/uploads/"

Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)


def save_file(file: UploadFile, filename: str) -> str:
    """
    Save the uploaded file to the local directory and return the file path.
    """
    try:
        file_location = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_location, "wb") as buffer:
            copyfileobj(file.file, buffer)

        return file_location
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save error: {str(e)}")


def delete_file(filename: str) -> None:
    """
    Delete a file from the upload directory.
    """
    try:
        file_location = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.exists(file_location):
            os.remove(file_location)
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File delete error: {str(e)}")
