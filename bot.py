import asyncio
import logging
import os
import random
import time
from typing import Dict, Optional

from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, BusinessConnection
from aiogram.filters import CommandStart
from dotenv import load_dotenv

load_dotenv()

# ================== Config ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable မရှိပါ")

OFFLINE_THRESHOLD_MINUTES = 8          # ဒီထက်ကြာရင် Offline
ONLINE_DELAY_SECONDS = 120             # ၂ မိနစ်
AUTO_REPLY_COOLDOWN_SECONDS = 600      # chat တစ်ခုကို ၁၀ မိနစ်အတွင်း တစ်ကြိမ်ပဲ auto-reply

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# ================== Reply texts (၂၀ မျိုး) ==================
OFFLINE_REPLIES = [
    "🐜 💩စားနေပါသည် ပြီးမှ စာပြန်ထားလိုက်ပါမယ်💗",
    "🍦 အီးစားနေလို့ နည်းနည်းလေး စောင့်ပေးပါဦးနော်~",
    "🐜 တစ်ခုခု လုပ်နေလို့ အခု မအားသေးဘူး နောက်မှ ပြန်မယ်နော်",
    "💤 ခဏ အနားယူနေပါတယ် ပြီးရင် စာပြန်ပါမယ်",
    "🍦 အီးပုံးကြီးနဲ့ ရုန်းကန်နေဆဲ... နောက်မှ ပြန်ပြောမယ်",
    "🐜 အလုပ်များနေလို့ အခု မပြန်နိုင်သေးဘူး ခဏစောင့်ပေးပါ",
    "🍕 စားနေပါတယ် ပြီးမှ ပြန်မယ်နော်~",
    "🐜 ခဏလေး အလုပ်ရှုပ်နေပါတယ် နောက်မှ စာပြန်ပါမယ်",
    "🍦 အီးစားရင်း စဉ်းစားနေတယ်... နည်းနည်းစောင့်ပေးပါ",
    "🐜 အခု မအားဘူး ပြီးရင် ချက်ချင်း ပြန်မယ်",
    "💤 နည်းနည်းလေး အိပ်ချင်နေတယ် နောက်မှ ပြန်ပြောမယ်",
    "🍦 ပွတ်ဆိတ် အီးစားနေပါသည် ပြီးမှ စာပြန်ထားလိုက်ပါမယ်",
    "🐜 တစ်ခုခု မအားသေးတာ ဖြစ်နိုင်ပါတယ် နည်းနည်းစောင့်ပေးပါ",
    "🍕 ဗိုက်ဆာလို့ စားနေပါတယ် ပြီးမှ ပြန်မယ်",
    "🐜 အလုပ်နဲ့ ရုန်းကန်နေဆဲပါ နောက်မှ စာပြန်ပါမယ်",
    "🍦 အီးတစ်ခွက် သောက်နေပါတယ် ခဏစောင့်ပေးပါဦး",
    "🐜 အခု လက်မအားသေးဘူး ပြီးရင် ပြန်မယ်နော်",
    "💤 ခဏ အနားယူနေပါတယ် မကြာခင် ပြန်စာပို့ပါမယ်",
    "🍦 အီးစားရင်း ပျော်နေပါတယ် နောက်မှ ပြန်ပြောမယ်~",
    "🐜 တစ်ခုခု လုပ်နေလို့ အခု မပြန်နိုင်သေးပါ နည်းနည်းစောင့်ပေးပါ",
]

ONLINE_DELAYED_REPLIES = [
    "🍦 တစ်ခုခု မအားသေးတာ ဖြစ်နိုင်ပါတယ်...\nနည်းနည်းလေး စောင့်ပေးပါဦးနော် 😊",
    "🐜 အခု လက်လွတ်မနေသေးဘူး နည်းနည်းစောင့်ပေးပါနော်~",
    "🍦 ခဏလေး စောင့်ပေးပါဦး တစ်ခုခု လုပ်နေသေးတယ်",
    "🐜 မကြာခင် ပြန်မယ် နည်းနည်းလေး စောင့်ပေးပါ 😊",
    "🍦 အခု မအားသေးဘူး... ခဏနေရင် ပြန်ပြောမယ်",
    "🐜 တစ်ခုခု ရှုပ်နေသေးတယ် နည်းနည်းစောင့်ပေးပါဦး",
    "🍦 မကြာခင် ရောက်လာမယ် စောင့်ပေးပါနော်~",
    "🐜 အခု လက်မအားသေးဘူး ခဏနေရင် ပြန်မယ်",
    "🍦 တစ်ခုခု လုပ်နေဆဲပါ နည်းနည်းလေး စောင့်ပေးပါ 😊",
    "🐜 မအားသေးတာ ဖြစ်နိုင်ပါတယ် ခဏစောင့်ပေးပါဦး",
    "🍦 အခု နည်းနည်း ရှုပ်နေတယ် မကြာခင် ပြန်မယ်",
    "🐜 စောင့်ပေးပါဦးနော် ပြီးရင် ချက်ချင်း ပြန်မယ်",
    "🍦 တစ်ခုခု မအားသေးဘူး... နည်းနည်းလေး စောင့်ပါ",
    "🐜 အခု လက်လွတ်မနေသေးဘူး ခဏနေရင် ပြန်ပြောမယ်",
    "🍦 မကြာခင် စာပြန်ပါမယ် စောင့်ပေးပါနော် 😊",
    "🐜 ခဏလေးပဲ စောင့်ပေးပါဦး တစ်ခုခု လုပ်နေသေးတယ်",
    "🍦 အခု မအားသေးတာ ဖြစ်နိုင်ပါတယ် နည်းနည်းစောင့်ပေးပါ",
    "🐜 ပြီးရင် ပြန်မယ် ခဏစောင့်ပေးပါဦးနော်~",
    "🍦 တစ်ခုခု ရှုပ်နေသေးတယ် မကြာခင် ရောက်လာမယ်",
    "🐜 နည်းနည်းလေး စောင့်ပေးပါဦး ပြီးရင် ချက်ချင်း ပြန်မယ် 😊",
]

