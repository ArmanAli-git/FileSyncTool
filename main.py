import webview, shutil
from pathlib import Path

#  <------  GLOBAL VARIABLES  ------>
path_A = "Path not found"
path_B = "Path not found"
total_work = 0
work_done = 1

#  <------  FUNCTIONS  ------>
class Python_api():
    def select_A(self):
        global path_A
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            path_A = Path(pick[0])
        else:
            pass

        return str(path_A)


    def select_B(self):
        global path_B
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            path_B = Path(pick[0])
        else:
            pass

        return str(path_B)


    def sync(self):
        global total_work
        global work_done

        items_A = {item for item in path_A.rglob("*")}
        items_B = {item for item in path_B.rglob("*")}

        rel_items_A = {item.relative_to(path_A) for item in items_A}
        rel_items_B = {item.relative_to(path_B) for item in items_B}

        missing_in_A = rel_items_B - rel_items_A
        missing_in_B = rel_items_A - rel_items_B
        inter_AB = rel_items_A & rel_items_B

        total_work = len(missing_in_A) + len(missing_in_B) + len(inter_AB)

        self._window.evaluate_js("progressShow()")

        self.copy(path_B, path_A, missing_in_A)
        self.copy(path_A, path_B, missing_in_B)
        self.update(inter_AB)

        work_done = 1
        self._window.evaluate_js("progressHide()")
        return "Synced!"
            

    def copy(self, src_path, dst_path, items):
        if len(items) == 0:
            return

        for item in items:
            self.update_bar()

            src_item = src_path/item
            dst_item = dst_path/item
        
            if src_item.is_file():
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_item, dst_item)
            elif src_item.is_dir():
                dst_item.mkdir(parents=True, exist_ok=True)
            

    def update(self, inter_AB):
        if len(inter_AB) == 0:
            return

        for item in inter_AB:

            item_A = path_A/item
            item_B = path_B/item

            if item_A.is_file() and item_B.is_file():
                if item_A.stat().st_mtime > item_B.stat().st_mtime:
                    self.copy(path_A, path_B, [item])
                elif item_B.stat().st_mtime > item_A.stat().st_mtime:
                    self.copy(path_B, path_A, [item])
                else:
                    self.update_bar()
            elif item_A.is_dir() and item_B.is_dir():
                self.update_bar()

    
    def update_bar(self):
        global work_done
        global total_work

        self._window.evaluate_js(f"updateProgress(({work_done}/{total_work}) * 100)")
        work_done += 1


#  <------  MAIN WINDOW  ------>
api = Python_api()
window = webview.create_window("File Sync Tool", "./web_GUI/index.html", js_api=api)
api._window = window
webview.start()