import os
import re


class PathHandler:
    def __init__(self, paths: list):
        self.paths = paths

    def get_path_to_file(self) -> str:
        paths_to_files = re.sub(r'\.\w{1,5}$', "", self.paths[0])
        file_name = re.sub(r'\.\w{1,5}$', "", os.path.basename(self.paths[0]))

        return paths_to_files.replace(file_name, "")

    def common_combine(self) -> list:
        return self.paths

    def last_combine(self) -> list:
        result_list = []
        counter_plus = 0
        counter_minus = -1

        for i in range(1, len(self.paths) + 1):
            if counter_plus and abs(counter_minus) - 1 == int((len(self.paths) + 1) / 2):
                break
            else:
                result_list.append(self.paths[counter_plus])
                counter_plus += 1
                result_list.append(self.paths[counter_minus])
                counter_minus -= 1
        return result_list

    def middle_combine(self) -> list:
        result_list = []
        counter_one = 0
        counter_two = int((len(self.paths) + 1) / 2)

        for i in range(1, len(self.paths) + 1):
            if counter_two == len(self.paths):
                break
            else:
                result_list.append(self.paths[counter_one])
                counter_one += 1
                result_list.append(self.paths[counter_two])
                counter_two += 1
        return result_list

    def get_list_file_name(self) -> list:
        filter_list_file = []
        for path in self.paths:
            filter_list_file.append(re.sub(r'\.\w{1,5}$', "", os.path.basename(path)))

        return filter_list_file

    def del_pages(self, skip_pages: list) -> list:
        if skip_pages:
            for i in reversed(sorted(skip_pages)):
                if i != 0:
                    self.paths.pop(i - 1)
            return self.paths
        return self.paths

    def sorting_paths(self) -> list:
        pre_sorted_list = []
        sorted_list_files_organizer = []

        for i in self.paths:
            if re.match(r"(.*)\((\d*)\)(.*)", i):
                pre_sorted_list.append(i)
            else:
                pre_sorted_list.append(False)

        if False not in pre_sorted_list:
            for i in sorted(self.paths, key=lambda x: int(re.search(r"(.*)\((\d*)\)(.*)", x)[2])):
                sorted_list_files_organizer.append(i)
            return sorted_list_files_organizer
        else:
            return self.paths
