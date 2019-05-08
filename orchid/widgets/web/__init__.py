from enum import Enum
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QUrl
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox, QStyle, QAction
from PyQt5.QtGui import QIcon, QContextMenuEvent
from PyQt5.QtWebEngineCore import QWebEngineRegisterProtocolHandlerRequest
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView, QWebEnginePage, QWebEngineCertificateError, QWebEngineClientCertificateSelection
from PyQt5.QtNetwork import QAuthenticator
from orchid.widgets.windows import DesktopWindow, PopupWindow


class WebPage(QWebEnginePage):
    """
    A :class:`QWebEnginePage` that positions common web page notifications correctly for :module:`orchid`.
    """

    class WebAction(Enum):
        Forward = QWebEnginePage.Forward
        Back = QWebEnginePage.Back
        Reload = QWebEnginePage.Reload
        Stop = QWebEnginePage.Stop

    class RenderProcessTerminationStatus(Enum):
        NormalTerminationStatus = QWebEnginePage.NormalTerminationStatus
        AbnormalTerminationStatus = QWebEnginePage.AbnormalTerminationStatus
        CrashedTerminationStatus = QWebEnginePage.CrashedTerminationStatus
        KilledTerminationStatus = QWebEnginePage.KilledTerminationStatus

    class WebWindowType(Enum):
        WebBrowserWindow = QWebEnginePage.WebBrowserWindow
        WebBrowserTab = QWebEnginePage.WebBrowserTab
        WebDialog = QWebEnginePage.WebDialog
        WebBrowserBackgroundTab = QWebEnginePage.WebBrowserBackgroundTab

    def __init__(self, profile: QWebEngineProfile, parent: QObject = None) -> None:
        """
        Creates a :class:`WebPage` with the given web profile and makes connections to handle common signals.

        :param profile: The :class:`QWebEngineProfile` that manages the way this page reacts.
        :type profile: QWebEngineProfile
        :param parent: An optional :class:`QObject` parent for this page.
        :type parent: QObject
        """
        super().__init__(profile, parent)
        self.authenticationRequired.connect(self._on_authentication_required)
        self.featurePermissionRequested.connect(self._on_feature_permission_requested)
        self.proxyAuthenticationRequired.connect(self._on_proxy_authentication_required)
        self.registerProtocolHandlerRequested.connect(self._on_register_protocol_handler_requested)
        self.selectClientCertificate.connect(self._on_select_client_certificate)

    def certificateError(self, error: QWebEngineCertificateError) -> bool:
        """
        Displays a certificate error for the user.

        :return: True if the error was able to be overridden, false otherwise.
        :rtype: bool
        """
        if error.isOverridable():
            dialog = QDialog(self)
            dialog.setModal(True)
            dialog.setWindowFlags(dialog.windowFlags() & Qt.WindowContextHelpButtonHint)
            dialog.setWindowTitle(self.tr("Certificate Error"))
            return dialog.exec() == QDialog.Accepted

        QMessageBox.critical(self, self.tr("Certificate Error"), error.errorDescription())
        return False

    def _on_authentication_required(self, request: QUrl, auth: QAuthenticator) -> None:
        """
        Displays a log in box for the user to attempt to log into the site.

        :param request: The QUrl of the site that requested the log in.
        :type request: QUrl
        :param auth: The :class:`QAuthenticator` that will hold login details for the user.
        :type auth: QAuthenticator
        """
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setWindowFlags(dialog.windowFlags() & Qt.WindowContextHelpButtonHint)

        # TODO: Get username and password here.
        # Get the username and password to authenticate.
        # if dialog.exec() == QDialog.Accepted:
        #     auth.setUser()
        #     auth.setPassword()
        # else:
        auth = None

    def _on_feature_permission_requested(self, request: QUrl, feature, Feature) -> None:
        """
        Displays a notification for the user to accept or deny a feature request from a website.

        :param request: The :class:`QUrl` that made the request for the feature.
        :type request: QUrl
        :param feature: The feature that was requested.
        :type feature: Feature
        """
        # Map features to questions to ask the user.
        features = {
            QWebEnginePage.Geolocation: self.tr("Allow {} to access your location information?".format(request.host())),
            QWebEnginePage.MediaAudioCapture: self.tr("Allow {} to access your microphone?".format(request.host())),
            QWebEnginePage.MediaVideoCapture: self.tr("Allow {} to access your webcam?".format(request.host())),
            QWebEnginePage.MediaAudioVideoCapture: self.tr("Allow {} to access your microphone and webcam?".format(request.host())),
            QWebEnginePage.MouseLock: self.tr("Allow {} to lock your mouse cursor?".format(request.host())),
            QWebEnginePage.DesktopVideoCapture: self.tr("Allow {} to capture video of your desktop?".format(request.host())),
            QWebEnginePage.DesktopAudioVideoCapture: self.tr("Allow {} to capture audio and video of your desktop?".format(request.host()))
        }

        # Ask the user if permission should be granted.
        question = features.get(feature, "")
        if not question.isEmpty() and QMessageBox.question(self, self.tr("Permission Request"), question) == QMessageBox.Yes:
            self.setFeaturePermission(request, feature, self.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(request, feature, self.PermissionDeniedByUser)

    def _on_proxy_authentication_required(self, request: QUrl, auth: QAuthenticator, proxy_host: str) -> None:
        """
        Displays a notification for the user to log in to the proxy.

        :param request: The :class:`QUrl` that made the request for the proxy log in.
        :type request: QUrl
        :param auth: The :class:`QAuthenticator` that takes the username and password.
        :type auth: QAuthenticator
        :param proxy_host: The name of the host that made the request for the proxy log in.
        :type proxy_host: str
        """
        dialog = QDialog(self)
        dialog.setModal(True)
        dialog.setWindowFlags(dialog.windowFlags() & Qt.WindowContextHelpButtonHint)

        # TODO: Get username and password here.
        # Get the username and password for the proxy.
        # if dialog.exec() == QDialog.Accepted:
        #     auth.setUser()
        #     auth.setPassword()
        # else:
        auth = None

    def _on_register_protocol_handler_requested(self, request: QWebEngineRegisterProtocolHandlerRequest) -> None:
        """
        Displays a notification for the user to confirm opening specific types of links with a specific handler.

        :param request: The :class:`QWebEngineRegisterProtocolHandlerRequest` that is asking if the handler should be
        allowed to open specific types of links. The type of handler and the type of link are contained in this object.
        :type request: QWebEngineRegisterProtocolHandlerRequest
        """
        answer = QMessageBox.question(self, self.tr("Permission Request"),
                                      self.tr("Allow {} to open all {} links?".format(request.origin().host(),
                                                                                      request.scheme())))
        if answer == QMessageBox.Yes:
            request.accept()
        else:
            request.reject()

    def _on_select_client_certificate(self, selection: QWebEngineClientCertificateSelection) -> None:
        """
        Selects the first client certificates in the given selection.

        :param selection: The :class:`QWebEngineClientCertificateSelection`
        :type selection: QWebEngineClientCertificateSelection
        """
        selection.select(selection.certificates().at(0))  # Select the first certificate.


class WebView(QWebEngineView):
    """
    A :class:`QWebEngineView` that displays a :class:`WebPage` on the screen.
    """

    # Class signals.
    signal_webaction_state_changed = pyqtSignal(WebPage.WebAction, bool)
    signal_favicon_changed = pyqtSignal(QIcon)
    signal_dev_tools_requested = pyqtSignal(WebPage)

    def __init__(self, parent: QWidget = None) -> None:
        """
        Creates the :class:`WebView` with a 100 percent load status. Also, connects signals for custom behaviors.

        :param parent: An optional :class:`QWidget` parent for this view.
        :type parent: QWidget
        """
        super().__init__(parent)
        self._load_progress = 100
        self.loadStarted.connect(self._on_load_started)
        self.loadProgress.connect(self._on_load_progress_changed)
        self.loadFinished.connect(self._on_load_finished)
        self.iconChanged.connect(self._on_favicon_changed)
        self.renderProcessTerminated.connect(self._on_render_process_terminated)

    def _on_load_started(self) -> None:
        """
        Resets load progress to zero and notifies listeners of a favicon change.
        """
        self._load_progress = 0
        self.signal_favicon_changed.emit(self.get_icon())

    def _on_load_progress_changed(self, progress: int) -> None:
        """
        Updates the load progress with the given progress.

        :param progress: The percent from 0 to 100 of the :class:`WebPage` in this :class:`WebView` that is loaded.
        :type progress: int
        """
        self._load_progress = progress

    def _on_load_finished(self, success: bool) -> None:
        """
        Updates the load progress to 100 if the load was a success or -1 if it was a failure.

        :param success: The load state of the :class:`WebPage`. If this is True then the load percent is 100.
        :type success: bool
        """
        self._load_progress = 100 if success else -1
        # TODO: Do I need this?
        # self.signal_favicon_changed.emit(self.get_icon())

    def _on_favicon_changed(self, icon: QIcon) -> None:
        """
        Notifies listeners of a favicon change.

        :param icon: The new favicon for the :class:`WebView`.
        :type icon: QIcon
        """
        self.signal_favicon_changed.emit(self.get_icon())

    def _on_render_process_terminated(self, status: WebPage.RenderProcessTerminationStatus, status_code: int) -> None:
        """
        Shows the user a notification that the page failed to load and checks if they want to try to reload it.

        :param status: The :class:`RenderProcessTerminationStatus` that explains why the page did not load.
        :type status: RenderProcessTerminationStatus
        :param status_code: The exit code produced by the termination.
        :type status_code: int
        """
        if status == WebPage.RenderProcessTerminationStatus.NormalTerminationStatus:
            msg = self.tr("Render process normal exit.")
        elif status == WebPage.RenderProcessTerminationStatus.AbnormalTerminationStatus:
            msg = self.tr("Render process abnormal exit.")
        elif status == WebPage.RenderProcessTerminationStatus.CrashedTerminationStatus:
            msg = self.tr("Render process crashed.")
        elif status == WebPage.RenderProcessTerminationStatus.KilledTerminationStatus:
            msg = self.tr("Render process killed.")

        # Notifiy the user the page failed to load and see if they want to reload it.
        reply = QMessageBox.Question(self.window(), msg, self.tr("Render process exited with code: {}\nDo you want to reload the page?".format(status_code)))
        if reply == QMessageBox.Yes:
            # TODO: Should this be done in a new thread?
            self.reload()

    def _on_webaction_changed(self, webaction: WebPage.WebAction, state: bool) -> None:
        """
        Notifies listeners that a page's :class:`WebAction` has been enabled or disabled.

        :param webaction: The :class:`WebAction` that was enabled to disabled.
        :type webaction: WebAction
        :param state: True if the action was enabled, false if it was disabled.
        :type state: bool
        """
        self.signal_webaction_state_changed.emit(webaction, state)

    def _on_dev_tools_requested(self) -> None:
        """
        Notifies listeners of a dev tools request at the current page.
        """
        self.signal_dev_tools_requested.emit(self.page())

    def set_page(self, page: WebPage) -> None:
        """
        Sets up signals for :class:`WebAction` changes and then sets this :class:`WebView`'s :class:`WebPage` to the given page.

        :param page: The class:`WebPage` that this view should display.
        :type page: WebPage
        """
        # Forward webaction.
        webaction = WebPage.WebAction.Forward
        action = page.action(webaction)
        action.changed.connect(self._on_webaction_changed(webaction, action.isEnabled()))

        # Back webaction.
        webaction = WebPage.WebAction.Back
        action = page.action(webaction)
        action.changed.connect(self._on_webaction_changed(webaction, action.isEnabled()))

        # Reload webaction.
        webaction = WebPage.WebAction.Reload
        action = page.action(webaction)
        action.changed.connect(self._on_webaction_changed(webaction, action.isEnabled()))

        # Stop webaction.
        webaction = WebPage.WebAction.Stop
        action = page.action(webaction)
        action.changed.connect(self._on_webaction_changed(webaction, action.isEnabled()))

        super().setPage(page)

    def get_load_progress(self) -> int:
        """
        Returns the current load progress of the :class:`WebPage` in this :class:`WebView` as a percent from 0 to 100.

        :return: The percent this view is loaded. Errors are indicated with a negative load progress.
        :rtype: int
        """
        return self._load_progress

    def is_webaction_enabled(self, webaction: WebPage.WebAction) -> bool:
        """
        Returns the enabled state of the given WebAction.

        :param webaction: The WebAction whose enabled state is returned.
        :type webaction: WebAction
        :return: True if the given WebAction is enabled, false otherwise.
        :rtype: bool
        """
        return self.page().action(webaction).isEnabled()

    def get_favicon(self) -> QIcon:
        """
        Returns the current's :class:`WebPage`'s favicon if it has one, a loading icon if the page is still loading, an
        error icon if it failed loading, or a default icon if the page has no favicon.

        :return: The page's icon.
        :rtype: QIcon
        """
        icon = self.icon()

        # Return the page's favicon if it exists.
        if icon is not None:
            return icon

        # If it does not exist, return another icon.
        if self._load_progress < 0:
            # There was a load error, return an error icon.
            return self.style().standardIcon(QStyle.SP_BrowserStop)
        elif self._load_progress < 100:
            # There is a page loading now, return a loading icon.
            return self.style().standardIcon(QStyle.SP_BrowserReload)
        else:
            # The page is loaded but it has no favicon, use a default one.
            # TODO: Make a default favicon.
            return self.style().standardIcon(QStyle.SP_MessageBoxInformation)

    def createWindow(self, window_type: WebPage.WebWindowType) -> QWebEngineView:
        """
        Returns a new :class:`QWebEngineView` to display a newly requested page in. This commonly happens when a link
        with target="_blank" is clicked. If an unknown type of window is requested, None is returned.

        :param window_type: The type of the new window to create for the new page.
        :type window_type: WebWindowType
        :return: A :class:`QWebEngineView` that will hold the page being opened.
        :rtype: QWebEngineView
        """
        tab_widget = DesktopWindow().get_central_widget()

        if window_type == WebPage.WebWindowType.WebBrowserTab:
            # Add a new tab to the main tab widget for the new page.
            return tab_widget.add_tab()
        elif window_type == WebPage.WebWindowType.WebBrowserBackgroundTab:
            # Add a new background tab to the main tab widget for the new page.
            return tab_widget.add_background_tab()
        elif window_type == WebPage.WebWindowType.WebBrowserWindow:
            # Use this view's tab for the new page.
            return tab_widget.current_tab()
        elif window_type == WebPage.WebWindowType.WebDialog:
            # Show a popup window for the new page.
            popup_window = PopupWindow(self.page().profile())
            popup_window.signal_dev_tools_requested.connect(self._on_dev_tools_requested())
            return popup_window.view()
        else:
            # An unknown type of page was requested.
            return None

    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        """
        Renames or creates the "Inspect Element" menu item and then shows the context menu.

        :param event: The :class:`QContextMenuEvent` that triggered this menu popping up.
        :type event: QContextMenuEvent
        """
        menu = self.page().createStandardContextMenu()
        actions = menu.actions()
        webaction = self.page().action(WebPage.InspectElement)

        # Add "Inspect Element" option if it's not in the list.
        if webaction not in actions:
            # Add a seperator if "View Source" isn't there either.
            if self.page().action(WebPage.ViewSource) not in actions:
                menu.addSeperator()

            # Create an inspect action and add it to the menu.
            action = QAction(menu)
            action.setText(self.tr("Open inspector in new window"))
            action.triggered.connect(self._on_dev_tools_requested)
            menu.insertAction(action)
        else:
            actions[actions.index(webaction)].setText(self.tr("Inspect element"))

        # Show the menu.
        menu.popup(event.globalPos())
