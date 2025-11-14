import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def calculate_technical_indicators(df):
    """计算各种技术指标"""

    # 确保数据按日期排序
    df = df.sort_index()

    # 移动平均线
    df['MA5'] = df['收盘'].rolling(window=5).mean()
    df['MA10'] = df['收盘'].rolling(window=10).mean()
    df['MA20'] = df['收盘'].rolling(window=20).mean()
    df['MA60'] = df['收盘'].rolling(window=60).mean()

    # 指数移动平均线
    df['EMA12'] = df['收盘'].ewm(span=12).mean()
    df['EMA26'] = df['收盘'].ewm(span=26).mean()

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

    df['RSI14'] = calculate_rsi(df['收盘'], 14)
    df['RSI6'] = calculate_rsi(df['收盘'], 6)

    # 布林带
    df['BB_Middle'] = df['收盘'].rolling(window=20).mean()
    bb_std = df['收盘'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
    df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
    df['BB_Width'] = (df['BB_Upper'] - df['BB_Lower']) / df['BB_Middle']

    # 成交量相关
    df['Volume_MA5'] = df['成交量'].rolling(window=5).mean()
    df['Volume_Ratio'] = df['成交量'] / df['Volume_MA5']

    # 价格位置
    df['Price_vs_MA20'] = (df['收盘'] - df['MA20']) / df['MA20'] * 100
    df['Price_vs_MA60'] = (df['收盘'] - df['MA60']) / df['MA60'] * 100

    # 波动率
    df['Volatility'] = df['收盘'].pct_change().rolling(window=20).std() * 100

    return df


def analyze_trend(df):
    """分析趋势强度"""
    current_price = df['收盘'].iloc[-1]

    # 均线排列分析
    ma_conditions = 0
    total_ma_conditions = 4

    if df['MA5'].iloc[-1] > df['MA10'].iloc[-1]:
        ma_conditions += 1
    if df['MA10'].iloc[-1] > df['MA20'].iloc[-1]:
        ma_conditions += 1
    if df['MA20'].iloc[-1] > df['MA60'].iloc[-1]:
        ma_conditions += 1
    if current_price > df['MA20'].iloc[-1]:
        ma_conditions += 1

    trend_strength = ma_conditions / total_ma_conditions

    return trend_strength


def analyze_momentum(df):
    """分析动量指标"""
    momentum_score = 0
    total_factors = 4

    # MACD分析
    if df['MACD'].iloc[-1] > 0 and df['DIF'].iloc[-1] > df['DEA'].iloc[-1]:
        momentum_score += 1

    # RSI分析
    rsi14 = df['RSI14'].iloc[-1]
    if 30 < rsi14 < 70:  # 避免超买超卖
        momentum_score += 1
    elif rsi14 > 50:  # 偏强
        momentum_score += 0.5

    # 价格位置
    if df['Price_vs_MA20'].iloc[-1] > 0:
        momentum_score += 1

    # 布林带位置
    if df['收盘'].iloc[-1] > df['BB_Middle'].iloc[-1]:
        momentum_score += 1

    return momentum_score / total_factors


def analyze_volume(df):
    """分析成交量"""
    volume_score = 0
    total_factors = 2

    # 量比
    volume_ratio = df['Volume_Ratio'].iloc[-1]
    if 0.8 < volume_ratio < 2:  # 正常放量
        volume_score += 1
    elif volume_ratio > 1.2:  # 温和放量
        volume_score += 0.5

    # 成交量趋势
    if df['成交量'].iloc[-1] > df['Volume_MA5'].iloc[-1]:
        volume_score += 1

    return volume_score / total_factors


def analyze_support_resistance(df):
    """分析支撑阻力"""
    support_score = 0
    total_factors = 3

    current_price = df['收盘'].iloc[-1]

    # 布林带下轨支撑
    if current_price > df['BB_Lower'].iloc[-1]:
        support_score += 1

    # MA20支撑
    if current_price > df['MA20'].iloc[-1]:
        support_score += 1

    # MA60支撑
    if current_price > df['MA60'].iloc[-1]:
        support_score += 1

    return support_score / total_factors


def calculate_buy_probability(stock_code):
    """计算买入概率"""
    try:
        # 获取股票数据
        print(f"正在获取 {stock_code} 的数据...")

        # 尝试不同的数据接口
        try:
            stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20200101", adjust="qfq")
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data.set_index('日期', inplace=True)
            # 重命名列以匹配后续代码
            stock_data = stock_data.rename(columns={'收盘': '收盘', '成交量': '成交量'})
        except:
            # 如果第一个接口失败，尝试另一个
            stock_data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", adjust="qfq")
            stock_data['日期'] = pd.to_datetime(stock_data['日期'])
            stock_data.set_index('日期', inplace=True)
            stock_data = stock_data.rename(columns={'收盘': '收盘', '成交量': '成交量'})

        if len(stock_data) < 100:
            return 0, "数据不足，无法进行有效分析"
        else:
            print(f"获取 {stock_code} 的数据成功, 获取条数{len(stock_data)}！")

        # 计算技术指标
        df = calculate_technical_indicators(stock_data)

        # 移除NaN值
        df = df.dropna()

        if len(df) < 30:
            return 0, "有效数据不足"

        # 各项分析得分
        trend_score = analyze_trend(df)
        momentum_score = analyze_momentum(df)
        volume_score = analyze_volume(df)
        support_score = analyze_support_resistance(df)

        # 计算综合概率（加权平均）
        weights = {
            'trend': 0.35,  # 趋势最重要
            'momentum': 0.30,  # 动量次重要
            'support': 0.20,  # 支撑阻力
            'volume': 0.15  # 成交量
        }

        total_probability = (
                                    trend_score * weights['trend'] +
                                    momentum_score * weights['momentum'] +
                                    support_score * weights['support'] +
                                    volume_score * weights['volume']
                            ) * 100

        # 生成分析报告
        analysis_report = generate_analysis_report(df, trend_score, momentum_score, volume_score, support_score)

        return round(total_probability, 2), analysis_report

    except Exception as e:
        return 0, f"分析过程中出现错误: {str(e)}"


def generate_analysis_report(df, trend_score, momentum_score, volume_score, support_score):
    """生成详细分析报告"""
    current_price = df['收盘'].iloc[-1]

    report = f"""
=== 股票技术分析报告 ===
当前价格: {current_price:.2f}

趋势分析 (权重35%):
- 5日均线: {df['MA5'].iloc[-1]:.2f}
- 10日均线: {df['MA10'].iloc[-1]:.2f}
- 20日均线: {df['MA20'].iloc[-1]:.2f}
- 60日均线: {df['MA60'].iloc[-1]:.2f}
- 趋势强度得分: {trend_score * 100:.1f}%

动量分析 (权重30%):
- MACD: {df['MACD'].iloc[-1]:.4f}
- RSI(14): {df['RSI14'].iloc[-1]:.1f}
- 价格相对20日线: {df['Price_vs_MA20'].iloc[-1]:.1f}%
- 动量得分: {momentum_score * 100:.1f}%

支撑分析 (权重20%):
- 布林下轨: {df['BB_Lower'].iloc[-1]:.2f}
- 当前相对位置: {(current_price - df['BB_Lower'].iloc[-1]) / (df['BB_Upper'].iloc[-1] - df['BB_Lower'].iloc[-1]) * 100:.1f}%
- 支撑得分: {support_score * 100:.1f}%

成交量分析 (权重15%):
- 量比: {df['Volume_Ratio'].iloc[-1]:.2f}
- 成交量得分: {volume_score * 100:.1f}%

建议: {'可以考虑买入' if (trend_score + momentum_score + support_score + volume_score) / 4 > 0.6 else '建议观望'}
"""
    return report


# 使用示例
if __name__ == "__main__":
    # 输入股票代码（支持沪深A股）
    stock_code = "600815"  # 例如：平安银行

    probability, report = calculate_buy_probability(stock_code)

    print(f"\n买入概率: {probability}%")
    print(report)

    # 风险提示
    print("\n" + "=" * 50)
    print("风险提示: 此分析仅基于技术指标，不构成投资建议!")
    print("投资有风险，入市需谨慎!")
    print("=" * 50)
