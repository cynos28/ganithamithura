# Shape Service

## Project Description

This service aims to provide a basic understanding of 3D and 2D shapes. It includes features such as an AI model to identify shapes using real-world images, shape-related games, a drawing canvas for practice, and progress reports to measure user game progress.

## Getting Started

1.  **Clone the repository**

    ```bash
    git clone <repository_url>
    cd shape-service
    ```

## Folder Structure

```
D:\Dilshan_FYP\Dilshan_repo\ganithamithura\shape-service\
├───.env
├───.python-version
├───pyproject.toml
├───README.md
├───uv.lock
├───.venv\
│   ├───Lib\...
│   └───Scripts\...
├───app\
│   ├───_init_.py
│   ├───main.py
│   ├───__pycache__\
│   │   └───main.cpython-313.pyc
│   ├───constants\
│   │   └───constants.py
│   ├───controllers\
│   ├───endpoints\
│   │   ├───endpoints.py
│   │   └───__pycache__\
│   │       └───endpoints.cpython-313.pyc
│   ├───models\
│   │   └───model.py
│   └───services\
│       └───__init__.py
├───assets\
├───database\
│   └───database.py
└───shape_service.egg-info\
    ├───dependency_links.txt
    ├───entry_points.txt
    ├───PKG-INFO
    ├───requires.txt
    ├───SOURCES.txt
    └───top_level.txt
```

## Execution Steps

1.  **Install Dependencies**

    This project uses `pyproject.toml` to manage its dependencies. Install them using `uv`:

    ```bash
    uv pip install -e .
    ```

2.  **Run the Application**

    ```bash
    uvicorn app.main:app --reload
    ```

    The application will be accessible at `http://127.0.0.1:8000`.
    The API documentation will be available at `http://127.0.0.1:8000/docs`.
