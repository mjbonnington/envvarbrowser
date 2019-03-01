#!/usr/bin/python

# edit_envvar.py
#
# Mike Bonnington <mjbonnington@gmail.com>
# (c) 2018-2019
#
# Environment Variables Browser
# A simple dialog for editing an environment variable (key and value).
# If the value is a list of paths, display in a more user-readable format.


import os
import sys

from Qt import QtCore, QtGui, QtWidgets
import ui_template as UI

# Import custom modules
#import osOps


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

# Set window title and object names
WINDOW_TITLE = "Edit Environment Variable"
WINDOW_OBJECT = "EditEnvVarUI"

# Set the UI and the stylesheet
UI_FILE = 'edit_envvar.ui'
STYLESHEET = 'style.qss'  # Set to None to use the parent app's stylesheet

# Other options
STORE_WINDOW_GEOMETRY = False


# ----------------------------------------------------------------------------
# Main dialog class
# ----------------------------------------------------------------------------

class Dialog(QtWidgets.QDialog, UI.TemplateUI):
	""" Edit Environment Variable dialog class.
	"""
	def __init__(self, parent=None):
		super(Dialog, self).__init__(parent)
		self.parent = parent

		self.setupUI(window_object=WINDOW_OBJECT, 
		             window_title=WINDOW_TITLE, 
		             ui_file=UI_FILE, 
		             stylesheet=STYLESHEET, 
		             store_window_geometry=STORE_WINDOW_GEOMETRY)  # re-write as **kwargs ?

		self.conformFormLayoutLabels(self.ui)

		# Set window flags
		self.setWindowFlags(QtCore.Qt.Dialog)

		# Set other Qt attributes
		self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

		# Set icons
		self.ui.browse_toolButton.setIcon(self.iconSet('folder-open.svg'))
		self.ui.add_toolButton.setIcon(self.iconSet('add.svg'))
		self.ui.remove_toolButton.setIcon(self.iconSet('remove.svg'))
		self.ui.moveUp_toolButton.setIcon(self.iconSet('move-up.svg'))
		self.ui.moveDown_toolButton.setIcon(self.iconSet('move-down.svg'))
		self.ui.browseList_toolButton.setIcon(self.iconSet('folder-open.svg'))

		# Connect signals & slots
		self.ui.key_lineEdit.textChanged.connect(self.updateUI)
		self.ui.value_lineEdit.textChanged.connect(self.updateUI)
		self.ui.browse_toolButton.clicked.connect(self.browseDir)

		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.ok)
		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)

		# Context menus
		self.addContextMenu(self.ui.browse_toolButton, "Browse directory...", self.browseDir) #, 'icon_folder')
		self.addContextMenu(self.ui.browse_toolButton, "Browse file...", self.browseFile) #, 'icon_file')
		# self.addContextMenu(self.ui.browseList_toolButton, "Browse directory...", self.browseDir) #, 'icon_folder')
		# self.addContextMenu(self.ui.browseList_toolButton, "Browse file...", self.browseFile) #, 'icon_file')

		# Set input validators
		alphanumeric_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r'[a-zA-Z_][a-zA-Z0-9_]*'), self.ui.key_lineEdit)
		self.ui.key_lineEdit.setValidator(alphanumeric_validator)


	def display(self, key, value):
		""" Display the dialog.
		"""
		if key:
			self.setWindowTitle("%s: %s" %(WINDOW_TITLE, key))
			self.ui.key_lineEdit.setReadOnly(True)
		else:
			self.setWindowTitle("Add New Environment Variable")

		self.ui.key_lineEdit.setText(key)
		self.ui.value_lineEdit.setText(value)

		# Set up list view if value contains multiple paths
		if os.pathsep in value:
			self.updateValueList(value)
			self.ui.value_lineEdit.textEdited.connect(self.updateValueList)
			self.ui.valueList_frame.show()
			self.ui.browse_toolButton.hide() # ideally move to toolbar
			self.ui.toolbar_frame.hide() # temporary until implemented fully
		else:
			self.ui.valueList_frame.hide()
			self.setFixedHeight(self.minimumSizeHint().height())

		self.updateUI()

		return self.exec_()


	def updateValueList(self, value):
		""" Update the value list view.
		"""
		valueList = value.split(os.pathsep)
		self.ui.valueList_listWidget.clear()
		self.ui.valueList_listWidget.addItems(valueList)
		# for index in range(self.ui.valueList_listWidget.count()):
		# 	item = self.ui.valueList_listWidget.item(index)
		# 	item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)


	def updateUI(self):
		""" Disables the OK button if either of the text fields are empty or
			invalid.
		"""
		enable = True
		if self.ui.key_lineEdit.text() == "":
			enable = False
		if self.ui.value_lineEdit.text() == "":
			enable = False

		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(enable)

		# Change key text to uppercase
		#self.ui.key_lineEdit.setText(self.ui.key_lineEdit.text().upper())


	def browseDir(self):
		""" Opens a dialog from which to select a folder.
		"""
		#startingDir = osOps.translatePath(self.ui.value_lineEdit.text())
		startingDir = self.ui.value_lineEdit.text()
		if os.path.isdir(startingDir):
			dialogHome = startingDir
		else:
			dialogHome = os.environ.get('JOB', os.getcwd())

		# Append slash to path if it's a Windows drive letter, otherwise file
		# dialog won't open the correct location
		if dialogHome.endswith(':'):
			dialogHome += '/'

		dialogPath = self.folderDialog(dialogHome)

		if dialogPath:
			self.ui.value_lineEdit.setText(dialogPath)


	def browseFile(self):
		""" Opens a dialog from which to select a file.
		"""
		#startingDir = os.path.dirname(osOps.translatePath(self.ui.value_lineEdit.text()))
		startingDir = os.path.dirname(self.ui.value_lineEdit.text())
		if os.path.isdir(startingDir):
			dialogHome = startingDir
		else:
			dialogHome = os.environ.get('JOB', os.getcwd())

		# Append slash to path if it's a Windows drive letter, otherwise file
		# dialog won't open the correct location
		if dialogHome.endswith(':'):
			dialogHome += '/'

		dialogPath = self.fileDialog(dialogHome)

		if dialogPath:
			self.ui.value_lineEdit.setText(dialogPath)


	def ok(self):
		""" Dialog accept function.
		"""
		self.key = self.ui.key_lineEdit.text()
		self.value = self.ui.value_lineEdit.text()
		self.accept()


	def keyPressEvent(self, event):
		""" Override function to prevent Enter / Esc keypresses triggering
			OK / Cancel buttons.
		"""
		if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
			return


	def hideEvent(self, event):
		""" Event handler for when window is hidden.
		"""
		self.storeWindow()  # Store window geometry
