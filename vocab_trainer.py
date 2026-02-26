#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超有趣口语词汇训练工具
特色：AI生成搞笑例句 + 情景对话 + 闯关游戏
"""

import os
import json
import random
import time
from datetime import datetime, timedelta
from openai import OpenAI

# PPIO API 配置
PPIO_API_KEY = os.getenv("PPIO_API_KEY", "your-ppio-key")
PPIO_BASE_URL = "https://api.ppinfra.com/v3/openai"

client = OpenAI(api_key=PPIO_API_KEY, base_url=PPIO_BASE_URL)

# 词汇数据库文件
VOCAB_DB = "vocab_data.json"
PROGRESS_DB = "learning_progress.json"


# ==================== 词汇库 ====================

VOCABULARY = {
    "初级": [
        {"word": "awkward", "meaning": "尴尬的", "category": "形容词"},
        {"word": "procrastinate", "meaning": "拖延", "category": "动词"},
        {"word": "overwhelmed", "meaning": "不知所措的", "category": "形容词"},
        {"word": "vibe", "meaning": "氛围，感觉", "category": "名词"},
        {"word": "savage", "meaning": "野蛮的；毒舌的", "category": "形容词"},
        {"word": "sketchy", "meaning": "可疑的，不靠谱的", "category": "形容词"},
        {"word": "ghost", "meaning": "突然消失（不回消息）", "category": "动词"},
        {"word": "salty", "meaning": "生气的，不爽的", "category": "形容词"},
        {"word": "shade", "meaning": "讽刺，暗讽", "category": "名词/动词"},
        {"word": "flex", "meaning": "炫耀", "category": "动词"},
    ],
    "中级": [
        {"word": "procrastination", "meaning": "拖延症", "category": "名词"},
        {"word": "burnout", "meaning": "精疲力竭", "category": "名词"},
        {"word": "gaslighting", "meaning": "煤气灯效应（心理操控）", "category": "名词"},
        {"word": "cringe", "meaning": "尴尬到缩", "category": "动词/形容词"},
        {"word": "simp", "meaning": "舔狗", "category": "名词"},
        {"word": "sus", "meaning": "可疑的（suspicious缩写）", "category": "形容词"},
        {"word": "lowkey", "meaning": "低调地，有点", "category": "副词"},
        {"word": "highkey", "meaning": "高调地，明显地", "category": "副词"},
        {"word": "vibe check", "meaning": "氛围检查", "category": "短语"},
        {"word": "no cap", "meaning": "不吹牛，真的", "category": "短语"},
    ],
    "高级": [
        {"word": "cognitive dissonance", "meaning": "认知失调", "category": "名词"},
        {"word": "imposter syndrome", "meaning": "冒名顶替综合征", "category": "名词"},
        {"word": "schadenfreude", "meaning": "幸灾乐祸", "category": "名词"},
        {"word": "serendipity", "meaning": "意外发现美好事物", "category": "名词"},
        {"word": "ethereal", "meaning": "飘渺的，超凡脱俗的", "category": "形容词"},
        {"word": "ephemeral", "meaning": "短暂的", "category": "形容词"},
        {"word": "ubiquitous", "meaning": "无处不在的", "category": "形容词"},
        {"word": "juxtaposition", "meaning": "并列对比", "category": "名词"},
        {"word": "cathartic", "meaning": "宣泄的，净化心灵的", "category": "形容词"},
        {"word": "existential", "meaning": "存在主义的", "category": "形容词"},
    ]
}


# ==================== AI 生成搞笑例句 ====================

def generate_funny_example(word, meaning):
    """用 AI 生成超搞笑/夸张的例句"""
    prompt = f"""你是一个超级有创意的英语老师，擅长用搞笑、夸张、戏剧化的例句帮学生记住单词。

单词: {word}
中文意思: {meaning}

请生成3个例句，要求：
1. 第一个：日常对话场景，但要有戏剧性
2. 第二个：超级夸张搞笑的场景
3. 第三个：网络流行文化梗

每个例句格式：
英文例句
中文翻译
---

