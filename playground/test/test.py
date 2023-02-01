from pathlib import Path

from phml import PHML
from watchdog.observers import Observer

from mophidian.FileSystem import (
    FileState,
    Layout,
    Component,
    Renderable,
    Static
)
from mophidian.core import build, render_pages, write_static_files
from mophidian.Server.server import Server, ServerThread
from mophidian.Server.watchdog import Handler
from mophidian import states

file_system, static_files, component_files, phml = build()

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

def update_static(static: Static):
    static.state = FileState.UPDATED
    write_static_files(file_system, static_files, states["dest"])
    
def remove_static(static: Static):
    static.state = FileState.DELETED
    write_static_files(file_system, static_files, states["dest"])

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
if Path("src/pages/sub/layout.phml").is_file():
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
if True:
    input("Updated layout. Press enter to remove layout...")
    layout = file_system.find("sub/layout.phml")
    if layout is not None and isinstance(layout, Layout):
        remove_layout(layout)


#! Update component
if Path("src/components/Sample.phml").is_file():
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


#! Remove component
if True:
    input("Updated component. Press enter to remove component...")
    component = component_files.find("Sample.phml")
    if component is not None and isinstance(component, Component):
        remove_component(component, phml)


#! Update page
if Path("src/pages/page.phml").is_file():    
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


#! Remove page
if True:
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
    
    
#! Update static file
if Path("src/pages/sub/sub_style.css").is_file() and Path("public/global.css").is_file():
    input("Removed page. Press enter to update a static file...")
    old_statc_data = ""
    old_public_data = ""
    with open("src/pages/sub/sub_style.css", "r", encoding="utf-8") as static:
        old_statc_data = static.read()
    with open("public/global.css", "r", encoding="utf-8") as public:
        old_public_data = public.read()

    with open("src/pages/sub/sub_style.css", "w", encoding="utf-8") as static:
        static.write(
            """\
    * {
    box-sizing: border-box;
    }\
    """
        )
    with open("public/global.css", "w", encoding="utf-8") as static:
        static.write(
            """\
    * {
    box-sizing: border-box;
    }\
    """
        )

    static = file_system.find("src/pages/sub/sub_style.css")
    public = static_files.find("public/global.css")

    if static is not None and isinstance(static, Static):
        update_static(static)
        
    if public is not None and isinstance(public, Static):
        update_static(public)

    with open("src/pages/sub/sub_style.css", "w", encoding="utf-8") as statc:
        statc.write(old_statc_data)
    with open("public/global.css", "w", encoding="utf-8") as public:
        public.write(old_public_data)
        

#! Remove static file
if True:
    input("Updated static file. Press enter to remove a static file...")
    static = file_system.find("src/pages/sub/sub_style.css")
    public = static_files.find("public/global.css")
    if static is not None and isinstance(static, Static):
        remove_static(static)
    if public is not None and isinstance(public, Static):
        remove_static(public)
    input("Removed static file. Press enter to finish...")


# server = ServerThread(Server(port=8081))
# try:
#     server.start()
#     while True: pass
# except KeyboardInterrupt:
#     server.stop()
#     input(server.stopped())
