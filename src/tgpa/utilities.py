# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 10:23:16 2022

@author: YB263935
"""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                UTILITIES
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

#Imports
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os
import sys
import pickle
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from os import walk
from pathlib import Path

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                             Gestion des chemins
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Récupérer, Acquérir des chemins de dossiers et/ou fichiers

def getAFilesPath(window_title = None, filetypes  = [('All files','*.*')]) :
    
    """Renvoie le chemin vers un fichier"""
    
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfile(title = window_title, filetypes=filetypes)
    return(path.name)

def getFilesPaths(window_title = None) :
    
    """Renvoie les chemins respectifs de plusieurs fichiers dans une liste"""
    
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilenames(parent = root, title = window_title)
    return(path)

def getADirsPath(window_title = None):
    
    """Renvoie le chemin vers un dossier"""
    
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askdirectory(title = window_title)
    return(path)    

def create_folder(name):
    
    """ create a folder """
    
    if not os.path.exists(name):
        os.makedirs(name)

def getAFilesPathToSave(window_title = None, filetypes  = [('All files','*.*')]) :
    
    """Renvoie un chemin pour un fichier à sauvegarder"""
    
    root = tk.Tk()
    root.withdraw()
    path = filedialog.asksaveasfile(title = window_title, filetypes=filetypes)
    return(path.name)

def files_name_to_list(path):
    
    """ Renvoie une liste contenant les noms des fichiers excels des essais de
    Devenir"""
    
    listeFichiers = [] #Instancie la liste des noms de fichiers
    
    for (files_path, sousRepertoires, fichiers) in walk(path): #Ajoute les noms
        listeFichiers.extend(fichiers)
        
    for i in range(0,len(listeFichiers)) : 
        listeFichiers[i] = path + '/' + listeFichiers[i]
        

    return(listeFichiers) #Retourne la liste des noms et le chemin absolu


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                       Gestion des fichiers de données
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#Convertir en dataframe des fichiers de mesures, tracer des courbes, modifier
#des fichiers de données type excel, [...]

"""""""""""""""""""""""""""""""""Fichiers lvm"""""""""""""""""""""""""""""""""

def lvm_to_df(lvm_file_path, skiprows=22):
    
    """Converti un fichier lvm en dataframe"""
    #Note : La longueur de l'en-tête, fixée à 22, est un paramètre modifiable
    
    return(pd.read_csv(lvm_file_path, sep='\t', on_bad_lines='skip',
                     skiprows=skiprows, decimal=','))

"""""""""""""""""""""""""""""""""Fichiers h5"""""""""""""""""""""""""""""""""

#imports
import h5py

def channel_attr_to_dict(channel):
    
    """Get a signal's attributes (channel, ...)"""
    
    #Get and shape channel's attributes
    channel = str(channel.attrs["label"]).replace("{","") #Withdraw "{"
    channel = channel.replace("}","")[1:][1:][:-1].split(',') #withdraw "}"
    channel = [e.split(':') for e in channel] #withdraw ":"
    
    #Get those attributes in a dictionary
    dict1 = {}
    for e in channel : dict1[e[0].split('"')[1]] = e[1].split('"')[1]
    return(dict1)

def get_card_data_into_dataframe(card, time):
    
    """Get all signals' data into a table, referenced with their channel"""
    
    data_columns = [e for e in card] #Get the columns' names
    data = [card[i][()] for i in data_columns] #Get the data in a matrix
    data_f = []
    for array in data : 
        data_f.append([e[0] for e in array])
    #data1 = [array[0] for array in data1]
    Ldict = [channel_attr_to_dict(card[e]) for e in data_columns] #Get dictionaries with channels' number
    Lchannels = [e["data"].split("\'")[1][:-1] for e in Ldict]
    Lchannels = [e.split(" ")[-1] for e in Lchannels]
    
    #Get the channels' number 
    dct = {}
    for i in range(0,len(Lchannels)) : 
        dct[Lchannels[i]] = data[i]
                
    return(pd.DataFrame(np.array(data_f).transpose(), columns = Lchannels, index=time))    

def h5py_to_dataframe(h5py_file_path, scan:str, detector:str,axes:str, data:str,cards:[str]) :
    
    """Get data from h5py file into a dataframe table"""
    
    with h5py.File(h5py_file_path, "r",locking=False) as f:
        
        #Get time information
        time = [pd.Timestamp(e,unit='s', tz='Europe/Paris') for e in f['RawData'][scan][detector][axes]["Axis00"]]

        #Get the card's data
        Lcard = [f['RawData'][scan][detector][data][card] for card in cards]
        
        #Get the cards data into a dataframe
        dfs = [get_card_data_into_dataframe(card,time) for card in Lcard]
        
    return(dfs)

