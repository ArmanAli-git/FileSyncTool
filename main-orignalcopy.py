from PySide6.QtWidgets import *
from pathlib import Path
from PySide6.QtCore import Qt
import shutil, sys

#  <------  GLOBAL VARIABLES  ------>
paths = {"A" : None, "B" : None}

#  <------  FUNCTIONS  ------>
def select_A():
    path = QFileDialog.getExistingDirectory()
    if path:
        paths["A"] = Path(path)
        label_A.setText(path)


def select_B():
    path = QFileDialog.getExistingDirectory()
    if path:
        paths["B"] = Path(path)
        label_B.setText(path)


def sync_items():
    items_A = {item for item in paths["A"].rglob("*")}
    items_B = {item for item in paths["B"].rglob("*")}

    rel_items_A = {item.relative_to(paths["A"]) for item in items_A}
    rel_items_B = {item.relative_to(paths["B"]) for item in items_B}

    missing_in_A = rel_items_B - rel_items_A
    missing_in_B = rel_items_A - rel_items_B
    inter_AB = rel_items_A & rel_items_B

    progress_bar.setVisible(True)

    copy_items(paths["B"], paths["A"], missing_in_A)
    copy_items(paths["A"], paths["B"], missing_in_B)
    sync_latest(inter_AB)

    progress_bar.setVisible(False)

    label_sync.setText("Sync is done!")
    label_sync.setStyleSheet("color: green;")
        

def copy_items(src_path, dst_path, items):
    total_pr = len(items)

    if total_pr > 0:
        progress_bar.setRange(0, total_pr)
        
        for i, item in enumerate(items, start=1):
            src_item = src_path/item
            dst_item = dst_path/item
        
            if src_item.is_file():
                dst_item.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_item, dst_item)
                
            elif src_item.is_dir():
                dst_item.mkdir(parents=True, exist_ok=True)
            
            progress_bar.setValue(i)
            QApplication.processEvents()

    else:
        progress_bar.setRange(0, 100)
        progress_bar.setValue(100)


def sync_latest(inter_AB):
    total_pr = len(inter_AB)

    if total_pr > 0:
        progress_bar.setRange(0, total_pr)

        for i, item in enumerate(inter_AB, start=1):
            item_A = paths["A"]/item
            item_B = paths["B"]/item

            if item_A.is_file() and item_B.is_file():
                if item_A.stat().st_mtime > item_B.stat().st_mtime:
                    copy_items(paths["A"], paths["B"], [item])
                elif item_B.stat().st_mtime > item_A.stat().st_mtime:
                    copy_items(paths["B"], paths["A"], [item])
                    
            elif item_A.is_dir() and item_B.is_dir():
                pass
        
            progress_bar.setValue(i)
            QApplication.processEvents()
    else:
        progress_bar.setRange(0, 100)
        progress_bar.setValue(100)



#  <------  APPLICATION/WINDOW  ------>
app = QApplication(sys.argv)
window = QMainWindow()

#  <------  BUTTON A  ------>
button_A = QPushButton("Directory A")
button_A.setFixedSize(150, 70)
label_A = QLabel("Not selected")
label_A.setAlignment(Qt.AlignCenter)

layout_A = QVBoxLayout()
layout_A.addStretch()
layout_A.addWidget(button_A, alignment = Qt.AlignCenter)
layout_A.addWidget(label_A, alignment = Qt.AlignCenter)
layout_A.addStretch()

#  <------  BUTTON B  ------>
button_B = QPushButton("Directory B")
button_B.setFixedSize(150, 70)
label_B = QLabel("Not selected")
label_B.setAlignment(Qt.AlignCenter)

layout_B = QVBoxLayout()
layout_B.addStretch()
layout_B.addWidget(button_B, alignment = Qt.AlignCenter)
layout_B.addWidget(label_B, alignment = Qt.AlignCenter)
layout_B.addStretch()

#  <------  BUTTON SYNC  ------>
button_sync = QPushButton("Sync A and B")
button_sync.setFixedSize(150, 70)
label_sync = QLabel("")
label_sync.setAlignment(Qt.AlignCenter)

layout_sync = QVBoxLayout()
layout_sync.addStretch()
layout_sync.addWidget(button_sync, alignment = Qt.AlignCenter)
layout_sync.addWidget(label_sync, alignment = Qt.AlignCenter)
layout_sync.addStretch()

#  <------  PROGRESS BAR  ------>
progress_bar = QProgressBar()
progress_bar.setVisible(False)

layout_pb = QHBoxLayout()
layout_pb.addWidget(progress_bar)

#  <------  LAYOUT AB  ------>
layout_AB = QHBoxLayout()
layout_AB.addLayout(layout_A)
layout_AB.addLayout(layout_B)

#  <------  LAYOUT AB & SYNC  ------>
layout_main = QVBoxLayout()
layout_main.addLayout(layout_AB)
layout_main.addLayout(layout_sync)
layout_main.addLayout(layout_pb)


#  <------  MAIN WIDGET  ------>
widget_main = QWidget()
widget_main.setLayout(layout_main)
window.setCentralWidget(widget_main)

#  <------  LOGICAL PART  ------>
button_A.clicked.connect(select_A)
button_B.clicked.connect(select_B)
button_sync.clicked.connect(sync_items)

#  <------  MAIN WINDOW CONFIGS  ------>
window.setWindowTitle("File Sync Tool")
window.resize(800, 500)
window.setMinimumSize(500, 300)
window.setMaximumSize(1000, 800)
window.show()
app.exec()
