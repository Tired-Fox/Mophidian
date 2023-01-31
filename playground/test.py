from pathlib import Path
from mophidian.FileSystem.nodes import Container, File, Page, Directory, FileState, Nav
from mophidian.FileSystem import render_pages
from phml import PHML
from mophidian.Server.server import Server, ServerThread

file_system = Directory("test")

page_2 = Page("test/sub/sample_2.phml", ignore="test")
page_1 = Page("test/sample.phml", ignore="test")
file_system.add(page_1)
file_system.add(page_2)

print(file_system)
render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))
input("Enter to continue...")
page_2.state = FileState.DELETED
full_path = page_2.full_path
render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))
print(file_system)
input("Enter to continue...")
page_2.state = FileState.UPDATED
file_system.add(page_2)
render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))
print(file_system)

# server_thread = Thread(target=lambda: .serve_forever(), daemon=True)
server = ServerThread(Server(port=8081))
try:
    server.start()
    while True: pass
except KeyboardInterrupt:
    server.stop()
    input(server.stopped())