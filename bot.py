import logging, re, random, json, os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class SmartTelegramBot:
    def __init__(self, token):
        self.token = token
        self.app = ApplicationBuilder().token(token).build()
        self.response_data = {}
        self.user_contexts = {}
        self.bot_name = "حمال"  # نام ربات برای صدا زدن
        self.load_responses()
        self.ensure_default_categories()
        self.load_settings()
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("learn", self.learn_command))
        self.app.add_handler(CommandHandler("setname", self.set_name_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_error_handler(self.error_handler)

    def load_responses(self):
        try:
            if os.path.exists('bot_responses.json'):
                with open('bot_responses.json', 'r', encoding='utf-8') as f:
                    self.response_data = json.load(f)
                    logging.info("پاسخ‌ها بارگذاری شدند")
            else:
                self.init_default_responses()
                self.save_responses()
        except Exception as e:
            logging.error(f"خطا در بارگذاری پاسخ‌ها: {e}")
            self.init_default_responses()
            self.save_responses()

    def load_settings(self):
        try:
            if os.path.exists('bot_settings.json'):
                with open('bot_settings.json', 'r', encoding='utf-8') as f:
                    self.bot_name = json.load(f).get("bot_name", self.bot_name)
                    logging.info(f"نام ربات: {self.bot_name}")
        except Exception as e:
            logging.error(f"خطا در بارگذاری تنظیمات: {e}")
            self.save_settings()

    def save_settings(self):
        try:
            with open('bot_settings.json', 'w', encoding='utf-8') as f:
                json.dump({"bot_name": self.bot_name}, f, ensure_ascii=False, indent=4)
                logging.info("تنظیمات ذخیره شدند")
        except Exception as e:
            logging.error(f"خطا در ذخیره تنظیمات: {e}")

    def generate_extended_default_responses(self):
        """تولید 200 خط دیالوگ بی‌ادبانه برای دسته‌ی default"""
        base_lines = [
            "حرفات مزخرفه!", 
            "واقعاً غبیت می‌کنی!", 
            "این حرفا اصلاً قابل قبول نیست!", 
            "دلم برا تو تنگ شده، چون همیشه مزخرفی!", 
            "هر چی بگی بی‌ارزشه!", 
            "تو مثل یه بی‌فایده هستی!", 
            "هیچی نمی‌فهمی، حرفات بی‌معناست!", 
            "تو هیچ وقت نتونی به من برسی!", 
            "فکر نمی‌کردم اینقدر مزخرف باشی!", 
            "آخه دیگه! حرفای بی‌معنی می‌زنی!",
            "حرفاتو یه جوری می‌زنم که اذیتت کنم!",
            "این حرفای تو مثل زباله‌ست!",
            "با این حرف‌ها اصلاً کس دقت نمی‌کنه!",
            "از حرفات کثیف‌تر چیزی نداری!",
            "تو حرف می‌زنی اما هیچ‌چی نمی‌گی!",
            "حتی یه بچه هم نمی‌تونه حرفات رو بفهمه!",
            "تو یک نابغه نیستی، فقط یه مزخرفی!",
            "حرفای تو مثل هوای بسته‌ست!",
            "حقیقتش رو بگو، هیچ چیز جدیدی نمی‌گویی!",
            "تو اصلاً نمی‌تونی یه جمله درست بگی!"
        ]
        responses = []
        for i in range(200):
            responses.append(random.choice(base_lines) + f" (نسخه {i+1})")
        return responses

    def init_default_responses(self):
        self.response_data = {
            "greetings": {
                "patterns": ["سلام", "درود", "خوبی", "چطوری", "hi", "hello", "های", "هلو"],
                "responses": [
                    "سلام لعنتی! چی میخوای از من؟", 
                    "درود! بیا ببینم حال لعنتیت چیه!", 
                    "سلام، خوش اومدی به دنیای بی‌رحم من!"
                ]
            },
            "questions": {
                "patterns": ["چی", "کی", "چرا", "چگونه", "کجا", "چطور", "?", "؟"],
                "responses": [
                    "سوال خوبی پرسیدی، ولی شاید جواب ندهم چون حال لعنتی ندارم!", 
                    "جواب میدم، ولی یادت نره که حرفات همیشه مثل یه مزخرفیه!", 
                    "این سوال جالبه، ولی مثل سوالات بی‌ارزش توئه!"
                ]
            },
            "thanks": {
                "patterns": ["ممنون", "مرسی", "سپاس", "thank", "thanks", "تشکر"],
                "responses": [
                    "خواهش می‌کنم لعنتی!", 
                    "حالا لطف کردی!", 
                    "خوشحالم که تونستم کاری بکنم، هرچند مثل تو همیشه ناکارآمدی!"
                ]
            },
            "default": {
                "responses": self.generate_extended_default_responses()
            },
            "bot_called": {
                "responses": [
                    "بله لعنتی، گوش می‌کنم!", 
                    "در خدمتم، حتی اگه مثل همیشه ناکارآمدی!", 
                    "جانم؟ بیا ببینم چی میخوای لعنتی!"
                ]
            }
        }

    def ensure_default_categories(self):
        defaults = {
            "default": {"responses": self.generate_extended_default_responses()},
            "bot_called": {"responses": ["بله لعنتی، گوش می‌کنم!", "در خدمتم!", "جانم؟"]},
            "greetings": {
                "patterns": ["سلام", "درود", "خوبی", "چطوری", "hi", "hello", "های", "هلو"],
                "responses": ["سلام لعنتی! چی میخوای؟", "درود! حال لعنتیت چیه؟", "سلام، خوش اومدی به دنیای من!"]
            }
        }
        changed = False
        for cat, data in defaults.items():
            if cat not in self.response_data:
                self.response_data[cat] = data
                changed = True
            else:
                if "responses" not in self.response_data[cat]:
                    self.response_data[cat]["responses"] = data["responses"]
                    changed = True
                if "patterns" in data and "patterns" not in self.response_data[cat]:
                    self.response_data[cat]["patterns"] = data["patterns"]
                    changed = True
        if changed:
            self.save_responses()
            logging.info("دسته‌های پیش‌فرض به‌روز شدند")

    def save_responses(self):
        try:
            with open('bot_responses.json', 'w', encoding='utf-8') as f:
                json.dump(self.response_data, f, ensure_ascii=False, indent=4)
                logging.info("پاسخ‌ها ذخیره شدند")
        except Exception as e:
            logging.error(f"خطا در ذخیره پاسخ‌ها: {e}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            f"سلام {update.effective_user.first_name}! من یه ربات لعنتی و هوشمندم. واسه صدا زدن من کافیه اسمم ({self.bot_name}) رو بگی!"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = f"""/start - شروع
/help - راهنما
/learn [الگو] | [پاسخ] - آموزش
/setname [نام] - تغییر نام (فعلی: {self.bot_name})

برای صحبت با من، اول اسم من رو صدا بزنید (مثال: "{self.bot_name} سلام چطوری؟")
مثال آموزش: /learn سلام چطوری | من خوبم، ولی تو یه بی‌فایده لعنتی هستی!"""
        await update.message.reply_text(help_text)

    async def set_name_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        new_name = update.message.text[9:].strip()
        if not new_name:
            await update.message.reply_text(f"لطفاً یه نام وارد کن. نام فعلی: {self.bot_name}")
            return
        old_name = self.bot_name
        self.bot_name = new_name
        self.save_settings()
        await update.message.reply_text(f"نام من از '{old_name}' به '{self.bot_name}' تغییر کرد!")

    async def learn_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        content = update.message.text[7:].strip()
        if '|' not in content:
            await update.message.reply_text("فرمت اشتباه. استفاده: /learn الگو | پاسخ")
            return
        pattern, response = map(str.strip, content.split("|", 1))
        if not pattern or not response:
            await update.message.reply_text("الگو و پاسخ نمیتونن خالی باشن!")
            return
        cat = self.find_category_for_pattern(pattern)
        if not cat:
            new_cat = f"custom_{len(self.response_data)}"
            self.response_data[new_cat] = {"patterns": [pattern], "responses": [response]}
        else:
            if pattern not in self.response_data[cat].get("patterns", []):
                self.response_data[cat].setdefault("patterns", []).append(pattern)
            if response not in self.response_data[cat].get("responses", []):
                self.response_data[cat].setdefault("responses", []).append(response)
        self.save_responses()
        await update.message.reply_text(f"یاد گرفتم! وقتی چیزی شبیه '{pattern}' بگن، با '{response}' پاسخ می‌دم.")

    def find_category_for_pattern(self, pattern):
        best_cat, best_sim = None, 0.5
        for cat, data in self.response_data.items():
            if cat in ["default", "bot_called"] or "patterns" not in data:
                continue
            for pat in data["patterns"]:
                sim = self.calculate_similarity(pattern, pat)
                if sim > best_sim:
                    best_sim, best_cat = sim, cat
        return best_cat

    def calculate_similarity(self, t1, t2):
        try:
            t1, t2 = re.sub(r'\s+', ' ', t1.lower().strip()), re.sub(r'\s+', ' ', t2.lower().strip())
            if t1 in t2 or t2 in t1:
                return 0.8
            w1, w2 = set(re.findall(r'\b\w+\b', t1)), set(re.findall(r'\b\w+\b', t2))
            return len(w1 & w2) / len(w1 | w2) if w1 and w2 else 0
        except Exception as e:
            logging.error(f"خطا در محاسبه شباهت: {e}")
            return 0

    def is_bot_called(self, text):
        try:
            return self.bot_name.lower() in text.lower()
        except Exception as e:
            logging.error(f"خطا در بررسی نام: {e}")
            return False

    def update_user_context(self, user_id, message_text):
        self.user_contexts.setdefault(user_id, {"history": []})["history"].append(message_text)
        if len(self.user_contexts[user_id]["history"]) > 5:
            self.user_contexts[user_id]["history"].pop(0)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            text = update.message.text
            user_id = update.effective_user.id
            self.update_user_context(user_id, text)
            if self.is_bot_called(text) or update.message.reply_to_message:
                response = self.analyze_message(text)
                await update.message.reply_text(response)
        except Exception as e:
            logging.error(f"خطا در رسیدگی به پیام: {e}")
            try:
                await update.message.reply_text("متأسفم، مشکلی پیش آمده. دوباره تلاش کن.")
            except:
                pass

    def analyze_message(self, text):
        try:
            self.ensure_default_categories()
            text_lower = text.lower()
            keyword_responses = {
                "خوبی": "خوبم لعنتی! اما تو همچنان مثل یه بی‌ارزش زباله هستی!",
                "چطوری": "چطوری؟ مثل همیشه ناکارآمد، حال لعنتی خوبی نداری!"
            }
            for keyword, resp in keyword_responses.items():
                if keyword in text_lower:
                    return resp
            if text_lower.strip() == self.bot_name.lower().strip():
                return random.choice(self.response_data["bot_called"]["responses"])
            msg = re.sub(rf'{self.bot_name}', '', text, flags=re.IGNORECASE).strip()
            if not msg:
                return random.choice(self.response_data["bot_called"]["responses"])
            scores = {}
            for cat, data in self.response_data.items():
                if cat in ["default", "bot_called"] or "patterns" not in data:
                    continue
                score = max((0.9 if pat.lower() in msg.lower() else self.calculate_similarity(msg, pat)) for pat in data["patterns"])
                if score > 0.4:
                    scores[cat] = score
            return random.choice(self.response_data[max(scores, key=scores.get)]["responses"]) if scores else random.choice(self.response_data["default"]["responses"])
        except Exception as e:
            logging.error(f"خطا در تحلیل پیام: {e}")
            return "متأسفم، مشکلی پیش آمده. دوباره تلاش کن."

    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        logging.error(f"خطا: {context.error}")
        if update and isinstance(update, Update) and update.effective_message:
            try:
                await update.effective_message.reply_text("با عرض پوزش، خطایی رخ داده. لطفاً دوباره تلاش کن.")
            except:
                pass

    def run(self):
        logging.info("ربات در حال اجراست...")
        self.app.run_polling()

if __name__ == '__main__':
    TOKEN = "7473433081:AAH1ISzqMI1l6t6n_H9_JYvVfpvXj-Lzvik"
    try:
        bot = SmartTelegramBot(TOKEN)
        bot.run()
    except Exception as e:
        logging.critical(f"خطای بحرانی: {e}")
