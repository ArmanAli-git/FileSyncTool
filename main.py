import shutil
from pathlib import Path
import webview
import Cloud
from datetime import datetime


drive = Cloud.Engine()


#  <------  FUNCTIONS  ------>
class PythonApi:
    
    #   <------  LOCAL  ------>
    def __init__(self):
        self.path_A = "Path not found"
        self.path_B = "Path not found"
        self.path_C = None
        self.root_id = ""
        self.total_work = 0
        self.work_done = 1
        self.cloud_cache = []


    def truncate_path(self, path):
        tpath = list(path.parts)

        for i in range(1, len(tpath)):
            lenght = len("\\".join(tpath[i::]))
            if lenght < 25:
                if i > 2:
                    return fr"{tpath[0]}...\{"\\".join(tpath[i::])}"
                else:
                    return str(path)
    
    
    def select_A(self):
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            self.path_A = Path(pick[0])
        else:
            return None
        return self.truncate_path(self.path_A), self.path_A.name, str(self.path_A)


    def select_B(self):
        pick = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if pick:
            self.path_B = Path(pick[0])
        else:
            return None
        return self.truncate_path(self.path_B), self.path_B.name, str(self.path_B)


    def compare_l2l(self):
        items_A = {item for item in self.path_A.rglob("*")}
        items_B = {item for item in self.path_B.rglob("*")}

        rel_items_A = {item.relative_to(self.path_A) for item in items_A}
        rel_items_B = {item.relative_to(self.path_B) for item in items_B}

        missing_in_A = rel_items_B - rel_items_A
        missing_in_B = rel_items_A - rel_items_B
        inter_AB = rel_items_A & rel_items_B

        return missing_in_A, missing_in_B, inter_AB


    def compare_l2c(self):
        items_A = {item for item in self.path_A.rglob("*")}

        rel_items_A = {str(item.relative_to(self.path_A)).replace("\\", "/") for item in items_A}
        rel_items_C = {item["path"] for item in self.cloud_cache}

        missing_in_A = rel_items_C - rel_items_A
        missing_in_C = rel_items_A - rel_items_C
        inter_local = rel_items_A & rel_items_C

        missing_in_A = [item for item in self.cloud_cache if item["path"] in missing_in_A]
        inter_cloud = [item for item in self.cloud_cache if item["path"] in inter_local]

        return missing_in_A, missing_in_C, (inter_local, inter_cloud)


    def sync(self, cloud, cloud_folder):
        if cloud == True:
            self.cache(cloud_folder)
            
            missing_in_A, missing_in_C, inter_AC = self.compare_l2c()

            self.total_work = len(missing_in_A) + len(missing_in_C) + len(inter_AC)

            self._window.evaluate_js("progressBar('show')")

            self.downloader(self.path_A, missing_in_A)
            self.uploader(self.path_A, self.path_C, missing_in_C)
            self.updater(inter_AC)

            self.work_done = 1
            self._window.evaluate_js("progressBar('hide')")


        elif cloud == False:
            missing_in_A, missing_in_B, inter_AB = self.compare_l2l()

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


    def create_folder(self, folder_name):
        return drive.create_folder(folder_name)
        
        
    def scan_root(self):
        return drive.scan_root()   


    def lock_target_folder(self, folder_id):
        drive.lock_target_folder(folder_id) 
        self.path_C = folder_id


    def scan_target_dir(self, cloud_folder):
        drive.scan_target_directory(cloud_folder)


    def cache(self, target_folder):
        for item in drive.scan_target_directory(target_folder):
            item_meta = {"id": item["id"], "name":item["name"], "path":item["path"], "is_dir":item["is_dir"], "modified":item["modified"]}
            self.cloud_cache.append(item_meta)


    def downloader(self, local_path, items_info):
        if len(items_info) == 0:
            return

        for item in items_info:
            self.update_bar()

            local_item = local_path / item["path"]

            if not item["is_dir"]:
                local_item.parent.mkdir(parents=True, exist_ok=True)
                drive.download(item["id"], local_item)
            else:
                local_item.mkdir(parents=True, exist_ok=True)


    def uploader(self, local_path, cloud_path, items):
        if len(items) == 0:
            return

        for item in items:
            self.update_bar()

            local_item = local_path / item

            if local_item.is_file():
                parent_id = drive.get_or_create_path(str(Path(item).parent), cloud_path)
                drive.upload(local_item, parent_id)
            elif local_item.is_dir():
                drive.get_or_create_path(item, cloud_path)


    def updater(self, inter_AC):
        inter_local, inter_cloud = inter_AC

        if len(inter_local) == 0:
            return

        cloud_lookup = {c["path"]: c for c in inter_cloud}

        for item in inter_local:
            full_A = self.path_A / item
            full_C = cloud_lookup[item]

            local_mtime = full_A.stat().st_mtime

            full_C_mtime_str = full_C["modified"].replace("Z", "+00:00")
            cloud_mtime = datetime.fromisoformat(full_C_mtime_str).timestamp()

            if full_A.is_file() and not full_C["is_dir"]:
                if local_mtime > cloud_mtime:
                    self.uploader(self.path_A, self.path_C, [item])
                elif cloud_mtime > local_mtime:
                    self.downloader(self.path_A, [full_C])
                else:
                    self.update_bar()
            elif full_A.is_dir() and full_C["is_dir"]:
                self.update_bar()


#  <------  MAIN WINDOW  ------>
API = PythonApi()
WINDOW = webview.create_window("File Sync Tool", "http://localhost:5500/web_GUI", js_api=API, width=800, height=600, resizable=True)
API._window = WINDOW
webview.start(debug=True)