import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QScrollArea,
    QLabel,
    QFrame,
    QMessageBox,
    QSpinBox,
)
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPixmap, QPainter, QPen, QImage, QCursor
from PIL import Image


class ImageLabel(QLabel):
    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.original_image = QPixmap(image_path)
        self.crop_size = 512
        self.crop_x = 0
        self.crop_y = 0

        # Mouse tracking for drag
        self.setMouseTracking(True)
        self.dragging = False
        self.start_pos = None
        self.start_crop_x = 0
        self.start_crop_y = 0

        # Scale image to fit window while maintaining aspect ratio
        self.display_image = self.original_image.scaled(
            600, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        # Calculate scaling factor
        self.scale_factor = self.display_image.width() / self.original_image.width()

        # Set initial crop position to center
        if self.original_image.width() >= self.crop_size:
            self.crop_x = (self.original_image.width() - self.crop_size) // 2
        if self.original_image.height() >= self.crop_size:
            self.crop_y = (self.original_image.height() - self.crop_size) // 2

        self.update_display()
        self.setFrameStyle(QFrame.Box)
        self.setAlignment(Qt.AlignCenter)

    def update_display(self):
        # Create a copy of the display image
        display_with_crop = self.display_image.copy()

        # Draw red rectangle for crop area
        painter = QPainter(display_with_crop)
        pen = QPen(Qt.red, 3)
        painter.setPen(pen)

        # Calculate scaled crop rectangle
        scaled_x = int(self.crop_x * self.scale_factor)
        scaled_y = int(self.crop_y * self.scale_factor)
        scaled_size = int(self.crop_size * self.scale_factor)

        painter.drawRect(scaled_x, scaled_y, scaled_size, scaled_size)

        painter.end()

        self.setPixmap(display_with_crop)

    def is_inside_crop_box(self, pos):
        """Check if position is inside the crop box"""
        # Get the actual image position within the label widget
        label_rect = self.rect()
        pixmap_rect = self.pixmap().rect()

        # Calculate offset to center image in label
        x_offset = (label_rect.width() - pixmap_rect.width()) // 2
        y_offset = (label_rect.height() - pixmap_rect.height()) // 2

        # Calculate scaled crop box position with offset
        scaled_x = int(self.crop_x * self.scale_factor) + x_offset
        scaled_y = int(self.crop_y * self.scale_factor) + y_offset
        scaled_size = int(self.crop_size * self.scale_factor)

        return (
            scaled_x <= pos.x() <= scaled_x + scaled_size
            and scaled_y <= pos.y() <= scaled_y + scaled_size
        )

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()
            self.start_crop_x = self.crop_x
            self.start_crop_y = self.crop_y

            if self.is_inside_crop_box(event.pos()):
                # Start dragging the crop box
                self.dragging = True
            else:
                # Click outside box - move box to center on click
                # Get the actual image position within the label widget
                label_rect = self.rect()
                pixmap_rect = self.pixmap().rect()

                # Calculate offset to center image in label
                x_offset = (label_rect.width() - pixmap_rect.width()) // 2
                y_offset = (label_rect.height() - pixmap_rect.height()) // 2

                # Adjust click position to be relative to the image, not the widget
                adjusted_x = event.x() - x_offset
                adjusted_y = event.y() - y_offset

                # Convert to original image coordinates
                x = int(adjusted_x / self.scale_factor)
                y = int(adjusted_y / self.scale_factor)

                # Center crop box on click position
                self.crop_x = x - self.crop_size // 2
                self.crop_y = y - self.crop_size // 2

                # Ensure crop box stays within image bounds
                self.crop_x = max(
                    0, min(self.crop_x, self.original_image.width() - self.crop_size)
                )
                self.crop_y = max(
                    0, min(self.crop_y, self.original_image.height() - self.crop_size)
                )

                self.update_display()

    def mouseMoveEvent(self, event):
        if self.dragging:
            # Calculate movement
            delta = event.pos() - self.start_pos
            delta_x = int(delta.x() / self.scale_factor)
            delta_y = int(delta.y() / self.scale_factor)

            # Move the crop box
            self.crop_x = self.start_crop_x + delta_x
            self.crop_y = self.start_crop_y + delta_y

            # Ensure crop box stays within image bounds
            self.crop_x = max(
                0, min(self.crop_x, self.original_image.width() - self.crop_size)
            )
            self.crop_y = max(
                0, min(self.crop_y, self.original_image.height() - self.crop_size)
            )

            self.update_display()

        else:
            # Update cursor based on what's under mouse
            if self.is_inside_crop_box(event.pos()):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            # Update cursor
            if self.is_inside_crop_box(event.pos()):
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.ArrowCursor)

    def get_crop_coordinates(self):
        return (
            self.crop_x,
            self.crop_y,
            self.crop_x + self.crop_size,
            self.crop_y + self.crop_size,
        )


class ImageCropperWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.image_labels = []
        self.image_directory = ""
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Image Cropper Tool")
        self.setGeometry(100, 100, 800, 900)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # Directory selection button
        self.select_dir_btn = QPushButton("Select Image Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        control_layout.addWidget(self.select_dir_btn)

        # Crop all button
        self.crop_all_btn = QPushButton("Crop All Images")
        self.crop_all_btn.clicked.connect(self.crop_all_images)
        self.crop_all_btn.setEnabled(False)
        control_layout.addWidget(self.crop_all_btn)

        # Crop size spinner
        control_layout.addWidget(QLabel("Crop Size:"))
        self.crop_size_spinner = QSpinBox()
        self.crop_size_spinner.setMinimum(32)  # Allow smaller crops
        self.crop_size_spinner.setMaximum(4096)  # Allow larger crops
        self.crop_size_spinner.setValue(512)
        self.crop_size_spinner.setSingleStep(8)
        self.crop_size_spinner.valueChanged.connect(self.update_crop_size)
        control_layout.addWidget(self.crop_size_spinner)

        # Resize output spinner
        control_layout.addWidget(QLabel("Resize to:"))
        self.resize_output_spinner = QSpinBox()
        self.resize_output_spinner.setMinimum(0)  # 0 means no resize
        self.resize_output_spinner.setMaximum(4096)
        self.resize_output_spinner.setValue(0)  # Default: no resize
        self.resize_output_spinner.setSingleStep(8)
        control_layout.addWidget(self.resize_output_spinner)
        control_layout.addWidget(QLabel("(0 = no resize)"))

        control_layout.addStretch()
        main_layout.addWidget(control_panel)

        # Create scroll area for images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Create container widget for images
        self.image_container = QWidget()
        self.image_layout = QVBoxLayout(self.image_container)
        self.image_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.image_container)
        main_layout.addWidget(self.scroll_area)

        # Status label
        self.status_label = QLabel("Select a directory to load images")
        main_layout.addWidget(self.status_label)

    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Image Directory", os.path.expanduser("~")
        )

        if directory:
            self.image_directory = directory
            self.load_images()

    def load_images(self):
        # Clear existing images
        for label in self.image_labels:
            label.deleteLater()
        self.image_labels.clear()

        # Get all image files in directory
        supported_formats = (".png", ".jpg", ".jpeg", ".bmp", ".gif")
        image_files = []

        for file in os.listdir(self.image_directory):
            if file.lower().endswith(supported_formats):
                image_files.append(os.path.join(self.image_directory, file))

        if not image_files:
            self.status_label.setText("No images found in selected directory")
            self.crop_all_btn.setEnabled(False)
            return

        # Load and display images
        for image_path in sorted(image_files):
            try:
                image_label = ImageLabel(image_path)
                image_label.crop_size = self.crop_size_spinner.value()
                self.image_layout.addWidget(image_label)
                self.image_labels.append(image_label)

                # Add filename label
                filename_label = QLabel(os.path.basename(image_path))
                filename_label.setAlignment(Qt.AlignCenter)
                self.image_layout.addWidget(filename_label)

            except Exception as e:
                print(f"Error loading {image_path}: {e}")

        self.status_label.setText(f"Loaded {len(self.image_labels)} images")
        self.crop_all_btn.setEnabled(True)

    def update_crop_size(self, value):
        for label in self.image_labels:
            label.crop_size = value
            # Recenter crop box
            if label.original_image.width() >= value:
                label.crop_x = (label.original_image.width() - value) // 2
            else:
                label.crop_x = 0

            if label.original_image.height() >= value:
                label.crop_y = (label.original_image.height() - value) // 2
            else:
                label.crop_y = 0

            label.update_display()

    def crop_all_images(self):
        if not self.image_labels:
            return

        # Create output directory
        output_dir = os.path.join(self.image_directory, "cropped")
        os.makedirs(output_dir, exist_ok=True)

        success_count = 0

        for label in self.image_labels:
            try:
                # Get crop coordinates
                x1, y1, x2, y2 = label.get_crop_coordinates()

                # Open and crop image
                image = Image.open(label.image_path)

                # Ensure crop box is within image bounds
                x2 = min(x2, image.width)
                y2 = min(y2, image.height)

                cropped = image.crop((x1, y1, x2, y2))

                # Resize if requested
                resize_value = self.resize_output_spinner.value()
                if resize_value > 0:
                    cropped = cropped.resize(
                        (resize_value, resize_value), Image.LANCZOS
                    )

                # Save cropped image
                filename = os.path.basename(label.image_path)
                output_path = os.path.join(output_dir, f"cropped_{filename}")
                cropped.save(output_path)

                success_count += 1

            except Exception as e:
                print(f"Error cropping {label.image_path}: {e}")

        self.status_label.setText(f"Cropped {success_count} images to {output_dir}")
        QMessageBox.information(
            self,
            "Cropping Complete",
            f"Successfully cropped {success_count} images.\nOutput directory: {output_dir}",
        )


def main():
    app = QApplication(sys.argv)
    window = ImageCropperWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
