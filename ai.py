import asyncio
import discord
import sys
from aiogram import F, types
from aiogram.filters import Command
from datetime import datetime

# Твои модули
import cf, ds, tg, kb, db

# --- DISCORD INIT (NO INTENTS) ---
ds.client = discord.Client()

# Кэш активных сессий {thread_id: tg_msg_id}
active_threads = {}

def get_now():
    return datetime.now().strftime("%H:%M")

def get_thread_name(content):
    """Парсит первую строку сообщения для названия ветки"""
    if not content:
        return get_now()
    # Берем первую строку, ограничиваем до 80 символов (лимит Discord 100)
    name = content.split('\n')[0].strip()[:80]
    return name if name else get_now()

# --- TG HANDLERS ---

@tg.dp.message(Command("start"))
async def start_cmd(m: types.Message):
    if m.from_user.id != cf.ADMIN_ID: return
    db.init()
    await m.answer(
        f"👋 **ReportEye** активен.\nМониторинг запущен.",
        reply_markup=kb.main_menu(cf.AUTO_ACCEPT),
        parse_mode="Markdown"
    )

@tg.dp.message(F.text == "🔄 Рестарт")
async def restart_session(m: types.Message):
    active_threads.clear()
    await m.answer("🗑 Память сессий очищена.")

@tg.dp.message(F.text == "📖 История")
async def history_cmd(m: types.Message):
    if m.from_user.id != cf.ADMIN_ID: return
    rows = db.get_history(5)
    if not rows: return await m.answer("История пуста.")
    
    res = "\n".join([f"• `{t}` | {s} → **{st}**" for s, st, t in rows])
    await m.answer(f"📂 **Последние события:**\n\n{res}", parse_mode="Markdown")

@tg.dp.message(F.text.contains("Автопринятие"))
async def toggle_auto(m: types.Message):
    cf.AUTO_ACCEPT = not cf.AUTO_ACCEPT
    await m.answer(
        f"Автопринятие: **{'ON' if cf.AUTO_ACCEPT else 'OFF'}**",
        reply_markup=kb.main_menu(cf.AUTO_ACCEPT),
        parse_mode="Markdown"
    )

# --- CALLBACKS ---

@tg.dp.callback_query(F.data.startswith("ok_"))
async def handle_10_4(c: types.CallbackQuery):
    _, ch_id, msg_id = c.data.split("_")
    try:
        channel = ds.client.get_channel(int(ch_id))
        msg = await channel.fetch_message(int(msg_id))
        
        # Парсим имя из первой строки сообщения
        t_name = get_thread_name(msg.content)
        thread = await msg.create_thread(name=t_name)
        await thread.send("10-4")
        
        active_threads[thread.id] = c.message.message_id
        db.update_status(msg_id, "10-4")
        
        await c.message.edit_text(
            f"✅ **10-4** | `{get_now()}`\n"
            f"Объект: `{msg.author.display_name}`",
            reply_markup=kb.manage_menu(thread.id, msg_id),
            parse_mode="Markdown"
        )
    except Exception as e:
        await c.answer(f"Ошибка: {e}", show_alert=True)

@tg.dp.callback_query(F.data.startswith("m20_"))
async def handle_10_20(c: types.CallbackQuery):
    _, th_id, msg_id = c.data.split("_")
    thread = ds.client.get_channel(int(th_id))
    if thread:
        await thread.send("10-20?")
        await c.answer("10-20?")

@tg.dp.callback_query(F.data.startswith("m00_"))
async def handle_10_0(c: types.CallbackQuery):
    _, th_id, msg_id = c.data.split("_")
    thread = ds.client.get_channel(int(th_id))
    if thread: 
        await thread.send("10-0")
    
    db.update_status(msg_id, "10-0")
    active_threads.pop(int(th_id), None)
    await c.message.edit_text(f"🏁 **10-0** | `{get_now()}`", reply_markup=None, parse_mode="Markdown")

# --- DISCORD EVENTS ---

@ds.client.event
async def on_ready():
    print(f"[{get_now()}] Connected as {ds.client.user}")

@ds.client.event
async def on_message(m):
    if m.author.id == ds.client.user.id: return

    if m.channel.id == cf.CH_CALLS:
        if "адвокат" in m.content.lower() or m.role_mentions:
            db.add_call(m.id, m.author.display_name, m.content)
            
            if cf.AUTO_ACCEPT:
                try:
                    # Автопринятие с парсингом первой строки
                    t_name = get_thread_name(m.content)
                    thread = await m.create_thread(name=t_name)
                    await thread.send("10-4")
                    
                    db.update_status(m.id, "Auto-10-4")
                    
                    msg_tg = await tg.bot.send_message(
                        cf.ADMIN_ID, 
                        f"🤖 **Auto-10-4**\n👤 `{m.author.display_name}`\n📝 `{m.content}`",
                        reply_markup=kb.manage_menu(thread.id, m.id),
                        parse_mode="Markdown"
                    )
                    active_threads[thread.id] = msg_tg.message_id
                    return
                except: pass

            await tg.bot.send_message(
                cf.ADMIN_ID,
                f"⚠️ **Вызов**\n"
                f"👤 `{m.author.display_name}`\n"
                f"📝 `{m.content}`",
                reply_markup=kb.call_menu(m.channel.id, m.id),
                parse_mode="Markdown"
            )

    if isinstance(m.channel, discord.Thread) and m.channel.id in active_threads:
        if m.author.id != ds.client.user.id:
            await tg.bot.send_message(
                cf.ADMIN_ID, 
                f"💬 **{m.author.display_name}**: {m.content}"
            )

# --- RUN ---
async def main():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    db.init()
    print(f"🚀 ReportEye Started...")
    asyncio.create_task(tg.dp.start_polling(tg.bot))
    try:
        await ds.client.start(cf.DS_TOKEN)
    except Exception as e:
        print(f"Fatal: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Offline.")
