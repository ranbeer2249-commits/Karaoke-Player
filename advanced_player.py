import sys
import os
import numpy as np
import threading
import time
import pyaudio
import wave
import librosa
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QFileDialog, QSlider, QLabel, 
                             QFrame, QSplitter, QProgressBar)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
import queue

class AudioStream:
    """Class to handle individual audio stream playback"""
    
    def __init__(self, audio_data, sample_rate, volume=1.0):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        self.volume = volume
        self.playing = False
        self.paused = False
        self.current_position = 0
        self.audio_queue = queue.Queue()
        self.p = pyaudio.PyAudio()
        
    def start_playback(self):
        self.playing = True
        self.paused = False
        self.current_position = 0
        
        def callback(in_data, frame_count, time_info, status):
            if not self.playing or self.paused:
                return (b'\x00' * frame_count * 4, pyaudio.paComplete)
            
            if self.current_position >= len(self.audio_data):
                self.playing = False
                return (b'\x00' * frame_count * 4, pyaudio.paComplete)
            
            # Get audio data for this frame
            end_pos = min(self.current_position + frame_count, len(self.audio_data))
            frame_data = self.audio_data[self.current_position:end_pos]
            
            # Apply volume
            frame_data = frame_data * self.volume
            
            # Convert to bytes
            if len(frame_data) < frame_count:
                # Pad with silence if needed
                frame_data = np.pad(frame_data, (0, frame_count - len(frame_data)))
            
            self.current_position += frame_count
            
            return (frame_data.astype(np.float32).tobytes(), pyaudio.paContinue)
        
        self.stream = self.p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=self.sample_rate,
            output=True,
            stream_callback=callback,
            frames_per_buffer=1024
        )
        self.stream.start_stream()
    
    def pause(self):
        self.paused = True
    
    def resume(self):
        self.paused = False
    
    def stop(self):
        self.playing = False
        if hasattr(self, 'stream'):
            self.stream.stop_stream()
            self.stream.close()
    
    def set_volume(self, volume):
        self.volume = volume
    
    def get_position(self):
        return self.current_position / self.sample_rate
    
    def get_duration(self):
        return len(self.audio_data) / self.sample_rate

class AudioProcessor(QThread):
    """Thread for processing audio files and generating waveforms"""
    waveform_ready = pyqtSignal(object, object, str)  # y, sr, filename
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        
    def run(self):
        try:
            # Load audio file
            y, sr = librosa.load(self.file_path, sr=None)
            self.waveform_ready.emit(y, sr, self.file_path)
        except Exception as e:
            print(f"Error loading audio: {e}")

