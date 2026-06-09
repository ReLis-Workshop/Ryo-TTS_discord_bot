import discord
from discord.ext import commands
import asyncio
import torch
import os

os.environ["OMP_NUM_THREADS"] = "6"
os.environ["MKL_NUM_THREADS"] = "6"

print(f"현재 설정된 스레드 수: {torch.get_num_threads()}")

env_path = os.path.join(os.path.dirname(__file__), '.env')

# 토큰 설정 (여기에 발급받은 토큰을 넣으세요)
TOKEN = os.getenv("DISCORD_TOKEN")

class MyBot(commands.Bot):
    def __init__(self):
        # 최신 slash command를 위해 intents 설정
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # 1. Cog 로드
        await self.load_extension('ryo')
        
        # 2. 특정 길드에 즉시 동기화 (해커톤용 치트키)
        try:
            # guild=None 이 기본값이며, 전 세계 서버에 배포됩니다.
            synced = await self.tree.sync()
            print(f"✅ 글로벌 슬래시 커맨드 {len(synced)}개 동기화 요청 완료")
            print("💡 주의: 글로벌 반영은 디스코드 서버 캐시로 인해 시간이 걸릴 수 있습니다.")
        except Exception as e:
            print(f"❌ 동기화 실패: {e}")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = MyBot()

if __name__ == "__main__":
    bot.run(TOKEN)
