#!/usr/bin/env python
import contextlib
import click

from mophidian.core.builder import Builder
from mophidian.moph_log import Logger

open_help = "If specified, then the live server will automatically open in the browser."
tailwind_help = "Enable tailwind compiling"
template_help = "Specify the type of template you would like to start with. Default 'blank'"


@click.group()
def cli():
    '''Group of all commands for this package.'''


@cli.command(name="new")
@click.option("--sass", flag_value=True, help=open_help, default=False)
@click.option("--tailwind", flag_value=True, help=tailwind_help, default=False)
@click.option("--no_defaults", flag_value=True, help=tailwind_help, default=False)
@click.option("--template", type=str, show_default=True, help=template_help, default="blank")
def new_command(sass: bool, tailwind: bool, no_defaults: bool, template: str):
    """Create a new mophidian project.

    Args:
        sass (bool): Whether to use sass integration.
        tailwind (bool): Whether to use tailwindcss integration
        no_defaults (bool): Don't use default values. Includes markdown extensions.
        template (str): Which template to use. Defaults to "blank".
    """
    from mophidian.core.new import generate

    generate(sass=sass, tailwind=tailwind, no_defaults=no_defaults, template=template)


@cli.command(name="serve")
@click.option("-o", "--open", flag_value=True, help=open_help, default=False)
def serve_command(open: bool):
    """Start a live reload server that auto builds and reloads on file changes.

    Args:
        open (bool): Whether to open in the default browser automatically.
    """
    import livereload

    # Init server and builder
    server = livereload.Server()
    builder = Builder(logger=Logger)

    # Change source dir to be source + website root for proper links
    builder.cfg.site.dest = ".dist/"
    old_dest = builder.cfg.site.dest
    builder.cfg.site.dest = builder.cfg.site.dest + builder.cfg.site.root

    # Full build before deploy
    builder.full()

    def rebuild(dirty: bool = False):
        builder.rebuild(dirty)

    # Watch pages, content, and static
    server.watch(
        filepath=builder.cfg.site.source,
        func=lambda: rebuild(True),
        delay="forever",
    )
    server.watch(
        filepath=builder.cfg.site.content,
        func=lambda: rebuild(True),
        delay="forever",
    )

    server.watch(
        filepath="components/",
        func=rebuild,
        delay="forever",
    )

    server.watch(
        filepath="layouts/",
        func=rebuild,
        delay="forever",
    )

    server.watch(
        filepath="static/",
        func=lambda: builder.copy_all_static_dir(dirty=True),
        delay="forever",
    )

    server.watch(filepath=builder.cfg.site.dest)

    # TODO start sass and tailwind watch commands
    Logger.Message("\n\n")

    Logger.Custom(f"Serving to http://localhost:3000/", label="Serve", clr="yellow")
    try:
        with contextlib.redirect_stdout(None):
            with contextlib.redirect_stderr(None):
                server.serve(
                    port=3000,
                    root=f"{old_dest}",
                    open_url_delay=0.3 if open else None,
                    live_css=True,
                    restart_delay=2,
                )
    finally:
        Logger.Custom("Shutting down...", label="Shutdown")
        builder.del_dest(old_dest)


# @click.option("-o", "--open", flag_value=True, help=open_help, default=False)s
# @click.option("-d", "--debug", flag_value=True, help=debug_help, default=False)
@cli.command(name="build")
def build_command():
    """Build the website in the specified dest directory."""
    Builder().full()


if __name__ == "__main__":
    cli()
