from __future__ import annotations
import threading
from pathlib import Path
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication,QFileDialog,QHBoxLayout,QLabel,QLineEdit,QListWidget,QMainWindow,QMessageBox,QProgressBar,QPushButton,QVBoxLayout,QWidget
from app.main import send_file,start_receiver

class DropArea(QListWidget):
    files_dropped=Signal(list)
    def __init__(self):
        super().__init__(); self.setAcceptDrops(True); self.setMinimumHeight(160); self.addItem("Drop files here")
    def dragEnterEvent(self,event):
        if event.mimeData().hasUrls(): event.acceptProposedAction()
    def dropEvent(self,event):
        paths=[u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths); event.acceptProposedAction()

class MainWindow(QMainWindow):
    rx=Signal(str,int,int); tx=Signal(int,int); status=Signal(str); done=Signal(str)
    def __init__(self):
        super().__init__(); self.setWindowTitle("DirectDrop"); self.resize(760,560); self.server=None
        self.receive_dir=Path.home()/"DirectDrop"/"Received"; self.receive_dir.mkdir(parents=True,exist_ok=True)
        root=QWidget(); box=QVBoxLayout(root)
        t=QLabel("DirectDrop"); t.setStyleSheet("font-size:28px;font-weight:700;"); box.addWidget(t)
        box.addWidget(QLabel("Offline laptop-to-laptop file transfer. Transport is independent of the physical link."))
        row=QHBoxLayout(); row.addWidget(QLabel("Listen port"))
        self.listen=QLineEdit("8765"); self.listen.setMaximumWidth(90); row.addWidget(self.listen)
        self.start_btn=QPushButton("Start Receiver"); self.start_btn.clicked.connect(self.start_receiver); row.addWidget(self.start_btn); row.addStretch(); box.addLayout(row)
        row2=QHBoxLayout(); row2.addWidget(QLabel("Peer IP"))
        self.peer=QLineEdit(); self.peer.setPlaceholderText("192.168.x.x"); row2.addWidget(self.peer)
        row2.addWidget(QLabel("Port")); self.peer_port=QLineEdit("8765"); self.peer_port.setMaximumWidth(90); row2.addWidget(self.peer_port)
        choose=QPushButton("Choose Files"); choose.clicked.connect(self.choose); row2.addWidget(choose); box.addLayout(row2)
        self.drop=DropArea(); self.drop.files_dropped.connect(self.send_paths); box.addWidget(self.drop)
        self.progress=QProgressBar(); box.addWidget(self.progress)
        self.label=QLabel("Receiver not started"); box.addWidget(self.label)
        box.addWidget(QLabel("Received files: "+str(self.receive_dir)))
        self.rx.connect(self.on_rx); self.tx.connect(self.on_tx); self.status.connect(self.label.setText)
        self.done.connect(self.on_done); self.setCentralWidget(root)

    def start_receiver(self):
        try:
            port=int(self.listen.text()); assert 1<=port<=65535
            self.server=start_receiver("0.0.0.0",port,self.receive_dir,on_progress=lambda n,r,t:self.rx.emit(n,r,t),on_complete=lambda p:self.done.emit(str(p)))
            self.start_btn.setEnabled(False); self.label.setText(f"Listening on {port}")
        except Exception as e:
            QMessageBox.critical(self,"Receiver error",str(e))

    def choose(self):
        files,_=QFileDialog.getOpenFileNames(self,"Select files"); self.send_paths(files)

    def send_paths(self,paths):
        host=self.peer.text().strip()
        try:
            port=int(self.peer_port.text()); assert 1<=port<=65535
        except Exception:
            QMessageBox.warning(self,"Invalid port","Enter a valid port."); return
        if not host:
            QMessageBox.warning(self,"Peer IP required","Enter the receiving laptop IP."); return
        for raw in paths:
            p=Path(raw)
            if p.is_file():
                threading.Thread(target=self._send,args=(host,port,p),daemon=True).start()

    def _send(self,host,port,path):
        try:
            self.status.emit("Sending: "+path.name)
            send_file(host,port,path,lambda s,t:self.tx.emit(s,t))
            self.status.emit("Sent: "+path.name)
        except Exception as e:
            self.status.emit(f"Send failed: {path.name} — {e}")

    def on_rx(self,name,received,total):
        self.progress.setValue(int(received*100/total) if total else 0); self.label.setText("Receiving: "+name)

    def on_tx(self,sent,total):
        self.progress.setValue(int(sent*100/total) if total else 0)

    def on_done(self,path):
        self.progress.setValue(100); self.label.setText("Received: "+Path(path).name)

def run():
    app=QApplication([]); w=MainWindow(); w.show(); app.exec()
