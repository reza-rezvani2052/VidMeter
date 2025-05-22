# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QGridLayout, QHBoxLayout, QHeaderView, QLineEdit,
    QMainWindow, QMenuBar, QProgressBar, QPushButton,
    QSizePolicy, QSlider, QSpacerItem, QStatusBar,
    QTableWidget, QTableWidgetItem, QToolButton, QVBoxLayout,
    QWidget)

from clickablevideowidget import ClickableVideoWidget
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(849, 553)
        icon = QIcon()
        icon.addFile(u":/app-icon.jpg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.actSaveProject = QAction(MainWindow)
        self.actSaveProject.setObjectName(u"actSaveProject")
        self.actSaveProject.setMenuRole(QAction.MenuRole.NoRole)
        self.actLoadProject = QAction(MainWindow)
        self.actLoadProject.setObjectName(u"actLoadProject")
        self.actLoadProject.setMenuRole(QAction.MenuRole.NoRole)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.btnSelectFiles = QPushButton(self.centralwidget)
        self.btnSelectFiles.setObjectName(u"btnSelectFiles")

        self.horizontalLayout.addWidget(self.btnSelectFiles)

        self.btnSelectPath = QPushButton(self.centralwidget)
        self.btnSelectPath.setObjectName(u"btnSelectPath")

        self.horizontalLayout.addWidget(self.btnSelectPath)

        self.btnProject = QToolButton(self.centralwidget)
        self.btnProject.setObjectName(u"btnProject")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnProject.sizePolicy().hasHeightForWidth())
        self.btnProject.setSizePolicy(sizePolicy)
        self.btnProject.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btnProject.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.horizontalLayout.addWidget(self.btnProject)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setObjectName(u"progressBar")
        self.progressBar.setMaximumSize(QSize(100, 16777215))
        self.progressBar.setMaximum(125)
        self.progressBar.setValue(0)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_3.addWidget(self.progressBar)

        self.btnPauseResume = QToolButton(self.centralwidget)
        self.btnPauseResume.setObjectName(u"btnPauseResume")
        sizePolicy.setHeightForWidth(self.btnPauseResume.sizePolicy().hasHeightForWidth())
        self.btnPauseResume.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.btnPauseResume)

        self.btnCancelProcess = QToolButton(self.centralwidget)
        self.btnCancelProcess.setObjectName(u"btnCancelProcess")
        sizePolicy.setHeightForWidth(self.btnCancelProcess.sizePolicy().hasHeightForWidth())
        self.btnCancelProcess.setSizePolicy(sizePolicy)

        self.horizontalLayout_3.addWidget(self.btnCancelProcess)


        self.horizontalLayout.addLayout(self.horizontalLayout_3)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)

        self.lineEditFolder = QLineEdit(self.centralwidget)
        self.lineEditFolder.setObjectName(u"lineEditFolder")
        self.lineEditFolder.setEnabled(False)
        self.lineEditFolder.setReadOnly(True)

        self.gridLayout.addWidget(self.lineEditFolder, 1, 0, 1, 2)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setSpacing(2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.ledSearchInTableFiles = QLineEdit(self.centralwidget)
        self.ledSearchInTableFiles.setObjectName(u"ledSearchInTableFiles")

        self.horizontalLayout_4.addWidget(self.ledSearchInTableFiles)

        self.btnClearSearch = QToolButton(self.centralwidget)
        self.btnClearSearch.setObjectName(u"btnClearSearch")

        self.horizontalLayout_4.addWidget(self.btnClearSearch)

        self.comboSearchColumn = QComboBox(self.centralwidget)
        self.comboSearchColumn.addItem("")
        self.comboSearchColumn.addItem("")
        self.comboSearchColumn.addItem("")
        self.comboSearchColumn.setObjectName(u"comboSearchColumn")

        self.horizontalLayout_4.addWidget(self.comboSearchColumn)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.tableFiles = QTableWidget(self.centralwidget)
        if (self.tableFiles.columnCount() < 2):
            self.tableFiles.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableFiles.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableFiles.setObjectName(u"tableFiles")
        self.tableFiles.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableFiles.setAlternatingRowColors(True)
        self.tableFiles.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableFiles.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableFiles.horizontalHeader().setStretchLastSection(True)
        self.tableFiles.verticalHeader().setStretchLastSection(False)

        self.verticalLayout_2.addWidget(self.tableFiles)


        self.gridLayout.addLayout(self.verticalLayout_2, 2, 0, 1, 1)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.video_widget = ClickableVideoWidget(self.centralwidget)
        self.video_widget.setObjectName(u"video_widget")
        self.video_widget.setMinimumSize(QSize(300, 200))

        self.verticalLayout.addWidget(self.video_widget)

        self.sliderSeek = QSlider(self.centralwidget)
        self.sliderSeek.setObjectName(u"sliderSeek")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.sliderSeek.sizePolicy().hasHeightForWidth())
        self.sliderSeek.setSizePolicy(sizePolicy1)
        self.sliderSeek.setOrientation(Qt.Orientation.Horizontal)

        self.verticalLayout.addWidget(self.sliderSeek)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.gridLayout.addLayout(self.verticalLayout, 2, 1, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.chkSubfolder = QCheckBox(self.centralwidget)
        self.chkSubfolder.setObjectName(u"chkSubfolder")
        self.chkSubfolder.setChecked(True)

        self.horizontalLayout_2.addWidget(self.chkSubfolder)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.btnChart = QPushButton(self.centralwidget)
        self.btnChart.setObjectName(u"btnChart")

        self.horizontalLayout_2.addWidget(self.btnChart)

        self.btnSaveToFile = QPushButton(self.centralwidget)
        self.btnSaveToFile.setObjectName(u"btnSaveToFile")
        icon1 = QIcon()
        icon1.addFile(u":/img/save.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btnSaveToFile.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.btnSaveToFile)


        self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 849, 25))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"VidMeter", None))
        self.actSaveProject.setText(QCoreApplication.translate("MainWindow", u"Save Project", None))
