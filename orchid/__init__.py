from sys import argv, exit
from platform import system as system_name
from logging import getLogger, basicConfig, DEBUG
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject
from orchid.widgets.windows import DesktopWindow
from orchid.utils.theme import Themer
if system_name() == "Windows":
    from orchid.wm import Win32WindowsManager as WindowsManager
elif system_name() == "Linux":
    from orchid.wm import XWindowsManager as WindowsManager
else:
    logger = getLogger(__name__)
    logger.critical("Failure to manage unknown OS.")
    exit(1)


class DesktopEnvironment(QObject):
    """
    The Orchid desktop environment.
    """

    def __init__(self) -> None:
        """
        Creates the :class:`WindowManager`, :class:`ActionArea`, and :class:`SideBar`. This also themes the whole
        app based on the theme file and configures the loggers.
        """
        super().__init__()

        # Create the Qt app.
        self._app = QApplication(argv)
        self._app.setApplicationName("Orchid")
        self._app.setApplicationVersion("2019.5.14")
        # TODO: self._app.setWindowIcon()

        # Configure loggers.
        basicConfig(level=DEBUG)
        self.logger = getLogger(__name__)

        # Theme the application.
        #Themer().apply_theme()

        # Create the desktop window.
        self._desktop = DesktopWindow()
        self._desktop.show()

        # Create the window manager.
        #self._wm_thread = QThread()
        #self._wm = WindowsManager()
        #self._wm.moveToThread(self._wm_thread)
        #self._wm_thread.started.connect(self._wm.run)
        #self._wm.start()
        #self._wm_thread.start()

    def run(self) -> int:
        """
        Startup the environment.
        :return: The exit code of the app.
        :rtype: int
        """
        result = self._app.exec()
        #self._wm.stop()
        #self._wm_thread.quit()
        #self._wm_thread.wait()
        return result
