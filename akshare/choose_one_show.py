import akshare as ak
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#import mplfinance as mpf
from datetime import datetime, timedelta
import matplotlib.dates as mdates

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


def calculate_technical_indicators(df):
    """计算各种技术指标"""

    # 确保数据按日期排序
    df = df.sort_index()

    # 移动平均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA60'] = df['close'].rolling(window=60).mean()

    # 指数移动平均线
    df['EMA12'] = df['close'].ewm(span=12).mean()
    df['EMA26'] = df['close'].ewm(span=26).mean()

    # MACD
    df['DIF'] = df['EMA12'] - df['EMA26']
    df['DEA'] = df['DIF'].ewm(span=9).mean()
    df['MACD'] = (df['DIF'] - df['DEA']) * 2

    # RSI
    def calculate_rsi(data, window=14):
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    df['RSI14'] = calculate_rsi(df['close'], 14)
    df['RSI6'] = calculate_rsi(df['close'], 6)

    # 布林带
    df['BB_Middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
    df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']

    # 成交量相关
    df['Volume_MA5'] = df['volume'].rolling(window=5).mean()
    df['Volume_Ratio'] = df['volume'] / df['Volume_MA5']

    # 价格位置
    df['Price_vs_MA20'] = (df['close'] - df['MA20']) / df['MA20'] * 100
    df['Price_vs_MA60'] = (df['close'] - df['MA60']) / df['MA60'] * 100

    # 波动率
    df['Volatility'] = df['close'].pct_change().rolling(window=20).std() * 100

    return df


def create_comprehensive_chart(stock_code, period=100):
    """创建综合技术分析图表"""

    try:
        # 获取股票数据
        print(f"正在获取 {stock_code} 的数据...")

        # 获取数据
        stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        stock_data['日期'] = pd.to_datetime(stock_data['日期'])
        stock_data.set_index('日期', inplace=True)

        # 重命名列以匹配mplfinance要求
        stock_data = stock_data.rename(columns={
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume'
        })

        # 只使用最近period天的数据
        if len(stock_data) > period:
            df = stock_data.iloc[-period:].copy()
        else:
            df = stock_data.copy()

        # 计算技术指标
        df = calculate_technical_indicators(df)
        df = df.dropna()

        # 创建图表
        fig = plt.figure(figsize=(16, 14))
        fig.suptitle(f'股票 {stock_code} 技术分析图表', fontsize=16, fontweight='bold')

        # 定义子图布局
        gs = plt.GridSpec(6, 1, figure=fig, height_ratios=[3, 1, 1, 1, 1, 1])

        # 1. K线图 + 移动平均线
        ax1 = fig.add_subplot(gs[0])
        ax1.set_title('K线图与移动平均线', fontsize=12, fontweight='bold')

        # 绘制K线
        dates = mdates.date2num(df.index)
        for i in range(len(df)):
            color = 'red' if df['close'].iloc[i] >= df['open'].iloc[i] else 'green'
            ax1.plot([dates[i], dates[i]], [df['low'].iloc[i], df['high'].iloc[i]],
                     color='black', linewidth=1)
            ax1.plot([dates[i], dates[i]], [df['open'].iloc[i], df['close'].iloc[i]],
                     color=color, linewidth=3)

        # 绘制移动平均线
        ax1.plot(dates, df['MA5'], label='MA5', color='blue', linewidth=1)
        ax1.plot(dates, df['MA10'], label='MA10', color='orange', linewidth=1)
        ax1.plot(dates, df['MA20'], label='MA20', color='green', linewidth=1.5)
        ax1.plot(dates, df['MA60'], label='MA60', color='red', linewidth=1.5)

        # 绘制布林带
        ax1.fill_between(dates, df['BB_Upper'], df['BB_Lower'], alpha=0.2, color='gray', label='布林带')
        ax1.plot(dates, df['BB_Upper'], color='gray', linewidth=0.5, alpha=0.7)
        ax1.plot(dates, df['BB_Lower'], color='gray', linewidth=0.5, alpha=0.7)

        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_ylabel('价格')

        # 2. 成交量
        ax2 = fig.add_subplot(gs[1], sharex=ax1)
        ax2.set_title('成交量', fontsize=12, fontweight='bold')

        # 绘制成交量柱状图
        colors = ['red' if close >= open else 'green' for close, open in zip(df['close'], df['open'])]
        ax2.bar(dates, df['volume'], color=colors, alpha=0.7, width=0.8)
        ax2.plot(dates, df['Volume_MA5'], color='blue', label='成交量MA5', linewidth=1)

        ax2.legend()
        ax2.grid(True, alpha=0.3)
        ax2.set_ylabel('成交量')

        # 3. MACD
        ax3 = fig.add_subplot(gs[2], sharex=ax1)
        ax3.set_title('MACD', fontsize=12, fontweight='bold')

        # 绘制MACD线
        ax3.plot(dates, df['DIF'], label='DIF', color='blue', linewidth=1)
        ax3.plot(dates, df['DEA'], label='DEA', color='red', linewidth=1)

        # 绘制MACD柱状图
        macd_colors = ['red' if x >= 0 else 'green' for x in df['MACD']]
        ax3.bar(dates, df['MACD'], color=macd_colors, alpha=0.5, width=0.8)

        # 零轴线
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.set_ylabel('MACD')

        # 4. RSI
        ax4 = fig.add_subplot(gs[3], sharex=ax1)
        ax4.set_title('RSI', fontsize=12, fontweight='bold')

        ax4.plot(dates, df['RSI14'], label='RSI14', color='purple', linewidth=1.5)
        ax4.plot(dates, df['RSI6'], label='RSI6', color='orange', linewidth=1, alpha=0.7)

        # 超买超卖线
        ax4.axhline(y=70, color='red', linestyle='--', linewidth=1, alpha=0.7, label='超买线')
        ax4.axhline(y=30, color='green', linestyle='--', linewidth=1, alpha=0.7, label='超卖线')
        ax4.axhline(y=50, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_ylabel('RSI')
        ax4.set_ylim(0, 100)

        # 5. 价格相对位置
        ax5 = fig.add_subplot(gs[4], sharex=ax1)
        ax5.set_title('价格相对位置 (%)', fontsize=12, fontweight='bold')

        ax5.plot(dates, df['Price_vs_MA20'], label='相对于MA20', color='blue', linewidth=1.5)
        ax5.plot(dates, df['Price_vs_MA60'], label='相对于MA60', color='red', linewidth=1.5)

        # 零轴线
        ax5.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

        ax5.legend()
        ax5.grid(True, alpha=0.3)
        ax5.set_ylabel('相对位置 %')

        # 6. 技术指标评分
        ax6 = fig.add_subplot(gs[5], sharex=ax1)
        ax6.set_title('技术指标信号强度', fontsize=12, fontweight='bold')

        # 计算各项指标的信号强度（简化版）
        trend_signal = np.where(df['close'] > df['MA20'], 1, -1) * 0.35
        macd_signal = np.where(df['MACD'] > 0, 1, -1) * 0.30
        rsi_signal = np.where(df['RSI14'] > 50, 1, -1) * 0.20
        volume_signal = np.where(df['Volume_Ratio'] > 1, 1, -1) * 0.15

        total_signal = trend_signal + macd_signal + rsi_signal + volume_signal

        # 绘制信号强度
        ax6.plot(dates, total_signal, label='综合信号', color='black', linewidth=2)
        ax6.fill_between(dates, 0, total_signal, where=total_signal >= 0,
                         color='red', alpha=0.3, label='买入信号')
        ax6.fill_between(dates, 0, total_signal, where=total_signal < 0,
                         color='green', alpha=0.3, label='卖出信号')

        ax6.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax6.legend()
        ax6.grid(True, alpha=0.3)
        ax6.set_ylabel('信号强度')
        ax6.set_xlabel('日期')

        # 设置x轴日期格式
        date_format = mdates.DateFormatter('%m-%d')
        for ax in [ax1, ax2, ax3, ax4, ax5, ax6]:
            ax.xaxis.set_major_formatter(date_format)

        # 自动调整布局
        plt.tight_layout()
        plt.show()

        # 打印当前技术指标值
        print_current_indicators(df, stock_code)

        return df

    except Exception as e:
        print(f"创建图表时出现错误: {str(e)}")
        return None


def print_current_indicators(df, stock_code):
    """打印当前技术指标值"""
    current = df.iloc[-1]

    print(f"\n{'=' * 60}")
    print(f"股票 {stock_code} 当前技术指标分析")
    print(f"{'=' * 60}")

    print(f"\n📈 价格信息:")
    print(f"   当前价格: {current['close']:.2f}")
    print(f"   相对20日线: {current['Price_vs_MA20']:+.2f}%")
    print(f"   相对60日线: {current['Price_vs_MA60']:+.2f}%")

    print(f"\n🎯 趋势指标:")
    print(f"   MA5: {current['MA5']:.2f} | MA20: {current['MA20']:.2f} | MA60: {current['MA60']:.2f}")
    print(f"   布林带位置: [{current['BB_Lower']:.2f}, {current['BB_Upper']:.2f}]")

    print(f"\n⚡ 动量指标:")
    print(f"   MACD: {current['MACD']:.4f} | DIF: {current['DIF']:.4f} | DEA: {current['DEA']:.4f}")
    print(f"   RSI14: {current['RSI14']:.1f} | RSI6: {current['RSI6']:.1f}")

    print(f"\n📊 成交量:")
    print(f"   当日成交量: {current['volume']:,.0f}")
    print(f"   量比: {current['Volume_Ratio']:.2f}")

    # 生成简单建议
    suggestion = generate_suggestion(current)
    print(f"\n💡 技术分析建议:")
    print(f"   {suggestion}")


def generate_suggestion(current):
    """根据技术指标生成简单建议"""
    suggestions = []

    # 趋势判断
    if current['close'] > current['MA20'] and current['MA5'] > current['MA20']:
        suggestions.append("趋势向上")
    elif current['close'] < current['MA20'] and current['MA5'] < current['MA20']:
        suggestions.append("趋势向下")
    else:
        suggestions.append("趋势震荡")

    # MACD判断
    if current['MACD'] > 0 and current['DIF'] > current['DEA']:
        suggestions.append("MACD金叉")
    elif current['MACD'] < 0 and current['DIF'] < current['DEA']:
        suggestions.append("MACD死叉")

    # RSI判断
    if current['RSI14'] > 70:
        suggestions.append("RSI超买")
    elif current['RSI14'] < 30:
        suggestions.append("RSI超卖")
    else:
        suggestions.append("RSI正常")

    # 成交量判断
    if current['Volume_Ratio'] > 1.5:
        suggestions.append("放量明显")
    elif current['Volume_Ratio'] < 0.8:
        suggestions.append("缩量调整")

    return " | ".join(suggestions)


def create_mplfinance_chart(stock_code, period=60):
    """使用mplfinance创建专业的K线图"""
    try:
        # 获取数据
        stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
        stock_data['日期'] = pd.to_datetime(stock_data['日期'])
        stock_data.set_index('日期', inplace=True)

        # 重命名列
        stock_data = stock_data.rename(columns={
            '开盘': 'Open',
            '收盘': 'Close',
            '最高': 'High',
            '最低': 'Low',
            '成交量': 'Volume'
        })

        # 只使用最近period天的数据
        if len(stock_data) > period:
            df = stock_data.iloc[-period:].copy()
        else:
            df = stock_data.copy()

        # 计算移动平均线
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA20'] = df['Close'].rolling(20).mean()

        """
        # 创建额外的图
        apds = [
            mpf.make_addplot(df['MA5'], color='blue', width=1, panel=0),
            mpf.make_addplot(df['MA20'], color='red', width=1.5, panel=0),
        ]

        # 创建图表
        fig, axes = mpf.plot(df,
                             type='candle',
                             style='charles',
                             addplot=apds,
                             title=f'股票 {stock_code} K线图',
                             ylabel='价格',
                             volume=True,
                             ylabel_lower='成交量',
                             figsize=(16, 10),
                             returnfig=True)
        """
        plt.show()

    except Exception as e:
        print(f"创建mplfinance图表时出现错误: {str(e)}")


# 使用示例
if __name__ == "__main__":
    # 输入股票代码
    stock_code = "600815"  # 例如：平安银行

    # 创建综合技术分析图表
    df = create_comprehensive_chart(stock_code, period=100)

    # 也可以创建专业的K线图
    # create_mplfinance_chart(stock_code, period=60)

    print("\n" + "=" * 60)
    print("风险提示: 技术分析仅供参考，不构成投资建议!")
    print("投资有风险，入市需谨慎!")
    print("=" * 60)
