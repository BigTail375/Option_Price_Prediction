from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import sys
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout, Flatten
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import MinMaxScaler

class TrainingMainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super(TrainingMainWindow, self).__init__(*args, **kwargs)
        self.createVariables()
        self.createWidgets()

    def createWidgets(self):
        self.setMinimumWidth(1000)
        self.setMinimumHeight(600)
        mainLayout = QHBoxLayout()

        readLayout = QVBoxLayout()
        trainingLayout = QVBoxLayout()

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
        
        mainLayout.addLayout(trainingLayout)

        trainInformationLayout = QVBoxLayout()
        trainGraphLayout = QVBoxLayout()
        trainingLayout.addLayout(trainInformationLayout)
        trainingLayout.addLayout(trainGraphLayout)

        trainLayout1 = QHBoxLayout()
        trainLayout2 = QHBoxLayout()
        trainLayout3 = QHBoxLayout()
        trainLayout4 = QHBoxLayout()
        for _ in trainLayout1, trainLayout2, trainLayout3, trainLayout4:
            trainInformationLayout.addLayout(_)
        
        trainLayout1.addWidget(QLabel('Interval:'))
        intervalCombo = self.intervalCombo = QComboBox()
        intervalCombo.addItems(self.intervalName)
        trainLayout1.addWidget(intervalCombo)
        trainLayout1.addWidget(QLabel('Model Type:'))
        modelTypeCombo = self.modelTypeCombo = QComboBox()
        modelTypeCombo.addItems(self.modelType)
        trainLayout1.addWidget(modelTypeCombo)
        
        trainLayout3.addWidget(QLabel('Sample count:'))
        sampleCountEdit = self.sampleCountEdit = QLineEdit()
        trainLayout3.addWidget(sampleCountEdit)
        # trainLayout3.addWidget(QLabel('Data count:'))
        # dataCountEdit = self.dataCountEdit = QLineEdit()
        # trainLayout3.addWidget(dataCountEdit)

        dataProcessingButton = self.dataProcessingButton = QPushButton('Data Processing')
        dataProcessingButton.clicked.connect(self.dataProcessingButtonClicked)
        trainLayout4.addWidget(dataProcessingButton)
        dataTrainingButton = self.dataTrainingButton = QPushButton('Data Training')
        dataTrainingButton.clicked.connect(self.dataTrainingButtonClicked)
        trainLayout4.addWidget(dataTrainingButton)

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
        self.intervalName = ['1D', '2D', '1W', '1M', '1Y', '3Y']
        self.intervalValue = [1, 2, 5, 20, 240, 720]
        self.modelType = ['RNN', 'LSTM', 'RNN + LSTM', 'CNN + RNN + LSTM', 'Transformer']
        self.inputFeatures = ['strike', 'ask', 'bid', 'stock price']
        self.selectedInputFeatures = []
        self.outputFeatures = ['premium', 'ask + bid']

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
                # for file in os.listdir(options_path)[-10:]:
                #     df = pd.read_csv(os.path.join(options_path, file))
                #     self.pastData.append(df[:])
                #     print(file)
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

    def dataProcessingButtonClicked(self):
        if len(self.fileList) == 0:
            QMessageBox.warning(self, "Alert", "No Available data!!!")
            return
        if self.sampleCountEdit.text() == '':
            QMessageBox.warning(self, "Alert", "Enter Sample Count!!!")
            return
        interval = self.intervalValue[self.intervalCombo.currentIndex()]
        sampleCount = int(self.sampleCountEdit.text())
        sampleCount += 1
        if len(self.fileList) < interval * sampleCount + 1:
            QMessageBox.warning(self, "Alert", "Not Enough Data!!!")
            return
        
        self.dataProcessing()

    def dataProcessing(self):
        interval = self.intervalValue[self.intervalCombo.currentIndex()]
        sampleCount = int(self.sampleCountEdit.text())
        sampleCount += 1

        selectedFiles = self.fileList[-1 - interval * sampleCount::interval]
        
        print(len(selectedFiles), selectedFiles[0])
        data = []
        self.progressText.setText("loading initial data ...")
        self.progressBar.setRange(0, len(selectedFiles))
        for index, file in enumerate(selectedFiles):
            file_path = self.folderPath + '/options/' + file + 'options.csv'
            df = pd.read_csv(file_path)
            selected_data = df[['contract', 'ask', 'bid']]
            data.append(selected_data)
            # if index == 0:  data = selected_data
            # else:   data = pd.concat([data, selected_data], axis = 0)
            self.progressBar.setValue(index + 1)
        data = pd.concat(data, axis = 0)
        dataCount = 100000
        curPos = 0
        self.progressText.setText("data preprocssing ...")
        self.progressBar.setRange(0, dataCount - 1)
        contract_group = data.groupby('contract')
        total_data = []
        for index, group in contract_group:
            group = group.reset_index(drop=True)
            if len(group) == len(selectedFiles):
                df = pd.DataFrame({'average': (group['ask'] + group['bid']) / 2})
                dt = pd.DataFrame({'difference': df['average'].diff().dropna()})
                total_data.append(dt)
                curPos += 1
            if curPos % 100 == 0:
                print(curPos)
            if curPos >= dataCount: break
            self.progressBar.setValue(curPos)
        total_data = pd.concat(total_data, axis = 1)
        total_data = total_data.values.transpose()
        print(total_data[:,:-1].shape, total_data[:,-1].shape)
        np.save('visualization/input.npy', total_data[:,:-1])
        np.save('visualization/output.npy', total_data[:,-1])
        self.progressText.setText('data processing finished!')
    def divide_data(self, data, train_rate, val_rate, test_rate):
        train = data[0 : int(len(data) * train_rate)]
        val = data[int(len(data) * train_rate) : int(len(data) * (train_rate + val_rate))]
        test = data[int(len(data) * (train_rate + val_rate)) : len(data)]
        return train, val, test
    
    def dataTrainingButtonClicked(self):
        X = np.load('visualization/input.npy')
        y = np.load('visualization/output.npy')

        permutation_index = np.random.permutation(len(X))
        X = X[permutation_index]
        y = y[permutation_index]
        y = y.reshape(-1, 1)

        scaler_x = MinMaxScaler()
        X = scaler_x.fit_transform(X)

        train_X, val_X, test_X = self.divide_data(X, 0.6, 0.2, 0.2)
        train_y, val_y, test_y = self.divide_data(y, 0.6, 0.2, 0.2)
        
        model = Sequential()
        model.add(LSTM(units=100, return_sequences=True, input_shape=(train_X.shape[1], 1)))
        model.add(LSTM(units=100, return_sequences=True))
        model.add(LSTM(units=100, return_sequences=True))
        model.add(LSTM(units=100, return_sequences=True))
        model.add(Flatten())
        model.add(Dense(units=1))

        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=3, min_lr=0.0001)
        model.compile(optimizer='adam', loss='MeanSquaredError', metrics=['mean_absolute_error'])
        checkpoint = ModelCheckpoint(filepath='/visualization/model/model_checkpoint_exp2_{epoch:02d}.h5', save_freq='epoch')

        history = model.fit(train_X, train_y, epochs=100, batch_size=1000, validation_data=(val_X, val_y), callbacks=[checkpoint, reduce_lr])
        model.save('visualization/model.h5')

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TrainingMainWindow()
    w.show()
    app.exec_()
