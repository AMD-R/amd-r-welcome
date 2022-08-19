#!/usr/bin/env python3
from PyQt5.QtWidgets import (QSizePolicy, QGridLayout, QVBoxLayout,
                             QLineEdit, QWidget, QPushButton, QLabel)
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtCore import (QPoint, QSize, pyqtSlot, pyqtSignal,
                          QParallelAnimationGroup, QPropertyAnimation)


class SliderWidget2(QWidget):
    """Creates a slider widget used for animated page changing.
    Parameters
    ----------
    widget: QWidget
        The first widget to display
    parent: QWidget
        The parent widget in which the widget will display in
    allow_previous: bool = True
        Allow this page to go to the previous page
    previous: QWidget = None
        Sets the previous slider widget to switch to
    slide_duration: int = 1000
        The amount of time in ms to switch between widgets
    next_text: str = "Next"
        The text to display for the button to switch to the next page
    previous_text: str = "Previous"
        The text to display for the button to switch to the previous page
    """
    finished = pyqtSignal()

    def __init__(self, widget: QWidget, parent: QWidget,
                 allow_previous: bool = True, previous: QWidget = None,
                 slide_duration: int = 1000,
                 next_text: str = "Next", previous_text: str = "Previous"):
        super().__init__()
        if not isinstance(previous, (self.__class__, type(None))):
            raise TypeError("Invalid previous widget")
        self.setParent(parent)
        self.next_widget: type(self) = None
        self.previous_widget: type(self) = previous
        self.slide_duration: int = slide_duration
        self.offset = 0

        # Setting up widget
        self.main_widget: QWidget = widget
        self.widget: QWidget = QWidget(self)
        self.widget.resizeEvent = self.widgetResizeEvent
        self.parent().resizeEvent = self.parentResizeEvent

        # Next Button
        self.next_button: QPushButton = QPushButton(next_text, self)
        self.next_button.clicked.connect(self.next)
        self.next_button.setVisible(False)
        # https://stackoverflow.com/questions/26128828/whats-the-proper-way-to-resize-widgets-in-a-layout
        self.next_button.setSizePolicy(QSizePolicy.Expanding,
                                       QSizePolicy.Fixed)

        # Previous Button
        self.previous_button: QPushButton = QPushButton(previous_text, self)
        self.previous_button.clicked.connect(self.previous)
        # https://stackoverflow.com/questions/26128828/whats-the-proper-way-to-resize-widgets-in-a-layout
        self.previous_button.setSizePolicy(QSizePolicy.Expanding,
                                           QSizePolicy.Fixed)
        if allow_previous and self.previous_widget:
            self.previous_button.setVisible(True)
        else:
            self.previous_button.setVisible(False)

        layout: QGridLayout = QGridLayout()
        layout.addWidget(widget,
                         0, 0, 1, 2)
        layout.addWidget(self.previous_button,
                         1, 0)
        layout.addWidget(self.next_button,
                         1, 1)
        self.widget.setLayout(layout)

    def create_next(self, widget: QWidget, allow_previous: bool = True,
                    overide_next: bool = False, slide_duration: int = 1000,
                    next_text: str = "Next", previous_text: str = "Previous"
                    ) -> "SliderWidget2":
        """Creates the next page.
        The new widget will be appended to the last page automatically.
        If overide_next is set to True. It will overide the current next page.
        Parameters
        ----------
        widget: QWidget
            The next widget to add to the sliding widget
        allow_previous: bool = True
            Allow next page to go back to the previous page
        overide_next: bool = False
            Determine if it will append to the last page or not
        slide_duration: int = self.
            The amount of time in ms to switch between widgets
        next_text: str = "Next"
            The text to display for the button to switch to the next page
        previous_text: str = "Previous"
            The text to display for the button to switch to the previous page

        Returns
        -------
        next_widget: SliderWidget2
            The widget to the next page
        """
        while self.next_widget and not overide_next:
            self = self.next_widget
        self.next_widget = self.__class__(widget, self.parent(),
                                          allow_previous, self, slide_duration,
                                          next_text, previous_text)
        self.next_button.setVisible(True)
        self.next_widget.offset = self.parent().width()
        return self.next_widget

    @pyqtSlot()
    def next(self, ):
        """Moves to the next page."""
        # Setting up new positions
        offset = QPoint(self.parent().width(), 0)
        self_pos_new = self.property("pos") - offset
        next_pos_new = self.next_widget.property("pos") - offset

        # Setting new offset
        self.offset = -self.parent().width()
        self.next_widget.offset = 0

        # Setting Up Animations
        anim_group = QParallelAnimationGroup(self)
        # Current widget
        anim_self = QPropertyAnimation(self, b"pos")
        anim_self.setEndValue(self_pos_new)
        anim_self.setDuration(self.slide_duration)
        anim_group.addAnimation(anim_self)
        # Next Widget
        anim_next = QPropertyAnimation(self.next_widget, b"pos")
        anim_next.setEndValue(next_pos_new)
        anim_next.setDuration(self.slide_duration)
        anim_group.addAnimation(anim_next)

        # Starting animation
        anim_group.start()
        anim_group.finished.connect(self.animation_finished)

    @pyqtSlot()
    def previous(self, ):
        """Moves to the previous page."""
        # Setting up new positions
        offset = QPoint(self.parent().width(), 0)
        self_pos_new = self.property("pos") + offset
        previous_pos_new = self.previous_widget.property("pos") + offset

        # Setting new offset
        self.offset = self.parent().width()
        self.previous_widget.offset = 0

        # Setting Up Animations
        anim_group = QParallelAnimationGroup(self)
        # Current widget
        anim_self = QPropertyAnimation(self, b"pos")
        anim_self.setEndValue(self_pos_new)
        anim_self.setDuration(self.slide_duration)
        anim_group.addAnimation(anim_self)
        # Next Widget
        anim_previous = QPropertyAnimation(self.previous_widget, b"pos")
        anim_previous.setDuration(self.slide_duration)
        anim_previous.setEndValue(previous_pos_new)
        anim_group.addAnimation(anim_previous)

        # Starting animation
        anim_group.start()
        anim_group.finished.connect(self.animation_finished)

    def widgetResizeEvent(self, event: QResizeEvent):
        """Moves all the widgets to the center.
        Parameters
        ----------
        event: QResizeEvent
            The resize event
        """
        super().resizeEvent(event)

        # Getting the size of the widget
        size: QSize = self.widget.size()
        # Resizing the slider widget
        self.resize(size)
        # Getting Values
        width: int = size.width()
        height: int = size.height()
        parent: QWidget = self.parent()
        offset: int = 0
        # Setting offset
        offset = self.offset
        x = parent.width() / 2 - width / 2 + offset
        y = parent.height() / 2 - height / 2
        # Creating new pos and setting it
        point: QPoint = QPoint(int(x),
                               int(y))
        self.setProperty("pos", point)

    def parentResizeEvent(self, event: QResizeEvent):
        """Updates widget postion when parent resizes.
        Parameters
        ----------
        event: QResizeEvent
            The resize event
        """
        super().resizeEvent(event)
        ratio = event.size().width() / event.oldSize().width()
        if ratio < 0:
            ratio = 1

        self.offset *= ratio
        self.widgetResizeEvent(event)

        while self.previous_widget is not None:
            self = self.previous_widget
            self.offset *= ratio
            self.widgetResizeEvent(event)

    def disable_next(self) -> None:
        """Disables the next button."""
        self.next_button.setEnabled(False)

    def disable_previous(self) -> None:
        """Disables the previous button."""
        self.previous_button.setEnabled(False)

    def enable_next(self) -> None:
        """Enables the next button."""
        self.next_button.setEnabled(True)

    def enable_previous(self) -> None:
        """Enables the previous button."""
        self.previous_button.setEnabled(True)

    def toggle_next(self) -> bool:
        """Toggles the enable state of the next button.
        Returns
        -------
        state: bool
            The new state of the next button
        """
        if self.next_button.isEnabled():
            self.disable_next()
        else:
            self.enable_next()
        return self.next_button.isEnabled()

    def toggle_previous(self) -> bool:
        """Toggles the enable state of the previous button.
        Returns
        -------
        state: bool
            The new state of the previous button
        """
        if self.previous_button.isEnabled():
            self.disable_previous()
        else:
            self.enable_previous()
        return self.previous_button.isEnabled()

    @pyqtSlot()
    def animation_finished(self):
        self.finished.emit()


class QLineEditWithLabel(QWidget):
    """QLineEdit widget attached with a label.

    Parameters
    ----------
    text: str
        The label for the QLineEdit
    """
    textChanged = pyqtSignal(str)

    def __init__(self, text: str, edit_text: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = QLabel(text)
        self.input_text = QLineEdit(edit_text)

        self.input_text.textChanged.connect(lambda text:
                                            self.textChanged.emit(text))

        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.label)
        self.main_layout.addWidget(self.input_text)

        self.setLayout(self.main_layout)

    def text(self) -> str:
        """Returns the text of the QLineEdit."""
        return self.input_text.text()