让人看完笑出来，印象深刻！"""

    try:
        response = client.chat.completions.create(
            model="claude-3-5-haiku-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"(AI生成失败: {str(e)})\n例句1: This is so {word}!\n这真是太{meaning}了！"


# ==================== 情景对话训练 ====================

SCENARIOS = {
    "餐厅点餐": {
        "description": "在美式餐厅点餐",
        "roles": ["你", "服务员"],
        "target_words": ["awkward", "vibe", "procrastinate"]
    },
    "面试": {
        "description": "参加科技公司面试",
        "roles": ["你", "面试官"],
        "target_words": ["overwhelmed", "procrastination", "burnout"]
    },
    "和朋友吵架": {
        "description": "和朋友发生矛盾",
        "roles": ["你", "朋友"],
        "target_words": ["salty", "shade", "ghost"]
    },
    "相亲": {
        "description": "第一次相亲见面",
        "roles": ["你", "相亲对象"],
        "target_words": ["awkward", "vibe", "cringe"]
    }
}


def scenario_practice(scenario_name):
    """情景对话练习"""
    scenario = SCENARIOS[scenario_name]

    print(f"\n🎭 情景: {scenario['description']}")
    print(f"🎯 目标词汇: {', '.join(scenario['target_words'])}")
    print("\n" + "="*50)

    prompt = f"""你是一个英语口语教练。模拟以下场景的对话：

场景: {scenario['description']}
角色: {', '.join(scenario['roles'])}
要求用到的词汇: {', '.join(scenario['target_words'])}

请生成一段3-5轮的对话示例，展示这些词汇的自然用法。
格式：
角色: 对话内容
中文翻译

然后给出练习任务：让用户用这些词造句。"""

    try:
        response = client.chat.completions.create(
            model="claude-3-5-sonnet-20241022",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=800
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"❌ 生成失败: {str(e)}")


# ==================== 闯关游戏 ====================

class VocabGame:
    def __init__(self):
        self.level = 1
        self.score = 0
        self.lives = 3

    def start_level(self, level_name):
        """开始新关卡"""
        words = VOCABULARY.get(level_name, VOCABULARY["初级"])

        print(f"\n🎮 关卡 {self.level}: {level_name}")
        print(f"❤️  生命值: {self.lives}")
        print(f"⭐ 得分: {self.score}")
        print("="*50)

        # 随机选5个词
        selected = random.sample(words, min(5, len(words)))

        for i, vocab in enumerate(selected, 1):
            print(f"\n【第 {i} 题】")

            # 随机选择题型
            question_type = random.choice(["英译中", "中译英", "造句"])

            if question_type == "英译中":
                print(f"单词: {vocab['word']}")
                answer = input("中文意思是: ").strip()
                correct = answer in vocab['meaning']

            elif question_type == "中译英":
                print(f"中文: {vocab['meaning']}")
                answer = input("英文单词是: ").strip().lower()
                correct = answer == vocab['word'].lower()

            else:  # 造句
                print(f"用 '{vocab['word']}' ({vocab['meaning']}) 造个句子:")
                sentence = input("你的句子: ").strip()

                if vocab['word'].lower() in sentence.lower():
                    print("✅ 很好！让AI帮你改进一下...")
                    # 调用AI改进句子
                    self.improve_sentence(sentence, vocab['word'], vocab['meaning'])
                    correct = True
                else:
                    print(f"❌ 句子里要包含 '{vocab['word']}' 哦")
                    correct = False

            if correct:
                self.score += 10
                print(f"✅ 正确！+10分")
                # 生成搞笑例句作为奖励
                print("\n🎁 奖励：AI生成的爆笑例句！")
                print(generate_funny_example(vocab['word'], vocab['meaning']))
            else:
                self.lives -= 1
                print(f"❌ 错误！正确答案: {vocab['meaning'] if question_type == '英译中' else vocab['word']}")
                print(f"❤️  剩余生命: {self.lives}")

            if self.lives == 0:
                print("\n💀 游戏结束！")
                print(f"最终得分: {self.score}")
                return False

            input("\n按回车继续...")

        self.level += 1
        print(f"\n🎉 通关！进入下一关！")
        return True

    def improve_sentence(self, sentence, word, meaning):
        """AI改进用户造的句子"""
        prompt = f"""用户用单词 '{word}' ({meaning}) 造了个句子：

