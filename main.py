import os
import re

from PIL import Image
from loguru import logger
from PyPDF2 import PdfMerger
from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from main_class import Ui_MainWindow


logger.add("debug.log", format="{time}, {level}, {message}", level="DEBUG", rotation="2 days", retention="2 days")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.application_func()

    def application_func(self):
        self.setWindowTitle("PDF organizer")
        self.progressBar_convert.setValue(0)
        self.label_complete_convert.hide()
        self.progressBar_organizer.setValue(0)
        self.label_complete_combine.hide()
        #connections
        self.pushButton_converter_path_open.clicked.connect(self.path)
        self.pushButton_organizer_path_open.clicked.connect(self.path_organizer)
        self.pushButton_convert.clicked.connect(self.convert_img)
        self.pushButton_organizer.clicked.connect(self.concatenating_pdf)
        self.checkBox_organizer_midlle_combine.clicked.connect(self.off_checkbox_last)
        self.checkBox_organizer_last_combine.clicked.connect(self.off_checkbox_middle)

    """ Converter """

    @logger.catch
    def path(self, bool_val=False):
        self.paths_to_files = QFileDialog.getOpenFileNames(self, filter="(*.png *.jpeg *.jpg *.bmp)")[0]
        self.hide_progressbar_convert(True)
        if self.paths_to_files:
            self.file_path_line(self.paths_to_files)

    @logger.catch
    def file_path_line(self, path: list):
        paths_to_files = re.sub(r'\.\w{1,5}$', "", path[0])
        file_name = re.sub(r'\.\w{1,5}$', "", os.path.basename(path[0]))
        self.lineEdit_converter_path.setText(paths_to_files.replace(file_name, ""))
        self.display_img(path)

    @logger.catch
    def collect_img(self, paths: list) -> list:
        filter_list_file = []
        for path in paths:
            filter_list_file.append(os.path.basename(path))

        return filter_list_file

    @logger.catch
    def display_img(self, path: list):
        self.listWidget_convert_object.clear()
        for i in self.collect_img(path):
            self.listWidget_convert_object.addItem(i)

    @logger.catch
    def current_date(self) -> str:
        return f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"

    @logger.catch
    def correct_path_file(self, file_name: str) -> str:
        """
        Поиск имени файла, который не совпадает с существующими
        :param file_name: 
        :return: file name
        """
        save_name_counter = 0
        if os.path.exists(f'{os.getcwd()}\\pdf\\{file_name}_{self.current_date()}.pdf'):
            while True:
                if os.path.exists(f'{os.getcwd()}\\pdf\\{file_name}_{self.current_date()} ({save_name_counter}).pdf'):
                    save_name_counter += 1
                    continue
                else:
                    return f'{os.getcwd()}\\pdf\\{file_name}_{self.current_date()} ({save_name_counter}).pdf'
        else:
            return f'{os.getcwd()}\\pdf\\{file_name}_{self.current_date()}.pdf'

    @logger.catch
    def convert_img(self, bool_val=False):
        self.progressBar_convert.setValue(0)
        self.hide_progressbar_convert(False)
        try:
            img_list = self.paths_to_files

            if self.check_out_folder():
                step = 0
                process = 100/len(img_list)

                for entry in img_list:
                    image_1 = Image.open(entry)
                    im_1 = image_1.convert('RGB')
                    file_name = re.sub(r'\.\w{1,5}$', "", os.path.basename(entry))
                    im_1.save(self.correct_path_file(file_name))
                    step += process
                    self.progressBar_convert.setValue(int(step))

                self.progressBar_convert.setValue(100)
                self.hide_progressbar_convert(True)
        except AttributeError:
            error = QMessageBox()
            error.setWindowTitle('Ошибка')
            error.setText('Выберите папку')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.setDefaultButton(QMessageBox.StandardButton.Ok)

            error.exec()
        except ZeroDivisionError:
            error = QMessageBox()
            error.setWindowTitle('Ошибка')
            error.setText('Выберите папку')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.setDefaultButton(QMessageBox.StandardButton.Ok)

            error.exec()

    @logger.catch
    def hide_progressbar_convert(self, flag: bool):
        if flag:
            self.progressBar_convert.setValue(0)
            self.progressBar_convert.hide()
            self.label_complete_convert.show()
        else:
            self.progressBar_convert.show()
            self.label_complete_convert.hide()

    @logger.catch
    def check_out_folder(self) -> bool:
        if not os.path.exists(os.getcwd() + "\pdf"):
            os.mkdir(os.getcwd() + "\pdf")
            return True
        else:
            return True


    """ Organizer """

    @logger.catch
    def off_checkbox_last(self, bool_val=False):
        self.checkBox_organizer_last_combine.setChecked(False)

    @logger.catch
    def off_checkbox_middle(self, bool_val=False):
        self.checkBox_organizer_midlle_combine.setChecked(False)

    @logger.catch
    def path_organizer(self, bool_val=False):
        self.paths_to_files_organizer = QFileDialog.getOpenFileNames(self, filter="(*.pdf)")[0]
        self.hide_progressbar_organizer(False)
        if self.paths_to_files_organizer:
            self.file_path_line_organizer(self.paths_to_files_organizer)

    @logger.catch
    def file_path_line_organizer(self, paths: list):
        paths_to_files = re.sub(r'\.\w{1,5}$', "", paths[0])
        file_name = re.sub(r'\.\w{1,5}$', "", os.path.basename(paths[0]))

        self.lineEdit_organizer_path.setText(paths_to_files.replace(file_name, ""))
        self.label_organizer_quantity_pages.setText(str(len(paths)))

    @logger.catch
    def skip_this_page(self) -> list:
        if self.lineEdit_organizer_skip_page.text() != "":
            list_re = re.split(r"(\d+)", self.lineEdit_organizer_skip_page.text())
            result = []
            for i in range(1, len(list_re)):
                if i % 2 != 0:
                    if list_re[i].isdigit:
                        result.append(int(list_re[i]))
            return result
        else:
            return []

    @logger.catch
    def del_skip_page(self, list_no_skip: list) -> list:
        result_list = list_no_skip
        if self.skip_this_page():
            for i in reversed(sorted(self.skip_this_page())):
                if i != 0:
                    result_list.pop(i-1)
            return result_list
        return result_list

    @logger.catch
    def sorting_list(self) -> list:
        '''
        Сортировка списка
        last
        1234 -> 1423
        middle 
        1234 -> 1324
        common
        1234 -> 1234
        :return: sort list 
        '''
        sorted_list_files_organizer = []
        result_list = []

        for i in sorted(self.paths_to_files_organizer,
                        key=lambda x: int(re.search(r"(.*)\((\d*)\)(.*)", x)[2])):
            sorted_list_files_organizer.append(i)

        if (self.checkBox_organizer_midlle_combine.isChecked() or self.checkBox_organizer_last_combine.isChecked()) and \
                (len(sorted_list_files_organizer) - len(self.skip_this_page())) % 2 != 0:
            error = QMessageBox()
            error.setWindowTitle('Ошибка')
            error.setText('Нельзя объединить не чётное количество файлов используя middle или last combine')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.setDefaultButton(QMessageBox.StandardButton.Ok)

            error.exec()
            return

        if self.checkBox_organizer_midlle_combine.isChecked():
            counter_one = 0
            counter_two = int((len(sorted_list_files_organizer) + 1) / 2)

            for i in range(1, len(sorted_list_files_organizer) + 1):
                if counter_two == len(sorted_list_files_organizer):
                    break
                else:
                    result_list.append(sorted_list_files_organizer[counter_one])
                    counter_one += 1
                    result_list.append(sorted_list_files_organizer[counter_two])
                    counter_two += 1
            return self.del_skip_page(result_list)
        elif self.checkBox_organizer_last_combine.isChecked():
            counter_plus = 0
            counter_minus = -1

            for i in range(1, len(sorted_list_files_organizer)+1):
                if counter_plus and abs(counter_minus)-1 == int((len(sorted_list_files_organizer)+1)/2):
                    break
                else:
                    result_list.append(sorted_list_files_organizer[counter_plus])
                    counter_plus += 1
                    result_list.append(sorted_list_files_organizer[counter_minus])
                    counter_minus -= 1
            return self.del_skip_page(result_list)
        else:
            return self.del_skip_page(sorted_list_files_organizer)

    @logger.catch
    def concatenating_pdf(self, bool_val=False):
        self.progressBar_organizer.setValue(0)
        self.hide_progressbar_organizer(False)
        try:
            if self.paths_to_files_organizer:
                sort_list = self.sorting_list()
                if sort_list:
                    pdf_merger = PdfMerger()
                    step = 0
                    process = 100 / len(sort_list)
                    for path in sort_list:
                        pdf_merger.append(path)
                        step += process
                        self.progressBar_organizer.setValue(int(step))

                    try:
                        path_to_save = QFileDialog.getSaveFileUrl(parent=None, caption="Save", filter="*.pdf")
                        pdf_merger.write(path_to_save[0].path()[1:])
                    except ValueError:
                        pass
            else:
                error = QMessageBox()
                error.setWindowTitle('Ошибка')
                error.setText('Выберите папку')
                error.setIcon(QMessageBox.Icon.Warning)
                error.setStandardButtons(QMessageBox.StandardButton.Ok)
                error.setDefaultButton(QMessageBox.StandardButton.Ok)

                error.exec()
        except AttributeError:
            error = QMessageBox()
            error.setWindowTitle('Ошибка')
            error.setText('Выберите папку')
            error.setIcon(QMessageBox.Icon.Warning)
            error.setStandardButtons(QMessageBox.StandardButton.Ok)
            error.setDefaultButton(QMessageBox.StandardButton.Ok)

            error.exec()

        self.hide_progressbar_organizer(True)

    @logger.catch
    def hide_progressbar_organizer(self, flag: bool):
        if flag:
            self.progressBar_organizer.setValue(0)
            self.progressBar_organizer.hide()
            self.label_complete_combine.show()
        else:
            self.progressBar_organizer.show()
            self.label_complete_combine.hide()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
