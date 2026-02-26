#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
猜数字游戏
- 随机生成1-100的数字
- 用户有4次猜测机会
- 每次提示太大或太小
"""

import random

def guess_number_game():
    """猜数字游戏主函数"""
    # 随机生成1-100的数字
    target_number = random.randint(1, 100)
    max_attempts = 4
    attempts = 0
    
    print("=" * 40)
    print("欢迎来到猜数字游戏！")
    print("我已经想好了一个1到100之间的数字")
    print(f"你有{max_attempts}次机会来猜中它！")
    print("=" * 40)
    
    while attempts < max_attempts:
        attempts += 1
        remaining = max_attempts - attempts + 1
        
        try:
            guess = int(input(f"\n第{attempts}次猜测（还剩{remaining}次机会），请输入你的猜测: "))
            
            # 检查输入是否在有效范围内
            if guess < 1 or guess > 100:
                print("请输入1到100之间的数字！")
                attempts -= 1  # 不计算这次无效尝试
                continue
            
            # 判断猜测结果
            if guess == target_number:
                print(f"\n🎉 恭喜你！你猜对了！")
                print(f"答案就是 {target_number}，你用了 {attempts} 次机会！")
                return True
            elif guess < target_number:
                print(f"太小了！提示：目标数字比 {guess} 大")
            else:
                print(f"太大了！提示：目标数字比 {guess} 小")
                
        except ValueError:
            print("请输入一个有效的数字！")
            attempts -= 1  # 不计算这次无效尝试
            continue
    
    # 如果4次机会都用完了
    print(f"\n😢 很遗憾，你已经用完了所有{max_attempts}次机会！")
    print(f"正确答案是：{target_number}")
    return False

def main():
    """主函数"""
    while True:
        guess_number_game()
        
        # 询问是否继续游戏
        play_again = input("\n是否再玩一次？(输入 'y' 或 'yes' 继续，其他任意键退出): ").lower()
        if play_again not in ['y', 'yes']:
            print("感谢游玩，再见！")
            break

if __name__ == "__main__":
    main()

