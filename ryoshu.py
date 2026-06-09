import sys
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import io
import os
import tempfile
import edge_tts
import torch
from rvc_python.infer import RVCInference
import re
import tempfile
import logging

# --- PyTorch 호환성 패치 ---
_original_load = torch.load
def _patched_load(*args, **kwargs):
    kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = _patched_load
# -------------------------

os.environ["OMP_NUM_THREADS"] = "6"
os.environ["MKL_NUM_THREADS"] = "6"

print(f"현재 설정된 스레드 수: {torch.get_num_threads()}")

log_path = "/home/user/Documents/ryoshu.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout) # 터미널(stdout)로만 쏩니다.
    ]
)
logger = logging.getLogger("RyoshuBot")
logger.info("🚀 로그 시스템이 정상적으로 시작되었습니다.")

class Ryoshu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # RVC 초기화 및 파라미터 고정
        self.rvc = RVCInference(
            device="cpu", 
            model_path="ryo_bot.pth", 
            index_path="added_IVF421_Flat_nprobe_1_ryo_bot_v2.index"
        )
        self.rvc.set_params(f0up_key=0, f0method="rmvpe", index_rate=0.3, filter_radius=2)
        
        # 설정 및 상태 관리
        self.max_length = 150  # 텍스트 과부하 방지 (글자 수 제한)
        self.consonant_map = {
            "ㄱ": "기역", "ㄴ": "니은", "ㄷ": "디귿", "ㄹ": "리을", "ㅁ": "미음",
            "ㅂ": "비읍", "ㅅ": "시옷", "ㅇ": "이응", "ㅈ": "지읒", "ㅊ": "치읓",
            "ㅋ": "키읔", "ㅌ": "티읕", "ㅍ": "피읖", "ㅎ": "히읗",
            "ㄲ": "쌍기역", "ㄸ": "쌍디귿", "ㅃ": "쌍비읍", "ㅆ": "쌍시옷", "ㅉ": "쌍지읒"
        }

    def select_language(self, text):
    # 1. 일본어 포함 여부 확인 (히라가나/가타카나 범위)
        if re.search(r'[\u3040-\u309F\u30A0-\u30FF]', text):
            return 'ja'
    # 2. 영어 비중 확인 (알파벳이 한글보다 많거나 특정 패턴일 때)
        elif re.search(r'[a-zA-Z]{3,}', text): # 알파벳이 3자 이상 연속되면 영어로 간주
            return 'en'
    # 3. 기본값은 한국어
        return 'ko'

    def preprocess_text(self, text):
        # 1. 과부하 방지: 글자 수 제한
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        # 2. 자음 변환
        for char, replacement in self.consonant_map.items():
            text = text.replace(char, replacement)
        return text

    async def generate_voice(self, text):
        # 1. 언어 감지 및 보이스 매핑 (동일)
        try:
            lang = self.select_language(text)
            logger.info(f"🎤 추론 시작 | 언어: {lang} | 텍스트: {text[:20]}...")
        except:
            lang = 'ko'

        voice_settings = {
            'ko': ('ko-KR-SunHiNeural', "-35Hz"),
            'ja': ('ja-JP-NanamiNeural', "-25Hz"),
            'en': ('en-US-AvaNeural', "-30Hz")
        }
        selected_voice, selected_pitch = voice_settings.get(lang, voice_settings['ko'])

        # 2. TTS 생성
        processed_text = self.preprocess_text(text) if lang == 'ko' else text
        communicate = edge_tts.Communicate(processed_text, selected_voice, rate="-10%", pitch=selected_pitch)
        
        temp_dir = "/dev/shm" 

        with tempfile.NamedTemporaryFile(suffix=".wav", dir=temp_dir, delete=False) as t_in, \
            tempfile.NamedTemporaryFile(suffix=".wav", dir=temp_dir, delete=False) as t_out:
            in_p, out_p = t_in.name, t_out.name

        try:
            await communicate.save(in_p)
            
            # 3. ❗️라이젠 4500 최적화: rmvpe 사용 및 스레드 분리
            self.rvc.set_params(f0method="rmvpe", index_rate=0.45, filter_radius=2)
            
            # CPU 점유율 폭발 방지를 위해 별도 스레드에서 실행
            await asyncio.to_thread(self.rvc.infer_file, in_p, out_p)
            
            with open(out_p, "rb") as f:
                return f.read()
        finally:
            if os.path.exists(in_p): os.remove(in_p)
            if os.path.exists(out_p): os.remove(out_p)

    # --- 실시간 채팅 감지 로직 ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return

        bot_vc = None
        
        # 채널 설명(Topic)에 '료'가 포함된 경우에만 반응
        if not message.channel.topic or "료" not in message.channel.topic:
            return

        # 커맨드는 무시
        if message.content.startswith("!"): return

        # 음성 채널 상태 확인
        if not message.author.voice: return
        
        user_vc = message.author.voice.channel
        # 현재 이 서버에 연결된 봇의 voice_client를 가져옴
        bot_vc = discord.utils.get(self.bot.voice_clients, guild=message.guild)

        if bot_vc is None:
            try:
                bot_vc = await user_vc.connect(timeout=20.0)
            except Exception as e:
                print(f"연결 에러: {e}")
                return
        elif bot_vc.channel != user_vc: # 이제 bot_vc가 확실히 존재하므로 에러 안 남
            await bot_vc.move_to(user_vc)

        # 음성 재생 중이면 패스
        if bot_vc.is_playing(): return

        try:
            audio_data = await self.generate_voice(message.content)
            source = discord.FFmpegPCMAudio(io.BytesIO(audio_data), pipe=True)
            bot_vc.play(source)
        except Exception as e:
            print(f"자동 재생 오류: {e}")

    # --- 명령어: 퇴장 ---
    @app_commands.command(name="퇴장", description="음성 채널에서 료슈를 내보냅니다.")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            await vc.disconnect()
            await interaction.response.send_message("물러나겠다.")
        else:
            await interaction.response.send_message("난 이미 이곳에 없다.", ephemeral=True)

    # --- 명령어: 이동 ---
    @app_commands.command(name="이동", description="료슈를 사용자의 현재 음성 채널로 불러옵니다.")
    async def move(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            return await interaction.response.send_message("네가 먼저 채널에 들어가라.", ephemeral=True)

        user_vc = interaction.user.voice.channel
        bot_vc = interaction.guild.voice_client

        if not bot_vc:
            await user_vc.connect()
            await interaction.response.send_message(f"{user_vc.name}으로 이동 완료.")
        else:
            # 안전한 이동을 위해 중지 후 이동
            if bot_vc.is_playing():
                bot_vc.stop()
            await bot_vc.move_to(user_vc)
            await interaction.response.send_message(f"채널을 {user_vc.name}으로 옮겼다.")

async def setup(bot):
    await bot.add_cog(Ryoshu(bot))