# ================== Storage ==================
connections: Dict[str, dict] = {}
owner_last_activity: Dict[int, float] = {}
pending_tasks: Dict[str, asyncio.Task] = {}
last_auto_reply: Dict[str, float] = {}  # "conn_id:chat_id" → timestamp


def get_owner_id(business_connection_id: str) -> Optional[int]:
    data = connections.get(business_connection_id)
    return data["owner_id"] if data else None


def is_owner_online(owner_id: int) -> bool:
    last = owner_last_activity.get(owner_id)
    if not last:
        return False
    return (time.time() - last) < (OFFLINE_THRESHOLD_MINUTES * 60)


def update_owner_activity(owner_id: int):
    owner_last_activity[owner_id] = time.time()


def can_auto_reply(task_key: str) -> bool:
    """cooldown မကုန်သေးရင် False"""
    last = last_auto_reply.get(task_key)
    if last is None:
        return True
    return (time.time() - last) >= AUTO_REPLY_COOLDOWN_SECONDS


def mark_auto_replied(task_key: str):
    last_auto_reply[task_key] = time.time()


# ================== Handlers ==================

@router.business_connection()
async def on_business_connection(event: BusinessConnection):
    if event.is_enabled:
        can_reply = bool(event.rights and event.rights.can_reply)
        connections[event.id] = {
            "owner_id": event.user.id,
            "can_reply": can_reply,
            "user_chat_id": event.user_chat_id,
        }
        update_owner_activity(event.user.id)
        logger.info(f"Connected: owner={event.user.id}, conn={event.id}")
    else:
        connections.pop(event.id, None)
        logger.info(f"Disconnected: conn={event.id}")


@router.business_message()
async def handle_business_message(message: Message):
    if not message.business_connection_id:
        return

    conn_id = message.business_connection_id
    owner_id = get_owner_id(conn_id)

    if owner_id is None:
        try:
            conn = await bot.get_business_connection(conn_id)
            if not conn.is_enabled:
                return
            connections[conn_id] = {
                "owner_id": conn.user.id,
                "can_reply": bool(conn.rights and conn.rights.can_reply),
                "user_chat_id": conn.user_chat_id,
            }
            owner_id = conn.user.id
        except Exception as e:
            logger.error(f"get_business_connection failed: {e}")
            return

    is_from_owner = message.from_user and message.from_user.id == owner_id
    is_from_bot = message.sender_business_bot is not None

    # ---------- Owner / Bot ကိုယ်တိုင် ပို့တဲ့ စာ ----------
    if is_from_owner or is_from_bot:
        if is_from_owner:
            update_owner_activity(owner_id)
            task_key = f"{conn_id}:{message.chat.id}"
            task = pending_tasks.pop(task_key, None)
            if task and not task.done():
                task.cancel()
            # Owner ပြန်လိုက်ရင် cooldown ပြန်စနိုင်အောင် ဖျက်
            last_auto_reply.pop(task_key, None)
            logger.info(f"Owner replied → reset auto-reply state for chat {message.chat.id}")
        return

    # ---------- တခြားသူဆီက စာ ----------
    chat_id = message.chat.id
    task_key = f"{conn_id}:{chat_id}"

    # cooldown မကုန်သေးရင် ဘာမှ မလုပ်
    if not can_auto_reply(task_key):
        logger.info(f"Cooldown active → skip auto-reply for chat {chat_id}")
        return

    # အရင် delayed task ရှိရင် ဖျက်
    old_task = pending_tasks.pop(task_key, None)
    if old_task and not old_task.done():
        old_task.cancel()

    if is_owner_online(owner_id):
        # Online → ၂ မိနစ် စောင့်ပြီး တစ်ကြိမ်ပဲ ပြန်
        async def delayed_reply():
            try:
                await asyncio.sleep(ONLINE_DELAY_SECONDS)
                if not can_auto_reply(task_key):
                    return
                text = random.choice(ONLINE_DELAYED_REPLIES)
                await bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    business_connection_id=conn_id,
                )
                mark_auto_replied(task_key)
                logger.info(f"Sent delayed online reply to chat {chat_id}")
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.error(f"Delayed reply error: {e}")
            finally:
                pending_tasks.pop(task_key, None)

        pending_tasks[task_key] = asyncio.create_task(delayed_reply())
        logger.info(f"Scheduled 2-min delayed reply for chat {chat_id}")

    else:
        # Offline → ချက်ချင်း တစ်ကြိမ်ပဲ ပြန်
        text = random.choice(OFFLINE_REPLIES)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                business_connection_id=conn_id,
            )
            mark_auto_replied(task_key)
            logger.info(f"Sent offline reply to chat {chat_id}")
        except Exception as e:
            logger.error(f"Offline reply failed: {e}")


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "မင်္ဂလာပါ!\n\n"
        "ဒီ bot ကို Settings → Chat Automation မှာ ချိတ်ပြီး သုံးနိုင်ပါတယ်။"
    )


async def main():
    dp.include_router(router)
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())