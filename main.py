import shutil
from pathlib import Path

import webview

import Cloud


drive = Cloud.Engine()

#  <------  FUNCTIONS  ------>
class PythonApi:
    
    #   <------  LOCAL  ------>
    def __init__(self):
        self.path_A = "Path not found"
        self.path_B = "Path not found"
        self.total_work = 0
        self.work_done = 1
        self.root_id = ""
    
    
    def select_A(self):
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            self.path_A = Path(pick[0])
        else:
            pass

        return str(self.path_A)


    def select_B(self):
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            self.path_B = Path(pick[0])
        else:
            pass

        return str(self.path_B)


    def compare_dir(self):
        items_A = {item for item in self.path_A.rglob("*")}
        items_B = {item for item in self.path_B.rglob("*")}

        rel_items_A = {item.relative_to(self.path_A) for item in items_A}
        rel_items_B = {item.relative_to(self.path_B) for item in items_B}

        missing_in_A = rel_items_B - rel_items_A
        missing_in_B = rel_items_A - rel_items_B
        inter_AB = rel_items_A & rel_items_B

        return missing_in_A, missing_in_B, inter_AB


    def sync(self):
        missing_in_A, missing_in_B, inter_AB = self.compare_dir()

        self.total_work = len(missing_in_A) + len(missing_in_B) + len(inter_AB)

        self._window.evaluate_js("progressBar('show')")

        self.copy(self.path_B, self.path_A, missing_in_A)
        self.copy(self.path_A, self.path_B, missing_in_B)
        self.update(inter_AB)

        self.work_done = 1
        self._window.evaluate_js("progressBar('hide')")


    def copy(self, src_path, dst_path, items):
        if len(items) == 0:
            return

        for item in items:
            self.update_bar()

            src_item = src_path / item
            dst_item = dst_path / item

            if src_item.is_file():
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_item, dst_item)
            elif src_item.is_dir():
                dst_item.mkdir(parents=True, exist_ok=True)


    def update(self, inter_AB):
        if len(inter_AB) == 0:
            return

        for item in inter_AB:
            item_A = self.path_A / item
            item_B = self.path_B / item

            if item_A.is_file() and item_B.is_file():
                if item_A.stat().st_mtime > item_B.stat().st_mtime:
                    self.copy(self.path_A, self.path_B, [item])
                elif item_B.stat().st_mtime > item_A.stat().st_mtime:
                    self.copy(self.path_B, self.path_A, [item])
                else:
                    self.update_bar()
            elif item_A.is_dir() and item_B.is_dir():
                self.update_bar()

    def update_bar(self):

        self._window.evaluate_js(f"updateProgress(({self.work_done}/{self.total_work}) * 100)")
        self.work_done += 1
        
        
    #   <------  CLOUD  ------>
    def authenticate_ready(self):
        drive.authenticate()
        self.root_id = drive.get_or_create_root()
        print(self.root_id)


    def create_folder(self, folder_name):
        return drive.create_folder(folder_name)
        
        
    def scan_root(self):
        return drive.scan_root()    
    
    def scan_target_dir(self):
        drive.scan_target_directiry()
        

#  <------  MAIN WINDOW  ------>
API = PythonApi()
WINDOW = webview.create_window("File Sync Tool", "./web_GUI/index.html", js_api=API)
API._window = WINDOW
webview.start(debug=False)