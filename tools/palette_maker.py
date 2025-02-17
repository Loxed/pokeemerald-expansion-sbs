from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QFileDialog,
                            QVBoxLayout, QHBoxLayout, QGraphicsScene, QGraphicsView,
                            QGraphicsRectItem, QGraphicsTextItem)
from PyQt5.QtGui import QColor, QFont, QFontMetrics, QPainter, QPen, QClipboard
from PyQt5.QtCore import Qt, QSize
from PIL import Image
import sys

def set_dark_theme(app):
    app.setStyle("Fusion")
    palette = app.palette()
    dark = QColor(45, 45, 45)
    text = QColor(220, 220, 220)
    highlight = QColor(42, 130, 218)
    
    palette.setColor(palette.Window, dark)
    palette.setColor(palette.WindowText, text)
    palette.setColor(palette.Base, QColor(30, 30, 30))
    palette.setColor(palette.AlternateBase, dark)
    palette.setColor(palette.ToolTipBase, dark)
    palette.setColor(palette.ToolTipText, text)
    palette.setColor(palette.Text, text)
    palette.setColor(palette.Button, dark)
    palette.setColor(palette.ButtonText, text)
    palette.setColor(palette.Highlight, highlight)
    palette.setColor(palette.HighlightedText, Qt.white)
    app.setPalette(palette)

class ColorExtractor(QWidget):
    def __init__(self):
        super().__init__()
        self.colors_list = []
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Porypalette")
        self.setMinimumSize(QSize(800, 600))
        
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Top buttons layout
        btn_layout = QHBoxLayout()
        self.btn_select = QPushButton("📁 Open Image")
        self.btn_copy = QPushButton("📋 Copy Colors")
        self.btn_select.setFixedHeight(40)
        self.btn_copy.setFixedHeight(40)
        self.btn_select.clicked.connect(self.extract_colors)
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        
        btn_layout.addWidget(self.btn_select)
        btn_layout.addWidget(self.btn_copy)
        layout.addLayout(btn_layout)
        
        # Color view
        self.color_view = QGraphicsView()
        self.color_scene = QGraphicsScene()
        self.color_view.setScene(self.color_scene)
        self.color_view.setRenderHints(QPainter.Antialiasing)
        
        layout.addWidget(self.color_view)
        self.setLayout(layout)

    def extract_colors(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        
        if not file_path:
            return
        
        try:
            with Image.open(file_path) as img:
                image = img.convert("RGB")
        except Exception as e:
            print(f"Error opening image: {e}")
            return
        
        self.color_scene.clear()
        self.colors_list = []
        seen_colors = set()
        
        box_size = 24
        padding = 15
        x_offset = padding
        y_offset = padding
        column_width = 250
        max_height = 600
        
        font = QFont("Consolas" if sys.platform == "win32" else "Monospace", 10)
        fm = QFontMetrics(font)
        text_height = fm.height()

        for pixel in image.getdata():
            if pixel not in seen_colors:
                seen_colors.add(pixel)
                self.colors_list.append(pixel)
                
                # Create color square
                rect = QGraphicsRectItem(x_offset, y_offset, box_size, box_size)
                rect.setBrush(QColor(*pixel))
                rect.setPen(QPen(Qt.NoPen))
                self.color_scene.addItem(rect)
                
                # Create text label
                text = QGraphicsTextItem(
                    f"#{pixel[0]:02X}{pixel[1]:02X}{pixel[2]:02X}\n"
                    f"R:{pixel[0]:03} G:{pixel[1]:03} B:{pixel[2]:03}"
                )
                text.setFont(font)
                text.setDefaultTextColor(Qt.white)
                text.setPos(x_offset + box_size + 10, 
                           y_offset + (box_size - text_height * 2) / 2)
                self.color_scene.addItem(text)
                
                # Update layout position
                y_offset += box_size + padding
                if y_offset + box_size > max_height:
                    y_offset = padding
                    x_offset += column_width

        self.color_scene.setSceneRect(0, 0, x_offset + column_width, max_height)

    def copy_to_clipboard(self):
        if not self.colors_list:
            return
        
        # Format colors as XXX XXX XXX with zero padding
        clipboard_text = "\n".join(
            f"{r:03} {g:03} {b:03}"
            for r, g, b in self.colors_list
        )
        
        QApplication.clipboard().setText(clipboard_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_theme(app)
    
    window = ColorExtractor()
    window.show()
    sys.exit(app.exec_())

