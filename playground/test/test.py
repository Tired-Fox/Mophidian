from pathlib import Path
from mophidian.FileSystem.nodes import (
    Container,
    File,
    Page,
    Directory,
    FileState,
    Nav,
    Layout,
    Component,
    Renderable
)
from mophidian.FileSystem import render_pages, build
from phml import PHML
from mophidian.Server.server import Server, ServerThread
from mophidian import states

file_system, static_files, component_files, nav, phml = build()

def update_layout(layout: Layout):
    layout.state = FileState.UPDATED
    file_system.build_hierarchy()
    for page in layout.linked_files:
        page.state = FileState.UPDATED
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )
    
def update_page(page: Renderable):
    page.state = FileState.UPDATED
    file_system.build_hierarchy()
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )

def update_component(component: Component, phml: PHML):
    phml.add((component.cname, component.full_path))
    for page in component.linked_files:
        page.state = FileState.UPDATED
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )


def remove_layout(layout: Layout):
    for page in layout.linked_files:
        page.state = FileState.UPDATED
    file_system.remove(layout.full_path)
    file_system.build_hierarchy()
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )
    
def remove_page(page: Renderable):
    page.state = FileState.DELETED
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )

def remove_component(component: Component, phml: PHML):
    for page in component.linked_files:
        page.state = FileState.UPDATED
    phml.remove(component.cname)
    render_pages(
        file_system, static_files, component_files, states["dest"], phml, file_system.build_nav()
    )

#! Update layout
input("Built default. Press enter to modify layout...")
old_layout_data = ""
with open("src/pages/sub/layout.phml", "r", encoding="utf-8") as layout:
    old_layout_data = layout.read()
with open("src/pages/sub/layout.phml", "w", encoding="utf-8") as layout:
    layout.write(
        """\
<>
    <h2>Edited</h2>
    <slot />
</>\
"""
    )
layout = file_system.find("sub/layout.phml")

if layout is not None and isinstance(layout, Layout):
    update_layout(layout)

with open("src/pages/sub/layout.phml", "w", encoding="utf-8") as layout:
    layout.write(old_layout_data)

#! Remove layout
input("Updated layout. Press enter to remove layout...")
layout = file_system.find("sub/layout.phml")
if layout is not None and isinstance(layout, Layout):
    remove_layout(layout)

#! Update component
input("Removed layout. Press enter to modify component...")
old_layout_data = ""
with open("src/components/Sample.phml", "r", encoding="utf-8") as layout:
    old_layout_data = layout.read()
with open("src/components/Sample.phml", "w", encoding="utf-8") as layout:
    layout.write(
        """\
<div>
    <p>Sample Component (Edited)</p>
<div>\
"""
    )

component = component_files.find("Sample.phml")

if component is not None and isinstance(component, Component):
    update_component(component, phml)

with open("src/components/Sample.phml", "w", encoding="utf-8") as layout:
    layout.write(old_layout_data)

input("Updated component. Press enter to remove component...")
component = component_files.find("Sample.phml")
if component is not None and isinstance(component, Component):
    remove_component(component, phml)
input("Removed component. Press enter to modify a page...")
old_layout_data = ""
with open("src/pages/page.phml", "r", encoding="utf-8") as layout:
    old_layout_data = layout.read()
with open("src/pages/page.phml", "w", encoding="utf-8") as layout:
    layout.write(
        """\
<h1>Home (Edited)</h1>\
"""
    )

page = file_system.find("src/pages/page.phml")

if page is not None and isinstance(page, Renderable):
    update_page(page)

with open("src/pages/page.phml", "w", encoding="utf-8") as layout:
    layout.write(old_layout_data)
input("Updated page. Press enter to remove a page...")

page = file_system.find("src/pages/page.phml")
if page is not None and isinstance(page, Renderable):
    remove_page(page)
    print(file_system)
    for layout in file_system.layouts():
        print(layout, layout.linked_files)
    input()
    for component in component_files.components():
        print(component, component.linked_files)
input("Removed page. Press enter to finish...")

# TODO: Test modifying and deleting static files
# ? updating/removing files and dirty rendering

# file_system = Directory("test")

# page_2 = Page("test/sub/sample_2.phml", ignore="test")
# page_1 = Page("test/sample.phml", ignore="test")
# file_system.add(page_1)
# file_system.add(page_2)

# print(file_system)
# render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))

# input("Enter to continue...")
# page_2.state = FileState.DELETED
# full_path = page_2.full_path
# render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))
# print(file_system)
# input("Enter to continue...")
# page_2.state = FileState.UPDATED
# file_system.add(page_2)
# render_pages(file_system, Directory(""), "dist/", PHML(), Nav("nav"))
# print(file_system)

# # server_thread = Thread(target=lambda: .serve_forever(), daemon=True)
# server = ServerThread(Server(port=8081))
# try:
#     server.start()
#     while True: pass
# except KeyboardInterrupt:
#     server.stop()
#     input(server.stopped())
