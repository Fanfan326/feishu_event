#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💣 单词炸弹 - 超刺激的词汇闯关游戏
亮点：限时答题 + 连击系统 + Boss关卡 + 成就系统
"""

import random
import time
import os

# ASCII 艺术
BOMB_ASCII = """
    💣
   ╱|╲
  ╱ | ╲
 ╱  |  ╲
╱___|___╲
"""

EXPLOSION = """
    💥💥💥
  💥  💥  💥
 💥   💥   💥
💥    💥    💥
 💥   💥   💥
  💥  💥  💥
    💥💥💥
"""

# 词汇库（按难度分类）
WORDS = {
    "简单": [
        {"word": "cat", "hint": "喵喵叫的动物", "answer": "猫"},
        {"word": "dog", "hint": "汪汪叫的动物", "answer": "狗"},
        {"word": "happy", "hint": "开心的", "answer": "开心"},
        {"word": "run", "hint": "跑步", "answer": "跑"},
        {"word": "book", "hint": "用来阅读的", "answer": "书"},
        {"word": "water", "hint": "H2O", "answer": "水"},
        {"word": "fire", "hint": "🔥", "answer": "火"},
        {"word": "love", "hint": "❤️", "answer": "爱"},
        {"word": "dream", "hint": "睡觉时做的", "answer": "梦"},
        {"word": "smile", "hint": "😊", "answer": "微笑"},
    ],
    "中等": [
        {"word": "awkward", "hint": "尴尬的", "answer": "尴尬"},
        {"word": "ghost", "hint": "👻突然消失", "answer": "消失"},
        {"word": "vibe", "hint": "氛围感觉", "answer": "氛围"},
        {"word": "flex", "hint": "💪炫耀", "answer": "炫耀"},
        {"word": "savage", "hint": "毒舌的", "answer": "毒舌"},
        {"word": "cringe", "hint": "尴尬到缩", "answer": "尴尬"},
        {"word": "salty", "hint": "生气不爽", "answer": "生气"},
        {"word": "lowkey", "hint": "低调地", "answer": "低调"},
        {"word": "sus", "hint": "可疑的", "answer": "可疑"},
        {"word": "simp", "hint": "舔狗", "answer": "舔狗"},
    ],
    "困难": [
        {"word": "serendipity", "hint": "意外惊喜", "answer": "惊喜"},
        {"word": "ephemeral", "hint": "短暂的", "answer": "短暂"},
        {"word": "ubiquitous", "hint": "无处不在", "answer": "无处不在"},
        {"word": "juxtaposition", "hint": "并列对比", "answer": "对比"},
        {"word": "schadenfreude", "hint": "幸灾乐祸", "answer": "幸灾乐祸"},
        {"word": "procrastinate", "hint": "拖延症", "answer": "拖延"},
        {"word": "overwhelmed", "hint": "不知所措", "answer": "不知所措"},
        {"word": "burnout", "hint": "精疲力竭", "answer": "精疲力竭"},
        {"word": "existential", "hint": "存在主义", "answer": "存在"},
        {"word": "cathartic", "hint": "宣泄的", "answer": "宣泄"},
    ]
}

# Boss 单词（超难）
BOSS_WORDS = [
    {"word": "antidisestablishmentarianism", "hint": "最长英文单词之一", "answer": "反对废除国教主义"},
    {"word": "pneumonoultramicroscopicsilicovolcanoconiosis", "hint": "超级长的医学术语", "answer": "肺病"},
    {"word": "supercalifragilisticexpialidocious", "hint": "迪士尼电影《欢乐满人间》", "answer": "好极了"},
]


class WordBombGame:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.level = 1
        self.lives = 3
        self.achievements = []

    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def show_bomb(self, seconds):
        """显示炸弹倒计时"""
        print(BOMB_ASCII)
        print(f"⏰ 倒计时: {seconds} 秒")
        print(f"💥 生命值: {'❤️ ' * self.lives}")
        print(f"⭐ 得分: {self.score}")
        print(f"🔥 连击: {self.combo}x")

    def countdown(self, question, time_limit):
        """限时答题"""
        print(f"\n📝 单词: {question['word']}")
        print(f"💡 提示: {question['hint']}")
        print(f"⏰ 时间: {time_limit} 秒")

        start_time = time.time()
        answer = input("\n你的答案: ").strip()
        elapsed = time.time() - start_time

        if elapsed > time_limit:
            print("\n" + EXPLOSION)
            print("💥 时间到！炸弹爆炸了！")
            return False, 0

        if answer in question['answer'] or answer == question['word']:
            bonus = max(0, int((time_limit - elapsed) * 10))
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            points = 10 + bonus + (self.combo * 5)
            self.score += points

            print(f"\n✅ 正确！+{points}分")
            print(f"🔥 连击: {self.combo}x")

            # 检查成就
            self.check_achievements()

            return True, points
        else:
            print(f"\n❌ 错误！正确答案: {question['answer']}")
            self.combo = 0
            return False, 0

    def check_achievements(self):
        """检查成就"""
        achievements = []

        if self.combo == 5 and "5连击" not in self.achievements:
            achievements.append("🏆 成就解锁：5连击")
            self.achievements.append("5连击")

        if self.combo == 10 and "10连击" not in self.achievements:
            achievements.append("🏆 成就解锁：连击高手")
            self.achievements.append("10连击")

        if self.score >= 100 and "百分小子" not in self.achievements:
            achievements.append("🏆 成就解锁：百分小子")
            self.achievements.append("百分小子")

        if self.score >= 500 and "单词大师" not in self.achievements:
            achievements.append("🏆 成就解锁：单词大师")
            self.achievements.append("单词大师")

        for ach in achievements:
            print(ach)

    def play_level(self, difficulty, num_questions):
        """玩一个关卡"""
        print(f"\n{'='*60}")
        print(f"🎮 关卡 {self.level}: {difficulty}")
        print(f"{'='*60}")

        words = random.sample(WORDS[difficulty], min(num_questions, len(WORDS[difficulty])))

        # 根据难度设置时间
        time_limits = {"简单": 10, "中等": 8, "困难": 6}
        time_limit = time_limits[difficulty]

        for i, question in enumerate(words, 1):
            print(f"\n【第 {i}/{num_questions} 题】")
            self.show_bomb(time_limit)

            correct, points = self.countdown(question, time_limit)

            if not correct:
                self.lives -= 1
                if self.lives == 0:
                    return False

            time.sleep(1)

        return True

    def boss_battle(self):
        """Boss 关卡"""
        print("\n" + "="*60)
        print("👾 BOSS 关卡！超级单词挑战！")
        print("="*60)

        boss = random.choice(BOSS_WORDS)

        print("\n⚠️  警告：超长单词来袭！")
        print(f"💡 提示: {boss['hint']}")
        print(f"📝 单词: {boss['word']}")
        print(f"   长度: {len(boss['word'])} 个字母！")

        print("\n选择策略:")
        print("1. 直接拼写单词（+100分）")
        print("2. 回答中文意思（+50分）")

        choice = input("\n选择 (1/2): ").strip()

        if choice == "1":
            answer = input("\n拼写单词: ").strip()
            if answer.lower() == boss['word'].lower():
                self.score += 100
                print("\n🎉 太厉害了！Boss被击败！+100分")
                return True
        else:
            answer = input("\n中文意思: ").strip()
            if answer in boss['answer']:
                self.score += 50
                print("\n✅ 正确！Boss被击退！+50分")
                return True

        print(f"\n❌ 失败！正确答案: {boss['answer']}")
        print(f"   单词: {boss['word']}")
        self.lives -= 1
        return False

    def show_final_stats(self):
        """显示最终统计"""
        print("\n" + "="*60)
        print("🎮 游戏结束！")
        print("="*60)
        print(f"\n最终得分: {self.score}")
        print(f"最高连击: {self.max_combo}x")
        print(f"通关关卡: {self.level - 1}")

        if self.achievements:
            print(f"\n🏆 解锁成就:")
            for ach in self.achievements:
                print(f"   • {ach}")

        # 评级
        if self.score >= 500:
            print("\n🌟 评级: S - 单词大师！")
        elif self.score >= 300:
            print("\n🌟 评级: A - 词汇高手！")
        elif self.score >= 150:
            print("\n🌟 评级: B - 不错哦！")
        else:
            print("\n🌟 评级: C - 继续努力！")

    def start(self):
        """开始游戏"""
        self.clear_screen()

        print("="*60)
        print("💣 单词炸弹 - 限时闯关游戏")
        print("="*60)
        print("\n🎯 游戏规则:")
        print("1. 限时回答单词意思")
        print("2. 超时炸弹爆炸，扣生命值")
        print("3. 连续答对有连击加分")
        print("4. 3条生命用完游戏结束")
        print("5. 每5关有Boss挑战")

        input("\n按回车开始游戏...")

        # 关卡序列
        levels = [
            ("简单", 3),
            ("简单", 4),
            ("中等", 3),
            ("中等", 4),
            ("困难", 3),
        ]

        for difficulty, num_q in levels:
            if not self.play_level(difficulty, num_q):
                break

            self.level += 1

            # 每3关有Boss
            if self.level % 3 == 0 and self.lives > 0:
                if not self.boss_battle():
                    if self.lives == 0:
                        break
                self.level += 1

        self.show_final_stats()


def main():
    """主函数"""
    while True:
        game = WordBombGame()
        game.start()

        play_again = input("\n再玩一次？(y/n): ").strip().lower()
        if play_again != 'y':
            print("\n👋 再见！Keep learning!")
            break


if __name__ == "__main__":
    main()
