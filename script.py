import cv2
import os
import zipfile
import numpy as np
from typing import List
from google.colab import files


def video_to_frames(video_path):
    frames = []
    # Abre o vídeo
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    # Variável para contar os frames
    frame_count = 0

    while True:
        # Captura um frame
        ret, frame = cap.read()
        if not ret:
            break

        frames.append(frame)
        frame_count += 1

    cap.release()
    print(f"Total de frames extraídos: {frame_count}")
    return frames


def order_frames(frames_list: list[list[any]], to_frames: list[tuple[int, int, int]]):
    with_strs = {}

    for to_frame in to_frames:
        start, end, frames_idx = to_frame
        frames = frames_list[frames_idx][start:end]
        for idx, frame in enumerate(frames, start=start):
            frame_path = f"frame_{idx:04d}"
            with_strs[frame_path] = frame

    return with_strs