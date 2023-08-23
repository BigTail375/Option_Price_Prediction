from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import os
import pandas as pd
import numpy as np
from tensorflow.keras.models import load_model

class VisualMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(VisualMainWindow, self).__init__(*args, **kwargs)
        self.createVariables()
        self.createWidgets()

    def createWidgets(self):
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        mainLayout = QHBoxLayout()

        readLayout = QVBoxLayout()
        predictLayout = QVBoxLayout()

        mainLayout.addLayout(readLayout)

        fileLayout = QHBoxLayout()
        pathEdit = self.pathEdit = QLineEdit("")
        pathEdit.setReadOnly(True)
        readButton = QPushButton("Upload csv")
        readButton.clicked.connect(self.readButtonClicked)
        fileLayout.addWidget(pathEdit)
        fileLayout.addWidget(readButton)

        historyLayout = QHBoxLayout()
        fileListGroup = QGroupBox("File List")
        fileListBox = self.fileListBox = QListWidget()
        fileListBox.currentRowChanged.connect(self.fileListRowChanged)
        fileListLayout = QVBoxLayout()
        fileListLayout.addWidget(fileListBox)
        fileListGroup.setLayout(fileListLayout)
        fileListGroup.setMaximumWidth(150)

        dataLayout = QVBoxLayout()

        stockTableBox = QGroupBox("stocks")
        stockTableLayout = QVBoxLayout()
        stockTable = self.stockTable = QTableWidget()
        stockTableLayout.addWidget(stockTable)
        stockTableBox.setLayout(stockTableLayout)

        optionTableBox = QGroupBox("options")
        optionTableLayout = QVBoxLayout()
        optionTable = self.optionTable = QTableWidget()
        optionTableLayout.addWidget(optionTable)
        optionTableBox.setLayout(optionTableLayout)

        dataLayout.addWidget(stockTableBox)
        dataLayout.addWidget(optionTableBox)

        historyLayout.addWidget(fileListGroup)
        historyLayout.addLayout(dataLayout)

        readLayout.addLayout(fileLayout)
        readLayout.addLayout(historyLayout)

        proLayout = QHBoxLayout()
        predictButton = QPushButton('Predict')
        predictButton.clicked.connect(self.predictButtonClicked)
        topNumBox = self.topNumBox = QSpinBox()
        topNumBox.valueChanged.connect(self.countChanged)
        topNumBox.setValue(10)
        topNumBox.setMinimum(10)
        topNumBox.setMaximum(50)

        proLayout.addWidget(predictButton)
        proLayout.addWidget(topNumBox)

        resultLayout = QHBoxLayout()

        predResultBox = QGroupBox('Predict Result')
        predResultLayout = QVBoxLayout()
        predResultTable = self.predResultTable = QTableWidget()
        predResultLayout.addWidget(predResultTable)
        viewPredLayout = QHBoxLayout()
        prevPredButton = self.prevPredButton = QPushButton('<')
        prevPredButton.clicked.connect(self.prevPredButtonClicked)
        showPredEdit = self.showPredEdit = QLineEdit('0')
        showPredEdit.setMaximumWidth(50)
        pageCountLabel = self.pageCountLabel = QLabel('/0')
        pageCountLabel.setMaximumWidth(50)
        showPredEdit.textChanged.connect(self.showPredEditChanged)
        nextPredButton = self.nextPredButton = QPushButton('>')
        nextPredButton.clicked.connect(self.nextPredButtonClicked)
        for _ in prevPredButton, showPredEdit, pageCountLabel, nextPredButton:
            viewPredLayout.addWidget(_)
        predResultLayout.addLayout(viewPredLayout)
        predResultBox.setLayout(predResultLayout)
        resultLayout.addWidget(predResultBox)

        filterLayout = QVBoxLayout()
        filterTopBox = QGroupBox('Top')
        filterTopLayout = QVBoxLayout()
        filterTopTable = self.filterTopTable = QTableWidget()
        filterTopLayout.addWidget(filterTopTable)
        filterTopBox.setLayout(filterTopLayout)

        filterBottomBox = QGroupBox('Bottom')
        filterBottomLayout = QVBoxLayout()
        filterBottomTable = self.filterBottomTable = QTableWidget()
        filterBottomLayout.addWidget(filterBottomTable)
        filterBottomBox.setLayout(filterBottomLayout)

        filterLayout.addWidget(filterTopBox)
        filterLayout.addWidget(filterBottomBox)
        resultLayout.addLayout(filterLayout)

        predictLayout.addLayout(proLayout)
        predictLayout.addLayout(resultLayout)

        mainLayout.addLayout(predictLayout)
        
        progressLayout = QHBoxLayout()
        progressText = self.progressText = QLabel('')
        progressText.setMinimumWidth(100)
        progressBar = self.progressBar = QProgressBar()
        progressBar.setMinimum(0)
        progressBar.setMaximum(1)
        progressBar.setValue(0)
        progressLayout.addWidget(progressText)
        progressLayout.addWidget(progressBar)

        centralLayout = QVBoxLayout()
        centralLayout.addLayout(mainLayout)
        centralLayout.addLayout(progressLayout)
        self.setLayout(centralLayout)

    def createVariables(self):
        self.folderPath = ''
        self.fileList = []
        self.pastData = []
        self.model = load_model('model.h5')
        self.predf = pd.DataFrame()
        self.sorted_predf_top = pd.DataFrame()
        self.sorted_predf_bottom = pd.DataFrame()
        self.count = 0
        self.curPredPos = 0
    def setFileList(self):
        self.fileListBox.clear()
        for item in self.fileList:
            self.fileListBox.addItem(item)
    
    def setTable(self, table, data, index):
        table.clear()
        table.setRowCount(index)
        table.setColumnCount(data.shape[1])
        table.setHorizontalHeaderLabels(data.columns)
        for i, row in data[0:index].iterrows():
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                table.setItem(i, j, item)
    def setHistoryTable(self, index):
        option_data = pd.read_csv(self.folderPath + "\\options\\" + self.fileList[index] + "options.csv")
        self.setTable(self.optionTable, option_data, 1000)
        
        stock_data = pd.read_csv(self.folderPath + "\\stocks\\" + self.fileList[index] + "stocks.csv")
        self.setTable(self.stockTable, stock_data, 1000)

    def readButtonClicked(self):
        self.progressText.setText('Loading csv files ...')
        folderPath = QFileDialog.getExistingDirectory(self, "Select Folder")
        options_path = folderPath + "/options"
        stocks_path = folderPath + "/stocks"
        if os.path.exists(options_path) and os.path.exists(stocks_path):
            if len(os.listdir(options_path)) == len(os.listdir(stocks_path)):
                self.folderPath = folderPath
                self.fileList = []
                for file in os.listdir(options_path):
                    self.fileList.append(file[0:10])
                self.setFileList()
                self.setHistoryTable(0)
                for file in os.listdir(options_path)[-10:]:
                    df = pd.read_csv(os.path.join(options_path, file))
                    self.pastData.append(df[:])
                    print(file)
                self.progressText.setText('Loading Completed!')
            else: 
                QMessageBox.warning(self, "Alert", "no matching with stock and option data")
                self.progressText.setText('')
                return
        else:
            QMessageBox.warning(self, "Alert", "There is no stock or option data")
            self.progressText.setText('')
            return
        self.pathEdit.setText(self.folderPath)

    def fileListRowChanged(self, current_row):
        self.setHistoryTable(current_row)

    def predictButtonClicked(self):
        allData = self.pastData[0]
        for i in range(1, 10):
            allData = pd.concat([allData, self.pastData[i]], ignore_index=True)
        grouped = allData.groupby('contract')
        contracts = []
        premium = []
        self.count = 0
        self.curPredPos = 0
        for key, group in grouped:
            if(len(group) == 10):
                self.count += 1
        print(self.count)
        self.progressBar.setRange(0, self.count - 1)
        self.progressText.setText("Data processing ...")
        cur = 0
        # self.count = 1000
        underlying = []
        for key, group in grouped:
            if(len(group) == 10):
                contracts.append(key)
                premium.append((group['bid'] + group['ask']) / 2)
                underlying.append(group['underlying'].iloc[0])
                cur += 1
                if cur % 1000 == 0:
                    self.progressBar.setValue(cur)
                    # break
        premium = np.array(premium)
        test = premium[:,1:] - premium[:,:-1]
        pred = np.array([[]])
        pred = np.transpose(pred)
        self.progressBar.setRange(0, 9)
        self.progressText.setText("Predicting ...")
        for i in range(10):
            pred = np.concatenate((pred, self.model.predict(test[int(self.count / 10 * i):int(self.count / 10 * (i + 1))]).round(4)))
            self.progressBar.setValue(i)
        print(pred.shape)

        self.predf = pd.DataFrame()
        self.predf['underlying'] = underlying
        self.predf['contract'] = contracts
        self.predf['premium'] = premium[:,-1]
        self.predf['predict_value'] = pred.flatten()
        self.predf['predict_percent'] = self.predf['predict_value'] / self.predf['premium'] * 100
        self.setTable(self.predResultTable, self.predf, 1000)

        show_count = int(self.topNumBox.value())
        
        self.sorted_predf_top = self.predf.sort_values(by='predict_value', ascending=False).reset_index(drop=True)
        self.setTable(self.filterTopTable, self.sorted_predf_top, show_count)
        self.sorted_predf_bottom = self.predf.sort_values(by='predict_value', ascending=True).reset_index(drop=True)
        self.setTable(self.filterBottomTable, self.sorted_predf_bottom, show_count)
        
        self.progressText.setText("Finished")
        self.showPredEdit.setText('0')
        self.pageCountLabel.setText(f'/{int(self.count / 1000)}')

    def countChanged(self):
        if len(self.predf) == 0:
            return
        show_count = int(self.topNumBox.value())
        self.sorted_predf_top = self.predf.sort_values(by='predict', ascending=False).reset_index(drop=True)
        self.setTable(self.filterTopTable, self.sorted_predf_top, show_count)
        self.sorted_predf_bottom = self.predf.sort_values(by='predict', ascending=True).reset_index(drop=True)
        self.setTable(self.filterBottomTable, self.sorted_predf_bottom, show_count)
    def prevPredButtonClicked(self):
        if self.count == 0:
            return
        if self.curPredPos <= 0:
            return
        t = int(self.showPredEdit.text()) - 1
        self.showPredEdit.setText(str(t))
        pass
    def nextPredButtonClicked(self):
        if self.count == 0:
            return
        if self.curPredPos >= int(self.count / 1000) - 1:
            return
        t = int(self.showPredEdit.text()) + 1
        self.showPredEdit.setText(str(t))
        pass
    def showPredEditChanged(self):
        if self.count == 0:
            return
        if self.showPredEdit.text() == '':
            return
        self.curPredPos = int(self.showPredEdit.text())
        self.setTable(self.predResultTable, self.predf[self.curPredPos * 1000: (self.curPredPos + 1) * 1000].reset_index(drop=True), 1000)
        pass
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = VisualMainWindow()
    w.show()
    app.exec_()
