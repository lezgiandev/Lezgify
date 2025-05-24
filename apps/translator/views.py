from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from gradio_client import Client
import tempfile
import shutil
import os
import base64


class TranslateAndTTSView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        russian_text = request.data.get('text')
        if not russian_text:
            return JsonResponse({'error': 'Text is required'}, status=400)

        try:
            translator_client = Client("stazizov/lezghian_translator_v1")
            lezgin_text = translator_client.predict(
                text=russian_text,
                api_name="/translate"
            )

            tts_client = Client("https://leks-forever-lez-tts.hf.space/")

            speaking_rate = 1
            noise_scale = 0
            add_pauses = True

            with tempfile.TemporaryDirectory() as temp_dir:
                audio_path = tts_client.predict(
                    lezgin_text,
                    speaking_rate,
                    noise_scale,
                    add_pauses,
                    fn_index=0
                )

                temp_file = os.path.join(temp_dir, "audio.wav")
                shutil.copy(audio_path, temp_file)

                with open(temp_file, 'rb') as f:
                    audio_data = f.read()

                audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            response_data = {
                'translation': lezgin_text,
                'audio': audio_base64,
                'audio_format': 'audio/wav'
            }

            return JsonResponse(response_data)

        except Exception as e:
            return JsonResponse(
                {'error': f'Processing error: {str(e)}'},
                status=500
            )


class TTSOnlyView(APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def post(request):
        lezgin_text = request.data.get('lezgin_text')
        if not lezgin_text:
            return JsonResponse({'error': 'lezgin_text необходим'}, status=400)

        try:
            tts_client = Client("https://leks-forever-lez-tts.hf.space/")

            speaking_rate = 1
            noise_scale = 0
            add_pauses = True

            with tempfile.TemporaryDirectory() as temp_dir:
                audio_path = tts_client.predict(
                    lezgin_text,
                    speaking_rate,
                    noise_scale,
                    add_pauses,
                    fn_index=0
                )

                temp_file = os.path.join(temp_dir, "audio.wav")
                shutil.copy(audio_path, temp_file)

                with open(temp_file, 'rb') as f:
                    audio_data = f.read()

                audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            return JsonResponse({
                'audio': audio_base64,
                'audio_format': 'audio/wav'
            })

        except Exception as e:
            return JsonResponse(
                {'error': f'TTS Error: {str(e)}'},
                status=500
            )