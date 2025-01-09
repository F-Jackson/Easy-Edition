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


def order_frames(
    frames_list: list[list[any]],
    to_frames: list[tuple[int, int, int]]
):
    with_strs = {}
    index = 0

    for to_frame in to_frames:
        start, end, frames_idx = to_frame
        frames_len = len(frames_list[frames_idx])
        start_percent = int((start / 100) * frames_len)
        end_percent = int((end / 100) * frames_len)
        start_percent = max(0, min(start_percent, frames_len))
        end_percent = max(0, min(end_percent, frames_len))

        # Pega os frames correspondentes
        frames = frames_list[frames_idx][start_percent:end_percent]

        for frame in frames:
            frame_path = f"frame_{index:04d}"
            with_strs[frame_path] = frame
            index += 1

    return with_strs


# Solicita o caminho do vídeo
to_path = input("Video path: ").strip()

# Processa o vídeo e ordena os frames
all_frames = video_to_frames(to_path)
if all_frames:  # Verifica se frames foram extraídos
    str_frames = order_frames([all_frames], [(0, 10, 0)])
    print(f"Keys: {list(str_frames.keys())}")
else:
    print("Nenhum frame foi extraído.")
