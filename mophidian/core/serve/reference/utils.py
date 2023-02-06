import socket
import os

root_path = os.path.dirname(os.path.dirname(__file__))


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def file_path_to_module_name(path: str) -> str:
    """Convert file path to module name"""
    return (
        os.path.abspath(path)
        .replace(root_path, "of")
        .replace(".py", "")
        .replace("/__init__", "")
        .replace("/", ".")
    )
