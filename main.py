import os
import re

from PIL import Image
from loguru import logger
from PyPDF2 import PdfMerger
from datetime import datetime

from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QFileDialog, QMessageBox

from main_class import Ui_MainWindow
from path_handler import PathHandler


logger.add("debug.log", format="{time}, {level}, {message}", level="DEBUG", rotation="2 days", retention="2 days")


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.__application_func()

    def __application_func(self):
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
        self.checkBox_organizer_midlle_combine.clicked.connect(self._off_checkbox_last)
        self.checkBox_organizer_last_combine.clicked.connect(self._off_checkbox_middle)

    """ Converter """

    @logger.catch
    def path(self, bool_val=False):
        paths_to_files = QFileDialog.getOpenFileNames(self, filter="(*.png *.jpeg *.jpg *.bmp)")[0]
        self.path_handler = PathHandler(paths_to_files)
        self._hide_progressbar_convert(False)
        if self.path_handler:
            self.__file_path_line()

    @logger.catch
    def convert_img(self, bool_val=False):
        self.progressBar_convert.setValue(0)
        self._hide_progressbar_convert(True)
        try:
            img_list = self.path_handler.common_combine()

            if self._check_out_folder():
                step = 0
                process = 100/len(img_list)

                for entry in img_list:
                    image_1 = Image.open(entry)
                    im_1 = image_1.convert('RGB')
                    file_name = re.sub(r'\.\w{1,5}$', "", os.path.basename(entry))
                    im_1.save(self._correct_path_file(file_name))
                    step += process
                    self.progressBar_convert.setValue(int(step))

                self.progressBar_convert.setValue(100)
                self._hide_progressbar_convert(True)
        except AttributeError:
            self._user_except('Ошибка')
        except ZeroDivisionError:
            self._user_except('Выберите папку')

    @logger.catch
    def __file_path_line(self):
        self.lineEdit_converter_path.setText(self.path_handler.get_path_to_file())
        self.__display_img()

    @logger.catch
    def __display_img(self):
        self.listWidget_convert_object.clear()
        for i in self.path_handler.get_list_file_name():
            self.listWidget_convert_object.addItem(i)

    @logger.catch
    def _current_date(self) -> str:
        return f"{datetime.now().day}.{datetime.now().month}.{datetime.now().year}"

    @logger.catch
    def _correct_path_file(self, file_name: str) -> str:
        """
        Поиск имени файла, который не совпадает с существующими
        :param file_name:
        :return: file name
        """
        save_name_counter = 0
        if os.path.exists(f'{os.getcwd()}\\pdf\\{file_name}_{self._current_date()}.pdf'):
            while True:
                if os.path.exists(f'{os.getcwd()}\\pdf\\{file_name}_{self._current_date()} ({save_name_counter}).pdf'):
                    save_name_counter += 1
                    continue
                else:
                    return f'{os.getcwd()}\\pdf\\{file_name}_{self._current_date()} ({save_name_counter}).pdf'
        else:
            return f'{os.getcwd()}\\pdf\\{file_name}_{self._current_date()}.pdf'

    @logger.catch
    def _hide_progressbar_convert(self, flag: bool):
        if flag:
            self.progressBar_convert.setValue(0)
            self.progressBar_convert.hide()
            self.label_complete_convert.show()
        else:
            self.progressBar_convert.show()
            self.label_complete_convert.hide()

    @logger.catch
    def _check_out_folder(self) -> bool:
        if not os.path.exists(os.getcwd() + "\pdf"):
            os.mkdir(os.getcwd() + "\pdf")
            return True
        else:
            return True

    """ Organizer """

    @logger.catch
    def path_organizer(self, bool_val=False):
        paths_to_files_organizer = QFileDialog.getOpenFileNames(self, filter="(*.pdf)")[0]
        self.path_handler_organizer = PathHandler(paths_to_files_organizer)
        self._hide_progressbar_organizer(False)
        if self.path_handler_organizer:
            self.____file_path_line_organizer()

    @logger.catch
    def concatenating_pdf(self, bool_val=False):
        self.progressBar_organizer.setValue(0)
        self._hide_progressbar_organizer(False)
        try:
            if self.path_handler_organizer.get_list_file_name():
                sort_list = self.__sorting_list()
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
                self._user_except('Выберите папку')
        except AttributeError:
            self._user_except('Выберите папку')

        self._hide_progressbar_organizer(True)

    @logger.catch
    def _off_checkbox_last(self, bool_val=False):
        self.checkBox_organizer_last_combine.setChecked(False)

    @logger.catch
    def _off_checkbox_middle(self, bool_val=False):
        self.checkBox_organizer_midlle_combine.setChecked(False)

    @logger.catch
    def ____file_path_line_organizer(self):
        self.lineEdit_organizer_path.setText(self.path_handler_organizer.get_path_to_file())
        self.label_organizer_quantity_pages.setText(str(len(self.path_handler_organizer.get_list_file_name())))

    @logger.catch
    def _skip_this_page(self) -> list:
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
    def __del_skip_page(self):
        if self._skip_this_page():
            self.path_handler_organizer.del_pages(self._skip_this_page())

    @logger.catch
    def __sorting_list(self) -> list:
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
        sorted_list_files_organizer = self.path_handler_organizer.sorting_paths()

        if (self.checkBox_organizer_midlle_combine.isChecked() or self.checkBox_organizer_last_combine.isChecked()) and \
                (len(sorted_list_files_organizer) - len(self._skip_this_page())) % 2 != 0:
            return self._user_except('Нельзя объединить не чётное количество файлов используя middle или last combine')

        self.__del_skip_page()

        if self.checkBox_organizer_midlle_combine.isChecked():
            return self.path_handler_organizer.middle_combine()
        elif self.checkBox_organizer_last_combine.isChecked():
            return self.path_handler_organizer.last_combine()
        else:
            return sorted_list_files_organizer

    @logger.catch
    def _hide_progressbar_organizer(self, flag: bool):
        if flag:
            self.progressBar_organizer.setValue(0)
            self.progressBar_organizer.hide()
            self.label_complete_combine.show()
        else:
            self.progressBar_organizer.show()
            self.label_complete_combine.hide()

    @logger.catch
    def _user_except(self, text: str):
        error = QMessageBox()
        error.setWindowTitle('Ошибка')
        error.setText(text)
        error.setIcon(QMessageBox.Icon.Warning)
        error.setStandardButtons(QMessageBox.StandardButton.Ok)
        error.setDefaultButton(QMessageBox.StandardButton.Ok)

        error.exec()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec())