class WaveformWidget(QWidget):
    """Custom widget for displaying audio waveforms"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.audio_data = None
        self.sample_rate = None
        self.current_position = 0
        self.duration = 0
        self.setMinimumHeight(150)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")
        
    def set_audio_data(self, audio_data, sample_rate):
        self.audio_data = audio_data
        self.sample_rate = sample_rate
        if audio_data is not None:
            self.duration = len(audio_data) / sample_rate
        self.update()
        
    def set_position(self, position):
        self.current_position = position
        self.update()
        
    def paintEvent(self, event):
        if self.audio_data is None:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Set up colors
        background_color = QColor(43, 43, 43)  # Dark gray
        waveform_color = QColor(0, 255, 127)   # Green
        position_color = QColor(255, 255, 0)   # Yellow
        
        # Fill background
        painter.fillRect(self.rect(), background_color)
        
        # Calculate dimensions
        width = self.width()
        height = self.height()
        
        # Downsample for display
        downsample_factor = max(1, len(self.audio_data) // width)
        display_data = self.audio_data[::downsample_factor]
        
        # Normalize data
        if len(display_data) > 0:
            max_val = np.max(np.abs(display_data))
            if max_val > 0:
                display_data = display_data / max_val
        
        # Draw waveform
        painter.setPen(QPen(waveform_color, 1))
        
        for i in range(min(len(display_data), width)):
            x = i
            y_center = height // 2
            amplitude = int(display_data[i] * (height // 2 - 10))
            painter.drawLine(x, y_center - amplitude, x, y_center + amplitude)
        
        # Draw position indicator
        if self.duration > 0:
            position_x = int((self.current_position / self.duration) * width)
            painter.setPen(QPen(position_color, 2))
            painter.drawLine(position_x, 0, position_x, height)

class AdvancedMP3Player(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Dual MP3 Player with Waveform")
        self.setGeometry(100, 100, 1200, 800)
        
        # Audio data storage
        self.track1_data = None
        self.track1_sr = None
        self.track1_path = None
        self.track2_data = None
        self.track2_sr = None
        self.track2_path = None
        
        # Audio streams
        self.track1_stream = None
        self.track2_stream = None
        
        # Audio processing threads
        self.track1_processor = None
        self.track2_processor = None
        
        # Setup UI
        self.setup_ui()
        
        # Timer for updating position
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.timer.start(100)  # Update every 100ms
        
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for top and bottom sections
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Top section - Track 1
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        
        # Track 1 controls
        track1_controls = QHBoxLayout()
        
        self.track1_load_btn = QPushButton("Load Track 1")
        self.track1_load_btn.clicked.connect(lambda: self.load_track(1))
        track1_controls.addWidget(self.track1_load_btn)
        
        self.track1_play_btn = QPushButton("Play")
        self.track1_play_btn.clicked.connect(lambda: self.play_track(1))
        self.track1_play_btn.setEnabled(False)
        track1_controls.addWidget(self.track1_play_btn)
        
        self.track1_pause_btn = QPushButton("Pause")
        self.track1_pause_btn.clicked.connect(lambda: self.pause_track(1))
        self.track1_pause_btn.setEnabled(False)
        track1_controls.addWidget(self.track1_pause_btn)
        
        self.track1_stop_btn = QPushButton("Stop")
        self.track1_stop_btn.clicked.connect(lambda: self.stop_track(1))
        self.track1_stop_btn.setEnabled(False)
        track1_controls.addWidget(self.track1_stop_btn)
        
        track1_controls.addStretch()
        
        # Track 1 volume control
        track1_controls.addWidget(QLabel("Volume:"))
        self.track1_volume_slider = QSlider(Qt.Horizontal)
        self.track1_volume_slider.setRange(0, 100)
        self.track1_volume_slider.setValue(70)
        self.track1_volume_slider.valueChanged.connect(lambda: self.set_volume(1))
        track1_controls.addWidget(self.track1_volume_slider)
        
        top_layout.addLayout(track1_controls)
        
        # Track 1 waveform
        self.track1_waveform = WaveformWidget()
        top_layout.addWidget(self.track1_waveform)
        
        # Track 1 progress
        track1_progress_layout = QHBoxLayout()
        self.track1_progress_bar = QProgressBar()
        self.track1_progress_bar.setRange(0, 100)
        track1_progress_layout.addWidget(self.track1_progress_bar)
        
        self.track1_time_label = QLabel("00:00 / 00:00")
        track1_progress_layout.addWidget(self.track1_time_label)
        
        top_layout.addLayout(track1_progress_layout)
        
        # Bottom section - Track 2
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        
        # Track 2 controls
        track2_controls = QHBoxLayout()
        
        self.track2_load_btn = QPushButton("Load Track 2")
        self.track2_load_btn.clicked.connect(lambda: self.load_track(2))
        track2_controls.addWidget(self.track2_load_btn)
        
        self.track2_play_btn = QPushButton("Play")
        self.track2_play_btn.clicked.connect(lambda: self.play_track(2))
        self.track2_play_btn.setEnabled(False)
        track2_controls.addWidget(self.track2_play_btn)
        
        self.track2_pause_btn = QPushButton("Pause")
        self.track2_pause_btn.clicked.connect(lambda: self.pause_track(2))
        self.track2_pause_btn.setEnabled(False)
        track2_controls.addWidget(self.track2_pause_btn)
        
        self.track2_stop_btn = QPushButton("Stop")
        self.track2_stop_btn.clicked.connect(lambda: self.stop_track(2))
        self.track2_stop_btn.setEnabled(False)
        track2_controls.addWidget(self.track2_stop_btn)
        
        track2_controls.addStretch()
        
        # Track 2 volume control
        track2_controls.addWidget(QLabel("Volume:"))
        self.track2_volume_slider = QSlider(Qt.Horizontal)
        self.track2_volume_slider.setRange(0, 100)
        self.track2_volume_slider.setValue(70)
        self.track2_volume_slider.valueChanged.connect(lambda: self.set_volume(2))
        track2_controls.addWidget(self.track2_volume_slider)
        
        bottom_layout.addLayout(track2_controls)
        
        # Track 2 waveform
        self.track2_waveform = WaveformWidget()
        bottom_layout.addWidget(self.track2_waveform)
        
        # Track 2 progress
        track2_progress_layout = QHBoxLayout()
        self.track2_progress_bar = QProgressBar()
        self.track2_progress_bar.setRange(0, 100)
        track2_progress_layout.addWidget(self.track2_progress_bar)
        
        self.track2_time_label = QLabel("00:00 / 00:00")
        track2_progress_layout.addWidget(self.track2_time_label)
        
        bottom_layout.addLayout(track2_progress_layout)
        
        # Add widgets to splitter
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setSizes([400, 400])  # Equal split
        
        # Global controls
        global_controls = QHBoxLayout()
        
        self.play_all_btn = QPushButton("Play All")
        self.play_all_btn.clicked.connect(self.play_all)
        global_controls.addWidget(self.play_all_btn)
        
        self.stop_all_btn = QPushButton("Stop All")
        self.stop_all_btn.clicked.connect(self.stop_all)
        global_controls.addWidget(self.stop_all_btn)
        
        global_controls.addStretch()
        
        main_layout.addLayout(global_controls)
        
        # Set styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #3c3c3c;
                color: white;
            }
            QPushButton {
                background-color: #555555;
                border: 1px solid #777777;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666666;
            }
            QPushButton:pressed {
                background-color: #444444;
            }
            QPushButton:disabled {
                background-color: #333333;
                color: #666666;
            }
            QSlider::groove:horizontal {
                border: 1px solid #777777;
                height: 8px;
                background: #555555;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                border: 1px solid #777777;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
            QProgressBar {
                border: 1px solid #777777;
                border-radius: 4px;
                text-align: center;
                background-color: #555555;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
            QLabel {
                color: white;
            }
        """)
        
    def load_track(self, track_num):
        file_path, _ = QFileDialog.getOpenFileName(
            self, f"Load Track {track_num}", "", "Audio Files (*.mp3 *.wav *.flac *.ogg)"
        )
        
        if file_path:
            if track_num == 1:
                self.track1_path = file_path
                self.track1_processor = AudioProcessor(file_path)
                self.track1_processor.waveform_ready.connect(
                    lambda y, sr, path: self.on_track_loaded(1, y, sr, path)
                )
                self.track1_processor.start()
            else:
                self.track2_path = file_path
                self.track2_processor = AudioProcessor(file_path)
                self.track2_processor.waveform_ready.connect(
                    lambda y, sr, path: self.on_track_loaded(2, y, sr, path)
                )
                self.track2_processor.start()
    
    def on_track_loaded(self, track_num, audio_data, sample_rate, file_path):
        if track_num == 1:
            self.track1_data = audio_data
            self.track1_sr = sample_rate
            self.track1_waveform.set_audio_data(audio_data, sample_rate)
            self.track1_play_btn.setEnabled(True)
            self.track1_pause_btn.setEnabled(True)
            self.track1_stop_btn.setEnabled(True)
        else:
            self.track2_data = audio_data
            self.track2_sr = sample_rate
            self.track2_waveform.set_audio_data(audio_data, sample_rate)
            self.track2_play_btn.setEnabled(True)
            self.track2_pause_btn.setEnabled(True)
            self.track2_stop_btn.setEnabled(True)
    
    def play_track(self, track_num):
        if track_num == 1 and self.track1_data is not None:
            if self.track1_stream is None:
                volume = self.track1_volume_slider.value() / 100.0
                self.track1_stream = AudioStream(self.track1_data, self.track1_sr, volume)
            self.track1_stream.start_playback()
        elif track_num == 2 and self.track2_data is not None:
            if self.track2_stream is None:
                volume = self.track2_volume_slider.value() / 100.0
                self.track2_stream = AudioStream(self.track2_data, self.track2_sr, volume)
            self.track2_stream.start_playback()
    
    def pause_track(self, track_num):
        if track_num == 1 and self.track1_stream:
            self.track1_stream.pause()
        elif track_num == 2 and self.track2_stream:
            self.track2_stream.pause()
    
    def stop_track(self, track_num):
        if track_num == 1 and self.track1_stream:
            self.track1_stream.stop()
            self.track1_stream = None
        elif track_num == 2 and self.track2_stream:
            self.track2_stream.stop()
            self.track2_stream = None
    
    def play_all(self):
        if self.track1_data is not None:
            self.play_track(1)
        if self.track2_data is not None:
            self.play_track(2)
    
    def stop_all(self):
        self.stop_track(1)
        self.stop_track(2)
    
    def set_volume(self, track_num):
        volume = getattr(self, f'track{track_num}_volume_slider').value() / 100.0
        if track_num == 1 and self.track1_stream:
            self.track1_stream.set_volume(volume)
        elif track_num == 2 and self.track2_stream:
            self.track2_stream.set_volume(volume)
    
    def update_position(self):
        # Update track 1 position
        if self.track1_stream and self.track1_stream.playing:
            current_time = self.track1_stream.get_position()
            duration = self.track1_stream.get_duration()
            
            # Update waveform position
            self.track1_waveform.set_position(current_time)
            
            # Update progress bar
            progress = int((current_time / duration) * 100) if duration > 0 else 0
            self.track1_progress_bar.setValue(progress)
            
            # Update time label
            current_str = self.format_time(current_time)
            duration_str = self.format_time(duration)
            self.track1_time_label.setText(f"{current_str} / {duration_str}")
        
        # Update track 2 position
        if self.track2_stream and self.track2_stream.playing:
            current_time = self.track2_stream.get_position()
            duration = self.track2_stream.get_duration()
            
            # Update waveform position
            self.track2_waveform.set_position(current_time)
            
            # Update progress bar
            progress = int((current_time / duration) * 100) if duration > 0 else 0
            self.track2_progress_bar.setValue(progress)
            
            # Update time label
            current_str = self.format_time(current_time)
            duration_str = self.format_time(duration)
            self.track2_time_label.setText(f"{current_str} / {duration_str}")
    
    def format_time(self, seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def closeEvent(self, event):
        self.stop_all()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = AdvancedMP3Player()
    player.show()
    sys.exit(app.exec_())