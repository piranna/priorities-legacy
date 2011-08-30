'''
Created on 13/05/2011

@author: piranna
'''
from gtk import Expander, VBox, ScrolledWindow, HButtonBox, Button
from gtk import TreeView, TreeViewColumn, CellRendererText


class Requeriment(Expander):
    def __init__(self):
        '''
        Constructor
        '''
        cellRendererText = CellRendererText()

        treeViewColumn = TreeViewColumn()
        treeViewColumn.pack_start(cellRendererText)

        treeView = TreeView()
        treeView.append_column(treeViewColumn)

        scrolledWindow = ScrolledWindow()
        scrolledWindow.add(treeView)

        btnAdd_Alternative = Button()
        btnDel_Alternative = Button()

        hButtonBox = HButtonBox()
        hButtonBox.pack_start(btnAdd_Alternative)
        hButtonBox.pack_start(btnDel_Alternative)

        vBox = VBox()
        vBox.pack_start(scrolledWindow)
        vBox.pack_start(hButtonBox)

        self.add(vBox)


    def AddAlternative(self, name, quantity=1):