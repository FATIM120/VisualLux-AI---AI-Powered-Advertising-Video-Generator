import os
import re
import torch
import numpy as np
from PIL import Image
from gtts import gTTS
from diffusers import StableVideoDiffusionPipeline
from moviepy.editor import (
    VideoFileClip,
    AudioFileClip,
    ImageSequenceClip,
    ImageClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip
)
import requests
from dotenv import load_dotenv
import subprocess

# Configurer MoviePy pour utiliser ImageMagick (nécessaire pour TextClip)
import moviepy.config as mpconf
try:
    from moviepy.config import get_setting as _get_setting
    if _get_setting("IMAGEMAGICK_BINARY") is None:
        # Exemple de chemin possible sous Windows ; modifiez si besoinfr
        possible_paths = [
            r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                mpconf.change_settings({"IMAGEMAGICK_BINARY": path})
                print(f"[DEBUG] ImageMagick trouvé et configuré : {path}")
                break
except Exception as e:
    print(f"[WARNING] Impossible de configurer ImageMagick automatiquement : {e}")

# Charger les variables d'environnement
load_dotenv()
GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-2.0-flash:generateContent"
)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class AdGenerator:
    def __init__(self):
        # Vérifier que ce constructeur est bien exécuté
        print("[DEBUG] _init_ d'AdGenerator appelé.")
        
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"[DEBUG] Répertoire de sortie : {self.output_dir}")

        # Templates pour la génération de scripts
        self.prompt_templates = {
            "fr": (
                "Prends ce texte mal formulé et reformule-le en un script publicitaire fluide, engageant "
                "et professionnel pour un audio de 30 secondes (60-80 mots). Utilise des phrases complètes, "
                "évite les abréviations, supprime tout formatage markdown, titres, puces, parenthèses ou "
                "caractères spéciaux. Exclue toute indication scénique comme (Musique ...), (Voix off : ...), "
                "ou instructions similaires. Rends le texte clair, uniquement le contenu parlé, adapté à une "
                "lecture audio naturelle : {}"
            ),
            "en": (
                "Take this poorly formatted text and rewrite it into a fluid, engaging, and professional ad "
                "script for a 30-second audio (60-80 words). Use complete sentences, avoid abbreviations, remove "
                "any markdown formatting, headings, bullets, parentheses, or special characters. Exclude any "
                "stage directions like (Music ...), (Voiceover: ...), or similar instructions. Make the text "
                "clear, only the spoken content, suitable for natural audio reading : {}"
            )
        }
        print(f"[DEBUG] prompt_templates définis pour : {list(self.prompt_templates.keys())}")

    def setup_gpu(self):
        """Configure GPU settings et vérifie la disponibilité GPU."""
        print("[DEBUG] Vérification de la disponibilité GPU...")
        if torch.cuda.is_available():
            vram = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            print(f"[INFO] VRAM disponible : {vram:.2f} Go")
            if vram < 8:
                print("[WARNING] VRAM faible (< 8 Go). Risque d'erreur CUDA out of memory.")
            return True
        else:
            print("[WARNING] GPU non disponible, utilisation du CPU (plus lent).")
            return False

    def call_gemini_api(self, text, langue="fr"):
        """Appelle l'API Gemini pour générer un script publicitaire."""
        if not GEMINI_API_KEY:
            raise ValueError("Clé API Gemini non configurée. Définissez GEMINI_API_KEY dans le fichier .env")

        # On sait que prompt_templates existe grâce au _init_
        prompt = self.prompt_templates.get(langue, self.prompt_templates["fr"]).format(text)
        print(f"[DEBUG] Prompt envoyé à Gemini (début) : {prompt[:60]}...")

        headers = {"Content-Type": "application/json"}
        params = {"key": GEMINI_API_KEY}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 200}
        }

        try:
            resp = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
            resp.raise_for_status()
            data = resp.json()
            cb = data["candidates"][0]["content"]
            if isinstance(cb, dict) and "parts" in cb:
                result = "".join(p.get("text", "") for p in cb["parts"]).strip()
            else:
                result = str(cb).strip()
            print(f"[INFO] Script généré par Gemini ({len(result.split())} mots).")
            return result
        except requests.RequestException as e:
            print(f"[ERROR] Erreur lors de l'appel API Gemini : {e}")
            print("[INFO] On retombe sur la méthode de nettoyage simple.")
            return self.clean_text(text)

    def clean_text(self, text):
        """Nettoie et reformate un texte pour le rendre adapté à une narration audio."""
        print("[DEBUG] Nettoyage du texte en fallback...")
        # Supprimer parenthèses et crochets
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"\[.*?\]", "", text)
        # Supprimer astérisques, hashtags, listes
        text = re.sub(r"\*{1,2}", "", text)
        text = re.sub(r"\#{1,6}\s+", "", text)
        text = re.sub(r"^\s*[\*\-]\s+", "", text, flags=re.MULTILINE)
        # Normaliser les espaces
        text = re.sub(r"\s+", " ", text).strip()
        # Remplacer abréviations pour TTS
        text = re.sub(r"\b(\d+)m\b", r"\1 mètres", text)
        text = re.sub(r"\b(\d+)h\b", r"\1 heures", text)
        text = re.sub(r"\b(\d+)%\b", r"\1 pour cent", text)
        text = re.sub(r"\bkm\b", r"kilomètres", text)
        text = re.sub(r"\bml\b", r"millilitres", text)
        text = re.sub(r"\bg\b", r"grammes", text)
        text = re.sub(r"€", r"euros", text)
        print(f"[DEBUG] Texte nettoyé (début) : {text[:60]}...")
        return text

    def text_to_speech(self, text, langue="fr", output_file=None):
        """Convertit le texte en audio avec gTTS."""
        if output_file is None:
            output_file = os.path.join(self.output_dir, "narration.mp3")

        try:
            word_count = len(text.split())
            duration_seconds = (word_count / 140) * 60  # estimation
            print(f"[INFO] Estimation durée audio : {duration_seconds:.2f}s ({word_count} mots).")
            tts = gTTS(text=text, lang=langue, slow=False)
            tts.save(output_file)
            print(f"[INFO] Audio TTS sauvegardé dans : {output_file}")
            return output_file, duration_seconds
        except Exception as e:
            print(f"[ERROR] Erreur lors de la conversion TTS : {e}")
            raise

    def generate_video_from_image(self, image_path, output_path=None, duration=5):
        """Génère une vidéo courte (14 frames) à partir d'une image via Stable Video Diffusion."""
        if output_path is None:
            output_path = os.path.join(self.output_dir, f"video_{os.path.basename(image_path)}.mp4")

        try:
            print(f"[INFO] Génération vidéo depuis l'image : {image_path}")
            pipe = StableVideoDiffusionPipeline.from_pretrained(
                "stabilityai/stable-video-diffusion-img2vid-xt",
                torch_dtype=torch.float16,
                variant="fp16"
            )
            device = "cuda" if torch.cuda.is_available() else "cpu"
            pipe.to(device)
            pipe.enable_model_cpu_offload()
            print(f"[DEBUG] Modèle chargé sur : {device}")

            image = Image.open(image_path).convert("RGB")
            image = image.resize((1024, 576))
            print("[DEBUG] Image redimensionnée pour diffusion vidéo.")

            output = pipe(
                image,
                num_frames=14,
                num_inference_steps=25,
                decode_chunk_size=8
            )
            frames = output.frames[0]
            frame_arrays = [np.array(frame) for frame in frames]
            clip = ImageSequenceClip(frame_arrays, fps=7).without_audio()
            clip.write_videofile(output_path, codec='libx264', fps=7, verbose=False)
            clip.close()
            print(f"[INFO] Vidéo générée et sauvegardée dans : {output_path}")
            return output_path
        except Exception as e:
            print(f"[ERROR] Erreur lors de la génération vidéo depuis l'image {image_path} : {e}")
            raise

    def create_ad_video(self, image_paths, audio_path, output_path=None, title=None, call_to_action=None):
        if output_path is None:
            output_path = os.path.join(self.output_dir, "video_publicitaire.mp4")
        temp_video = os.path.join(self.output_dir, "temp_video_noaudio.mp4")

        try:
            # 1) Vérifier que l'audio existe
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Le fichier audio {audio_path} n'existe pas")
            audio = AudioFileClip(audio_path)
            total_duration = audio.duration
            print(f"[INFO] Durée de l'audio : {total_duration:.2f}s")

            # 2) Générer une vidéo pour chaque image
            video_paths = []
            for img_path in image_paths:
                vid = self.generate_video_from_image(img_path)
                video_paths.append(vid)

            # 3) Charger les clips vidéo (sans audio)
            clips = []
            for vid_path in video_paths:
                clip = VideoFileClip(vid_path).without_audio()
                if clip.duration <= 0:
                    print(f"[WARNING] Clip {vid_path} durée nulle, fallback sur image statique.")
                    fallback = ImageClip(img_path).set_duration(2)
                    clip = fallback
                clips.append(clip)

            # 4) Calculer durée cible par clip
            clip_duration = total_duration / len(clips)
            print(f"[INFO] Chaque clip doit durer ~{clip_duration:.2f}s")

            # 5) Ajuster chaque clip à la durée souhaitée
            adjusted_clips = []
            for clip in clips:
                if clip.duration < clip_duration:
                    repeats = int(np.ceil(clip_duration / clip.duration))
                    repeated = concatenate_videoclips([clip] * repeats)
                    adjusted = repeated.subclip(0, clip_duration)
                else:
                    adjusted = clip.subclip(0, min(clip.duration, clip_duration))
                adjusted_clips.append(adjusted)

            # 6) Concaténer
            final_clip = concatenate_videoclips(adjusted_clips, method="compose")

            # 7) Ajuster si final_clip est plus court ou plus long que l'audio
            if final_clip.duration > total_duration:
                final_clip = final_clip.subclip(0, total_duration)
            elif final_clip.duration < total_duration:
                final_clip = final_clip.fx(lambda c: c.set_duration(total_duration))

            # 8) (optionnel) Ajouter titre / CTA si ImageMagick dispo…

            # 9) Exporter la vidéo sans audio
            print("[INFO] Étape 1 : création de la vidéo sans audio…")
            final_clip.set_duration(total_duration).write_videofile(
                temp_video,
                codec='libx264',
                fps=24,
                preset='medium',
                verbose=False,
                threads=4,
                audio=False
            )
            print(f"[DEBUG] temp_video_noaudio créé : {temp_video}")

            # 10) Étape 2 : combiner via FFmpeg avec mapping forcé
            print("[INFO] Étape 2 : ajout de l'audio via FFmpeg…")
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i", temp_video,
                "-i", audio_path,
                "-map", "0:v",
                "-map", "1:a",
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", "192k",
                "-shortest",
                output_path
            ]
            print(f"[DEBUG] Commande FFmpeg : {' '.join(ffmpeg_cmd)}")
            proc = subprocess.run(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if proc.returncode != 0:
                print("[ERROR] FFmpeg a échoué :")
                print(proc.stdout)
                print(proc.stderr)
                raise RuntimeError("FFmpeg n’a pas pu combiner audio et vidéo.")
            print(f"[INFO] Vidéo finale créée avec audio : {output_path}")

            # 11) Supprimer le temporaire
            if os.path.exists(temp_video):
                os.remove(temp_video)

            # 12) Fermer les ressources
            for c in clips + adjusted_clips:
                c.close()
            audio.close()
            final_clip.close()

            return output_path

        except Exception as e:
            print(f"[ERROR] Erreur dans create_ad_video : {e}")
            raise


def main():
    """Fonction principale pour l’exécution du programme."""
    generator = AdGenerator()
    # Vérifier que prompt_templates existe
    try:
        print(f"[DEBUG] prompt_templates = {generator.prompt_templates}")
    except AttributeError:
        print("[ERROR] prompt_templates n'existe pas ! Le constructeur n'a pas été appelé correctement.")
        return

    generator.setup_gpu()

    print("=== Générateur de Vidéos Publicitaires ===")

    # Choix de la langue
    while True:
        langue = input("Choisissez la langue (fr, en) : ").strip().lower()
        if langue in generator.prompt_templates:
            break
        print("Langue non supportée. Veuillez choisir parmi : fr, en")

    # Description du produit/service
    description = input("Entrez la description de votre produit ou service : ").strip()
    if not description:
        description = "Un produit révolutionnaire pour votre quotidien"
        print("[INFO] Description par défaut utilisée.")

    # Sélection des images
    print("\nSélection des images pour la vidéo (appuyez sur Entrée pour terminer) :")
    image_paths = []
    while True:
        image_path = input("Entrez le chemin d'une image (JPG/PNG) : ").strip()
        if not image_path:
            break
        if os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_paths.append(image_path)
            print(f"[INFO] Image ajoutée : {image_path}")
        else:
            print("[WARNING] Fichier invalide. Veuillez choisir une image JPG ou PNG existante.")

    if not image_paths:
        print("[ERROR] Aucune image sélectionnée. Utilisez au moins une image.")
        return

    # Titres et appels à l'action
    title = input("Entrez un titre à afficher au début (ou laissez vide) : ").strip()
    call_to_action = input("Entrez un appel à l'action pour la fin (ou laissez vide) : ").strip()

    # Vérifier ImageMagick pour l’utilisateur final
    try:
        from moviepy.config import get_setting
        imagemagick_path = get_setting("IMAGEMAGICK_BINARY")
        if imagemagick_path and os.path.exists(imagemagick_path):
            print(f"[INFO] ImageMagick trouvé : {imagemagick_path}")
        else:
            print("[WARNING] ImageMagick non trouvé. Les textes ne seront pas ajoutés à la vidéo.")
            print("Pour ajouter des textes, installez ImageMagick : https://imagemagick.org/script/download.php")
    except Exception as e:
        print(f"[WARNING] Erreur de vérification d'ImageMagick : {e}")

    try:
        # Génération du script
        print("\n[INFO] Génération du script publicitaire...")
        if GEMINI_API_KEY:
            script = generator.call_gemini_api(description, langue)
        else:
            print("[WARNING] Pas de clé API Gemini, utilisation du nettoyage de texte simple.")
            script = generator.clean_text(description)

        print("\n=== Script généré ===")
        print(script)

        # Conversion en audio
        print("\n[INFO] Conversion du script en audio...")
        audio_path, audio_duration = generator.text_to_speech(script, langue)

        # Création de la vidéo
        print("\n[INFO] Création de la vidéo (cela peut prendre plusieurs minutes)...")
        output_path = generator.create_ad_video(
            image_paths,
            audio_path,
            title=title if title else None,
            call_to_action=call_to_action if call_to_action else None
        )
        print(f"\n[SUCCESS] Vidéo publicitaire créée avec succès : {output_path}")

    except Exception as e:
        print(f"\n[ERROR] Erreur inattendue : {e}")
        # En cas d’erreur liée à ImageMagick, retenter sans textes
        if "ImageMagick" in str(e) and title and call_to_action:
            print("\n[INFO] Réessai sans ajout de textes…")
            try:
                output_path = generator.create_ad_video(
                    image_paths,
                    audio_path,
                    title=None,
                    call_to_action=None
                )
                print(f"\n[SUCCESS] Vidéo créée sans textes : {output_path}")
            except Exception as e2:
                print(f"[ERROR] Échec de la solution alternative : {e2}")


if __name__== "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Erreur fatale dans _main_ : {e}")