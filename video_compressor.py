import sys
import os
import moviepy.editor as mp
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QComboBox,
)
import subprocess
import dotenv

dotenv.load_dotenv()

DEFAULT_DIRECTORY = os.getenv("DEFAULT_DIRECTORY", "")


def convert_seconds_to_mmss(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"


def convert_mmss_to_seconds(mmss):
    try:
        minutes, seconds = map(int, mmss.split(":"))
        return minutes * 60 + seconds
    except ValueError:
        return 0


class VideoCompressorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Video Compressor")

        main_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        format_layout = QHBoxLayout()
        compression_layout = QHBoxLayout()
        settings_layout = QVBoxLayout()
        trim_layout = QHBoxLayout()
        gif_options_layout = QVBoxLayout()

        self.file_label = QLabel("No file selected")
        select_file_button = QPushButton("Choose video file")
        select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(select_file_button)
        file_layout.addWidget(self.file_label)

        self.format_group = {"mp4": QRadioButton(".mp4"), "gif": QRadioButton(".gif")}
        self.format_group["mp4"].setChecked(True)
        for format_button in self.format_group.values():
            format_button.toggled.connect(self.update_format_options)
            format_layout.addWidget(format_button)

        self.size_label = QLabel("Compress to:")
        self.size_combo = QComboBox()
        self.size_combo.addItems(["8MB", "10MB", "25MB", "Other"])
        self.size_combo.setCurrentText("10MB")
        self.size_combo.currentIndexChanged.connect(self.toggle_custom_size_field)
        compression_layout.addWidget(self.size_label)
        compression_layout.addWidget(self.size_combo)

        self.codec_label = QLabel("Select Codec:")
        self.codec_combo = QComboBox()
        self.codec_combo.addItems(["h264_nvenc", "libx264", "libx265"])
        settings_layout.addWidget(self.codec_label)
        settings_layout.addWidget(self.codec_combo)

        self.preset_label = QLabel("Select Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(["fast", "medium", "slow", "ultrafast", "superfast", "veryfast", "faster", "slower", "veryslow"])
        settings_layout.addWidget(self.preset_label)
        settings_layout.addWidget(self.preset_combo)

        self.custom_size_input = QLineEdit()
        self.custom_size_input.setPlaceholderText("Enter size in MB")
        self.custom_size_input.hide()
        compression_layout.addWidget(self.custom_size_input)

        self.start_time_entry = QLineEdit("00:00")
        self.end_time_entry = QLineEdit("End")
        trim_layout.addWidget(QLabel("Trim:"))
        trim_layout.addWidget(self.start_time_entry)
        trim_layout.addWidget(self.end_time_entry)

        self.gif_fps_label = QLabel("GIF FPS:")
        self.gif_fps_entry = QLineEdit("25")
        self.gif_res_label = QLabel("GIF Resolution (Vertical):")
        self.gif_res_entry = QComboBox()
        self.gif_res_entry.addItems(["240", "320", "480", "720", "1080", "Other"])
        self.gif_res_entry.currentIndexChanged.connect(
            self.toggle_custom_resolution_field
        )
        gif_options_layout.addWidget(self.gif_fps_label)
        gif_options_layout.addWidget(self.gif_fps_entry)
        gif_options_layout.addWidget(self.gif_res_label)
        gif_options_layout.addWidget(self.gif_res_entry)

        self.custom_res_input = QLineEdit()
        self.custom_res_input.setPlaceholderText("Enter custom vertical resolution")
        self.custom_res_input.hide()
        gif_options_layout.addWidget(self.custom_res_input)

        compress_button = QPushButton("Compress")
        compress_button.clicked.connect(self.compress_video)

        self.status_label = QLabel("Status: Waiting for input.")

        main_layout.addLayout(file_layout)
        main_layout.addLayout(format_layout)
        main_layout.addLayout(compression_layout)
        main_layout.addLayout(settings_layout)
        main_layout.addLayout(trim_layout)
        main_layout.addLayout(gif_options_layout)
        main_layout.addWidget(compress_button)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        self.update_format_options()

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            DEFAULT_DIRECTORY,
            "Video Files (*.mp4 *.avi *.mov *.mkv)",
            options=options,
        )
        if file_path:
            self.file_label.setText(file_path)
            try:
                video = mp.VideoFileClip(file_path)
                duration = video.duration
                self.end_time_entry.setText(convert_seconds_to_mmss(duration))
                self.status_label.setText(
                    f"Video loaded. Duration: {convert_seconds_to_mmss(duration)}"
                )
                print(f"Loaded video: {file_path}, duration: {duration}s")
            except Exception as e:
                self.show_error_message(f"Error loading video: {e}")
            finally:
                video.close()

    def toggle_custom_size_field(self):
        if self.size_combo.currentText() == "Other":
            self.custom_size_input.show()
        else:
            self.custom_size_input.hide()

    def toggle_custom_resolution_field(self):
        if self.gif_res_entry.currentText() == "Other":
            self.custom_res_input.show()
        else:
            self.custom_res_input.hide()

    def update_format_options(self):
        selected_format = "mp4" if self.format_group["mp4"].isChecked() else "gif"
        if selected_format == "mp4":
            self.size_label.show()
            self.size_combo.show()
            if self.size_combo.currentText() == "Other":
                self.custom_size_input.show()
            else:
                self.custom_size_input.hide()

            self.codec_label.show()
            self.codec_combo.show()
            self.preset_label.show()
            self.preset_combo.show()
            self.gif_fps_label.hide()
            self.gif_fps_entry.hide()
            self.gif_res_label.hide()
            self.gif_res_entry.hide()
            self.custom_res_input.hide()

        else:
            self.size_label.hide()
            self.size_combo.hide()
            self.codec_label.hide()
            self.codec_combo.hide()
            self.preset_label.hide()
            self.preset_combo.hide()
            self.custom_size_input.hide()
            self.gif_fps_label.show()
            self.gif_fps_entry.show()
            self.gif_res_label.show()
            self.gif_res_entry.show()
            if self.gif_res_entry.currentText() == "Other":
                self.custom_res_input.show()

    def compress_video(self):
        file_path = self.file_label.text()
        if not os.path.isfile(file_path):
            self.status_label.setText("Please select a valid video file.")
            return

        if self.format_group["mp4"].isChecked():
            selected_size = self.size_combo.currentText()
            if selected_size == "Other":
                try:
                    target_size_mb = int(self.custom_size_input.text())
                except ValueError:
                    self.show_error_message("Invalid custom size.")
                    return
            else:
                target_size_mb = int(selected_size[:-2])

            print(f"Target MP4 size: {target_size_mb}MB")
        else:
            fps = int(self.gif_fps_entry.text())
            selected_res = self.gif_res_entry.currentText()
            if selected_res == "Other":
                try:
                    vertical_resolution = int(self.custom_res_input.text())
                except ValueError:
                    self.show_error_message("Invalid custom resolution.")
                    return
            else:
                vertical_resolution = int(selected_res)

            print(f"Target GIF resolution: {vertical_resolution}px, FPS: {fps}")

        start_time = self.start_time_entry.text()
        end_time = self.end_time_entry.text()

        start_seconds = convert_mmss_to_seconds(start_time)
        end_seconds = convert_mmss_to_seconds(end_time)

        try:
            video = mp.VideoFileClip(file_path)
            video = video.subclip(start_seconds, end_seconds)

            output_format = "mp4" if self.format_group["mp4"].isChecked() else "gif"
            output_file = (
                os.path.splitext(file_path)[0] + "_compressed." + output_format
            )

            if output_format == "mp4":
                video = video.resize(newsize=(1280, 720))
                fps = 30

                audio_bitrate_kbps = 128

                video_duration = end_seconds - start_seconds
                total_bitrate = (target_size_mb * 8 * 1024 * 1024) / (1.073741824 * video_duration)

                target_bitrate_kbps = int((total_bitrate / 1000) - audio_bitrate_kbps)

                codec = self.codec_combo.currentText()
                preset = self.preset_combo.currentText()

                self.status_label.setText(f"Compressing MP4 to {target_size_mb}MB...")
                print(f"Calculated total bitrate: {int(total_bitrate / 1000)} kbps")
                print(f"Video bitrate: {target_bitrate_kbps} kbps, Audio bitrate: {audio_bitrate_kbps} kbps")
                print(f"Codec: {codec}, Preset: {preset}")

                video.write_videofile(
                    output_file,
                    fps=fps,
                    codec=codec,
                    bitrate=f"{target_bitrate_kbps}k",
                    audio_bitrate=f"{audio_bitrate_kbps}k",
                    preset=preset,
                    threads=6,
                )

            else:
                width = int(vertical_resolution * 16 / 9)
                video = video.resize(newsize=(width, vertical_resolution))

                self.status_label.setText(f"Compressing GIF at {fps} FPS...")
                print(f"Resizing video to {width}x{vertical_resolution}px for GIF")

                video.write_gif(output_file, fps=fps, program="ffmpeg")

            self.status_label.setText(f"Compression completed: {output_file}")
            print(f"Compression completed: {output_file}")

            subprocess.Popen(f'explorer /select,"{output_file.replace("/", "\\")}"')
        except Exception as e:
            self.show_error_message(f"Error: {e}")
            print(f"Error during compression: {e}")

            if os.path.isfile(output_file):
                print(f"Deleting output file: {output_file}")
                os.remove(output_file)
            for file in os.listdir(os.getcwd()):
                if file.endswith("TEMP_MPY_wvf_snd.mp3"):
                    print(f"Deleting temporary audio file: {file}")
                    os.remove(file)
        finally:
            video.close()


    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoCompressorApp()
    window.show()
    sys.exit(app.exec_())
