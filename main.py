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


    def truncate(self, path):
        part = list(path.parts)

        for i in range(1, len(part)):
            truncated = "\\".join(part[i::])
            if len(truncated) < 25:
                return fr"{part[0]}...\{truncated}" if i > 1 else str(path)
        return str(path)
    
    
    def locations(self, loc):
        p = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if not p: return None

        path = Path(p[0])
        setattr(self, f"path_{loc.upper()}", path)
        return self.truncate(path), path.name, str(path)
        

    def compare_l2l(self):
        rel_A = {i.relative_to(self.path_A) for i in self.path_A.rglob("*")}
        rel_B = {i.relative_to(self.path_B) for i in self.path_B.rglob("*")}

        return rel_B - rel_A, rel_A - rel_B, rel_A & rel_B


    def compare_l2c(self):
        rel_A = {str(i.relative_to(self.path_A)).replace("\\", "/") for i in self.path_A.rglob("*")}
        rel_C = {i["path"] for i in self.cloud_cache}

        miss_A = [i for i in self.cloud_cache if i["path"] in (rel_C - rel_A)]
        inter_C = [i for i in self.cloud_cache if i["path"] in (rel_A & rel_C)]

        return miss_A, rel_A - rel_C, (rel_A & rel_C, inter_C)


    def sync(self, is_cloud, C_folder):
        if is_cloud:
            self.cache(C_folder)
            miss_A, miss_C, inter_AC = self.compare_l2c()
            self.total_work = len(miss_A) + len(miss_C) + len(inter_AC)

        else:
            miss_A, miss_B, inter_AB = self.compare_l2l()
            self.total_work = len(miss_A) + len(miss_B) + len(inter_AB)

        self._window.evaluate_js("progressBar('show')")

        if is_cloud:
            self.downloader(self.path_A, miss_A)
            self.uploader(self.path_A, self.path_C, miss_C)
            self.updater(inter_AC)
        else:
            self.copy(self.path_B, self.path_A, miss_A)
            self.copy(self.path_A, self.path_B, miss_B)
            self.update(inter_AB)

        self.work_done = 1
        self._window.evaluate_js("progressBar('hide')")


    def copy(self, src, dst, items):
        for i in items:
            self.update_bar()

            s, d = src / i, dst / i

            if s.is_file():
                d.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(s, d)
            elif s.is_dir():
                d.mkdir(parents=True, exist_ok=True)


    def update(self, inter_AB):
        for i in inter_AB:
            a, b = self.path_A / i, self.path_B / i

            if a.is_file() and b.is_file():
                if a.stat().st_mtime > b.stat().st_mtime:
                    self.copy(self.path_A, self.path_B, [i])
                elif b.stat().st_mtime > a.stat().st_mtime:
                    self.copy(self.path_B, self.path_A, [i])
                else:
                    self.update_bar()
            elif a.is_dir() and b.is_dir():
                self.update_bar()


    def update_bar(self):
        self._window.evaluate_js(f"updateProgressBar(({self.work_done}/{self.total_work}) * 100)")
        self.work_done += 1
        
        
    #   <------  CLOUD  ------>
    def authenticate(self):
        drive.authenticate()
        self.root_id = drive.get_or_create_root()


    def create_folder(self, name):
        return drive.create_folder(name)


    def scan_root(self):
        return drive.scan_root()   
        

    def select_folder(self, id):
        drive.select_folder(id) 
        self.path_C = id


    def scan_selected_folder(self, C_folder):
        drive.scan_selected_folder(C_folder)


    def cache(self, target):
        self.cloud_cache = [
            {"id": i["id"], "name":i["name"], "path":i["path"], "is_dir":i["is_dir"], "modified":i["modified"]}
            for i in drive.scan_selected_folder(target)
        ]


    def downloader(self, local, cloud):
        for i in cloud:
            self.update_bar()

            local_i = local / i["path"]

            if not i["is_dir"]:
                local_i.parent.mkdir(parents=True, exist_ok=True)
                drive.download(i["id"], local_i)
            else:
                local_i.mkdir(parents=True, exist_ok=True)


    def uploader(self, local, cloud, items):
        for i in items:
            self.update_bar()

            local_i = local / i

            if local_i.is_file():
                parent_id = drive.get_or_create_path(str(Path(i).parent), cloud)
                drive.upload(local_i, parent_id)
            elif local_i.is_dir():
                drive.get_or_create_path(i, cloud)


    def updater(self, inter_AC):
        inter_A, inter_C = inter_AC
        cloud_lookup = {c["path"]: c for c in inter_C}

        for item in inter_A:
            full_A = self.path_A / item
            full_C = cloud_lookup[item]

            local_mtime = full_A.stat().st_mtime
            cloud_mtime = datetime.fromisoformat(full_C["modified"].replace("Z", "+00:00")).timestamp()

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
WINDOW = webview.create_window("File Sync Tool", "http://127.0.0.1:5500/web_GUI/index.html", js_api=API, width=800, height=600, resizable=True)
API._window = WINDOW
webview.start(debug=True)