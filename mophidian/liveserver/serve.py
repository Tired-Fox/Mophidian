import contextlib
import os
from subprocess import Popen, PIPE
import sys
from .observe import WatchFiles
from util import color, Color, Style, RESET
from compiler.build import Build
from ppm import PPM
from livereload import Server

_open_delay = 2
_port = 3000


def serve(open: bool):
    """Automatically reload browser tab upon file modification."""

    # Start by moving all static files to the site directory
    build = Build()
    build.full()

    old_stdout = sys.stdout
    old_stderr = sys.stderr
    with contextlib.redirect_stdout(None):
        with contextlib.redirect_stderr(None):
            old_stdout.write(
                color("Setting up server...\n\n", prefix=[Style.BOLD], suffix=[Style.NOBOLD])
            )

            server = Server()
            server.watch("./site/**/*", delay=build.config.build.delay)

            package_manager = PPM(build.config.integration.package_manager)

            tailwind_thread = None
            if build.config.integration.tailwind:
                old_stdout.write(
                    color(
                        "[",
                        color("INFO", prefix=[Color.CYAN]),
                        f"]",
                        prefix=[Style.BOLD],
                        suffix=[RESET],
                    )
                    + " Starting tailwindcss...\n"
                )
                old_stdout.flush()
                cmd = package_manager.ppm.run_command("tailwind:watch")
                tailwind_thread = Popen(cmd, stdout=PIPE, stderr=PIPE)

            # Use watchdog as to have an incremental build system
            old_stdout.write(
                color(
                    "[",
                    color("INFO", prefix=[Color.CYAN]),
                    f"]",
                    prefix=[Style.BOLD],
                    suffix=[RESET],
                )
                + " Attaching to filesystem for updates\n"
            )
            old_stdout.flush()

            watch_files = WatchFiles(build, old_stdout)
            watch_files.start()

            # Start livereload server and auto open site in browser
            try:
                old_stdout.write(
                    color(
                        "[",
                        color("INFO", prefix=[Color.CYAN]),
                        f"]",
                        prefix=[Style.BOLD],
                        suffix=[RESET],
                    )
                    + f" Starting server at http://[::]:{_port}/\n"
                )
                if open:
                    old_stdout.write(
                        color(
                            "[",
                            color("INFO", prefix=[Color.CYAN]),
                            f"]",
                            prefix=[Style.BOLD],
                            suffix=[RESET],
                        )
                        + " Opening server in browser\n"
                    )
                old_stdout.flush()
                server.serve(
                    port=_port,  # TODO Allow user to specify
                    host="localhost",
                    root="site/",  # TODO Allow user to specify
                    open_url_delay=_open_delay if open else None,
                    live_css=False,
                    default_filename="index.html",  # TODO: Allow user to specify
                )
                old_stdout.write(
                    color(
                        "[",
                        color("IMPORTANT", prefix=[Color.MAGENTA]),
                        "]",
                        prefix=[Style.BOLD],
                        suffix=[Style.NOBOLD],
                    )
                    + " Shutting Down...\n"
                )
            finally:
                # If the server is shutdown also stop watchdog
                watch_files.stop()
                if tailwind_thread is not None:
                    tailwind_thread.kill()
