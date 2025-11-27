
import os
import sys
import importlib.util
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def load_subapp_from_service(service_folder_name: str, alias: str):
    """Load a FastAPI `app` object from a service folder's `app/main.py`.

    This imports the module by path to avoid relying on installed package names
    (which in this repo are often `app` and can clash).
    """
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    main_path = os.path.join(repo_root, service_folder_name, 'app', 'main.py')
    if not os.path.exists(main_path):
        raise ImportError(f"Main app file not found for service '{service_folder_name}' at {main_path}")
    spec = importlib.util.spec_from_file_location(alias, main_path)
    module = importlib.util.module_from_spec(spec)
    loader = spec.loader
    if loader is None:
        raise ImportError(f"Unable to load module for {service_folder_name}")

    
    service_root = os.path.join(repo_root, service_folder_name)
    service_app_root = os.path.join(service_root, 'app')
    if service_app_root not in sys.path:
        sys.path.insert(0, service_app_root)

    
    if repo_root not in sys.path:
        sys.path.insert(1, repo_root)

    sys.modules[alias] = module
    loader.exec_module(module)
    if not hasattr(module, 'app'):
        raise ImportError(f"No 'app' FastAPI instance found in {main_path}")
    return getattr(module, 'app')


try:
    user_management_app = load_subapp_from_service('user_management_service', 'user_management_service_main')
    shape_service_app = load_subapp_from_service('shape_service', 'shape_service_main')
except ImportError as e:
    import traceback
    print(f"Error importing sub-applications: {e}")
    traceback.print_exc()
    print("Please ensure that all microservices exist and their source files are reachable.")
    exit(1)


app = FastAPI(title="Ganithamithura API Gateway")

# Basic CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Mount the sub-applications
app.mount("/auth", user_management_app)
app.mount("/shapes", shape_service_app)

@app.get("/")
async def root():
    return {"message": "Welcome to the Ganithamithura API Gateway"}
