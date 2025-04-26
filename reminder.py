from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

class Reminder:
    def __init__(self, bot: Bot):
        self.scheduler = AsyncIOScheduler()
        self.bot = bot
        
    def start(self):
        """Start the scheduler when event loop is running"""
        self.scheduler.start()

    async def schedule_reminder(self, chat_id: int, hour: int, minute: int):
        async def send_reminder():
            await self.bot.send_message(
                chat_id=chat_id,
                text="⏰ Time for your workout! 💪"
            )

        job_id = f"reminder_{chat_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        self.scheduler.add_job(
            send_reminder,
            'cron',
            hour=hour,
            minute=minute,
            id=job_id,
            timezone='Europe/Kyiv',  
)

    def shutdown(self):
        if self.scheduler.running:
             self.scheduler.shutdown(wait=False) 