#if QT_CONFIG(shortcut)
        self.actSaveProject.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actLoadProject.setText(QCoreApplication.translate("MainWindow", u"Load Project", None))
#if QT_CONFIG(shortcut)
        self.actLoadProject.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.btnSelectFiles.setText(QCoreApplication.translate("MainWindow", u"Select File(s)", None))
        self.btnSelectPath.setText(QCoreApplication.translate("MainWindow", u"Select Path", None))
        self.btnProject.setText(QCoreApplication.translate("MainWindow", u"Project", None))
#if QT_CONFIG(tooltip)
        self.btnPauseResume.setToolTip(QCoreApplication.translate("MainWindow", u"Pause/Resume", None))
#endif // QT_CONFIG(tooltip)
        self.btnPauseResume.setText(QCoreApplication.translate("MainWindow", u"\u23f8", None))
#if QT_CONFIG(tooltip)
        self.btnCancelProcess.setToolTip(QCoreApplication.translate("MainWindow", u"Cancel", None))
#endif // QT_CONFIG(tooltip)
        self.btnCancelProcess.setText(QCoreApplication.translate("MainWindow", u"\u274c", None))
        self.ledSearchInTableFiles.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Search in name or duration", None))
#if QT_CONFIG(tooltip)
        self.btnClearSearch.setToolTip(QCoreApplication.translate("MainWindow", u"\u274c Clear Search", None))
#endif // QT_CONFIG(tooltip)
        self.btnClearSearch.setText(QCoreApplication.translate("MainWindow", u"\u274c", None))
        self.comboSearchColumn.setItemText(0, QCoreApplication.translate("MainWindow", u"All Columns", None))
        self.comboSearchColumn.setItemText(1, QCoreApplication.translate("MainWindow", u"File Name", None))
        self.comboSearchColumn.setItemText(2, QCoreApplication.translate("MainWindow", u"Duration", None))

        ___qtablewidgetitem = self.tableFiles.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("MainWindow", u"Filename", None));
        ___qtablewidgetitem1 = self.tableFiles.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("MainWindow", u"Duration", None));
#if QT_CONFIG(tooltip)
        self.chkSubfolder.setToolTip(QCoreApplication.translate("MainWindow", u"Include Subfolders", None))
#endif // QT_CONFIG(tooltip)
        self.chkSubfolder.setText(QCoreApplication.translate("MainWindow", u"Subfolders", None))
        self.btnChart.setText(QCoreApplication.translate("MainWindow", u"Chart", None))
        self.btnSaveToFile.setText(QCoreApplication.translate("MainWindow", u"Save", None))
    # retranslateUi