{sentence}

请：
1. 指出语法错误（如果有）
2. 给出更地道的表达方式
3. 用emoji让反馈更有趣"""

        try:
            response = client.chat.completions.create(
                model="claude-3-5-haiku-20241022",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            print(response.choices[0].message.content)
        except Exception as e:
            print(f"(AI改进失败: {str(e)})")


# ==================== 记忆曲线复习 ====================

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


def add_to_review(word, meaning):
    """添加到复习计划（艾宾浩斯曲线）"""
    progress = load_progress()

    now = datetime.now()
    review_dates = [
        now + timedelta(hours=1),      # 1小时后
        now + timedelta(days=1),        # 1天后
        now + timedelta(days=2),        # 2天后
        now + timedelta(days=4),        # 4天后
        now + timedelta(days=7),        # 7天后
        now + timedelta(days=15),       # 15天后
    ]

    progress[word] = {
        "meaning": meaning,
        "first_learn": now.isoformat(),
        "review_dates": [d.isoformat() for d in review_dates],
        "review_count": 0
    }

    save_progress(progress)


def get_today_review():
    """获取今天要复习的单词"""
    progress = load_progress()
    today = datetime.now()

    to_review = []
    for word, data in progress.items():
        review_dates = [datetime.fromisoformat(d) for d in data['review_dates']]
        if data['review_count'] < len(review_dates):
            next_review = review_dates[data['review_count']]
            if next_review <= today:
                to_review.append((word, data['meaning']))

    return to_review


def review_session():
    """复习环节"""
    to_review = get_today_review()

    if not to_review:
        print("\n✅ 今天没有要复习的单词！")
        return

    print(f"\n📚 今日复习: {len(to_review)} 个单词")
    print("="*50)

    for word, meaning in to_review:
        print(f"\n单词: {word}")
        answer = input("回忆一下中文意思: ").strip()

        if answer in meaning:
            print(f"✅ 正确！意思是: {meaning}")
            # 更新复习次数
            progress = load_progress()
            progress[word]['review_count'] += 1
            save_progress(progress)
        else:
            print(f"❌ 答案: {meaning}")
            print("\n复习一下例句:")
            print(generate_funny_example(word, meaning))

        input("\n按回车继续...")


# ==================== 主菜单 ====================

def main_menu():
    """主菜单"""
    print("\n" + "="*50)
    print("🎓 超有趣口语词汇训练工具")
    print("="*50)
    print("\n1. 🎮 词汇闯关游戏")
    print("2. 🎭 情景对话训练")
    print("3. 🤣 AI生成爆笑例句")
    print("4. 📚 今日复习（记忆曲线）")
    print("5. 📊 学习统计")
    print("6. 🚪 退出")

    choice = input("\n选择功能 (1-6): ").strip()

    if choice == "1":
        game = VocabGame()
        for level_name in ["初级", "中级", "高级"]:
            if not game.start_level(level_name):
                break

    elif choice == "2":
        print("\n选择情景:")
        for i, scenario in enumerate(SCENARIOS.keys(), 1):
            print(f"{i}. {scenario}")

        idx = int(input("\n选择 (1-{}): ".format(len(SCENARIOS)))) - 1
        scenario_name = list(SCENARIOS.keys())[idx]
        scenario_practice(scenario_name)

    elif choice == "3":
        word = input("\n输入单词: ").strip()
        meaning = input("输入中文意思: ").strip()
        print("\n🤣 AI正在生成爆笑例句...")
        print(generate_funny_example(word, meaning))
        add_to_review(word, meaning)

    elif choice == "4":
        review_session()

    elif choice == "5":
        progress = load_progress()
        print(f"\n📊 学习统计")
        print(f"已学单词: {len(progress)} 个")
        print(f"今日待复习: {len(get_today_review())} 个")

    elif choice == "6":
        print("\n👋 再见！Keep learning!")
        return False

    return True


# ==================== 主程序 ====================

if __name__ == "__main__":
    print("🎉 欢迎使用超有趣口语词汇训练工具！")
    print("💡 亮点: AI爆笑例句 + 闯关游戏 + 情景对话")

    while True:
        if not main_menu():
            break
