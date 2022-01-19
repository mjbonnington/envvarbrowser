#!/usr/bin/python

# edit_envvar.py
#
# Mike Bonnington <mjbonnington@gmail.com>
# (c) 2018-2022
#
# Environment Variables Editor
# A simple dialog for editing an environment variable (key and value).
# If the value is a list of paths, display in a more user-readable format.


import os

from Qt import QtCore, QtGui, QtWidgets
import ui_template as UI

# Import custom modules


# ----------------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------------

cfg = dict(
	app_id="ic_envvar",  # This should match the Rez package name
	app_name="Edit Environment Variable", 
	window_object="editEnvVarUI", 

	ui_file=os.path.join(os.path.dirname(__file__), 'forms', 'edit_envvar.ui'), 
	stylesheet=None, 
	# icon='edit.svg', 

	store_window_geometry=False, 
)

# ----------------------------------------------------------------------------
# Main dialog class
# ----------------------------------------------------------------------------

class Dialog(QtWidgets.QDialog, UI.TemplateUI):
	"""Edit Environment Variable dialog class."""

	def __init__(self, parent=None):
		super(Dialog, self).__init__(parent)
		self.parent = parent

		# UI template setup
		self.setupUI(**cfg)
		self.conformFormLayoutLabels(self.ui)

		# Set window icon, flags and other Qt attributes
		self.setWindowIcon(self.iconSet('edit.svg', tintNormal=False))
		self.setWindowFlags(QtCore.Qt.Dialog)
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

		self.ui.valueList_listWidget.itemSelectionChanged.connect(self.updateToolbarUI)
		self.ui.valueList_listWidget.itemChanged.connect(self.updateEntry)
		self.ui.add_toolButton.clicked.connect(self.addEntry)
		self.ui.remove_toolButton.clicked.connect(self.removeEntry)
		self.ui.moveUp_toolButton.clicked.connect(self.moveEntryUp)
		self.ui.moveDown_toolButton.clicked.connect(self.moveEntryDown)

		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.ok)
		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)

		# Set input validators
		alphanumeric_validator = QtGui.QRegExpValidator(QtCore.QRegExp(r'[a-zA-Z_][a-zA-Z0-9_]*'), self.ui.key_lineEdit)
		self.ui.key_lineEdit.setValidator(alphanumeric_validator)


	def display(self, key, value):
		"""Display the dialog."""

		if key:
			self.setWindowTitle("%s: %s" % (self.windowTitle(), key))
			self.ui.key_lineEdit.setReadOnly(True)
		else:
			self.setWindowTitle("Add New Environment Variable")

		self.ui.key_lineEdit.setText(key)
		self.ui.value_lineEdit.setText(value)

		# Set up list view if value contains multiple paths
		if os.pathsep in value:  # Multi-path mode
			self.updateValueList(value)
			self.ui.value_lineEdit.textEdited.connect(self.updateValueList)
			self.ui.valueList_frame.show()
			self.addContextMenu(self.ui.browseList_toolButton, "Browse directory...", self.browseDirList)
			self.addContextMenu(self.ui.browseList_toolButton, "Browse file...", self.browseFileList)
			self.ui.browse_toolButton.hide()
		else:  # Single value mode
			self.ui.valueList_frame.hide()
			self.addContextMenu(self.ui.browse_toolButton, "Browse directory...", self.browseDir)
			self.addContextMenu(self.ui.browse_toolButton, "Browse file...", self.browseFile)
			self.setFixedHeight(self.minimumSizeHint().height())

		self.updateUI()
		self.updateToolbarUI()

		return self.exec_()


	def updateToolbarUI(self):
		"""Update the toolbar UI based on the current selection."""

		# No items selected...
		if len(self.ui.valueList_listWidget.selectedItems()) == 0:
			self.ui.remove_toolButton.setEnabled(False)
			self.ui.moveUp_toolButton.setEnabled(False)
			self.ui.moveDown_toolButton.setEnabled(False)
			self.ui.browseList_toolButton.setEnabled(False)
		# More than one item selected...
		else:
			self.ui.remove_toolButton.setEnabled(True)
			self.ui.moveUp_toolButton.setEnabled(True)
			self.ui.moveDown_toolButton.setEnabled(True)
			self.ui.browseList_toolButton.setEnabled(True)


	def updateValueList(self, value):
		"""Update the value list view."""

		self.valueList = value.split(os.pathsep)

		self.ui.valueList_listWidget.clear()
		self.ui.valueList_listWidget.addItems(self.valueList)

		# Make items editable
		for index in range(self.ui.valueList_listWidget.count()):
			item = self.ui.valueList_listWidget.item(index)
			item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)


	def updateValueLine(self):
		"""Update the value line edit."""

		valueStr = os.pathsep.join(n for n in self.valueList)

		# self.ui.value_lineEdit.blockSignals(True)
		self.ui.value_lineEdit.setText(valueStr)
		# self.ui.value_lineEdit.blockSignals(False)


	def updateEntry(self, item):
		"""Update an entry after editing."""

		i = self.ui.valueList_listWidget.indexFromItem(item).row()
		self.valueList[i] = item.text()
		self.updateValueLine()


	def addEntry(self):
		"""Add an entry to the value list view.

		The entry will be added before the selected row. If nothing is
		selected, append the entry to the end.
		"""
		newItem = QtWidgets.QListWidgetItem()
		newItem.setFlags(newItem.flags() | QtCore.Qt.ItemIsEditable)

		selectionLs = self.ui.valueList_listWidget.selectedItems()
		if selectionLs:
			for item in selectionLs:
				i = self.ui.valueList_listWidget.indexFromItem(item).row()
				self.valueList.insert(i, "")
				self.ui.valueList_listWidget.insertItem(i, newItem)
		else:
			self.valueList.append("")
			self.ui.valueList_listWidget.addItem(newItem)

		self.updateValueLine()


	def removeEntry(self):
		"""Remove an entry from the value list view."""

		for item in self.ui.valueList_listWidget.selectedItems():
			i = self.ui.valueList_listWidget.indexFromItem(item).row()
			self.valueList.pop(i)
			self.ui.valueList_listWidget.takeItem(i)

		self.updateValueLine()


	def moveEntryUp(self):
		"""Move an entry up in the value list view."""

		self.moveEntry(-1)


	def moveEntryDown(self):
		"""Move an entry down in the value list view."""

		self.moveEntry(1)


	def moveEntry(self, amount):
		"""Move an entry up or down by amount in the value list view."""

		for item in self.ui.valueList_listWidget.selectedItems():
			i = self.ui.valueList_listWidget.indexFromItem(item).row()
			if 0 <= i+amount < len(self.valueList):
				valueToMove = self.valueList[i]
				self.valueList.pop(i)
				self.valueList.insert(i+amount, valueToMove)
			itemToMove = self.ui.valueList_listWidget.takeItem(i)
			self.ui.valueList_listWidget.insertItem(i+amount, itemToMove)
			self.ui.valueList_listWidget.setCurrentItem(itemToMove)

		self.updateValueLine()


	def updateUI(self):
		"""Disable the OK button if either of the text fields are empty or
		invalid.
		"""
		enable = True
		if self.ui.key_lineEdit.text() == "":
			enable = False
		if self.ui.value_lineEdit.text() == "":
			enable = False

		self.ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(enable)

		# Change key text to uppercase
		# self.ui.key_lineEdit.setText(self.ui.key_lineEdit.text().upper())


	def browseDir(self):
		"""Open a folder browser (single entry)."""

		startingDir = self.ui.value_lineEdit.text()
		dialogPath = self.browse(startingDir, folder=True)
		if dialogPath:
			self.ui.value_lineEdit.setText(dialogPath)


	def browseFile(self):
		"""Open a file browser (single entry)."""

		startingDir = os.path.dirname(self.ui.value_lineEdit.text())
		dialogPath = self.browse(startingDir, folder=False)
		if dialogPath:
			self.ui.value_lineEdit.setText(dialogPath)


	def browseDirList(self):
		"""Open a folder browser (multi-path entry)."""

		for item in self.ui.valueList_listWidget.selectedItems():
			startingDir = item.text()
			dialogPath = self.browse(startingDir, folder=True)
			if dialogPath:
				item.setText(dialogPath)


	def browseFileList(self):
		"""Open a file browser (multi-path entry)."""

		for item in self.ui.valueList_listWidget.selectedItems():
			startingDir = os.path.dirname(item.text())
			dialogPath = self.browse(startingDir, folder=False)
			if dialogPath:
				item.setText(dialogPath)


	def browse(self, startingDir, folder=True):
		"""Open a dialog from which to select a file or folder."""

		if os.path.isdir(startingDir):
			dialogHome = startingDir
		else:
			dialogHome = os.environ.get('IC_JOB', os.getcwd())

		# Append slash to path if it's a Windows drive letter, otherwise file
		# dialog won't open the correct location
		if dialogHome.endswith(':'):
			dialogHome += '/'

		if folder:
			return self.folderDialog(dialogHome)
		else:
			return self.fileDialog(dialogHome)


	def ok(self):
		"""Dialog accept function."""

		self.key = self.ui.key_lineEdit.text()
		self.value = self.ui.value_lineEdit.text()
		self.accept()


	def keyPressEvent(self, event):
		"""Event handler to detect when key is pressed."""

		# Prevent Enter / Esc keypresses triggering OK / Cancel buttons.
		if event.key() == QtCore.Qt.Key_Return \
		or event.key() == QtCore.Qt.Key_Enter:
			return


	def hideEvent(self, event):
		"""Event handler for when window is hidden."""

		self.storeWindow()  # Store window geometry
