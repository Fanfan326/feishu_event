#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超实用口语词汇训练工具 V2
亮点：单词拆解 + 记忆方法 + 趣味例句 + 闯关游戏
"""

import os
import json
import random
import time
from datetime import datetime, timedelta

# 词汇数据库文件
PROGRESS_DB = "learning_progress_v2.json"


# ==================== 完整词汇库（含拆解和记忆法）====================

VOCABULARY = {
    "初级": [
        {
            "word": "awkward",
            "meaning": "尴尬的",
            "category": "形容词",
            "breakdown": "awk(尴尬声) + ward(朝向)",
            "memory_tip": "💡 想象：说话时发出'awk awk'的尴尬声音\n联想：awk 像乌鸦叫，很尴尬",
            "examples": [
                "The silence was awkward.\n沉默很尴尬。",
                "I felt awkward meeting my ex.\n遇到前任很尴尬。",
                "Stop making this awkward!\n别搞得这么尴尬！"
            ],
            "funny": "面试官：5年后你想做什么？\n我：庆祝你问我这个问题的五周年。\n*场面一度十分 awkward* 😬"
        },
        {
            "word": "vibe",
            "meaning": "氛围，感觉",
            "category": "名词",
            "breakdown": "来自 vibration(振动) 的缩写",
            "memory_tip": "💡 记忆法：vibe = 震动的感觉 = 氛围\n🎵 想象音乐的振动带来好氛围",
            "examples": [
                "Good vibes only! 只要好氛围！",
                "I love the vibe here. 我爱这里的氛围。",
                "Bad vibes, let's go. 氛围不对，走吧。"
            ],
            "funny": "老板：团队要有好vibe！\n我：那先从涨工资开始吧 🤑"
        },
        {
            "word": "ghost",
            "meaning": "突然消失（不回消息）",
            "category": "动词",
            "breakdown": "ghost = 鬼👻 = 像鬼一样消失",
            "memory_tip": "💡 联想：像鬼一样突然消失\n就是现在流行的'消失术'",
            "examples": [
                "He ghosted me after the date. 约会后他消失了。",
                "Don't ghost your friends! 别对朋友玩消失！",
                "She's been ghosting me for a week. 她消失一周了。"
            ],
            "funny": "约会对象：晚安\n我：晚安\n*然后他就真的和鬼一样消失了* 👻"
        },
        {
            "word": "salty",
            "meaning": "生气的，不爽的",
            "category": "形容词",
            "breakdown": "salty = 咸的 → 表情'酸'= 不爽",
            "memory_tip": "💡 记忆：吃太咸会生气\n😤 联想：咸得发脾气",
            "examples": [
                "Why are you so salty? 你怎么这么不爽？",
                "He's salty about losing. 输了他很不爽。",
                "Don't be salty! 别生气！"
            ],
            "funny": "朋友赢了游戏：Easy!\n我（salty）：你就是运气好！🧂"
        },
        {
            "word": "flex",
            "meaning": "炫耀",
            "category": "动词",
            "breakdown": "flex = 肌肉💪 → 秀肌肉 → 炫耀",
            "memory_tip": "💡 想象健身教练秀肌肉\n记住：flex既是秀肌肉也是炫耀",
            "examples": [
                "Stop flexing your new car! 别炫耀你的新车！",
                "He's always flexing on Instagram. 他总在ins上炫耀。",
                "Weird flex but OK. 奇怪的炫耀，但行吧。"
            ],
            "funny": "有钱人：我不小心买了3套房\n我：Weird flex but OK 💸"
        },
        {
            "word": "procrastinate",
            "meaning": "拖延",
            "category": "动词",
            "breakdown": "pro(向前) + crastin(明天) + ate(动词)",
            "memory_tip": "💡 拆解记忆：pro推迟 + crastin明天\n= 推到明天 = 拖延\n🐌 想象：一只蜗牛说'明天再做'",
            "examples": [
                "I always procrastinate before exams. 考试前总拖延。",
                "Stop procrastinating! 别拖延了！",
                "Procrastination is my hobby. 拖延是我的爱好。"
            ],
            "funny": "今天要做的事：\n1. 停止拖延\n我：明天再说吧 😴"
        },
        {
            "word": "overwhelmed",
            "meaning": "不知所措的",
            "category": "形容词",
            "breakdown": "over(过度) + whelm(淹没)",
            "memory_tip": "💡 记忆：被wave(浪)淹没\n🌊 想象：被巨浪淹没 = 不知所措",
            "examples": [
                "I'm overwhelmed with work. 工作多到不知所措。",
                "She felt overwhelmed. 她感到不知所措。",
                "Don't be overwhelmed! 别慌！"
            ],
            "funny": "老板：这周有10个项目\n我：*overwhelmed* 我要辞职了 😵"
        },
        {
            "word": "savage",
            "meaning": "野蛮的；毒舌的",
            "category": "形容词",
            "breakdown": "sav(野生) + age(状态)",
            "memory_tip": "💡 联想：save + age = 原始野蛮\n现在常用于'毒舌'",
            "examples": [
                "That comment was savage! 这评论太毒舌了！",
                "She's so savage. 她太毒舌了。",
                "Savage reply! 神回复！"
            ],
            "funny": "朋友：我今天美吗？\n我：比昨天好一点\n朋友：Savage! 🔥"
        },
        {
            "word": "sketchy",
            "meaning": "可疑的，不靠谱的",
            "category": "形容词",
            "breakdown": "sketch(草图) + y(形容词)",
            "memory_tip": "💡 记忆：sketch草图 = 不完整 = 可疑\n🤨 像草图一样模糊不清",
            "examples": [
                "This website looks sketchy. 这网站看起来很可疑。",
                "That guy is sketchy. 那人不靠谱。",
                "Sketchy neighborhood. 可疑的街区。"
            ],
            "funny": "网站：输入信用卡赢iPhone！\n我：This is sketchy AF 🚨"
        },
        {
            "word": "shade",
            "meaning": "讽刺，暗讽",
            "category": "名词/动词",
            "breakdown": "shade = 阴影 → 阴阳怪气",
            "memory_tip": "💡 记忆：shade阴影 = 阴阳怪气\n'Throwing shade' = 丢阴影 = 讽刺",
            "examples": [
                "She threw shade at me. 她讽刺我。",
                "That's some serious shade! 这讽刺太狠了！",
                "No shade, but... 不是讽刺啊，但是..."
            ],
            "funny": "朋友：你今天穿得真...特别\nNo shade though! 😏"
        }
    ],
    "中级": [
        {
            "word": "burnout",
            "meaning": "精疲力竭",
            "category": "名词",
            "breakdown": "burn(燃烧) + out(完)",
            "memory_tip": "💡 记忆：burn烧 + out完 = 燃烧殆尽\n🔥 想象：蜡烛烧完了 = 精疲力竭",
            "examples": [
                "I'm experiencing burnout. 我精疲力竭了。",
                "Work burnout is real. 工作倦怠是真的。",
                "Avoid burnout! 避免过劳！"
            ],
            "funny": "周一：充满动力！\n周三：已burnout\n周五：行尸走肉 🧟"
        },
        {
            "word": "cringe",
            "meaning": "尴尬到缩",
            "category": "动词/形容词",
            "breakdown": "cr(皱) + inge → 尴尬得皱脸",
            "memory_tip": "💡 发音像'扣英吉'= 尴尬得抠脚趾\n😬 想象：尴尬到脸部扭曲",
            "examples": [
                "That's so cringe! 太尴尬了！",
                "I cringed so hard. 我尴尬死了。",
                "Cringe moment. 尴尬时刻。"
            ],
            "funny": "看自己5年前的朋友圈：\n*cringe* 我当时在想什么？ 🙈"
        },
        {
            "word": "lowkey",
            "meaning": "低调地，有点",
            "category": "副词",
            "breakdown": "low(低) + key(调)",
            "memory_tip": "💡 直译：低调 = 其实、有点\n🤫 暗搓搓地说'其实...'",
            "examples": [
                "I'm lowkey tired. 我有点累。",
                "Lowkey love this song. 其实挺喜欢这首歌。",
                "He's lowkey rich. 他其实挺有钱。"
            ],
            "funny": "朋友：你喜欢她吗？\n我：Lowkey...其实还行吧 😳"
        },
        {
            "word": "sus",
            "meaning": "可疑的",
            "category": "形容词",
            "breakdown": "suspicious 的缩写",
            "memory_tip": "💡 来自游戏《Among Us》\n🕵️ 谁是内鬼？That's sus!",
            "examples": [
                "That's sus! 可疑！",
                "You're acting sus. 你行为可疑。",
                "Sus behavior. 可疑行为。"
            ],
            "funny": "同事：我没拿你零食\n我：Sus! 嘴边有碎屑 🍪"
        },
        {
            "word": "simp",
            "meaning": "舔狗",
            "category": "名词",
            "breakdown": "可能来自 simpleton(傻子)",
            "memory_tip": "💡 网络用语：为女神做任何事\n🐕 想象：狗狗摇尾巴讨好主人",
            "examples": [
                "Don't be a simp! 别当舔狗！",
                "He's simping for her. 他在舔她。",
                "Simp behavior. 舔狗行为。"
            ],
            "funny": "女神：帮我买咖啡\nSimp：我立刻去！\n正常人：自己买 ☕"
        }
    ],
    "高级": [
        {
            "word": "serendipity",
            "meaning": "意外惊喜",
            "category": "名词",
            "breakdown": "seren(宁静) + dip(倾向) + ity",
            "memory_tip": "💡 发音记忆：'瑟润地批踢'\n🍀 想象：在宁静中发现意外惊喜",
            "examples": [
                "It was pure serendipity. 纯粹是意外惊喜。",
                "A moment of serendipity. 意外之喜的时刻。"
            ],
            "funny": "本来去买咖啡，结果遇到初恋\nSerendipity！（但尴尬了）😅"
        },
        {
            "word": "schadenfreude",
            "meaning": "幸灾乐祸",
            "category": "名词",
            "breakdown": "德语：schaden(伤害) + freude(快乐)",
            "memory_tip": "💡 德语外来词：伤害+快乐=幸灾乐祸\n😈 看别人倒霉自己开心",
            "examples": [
                "I felt a bit of schadenfreude. 我有点幸灾乐祸。"
            ],
            "funny": "傲慢同事摔倒了\n我心里：Schadenfreude! 😏\n（但表面还是要扶起来）"
        }
    ]
}


# ==================== 学习进度管理 ====================

def load_progress():
    """加载学习进度"""
    if os.path.exists(PROGRESS_DB):
        with open(PROGRESS_DB, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_progress(progress):
    """保存学习进度"""
    with open(PROGRESS_DB, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)


def add_to_progress(word, meaning):
    """添加到学习记录"""
    progress = load_progress()
    now = datetime.now().isoformat()

    if word not in progress:
        progress[word] = {
            "meaning": meaning,
            "first_learn": now,
            "review_count": 0,
            "last_review": now
        }
    else:
        progress[word]["review_count"] += 1
        progress[word]["last_review"] = now

    save_progress(progress)


# ==================== 学习卡片展示 ====================

def show_word_card(vocab):
    """展示单词学习卡片"""
    print("\n" + "="*60)
    print(f"📖 单词: {vocab['word']}")
    print(f"🔤 词性: {vocab['category']}")
    print(f"💬 意思: {vocab['meaning']}")
    print("="*60)

    # 单词拆解
    print(f"\n🔍 单词拆解:")
    print(f"   {vocab['breakdown']}")

    # 记忆方法
    print(f"\n{vocab['memory_tip']}")

    # 例句
    print(f"\n📝 例句:")
    for i, example in enumerate(vocab['examples'], 1):
        print(f"\n   {i}. {example}")

    # 搞笑场景
    if 'funny' in vocab:
        print(f"\n😂 搞笑场景:")
        print(f"   {vocab['funny']}")

    print("\n" + "="*60)


# ==================== 闯关游戏 ====================

class VocabGame:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3
        self.learned_words = []

    def start_level(self, level_name):
        """开始新关卡"""
        words = VOCABULARY.get(level_name, VOCABULARY["初级"])

        print(f"\n🎮 关卡 {self.level}: {level_name}")
        print(f"❤️  生命值: {self.lives}")
        print(f"⭐ 得分: {self.score}")
        print("="*60)

        # 随机选5个词
        selected = random.sample(words, min(5, len(words)))

        for i, vocab in enumerate(selected, 1):
            print(f"\n【第 {i}/5 题】")

            # 先展示单词卡片
            show_word_card(vocab)

            input("\n按回车开始答题...")

            # 随机选择题型
            question_type = random.choice(["英译中", "中译英", "造句"])

            if question_type == "英译中":
                print(f"\n📝 题目: {vocab['word']} 的中文意思是？")
                answer = input("你的答案: ").strip()
                correct = answer in vocab['meaning']

            elif question_type == "中译英":
                print(f"\n📝 题目: '{vocab['meaning']}' 的英文是？")
                answer = input("你的答案: ").strip().lower()
                correct = answer == vocab['word'].lower()

            else:  # 造句
                print(f"\n📝 题目: 用 '{vocab['word']}' 造个句子")
                sentence = input("你的句子: ").strip()
                correct = vocab['word'].lower() in sentence.lower()

            if correct:
                self.score += 10
                self.learned_words.append(vocab['word'])
                print(f"\n✅ 正确！+10分")
                add_to_progress(vocab['word'], vocab['meaning'])
            else:
                self.lives -= 1
                print(f"\n❌ 错误！")
                if question_type != "造句":
                    print(f"正确答案: {vocab['meaning'] if question_type == '英译中' else vocab['word']}")
                print(f"❤️  剩余生命: {self.lives}")

            if self.lives == 0:
                print("\n💀 游戏结束！")
                print(f"最终得分: {self.score}")
                print(f"学会了: {', '.join(self.learned_words)}")
                return False

            input("\n按回车继续...")

        self.level += 1
        print(f"\n🎉 {level_name}关卡通关！")
        return True


# ==================== 快速学习模式 ====================

def quick_learn_mode():
    """快速学习模式"""
    print("\n📚 快速学习模式")
    print("="*60)

    # 选择难度
    print("\n选择难度:")
    for i, level in enumerate(["初级", "中级", "高级"], 1):
        print(f"{i}. {level}")

    choice = input("\n选择 (1-3): ").strip()
    level_map = {"1": "初级", "2": "中级", "3": "高级"}
    level = level_map.get(choice, "初级")

    words = VOCABULARY[level]

    print(f"\n开始学习 {level} 词汇，共 {len(words)} 个")

    for i, vocab in enumerate(words, 1):
        print(f"\n进度: {i}/{len(words)}")
        show_word_card(vocab)
        add_to_progress(vocab['word'], vocab['meaning'])

        choice = input("\n按回车继续，输入 q 退出: ").strip().lower()
        if choice == 'q':
            break

    print(f"\n🎉 学完了！已记录到复习计划")


# ==================== 搜索单词 ====================

def search_word():
    """搜索单词"""
    query = input("\n🔍 输入要查询的单词: ").strip().lower()

    found = False
    for level, words in VOCABULARY.items():
        for vocab in words:
            if query in vocab['word'].lower():
                print(f"\n✅ 找到了！({level})")
                show_word_card(vocab)
                found = True

                # 询问是否加入学习
                choice = input("\n加入学习记录？(y/n): ").strip().lower()
                if choice == 'y':
                    add_to_progress(vocab['word'], vocab['meaning'])
                    print("✅ 已加入学习记录")
                break
        if found:
            break

    if not found:
        print(f"\n❌ 没找到 '{query}'")


# ==================== 今日复习 ====================

def review_today():
    """今日复习"""
    progress = load_progress()

    if not progress:
        print("\n还没有学过任何单词哦！")
        return

    # 找出所有学过的词
    words_to_review = list(progress.keys())

    if not words_to_review:
        print("\n没有需要复习的单词")
        return

    print(f"\n📚 开始复习，共 {len(words_to_review)} 个单词")
    print("="*60)

    random.shuffle(words_to_review)

    for i, word in enumerate(words_to_review[:10], 1):  # 最多复习10个
        print(f"\n【{i}/10】")
        print(f"单词: {word}")

        answer = input("回忆一下中文意思: ").strip()

        # 找到完整信息
        full_info = None
        for level, words in VOCABULARY.items():
            for vocab in words:
                if vocab['word'] == word:
                    full_info = vocab
                    break
            if full_info:
                break

        if full_info:
            if answer in full_info['meaning']:
                print(f"✅ 正确！")
                progress[word]['review_count'] += 1
            else:
                print(f"❌ 答案: {full_info['meaning']}")
                print("\n复习一下:")
                show_word_card(full_info)
                input("\n按回车继续...")

        progress[word]['last_review'] = datetime.now().isoformat()

    save_progress(progress)
    print("\n✅ 复习完成！")


# ==================== 学习统计 ====================

def show_stats():
    """显示学习统计"""
    progress = load_progress()

    if not progress:
        print("\n还没有学习记录")
        return

    print("\n📊 学习统计")
    print("="*60)
    print(f"已学单词: {len(progress)} 个")

    # 按复习次数排序
    sorted_words = sorted(progress.items(), key=lambda x: x[1]['review_count'], reverse=True)

    print("\n📈 复习次数 Top 5:")
    for word, data in sorted_words[:5]:
        print(f"  {word}: {data['review_count']} 次")

    print("\n💪 继续加油！")


# ==================== 主菜单 ====================

def main_menu():
    """主菜单"""
    print("\n" + "="*60)
    print("🎓 超实用口语词汇训练工具 V2")
    print("="*60)
    print("\n1. 📚 快速学习模式（带单词拆解）")
    print("2. 🎮 词汇闯关游戏")
    print("3. 🔍 搜索单词")
    print("4. 📖 今日复习")
    print("5. 📊 学习统计")
    print("6. 🚪 退出")

    choice = input("\n选择功能 (1-6): ").strip()

    if choice == "1":
        quick_learn_mode()
    elif choice == "2":
        game = VocabGame()
        for level_name in ["初级", "中级", "高级"]:
            if not game.start_level(level_name):
                break
    elif choice == "3":
        search_word()
    elif choice == "4":
        review_today()
    elif choice == "5":
        show_stats()
    elif choice == "6":
        print("\n👋 再见！Keep learning!")
        return False

    return True


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🎉 欢迎使用词汇训练工具 V2！")
    print("💡 新功能：单词拆解 + 记忆方法 + 搞笑例句")

    while True:
        if not main_menu():
            break
