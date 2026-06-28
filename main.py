import sys
import os
import shutil
import threading
import ssl
from datetime import datetime
from pathlib import Path
import webview


def resource_path(relative):
    """Return path to a bundled resource (inside _MEIPASS when frozen)."""
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / relative)


def exe_dir():
    """Return the directory containing the EXE (or the script dir when not frozen)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent

import Cloud

drive = Cloud.Engine()


#  <------  FUNCTIONS  ------>

class PythonApi:
    #   <------  LOCAL  ------>
    def __init__(self):
        self.path_A = None
        self.path_B = None
        self.path_C = None
        self.root_id = ""
        self.total_work = 0
        self.work_done = 1
        self.cloud_cache = []
        self.is_syncing = False

    def force_quit(self):
        self.is_syncing = False
        self._window.destroy()

    def truncate_path(self, path):
        part = list(path.parts)

        for p in range(1, len(part)):
            truncated = "\\".join(part[p::])

            if len(truncated) < 25:
                return rf"{part[0]}...\{truncated}" if p > 1 else str(path)

        return str(path)

    def get_locations(self, location):
        path = self._window.create_file_dialog(webview.FileDialog.FOLDER)

        if not path:
            return None

        path = Path(path[0])

        setattr(self, f"path_{location.upper()}", path)
        return self.truncate_path(path), path.name, str(path)

    def drop_locations(self, location):
        if location == "a":
            self.path_A = None
        elif location =="b":
            self.path_B = None
        elif location == "c":
            self.path_C = None
            drive.target_id = None

    def compare_l2l(self):
        rel_A = {item.relative_to(self.path_A) for item in self.path_A.rglob("*")}
        rel_B = {item.relative_to(self.path_B) for item in self.path_B.rglob("*")}

        return (rel_B - rel_A), (rel_A - rel_B), (rel_A & rel_B)

    def compare_l2c(self):
        rel_A = {
            str(item.relative_to(self.path_A)).replace("\\", "/")
            for item in self.path_A.rglob("*")
        }

        rel_C = {item["path"] for item in self.cloud_cache}

        miss_A = [item for item in self.cloud_cache if item["path"] in (rel_C - rel_A)]
        inter_C = [item for item in self.cloud_cache if item["path"] in (rel_A & rel_C)]

        return miss_A, rel_A - rel_C, (rel_A & rel_C, inter_C)

    def synchronize_files(self, is_cloud):
        self.is_syncing = True
        try:
            if is_cloud:
                if not self.path_A or not self.path_A.exists():
                    raise FileNotFoundError(self.path_A)
                self.cache_C(self.path_C)
                miss_A, miss_C, inter_AC = self.compare_l2c()
                self.total_work = len(miss_A) + len(miss_C) + len(inter_AC)
            else:
                if not self.path_A or not self.path_A.exists():
                    raise FileNotFoundError(self.path_A)
                if not self.path_B or not self.path_B.exists():
                    raise FileNotFoundError(self.path_B)
                miss_A, miss_B, inter_AB = self.compare_l2l()
                self.total_work = len(miss_A) + len(miss_B) + len(inter_AB)

            self._window.evaluate_js("progressBar('show')")

            if is_cloud:
                self.download_files(self.path_A, miss_A)
                self.upload_files(self.path_A, self.path_C, miss_C)
                self.update_files(inter_AC)
            else:
                self.copy_files(self.path_B, self.path_A, miss_A)
                self.copy_files(self.path_A, self.path_B, miss_B)
                self.copy_latest(inter_AB)

            self.work_done = 1
            self._window.evaluate_js("progressBar('hide')")
            return {"ok": True}

        except PermissionError:
            self._window.evaluate_js("progressBar('hide')")
            return {"ok": False, "error": "Permission denied. A file or folder could not be accessed."}

        except FileNotFoundError:
            self._window.evaluate_js("progressBar('hide')")
            return {"ok": False, "error": "A selected folder no longer exists. Please re-select it."}

        except (ssl.SSLError, ConnectionError, TimeoutError, OSError) as e:
            if isinstance(e, (ssl.SSLError, ConnectionError, TimeoutError)):
                self._window.evaluate_js("progressBar('hide')")
                return {"ok": False, "error": "Network error. Please check your internet connection."}
            self._window.evaluate_js("progressBar('hide')")
            return {"ok": False, "error": "A system error occurred. Please check your disk or storage."}

        except Exception:
            self._window.evaluate_js("progressBar('hide')")
            return {"ok": False, "error": "An unknown error occurred. Please try again."}
        
        finally:
            self.is_syncing = False

    def copy_files(self, src, dst, items):
        for item in items:
            self.update_bar()

            src_item, dst_item = src / item, dst / item

            if src_item.is_file():
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_item, dst_item)
            elif src_item.is_dir():
                dst_item.mkdir(parents=True, exist_ok=True)

    def copy_latest(self, inter_AB):
        for item in inter_AB:
            a_item, b_item = self.path_A / item, self.path_B / item

            if a_item.is_file() and b_item.is_file():
                if a_item.stat().st_mtime > b_item.stat().st_mtime:
                    self.copy_files(self.path_A, self.path_B, [item])
                elif b_item.stat().st_mtime > a_item.stat().st_mtime:
                    self.copy_files(self.path_B, self.path_A, [item])
                else:
                    self.update_bar()
            elif a_item.is_dir() and b_item.is_dir():
                self.update_bar()

    def update_bar(self):
        self._window.evaluate_js(
            f"updateProgressBar(({self.work_done}/{self.total_work}) * 100)"
        )
        self.work_done += 1

    #   <------  CLOUD  ------>
    def authenticate(self):
        drive.authenticate()
        self.root_id = drive.get_create_root()

    def create_folder(self, name):
        return drive.create_folder(name)

    def scan_root(self):
        return drive.scan_root()

    def select_folder(self, id):
        drive.select_folder(id)
        self.path_C = id

    def scan_selected_folder(self, C_folder):
        drive.scan_selected_folder(C_folder)

    def cache_C(self, target):
        self.cloud_cache = [
            {
                "id": i["id"],
                "name": i["name"],
                "path": i["path"],
                "is_dir": i["is_dir"],
                "modified": i["modified"],
            }
            for i in drive.scan_selected_folder(target)
        ]

    def download_files(self, local, cloud):
        for i in cloud:
            self.update_bar()

            local_i = local / i["path"]

            if not i["is_dir"]:
                local_i.parent.mkdir(parents=True, exist_ok=True)
                drive.download_files(i["id"], local_i)
            else:
                local_i.mkdir(parents=True, exist_ok=True)

    def upload_files(self, local, cloud, items):
        for i in items:
            self.update_bar()

            local_i = local / i

            if local_i.is_file():
                parent_id = drive.get_create_path(str(Path(i).parent), cloud)
                drive.upload_files(local_i, parent_id)
            elif local_i.is_dir():
                drive.get_create_path(i, cloud)

    def update_files(self, inter_AC):
        inter_A, inter_C = inter_AC
        cloud_lookup = {c["path"]: c for c in inter_C}

        for item in inter_A:
            full_A = self.path_A / item
            full_C = cloud_lookup[item]

            local_mtime = full_A.stat().st_mtime
            cloud_mtime = datetime.fromisoformat(
                full_C["modified"].replace("Z", "+00:00")
            ).timestamp()

            if full_A.is_file() and not full_C["is_dir"]:
                if local_mtime > cloud_mtime:
                    drive.delete_files(full_C["id"])
                    self.upload_files(self.path_A, self.path_C, [item])
                elif cloud_mtime > local_mtime:
                    self.download_files(self.path_A, [full_C])
                else:
                    self.update_bar()
            elif full_A.is_dir() and full_C["is_dir"]:
                self.update_bar()


#  <------  MAIN WINDOW  ------>
API = PythonApi()
WINDOW = webview.create_window(
    "File Sync Tool",
    resource_path("web_GUI/index.html"),
    js_api=API,
    width=800,
    height=600,
    resizable=False,
)
def on_closing():
    if API.is_syncing:
        threading.Thread(
            target=lambda: WINDOW.evaluate_js("showExitConfirm()"),
            daemon=True
        ).start()
        return False
WINDOW.events.closing += on_closing
API._window = WINDOW
webview.start(debug=False)
