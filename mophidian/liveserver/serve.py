import contextlib
import sys
from livereload import Server
from subprocess import Popen, PIPE

# Mophidian code
from .observe import WatchFiles
from compiler.build import Build
from moph_logger import Log, LL, FColor
from ppm import PPM


def serve(
    open: bool, debug: bool, port: int = 3000, entry_file: str = "index.html", open_delay: int = 2
):
    """Automatically reload browser tab upon file modification."""

    # Start by moving all static files to the site directory
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    log_level = LL.INFO

    if debug:
        log_level = LL.DEBUG

    logger = Log(output=old_stdout, level=log_level)

    build = Build(logger=logger)
    build.full()

    logger.Debug("serve arguments")
    logger.Debug(
        f"open={open}, debug={debug}, port={port}, entry_file={entry_file}, open_delay={open_delay}"
    )
    with contextlib.redirect_stdout(None):
        with contextlib.redirect_stderr(None):
            logger.Info("Setting up server")
            server = Server()
            logger.Debug(f"build.config.build.refresh_delay: {build.config.build.refresh_delay}")
            server.watch("./site/**/*", delay=build.config.build.refresh_delay)

            logger.Debug(
                f"build.config.integration.package_manager: {build.config.integration.package_manager}"
            )
            package_manager = PPM(build.config.integration.package_manager)

            tailwind_thread = None
            logger.Debug(f"build.config.integration.tailwind: {build.config.integration.tailwind}")
            if build.config.integration.tailwind:
                logger.Info("Starting tailwindcss")
                cmd = package_manager.ppm.run_command("tailwind:watch")
                tailwind_thread = Popen(cmd, stdout=PIPE, stderr=PIPE)

            sass_thread = None
            logger.Debug(f"build.config.integration.sass: {build.config.integration.sass}")
            if build.config.integration.sass:
                logger.Info("Starting sass")
                cmd = package_manager.ppm.run_command("css:watch")
                sass_thread = Popen(cmd, stdout=PIPE, stderr=PIPE)

            # Use watchdog as to have an incremental build system
            logger.Info("Attaching to filesystem for updates")
            watch_files = WatchFiles(build=build, logger=logger)
            watch_files.start()

            # Start livereload server and auto open site in browser
            try:
                logger.Info(f"Starting server at http://localhost:{port}/")
                if open:
                    logger.Info("Opening server in browser")
                server.serve(
                    port=port,
                    host="localhost",
                    root="site/",  # TODO: Allow user to specify
                    open_url_delay=open_delay if open else None,
                    live_css=False,
                    default_filename=entry_file,
                )
                logger.Custom("Cleaning up threads", clr=FColor.MAGENTA, label="SHUTDOWN")
            finally:
                # If the server is shutdown also stop watchdog
                watch_files.stop()
                if tailwind_thread is not None:
                    tailwind_thread.kill()

                if sass_thread is not None:
                    sass_thread.kill()
