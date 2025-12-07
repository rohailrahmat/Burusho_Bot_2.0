# Windows setup notes

If you're running the backend on Windows, some packages in `requirements.txt` (notably `numpy` and `pandas`) may attempt to build from source and fail without MSVC build tools.

Use the Windows-friendly requirements file to install only necessary runtime dependencies:

```powershell
Set-Location 'C:\Users\rohai\OneDrive\Desktop\FYP_2027\burushaski-chatbot\backend'
& 'C:\Users\rohai\OneDrive\Desktop\FYP_2027\.venv\Scripts\python.exe' -m pip install --upgrade pip setuptools wheel
& 'C:\Users\rohai\OneDrive\Desktop\FYP_2027\.venv\Scripts\python.exe' -m pip install -r .\requirements-windows.txt
```

If you need `pandas`/`numpy` later, install them from binary wheels or using `conda`/`mambaforge` which provides prebuilt packages on Windows.

To run the server locally:

```powershell
& 'C:\Users\rohai\OneDrive\Desktop\FYP_2027\.venv\Scripts\python.exe' -m uvicorn app:app --reload --port 8000
```