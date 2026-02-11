import traceback

import akshare as ak
import pandas as pd
import json
import os
from datetime import datetime
import time

# 缓存文件定义
CACHE_FILE = "high_dividend_cache.csv"  # 缓存结果文件
STATUS_FILE = "process_status.json"  # 处理状态文件
PRICE_CACHE_DIR = "price_cache"  # 股价数据缓存目录
EXPIRE_TIME = 15 * 24 * 3600  # 缓存过期时间（15天）


def load_status():
    """加载上次的处理状态"""
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None


def save_status(processed_codes, params, start_index=0):
    """保存当前处理状态"""
    status = {
        'processed_codes': processed_codes,
        'params': params,
        'start_index': start_index,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    with open(STATUS_FILE, 'w', encoding='utf-8') as f:
        json.dump(status, f, ensure_ascii=False, indent=2)


def load_cache():
    """加载已缓存的结果"""
    if os.path.exists(CACHE_FILE):
        return pd.read_csv(CACHE_FILE, dtype={'股票代码': str})
    return pd.DataFrame()


def save_cache(df):
    """保存结果到缓存"""
    if not df.empty:
        df.to_csv(CACHE_FILE, index=False, encoding='utf_8_sig')
        print(f"结果已缓存至 {CACHE_FILE}")


def get_price_cache_filename(code, start_date, end_date):
    """生成股价缓存文件名"""
    return os.path.join(PRICE_CACHE_DIR, f"{code}_{start_date}_{end_date}.csv")


def load_price_from_cache(code, start_date, end_date):
    """load stock price data from cache"""
    cache_file = get_price_cache_filename(code, start_date, end_date)
    if os.path.exists(cache_file):
        try:
            # 检查缓存文件是否过期（超过1天）
            cache_time = os.path.getmtime(cache_file)
            current_time = time.time()
            if current_time - cache_time < EXPIRE_TIME:
                return pd.read_csv(cache_file)
        except Exception:
            pass
    return None


def save_price_to_cache(price_df, code, start_date, end_date):
    """save stock prices to cache"""
    if not os.path.exists(PRICE_CACHE_DIR):
        os.makedirs(PRICE_CACHE_DIR)

    cache_file = get_price_cache_filename(code, start_date, end_date)
    try:
        price_df.to_csv(cache_file, index=False, encoding='utf_8_sig')
    except Exception:
        pass


def get_stock_price_with_cache(code, start_date, end_date):
    """获取股价数据（带缓存）"""
    # 先尝试从缓存加载
    price_df = load_price_from_cache(code, start_date, end_date)
    if price_df is not None and not price_df.empty:
        return price_df

    # 缓存不存在或过期，从网络获取
    try:
        price_df = ak.stock_zh_a_hist(symbol=code, period="daily",
                                      start_date=start_date, end_date=end_date, adjust="qfq")
        if not price_df.empty:
            # 保存到缓存
            save_price_to_cache(price_df, code, start_date, end_date)
        return price_df
    except Exception:
        return pd.DataFrame()


def get_high_dividend_stocks(years=3, min_dividend_per_share=0.1,
                             min_dividend_yield_threshold=1.0,
                             reset=False):
    """
    找出近些年高分红的A股股票（支持断点续跑）

    Parameters:
    years (int): 考察连续分红的年份数
    min_dividend_per_share (float): 每股现金分红的最小平均金额（元）
    min_dividend_yield_threshold (float): 平均股息率的最小百分比（%）
    reset (bool): 是否重置缓存和状态，重新开始
    """
    # 如果选择重置，则清除旧状态
    if reset:
        if os.path.exists(CACHE_FILE):
            os.remove(CACHE_FILE)
        if os.path.exists(STATUS_FILE):
            os.remove(STATUS_FILE)
        print("已清除所有缓存和状态，重新开始扫描。")
        cache_df = pd.DataFrame()
        processed_codes = []
        start_index = 0
    else:
        # 尝试加载缓存和状态
        cache_df = load_cache()
        status = load_status()

        # 检查状态是否有效（参数是否一致）
        valid_status = False
        if status:
            status_params = status['params']
            if (status_params.get('years') == years and
                    status_params.get('min_dividend_per_share') == min_dividend_per_share and
                    status_params.get('min_dividend_yield_threshold') == min_dividend_yield_threshold):
                valid_status = True
                processed_codes = status['processed_codes']
                start_index = status['start_index']
                print(f"恢复上次处理状态，已处理 {len(processed_codes)} 只股票，将从第 {start_index + 1} 只开始。")
            else:
                print("检测到筛选参数已变更，将重新开始扫描。")

        if not valid_status:
            processed_codes = []
            start_index = 0
            if not cache_df.empty:
                print(f"加载了 {len(cache_df)} 条历史缓存结果。")

    # 获取所有A股列表
    print("获取A股上市公司名单...")
    stock_info = ak.stock_info_a_code_name()
    stock_codes = stock_info['code'].tolist()
    total_stocks = len(stock_codes)
    print(f"共 {total_stocks} 只A股股票。")

    # 准备结果列表（从缓存开始）
    results = cache_df.to_dict('records') if not cache_df.empty else []

    # 记录当前参数
    current_params = {
        'years': years,
        'min_dividend_per_share': min_dividend_per_share,
        'min_dividend_yield_threshold': min_dividend_yield_threshold
    }

    # 遍历股票（从断点开始）
    for i in range(start_index, total_stocks):
        code = stock_codes[i]

        # 如果已处理过，则跳过（针对重置后重新读取缓存的情况）
        if code in processed_codes:
            continue

        # 进度显示
        if (i + 1) % 10 == 0:
            print(
                f"进度: {i + 1}/{total_stocks} ({(i + 1) / total_stocks * 100:.1f}%)， 当前已找到 {len(results)} 只高分红股票")
            # 每隔50只股票自动保存一次状态和缓存
            if (i + 1) % 50 == 0:
                save_status(processed_codes, current_params, i)
                if results:
                    temp_df = pd.DataFrame(results)
                    save_cache(temp_df)

        try:
            # 获取分红详情
            fhps_df = ak.stock_fhps_detail_em(symbol=code)
            if fhps_df.empty:
                processed_codes.append(code)
                continue

            # 数据预处理 - 适应新的列名结构
            # 检查是否有报告期和现金分红相关列
            if '报告期' not in fhps_df.columns or '现金分红-现金分红比例' not in fhps_df.columns:
                processed_codes.append(code)
                continue

            # 过滤有效的现金分红数据
            fhps_df = fhps_df[fhps_df['现金分红-现金分红比例'].notna()]
            fhps_df['现金分红-现金分红比例'] = pd.to_numeric(fhps_df['现金分红-现金分红比例'], errors='coerce')
            fhps_df = fhps_df.dropna(subset=['现金分红-现金分红比例'])

            # 过滤掉现金分红比例为0的记录
            fhps_df = fhps_df[fhps_df['现金分红-现金分红比例'] > 0]
            if fhps_df.empty:
                processed_codes.append(code)
                continue

            # 从报告期提取年份信息
            fhps_df['年份'] = pd.to_datetime(fhps_df['报告期'], errors='coerce').dt.year
            fhps_df = fhps_df.dropna(subset=['年份'])

            # 检查近 years 年的分红连续性
            current_year = datetime.now().year
            recent_years = list(range(current_year - years, current_year))
            recent_fhps = fhps_df[fhps_df['年份'].isin(recent_years)]

            # 筛选条件1: 近 years 年是否每年都分红？
            unique_years = recent_fhps['年份'].nunique()
            if unique_years < years:
                processed_codes.append(code)
                continue

            # 筛选条件2: 近 years 年平均每股分红是否达标？
            # 使用现金分红比例作为每股分红（需要转换为元）
            avg_dividend_per_share = recent_fhps['现金分红-现金分红比例'].mean() / 10  # 假设比例需要除以10转换为元
            if avg_dividend_per_share < min_dividend_per_share:
                processed_codes.append(code)
                continue

            # 计算近一年平均股价（用于股息率）
            avg_price = None
            try:
                end_date = datetime.now().strftime('%Y%m%d')
                start_date = (datetime.now().replace(year=current_year - 1)).strftime('%Y%m%d')
                # 使用带缓存的股价获取函数
                price_df = get_stock_price_with_cache(code, start_date, end_date)
                if not price_df.empty:
                    avg_price = price_df['收盘'].mean()
            except Exception as e:
                print(f"获取股票 {code} 价格数据失败: {e}")
                pass

            # 计算股息率
            avg_dividend_yield = None
            if avg_price and avg_price > 0:
                avg_dividend_yield = (avg_dividend_per_share / avg_price) * 100

            # 筛选条件3: 平均股息率是否达标？
            if avg_dividend_yield and avg_dividend_yield < min_dividend_yield_threshold:
                processed_codes.append(code)
                continue

            # 记录符合条件的股票
            stock_name = stock_info[stock_info['code'] == code]['name'].iloc[0] if not stock_info[
                stock_info['code'] == code].empty else "N/A"
            results.append({
                '股票代码': code,
                '股票名称': stock_name,
                f'近{years}年连续分红': '是',
                f'近{years}年平均每股分红(元)': round(avg_dividend_per_share, 4),
                '近一年平均股价(元)': round(avg_price, 2) if avg_price else '数据缺失',
                '平均股息率(%)': round(avg_dividend_yield, 2) if avg_dividend_yield else '数据缺失',
                '最新分红年度': int(recent_fhps['年份'].iloc[-1]),
                '扫描时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })

            processed_codes.append(code)

            # 礼貌休眠
            time.sleep(0.5)

        except Exception as e:
            # 出错时也记录为已处理，避免下次重复处理同一失败代码
            processed_codes.append(code)
            continue

    # 全部处理完成后，保存最终状态
    save_status(processed_codes, current_params, total_stocks)

    # 转换为DataFrame并排序
    if results:
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values(by=f'近{years}年平均每股分红(元)', ascending=False)
        return results_df
    else:
        return pd.DataFrame()


def main():
    """主函数：参数设置与执行"""
    print("=" * 60)
    print("A股高分红股票扫描程序（支持断点续跑）")
    print("=" * 60)

    # 参数设置（可根据需要修改）
    YEARS_TO_CHECK = 5
    MIN_DIVIDEND_PER_SHARE = 0.1
    MIN_DIVIDEND_YIELD = 1.5
    RESET_CACHE = True  # 设为 True 可清除缓存重新开始

    print(f"筛选参数：")
    print(f"  - 连续分红年数: {YEARS_TO_CHECK}年")
    print(f"  - 最低每股分红: {MIN_DIVIDEND_PER_SHARE}元")
    print(f"  - 最低股息率: {MIN_DIVIDEND_YIELD}%")
    print(f"  - 重置缓存: {RESET_CACHE}")
    print("-" * 60)

    # 执行扫描
    start_time = time.time()
    high_dividend_stocks = get_high_dividend_stocks(
        years=YEARS_TO_CHECK,
        min_dividend_per_share=MIN_DIVIDEND_PER_SHARE,
        min_dividend_yield_threshold=MIN_DIVIDEND_YIELD,
        reset=RESET_CACHE
    )
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 60)
    print(f"扫描完成！耗时 {elapsed_time:.1f} 秒")

    if not high_dividend_stocks.empty:
        print(f"共找到 {len(high_dividend_stocks)} 只符合条件的股票：")

        # 显示结果
        pd.set_option('display.max_rows', None)
        pd.set_option('display.unicode.ambiguous_as_wide', True)
        pd.set_option('display.unicode.east_asian_width', True)
        pd.set_option('display.width', None)
        print(high_dividend_stocks.to_string(index=False))

        # 保存最终结果
        final_filename = f"high_dividend_stocks_final_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        high_dividend_stocks.to_csv(final_filename, index=False, encoding='utf_8_sig')
        save_cache(high_dividend_stocks)  # 更新缓存
        print(f"\n最终结果已保存至: {final_filename}")
        print(f"缓存已更新至: {CACHE_FILE}")
    else:
        print("未找到符合条件的股票。")

    print("=" * 60)


def show_status():
    """显示当前缓存和状态信息"""
    print("\n当前缓存状态：")
    print("-" * 40)

    # 检查缓存文件
    if os.path.exists(CACHE_FILE):
        cache_df = pd.read_csv(CACHE_FILE, dtype={'股票代码': str})
        print(f"缓存结果文件: {CACHE_FILE}")
        print(f"缓存股票数量: {len(cache_df)}")
        if len(cache_df) > 0:
            print("前5条缓存记录：")
            print(cache_df[['股票代码', '股票名称', '平均股息率(%)']].head().to_string(index=False))
    else:
        print("暂无缓存结果文件。")

    # 检查股价缓存目录
    print(f"\n股价缓存目录: {PRICE_CACHE_DIR}")
    if os.path.exists(PRICE_CACHE_DIR):
        price_cache_files = [f for f in os.listdir(PRICE_CACHE_DIR) if f.endswith('.csv')]
        print(f"股价缓存文件数量: {len(price_cache_files)}")

        # 统计缓存目录大小
        total_size = 0
        for f in price_cache_files:
            file_path = os.path.join(PRICE_CACHE_DIR, f)
            total_size += os.path.getsize(file_path)
        print(f"缓存目录大小: {total_size / 1024 / 1024:.2f} MB")
    else:
        print("暂无股价缓存目录。")

    # 检查状态文件
    print(f"\n状态文件: {STATUS_FILE}")
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r', encoding='utf-8') as f:
            status = json.load(f)
        print(f"上次处理时间: {status.get('timestamp', 'N/A')}")
        print(f"已处理股票数: {len(status.get('processed_codes', []))}")
        print(f"参数: 连续{status.get('params', {}).get('years', 'N/A')}年, "
              f"每股≥{status.get('params', {}).get('min_dividend_per_share', 'N/A')}元, "
              f"股息率≥{status.get('params', {}).get('min_dividend_yield_threshold', 'N/A')}%")
    else:
        print("暂无状态文件。")
    print("-" * 40)


if __name__ == "__main__":
    import sys

    # 支持命令行参数查看状态
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        show_status()
    else:
        main()