"""""""""""""""""""""""""""""""Fichiers pickel"""""""""""""""""""""""""""""""""

def save_as_pickle(name_pickle_out, structure_to_store):
    
    """Enregistre un DataFrame en format pickel"""
    
    output = open(name_pickle_out, 'wb')
    pickle.dump(structure_to_store, output)
    output.close()
    
def read_pickle(input_file):
    
    """Ouvre un pickle en format dataframe"""
    
    dictload = pickle.load(open(input_file, 'rb'))
    return dictload


"""""""""""""""""""""""""""""""Fichiers Excel"""""""""""""""""""""""""""""""""

from openpyxl import load_workbook


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                            Gestion des Pdfs
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
#Créer, modifier des pdf

def extractFromPdf():
    
    """Créer un pdf à partir de certaines pages (dont les numéros sont donnés
    par l'utilisateur) d'un autre pdf"""
    
    path_original_pdf = getAFilesPath() #Chemin absolu vers le pdf source
    original_pdf = PdfReader(str(path_original_pdf)) #Obtention fichier pdf
    #number_pages = original_pdf.getNumPages() #Nombre maximal de pages du pdf source
    output_pdf_path = getAFilesPathToSave() #Chemin absolu vers le pdf à enregistrer
    list_pages_to_extract = input('Veuillez renseigner les pages que vous voulez extraire du document original dans un format similaire à l exemple suivant  : 1 2 5 3 \n')
    
    #Création d'une liste des pages désirées de type nombre entiers
    list_pages_to_extract = list_pages_to_extract.split(' ') 
    for i in range(0, len(list_pages_to_extract)) : list_pages_to_extract[i] = int(list_pages_to_extract[i])
    pdf_writer = PdfWriter() #Création d'un fichier pdf de sortie
    
    #Récupération des pages désirées du pdf source dans le pdf de sortie
    for page_num in list_pages_to_extract : pdf_writer.addPage(original_pdf.getPage(page_num))
    
    #Enregistrement du fichier pdf de sortie dans le répertoire désiré
    with open(output_pdf_path,'wb') as out:
            pdf_writer.write(out)
    return()

def mergePdf():
    
    """Créer un pdf à partir de n pdf"""
    
    paths = getFilesPaths("Chemins vers les pdfs à fusionner")
    merge_file = PdfMerger()
    for path in paths:
        merge_file.append(PdfReader(path, 'rb'))
    output_pdf_path = getAFilesPathToSave() #Chemin absolu vers le pdf à enregistrer
    merge_file.write(output_pdf_path)
    return()
    
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                                    Widgets
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Widgets classes to go faster

from PyQt5.QtWidgets import QCheckBox, QVBoxLayout, QWidget, QApplication, QPushButton, QLabel
from pyqt_checkbox_list_widget.checkBoxListWidget import CheckBoxListWidget
from PyQt5.QtCore import Qt, QCoreApplication

class Widget(QWidget):

    def __init__(self,title, lst):
        super().__init__()
        self.__initUi(title, lst)

    def __initUi(self, title, lst):
        self.title = QLabel(title)
        self.title.setAlignment(Qt.AlignCenter)
        self.allCheckBox = QCheckBox('Check all')
        self.checked_items = []
        self.checkBoxListWidget = CheckBoxListWidget()
        self.checkBoxListWidget.addItems(lst)
        self.allCheckBox.stateChanged.connect(self.checkBoxListWidget.toggleState)
        self.button = QPushButton("Save the list")
        self.button.clicked.connect(self.save_the_list)
        self.lay = QVBoxLayout()
        self.lay.addWidget(self.title)
        self.lay.addWidget(self.allCheckBox)
        self.lay.addWidget(self.checkBoxListWidget)
        self.lay.addWidget(self.button)
        self.setLayout(self.lay)
    
    def save_the_list(self):
        for i in range(self.checkBoxListWidget.count()):
            item = self.checkBoxListWidget.item(i)
            if item.checkState() == 2:  # 2 means "Checked"
                self.checked_items.append(item.text())
            QCoreApplication.instance().quit()
        
        # Ici, tu peux manipuler la liste `checked_items` comme tu veux
        # Par exemple, tu peux l'enregistrer dans un fichier ou l'utiliser ailleurs
        
    
def getElementFromWidgetList(title,lst : []):
    
    app = QApplication(sys.argv)
    widget = Widget(title,lst)
    widget.show()
    app.exec_()
    return(widget.checked_items)
    


                


	

	

    
