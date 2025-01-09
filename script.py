!apt-get install webp


import subprocess
import os
from PIL import Image
import cv2
import zipfile

def zip_file(output_dir):
    # Cria o arquivo ZIP
    zip_path = f"{output_dir}.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(output_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zipf.write(file_path, os.path.relpath(file_path, output_dir))

    print(f"Arquivos zipados em {zip_path}")

def crop_image(frame, crop_area):
    if crop_area:
        x, y, w, h = crop_area  # Define as coordenadas e tamanho da área (x, y, largura, altura)
        
        # Verifica se a área de corte é válida
        if x + w <= frame.shape[1] and y + h <= frame.shape[0] and w > 0 and h > 0:
            frame = frame[y:y+h, x:x+w]  # Faz o crop
        else:
            print(f"Área de corte inválida para o frame. Corte ignorado.")
            return None  # Retorna None se a área de corte for inválida
    return frame

def video_to_frames(video_path, crop_area):
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

        frame = crop_image(frame, crop_area)

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


def save_frames_as_webp_with_compression(frames, output_dir: str):
    # Cria o diretório de saída se não existir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Salva cada frame como um arquivo WebP com Pillow e depois comprime com cwebp
    for idx, frame in frames.items():
        # Converte o frame de BGR (formato do OpenCV) para RGB (necessário para Pillow)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Cria uma imagem Pillow
        pil_image = Image.fromarray(rgb_frame)

        # Caminho para salvar o arquivo WebP temporário
        temp_frame_path = os.path.join(output_dir, f"{idx}_temp.webp")

        # Salva a imagem no formato WebP sem compressão
        pil_image.save(temp_frame_path, format="WEBP", quality=80, optimize=True)
        
        # Caminho final para a imagem otimizada
        final_frame_path = os.path.join(output_dir, f"{idx}.webp")

        # Comprime a imagem usando cwebp (com qualidade adicional)
        subprocess.run(['cwebp', temp_frame_path, '-q', '100', '-o', final_frame_path])

        # Remove o arquivo temporário
        os.remove(temp_frame_path)
        
        print(f"Salvando e comprimindo {final_frame_path}")



# Solicita o caminho do vídeo
crop_area = (
    0,
    0,
    int(input("CropW: ").strip()),
    int(input("CropH: ").strip())
)
out_dir = input("Out path: ").strip()

# Processa o vídeo e ordena os frames
getting = True
all_frames = []

while getting:
  to_path = input("Video path: ").strip()
  invert = input("Invert? (y/n): ").strip().lower() == "y"
  frames = video_to_frames(to_path, crop_area)

  if invert:
    frames = frames[::-1]

  all_frames.append(frames)
  getting = input("Get more? (y/n): ").strip().lower() == "y"

getting_to_frames = True
to_frames = []

while getting_to_frames:
  start = int(input("Start: ").strip())
  end = int(input("End: ").strip())
  frames_idx = int(input("Frames idx: ").strip())
  to_frames.append((start, end, frames_idx))
  getting_to_frames = input("Get more? (y/n): ").strip().lower() == "y"

if len(all_frames) > 0:  # Verifica se frames foram extraídos
    str_frames = order_frames(all_frames, to_frames)
    save_frames_as_webp_with_compression(str_frames, out_dir)

    zip = input("Zip? (y/n): ").strip().lower()
    if zip == "y":
        zip_file(out_dir)

    print("Frames salvos com sucesso!")
else:
    print("Nenhum frame foi extraído.")
