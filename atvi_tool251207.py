import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def choose_file():
    """弹出窗口，选择一个 CSV 文件"""
    root = tk.Tk()
    root.withdraw()  # 不显示主窗口
    file_path = filedialog.askopenfilename(
        title="请选择 RawData CSV 文件",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
    )
    return file_path

def clean_series(s):
    """对一列做简单清洗：去两端空格，把 NaN 变成空字符串"""
    s = s.astype(str).str.strip()
    s = s.replace({"nan": ""})
    return s

def compute_variation(df, id_col, textbook_cols):
    """计算每一行的 Distinct_forms / Variation_index / Total_tokens"""
    records = []
    for idx, row in df.iterrows():
        concept = row[id_col]
        values = row[textbook_cols]

        # 清洗：转字符串 + 去空格
        values = values.astype(str).str.strip()
        # 视 "" 和 "nan" 为缺失
        values = values.replace({"nan": ""})

        non_empty = values[values != ""]
        total_tokens = len(non_empty)

        if total_tokens == 0:
            distinct_forms = 0
            variation_index = np.nan
        else:
            distinct_forms = non_empty.nunique()
            variation_index = distinct_forms / total_tokens

        records.append({
            "Concept_or_ID": concept,
            "Distinct_forms": distinct_forms,
            "Total_tokens": total_tokens,
            "Variation_index": variation_index
        })

    var_df = pd.DataFrame(records)
    return var_df

def compute_similarity(df, textbook_cols):
    """计算教材之间的相似度矩阵：两教材在所有行中，用相同词的比例"""
    sim_df = pd.DataFrame(index=textbook_cols, columns=textbook_cols, dtype=float)

    # 先清洗所有教材列
    clean_df = df.copy()
    for col in textbook_cols:
        clean_df[col] = clean_series(clean_df[col])

    for i, col_i in enumerate(textbook_cols):
        for j, col_j in enumerate(textbook_cols):
            if i == j:
                sim_df.loc[col_i, col_j] = 1.0
            else:
                s1 = clean_df[col_i]
                s2 = clean_df[col_j]

                # 只在两列都非空的行上比较
                mask = (s1 != "") & (s2 != "")
                total_pairs = mask.sum()

                if total_pairs == 0:
                    sim_df.loc[col_i, col_j] = np.nan
                else:
                    same = (s1[mask] == s2[mask]).sum()
                    sim_df.loc[col_i, col_j] = same / total_pairs

    return sim_df

def plot_variation(var_df, top_n=20):
    """画出 Variation_index 最高的 Top N 行"""
    # 去掉没有 variation_index 的行
    sub = var_df.dropna(subset=["Variation_index"]).copy()
    if sub.empty:
        print("没有有效的 Variation_index 可供绘图。")
        return

    sub = sub.sort_values("Variation_index", ascending=False).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(sub["Concept_or_ID"].astype(str), sub["Variation_index"])
    plt.xlabel("Variation Index（变异度）")
    plt.ylabel("Concept_or_ID（语义点/对齐位置）")
    plt.title(f"Top {len(sub)} 变异度最高的语义点")
    plt.gca().invert_yaxis()  # 让最高的在上面
    plt.tight_layout()
    plt.show()

def plot_similarity(sim_df):
    """画出教材相似度的热力图"""
    plt.figure(figsize=(6, 5))
    data = sim_df.astype(float).values
    im = plt.imshow(data, vmin=0, vmax=1, cmap="viridis")

    plt.colorbar(im, label="Similarity（相似度）")

    labels = sim_df.index.tolist()
    plt.xticks(range(len(labels)), labels, rotation=45, ha="right")
    plt.yticks(range(len(labels)), labels)

    plt.title("Textbook Similarity Matrix（教材相似度矩阵）")
    plt.tight_layout()
    plt.show()

def main():
    print("=== ATVI 工具（Python 版）===\n")
    file_path = choose_file()
    if not file_path:
        print("未选择文件，程序结束。")
        return

    print(f"已选择文件：{file_path}")

    # 读入 CSV
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print("读取 CSV 出错：", e)
        return

    if df.shape[1] < 3:
        print("列数太少，至少需要 1 列 ID + 2 列教材。")
        return

    id_col = df.columns[0]
    textbook_cols_all = list(df.columns[1:])
    print("\n检测到以下教材列：")
    for idx, col in enumerate(textbook_cols_all, start=1):
        print(f"{idx}. {col}")

    choice = input("\n如果想使用全部教材列，直接回车；\n"
                   "如果只想选部分，请输入编号（如 1,3,4）：").strip()
    if choice:
        try:
            indices = [int(x) for x in choice.split(",")]
            textbook_cols = [textbook_cols_all[i-1] for i in indices]
        except Exception as e:
            print("解析编号出错，将使用全部教材列。错误信息：", e)
            textbook_cols = textbook_cols_all
    else:
        textbook_cols = textbook_cols_all

    print("\n将使用以下教材列进行计算：")
    for col in textbook_cols:
        print(" -", col)

    # 计算 Variation
    print("\n正在计算 Variation Index（变异度）...")
    var_df = compute_variation(df, id_col, textbook_cols)

    # 计算 Similarity
    print("正在计算 Textbook Similarity（教材相似度）...")
    sim_df = compute_similarity(df, textbook_cols)

    # 保存结果到与原文件同一目录
    base_dir = os.path.dirname(file_path)
    var_out = os.path.join(base_dir, "variation_results.csv")
    sim_out = os.path.join(base_dir, "similarity_matrix.csv")

    var_df.to_csv(var_out, index=False, encoding="utf-8-sig")
    sim_df.to_csv(sim_out, encoding="utf-8-sig")

    print(f"\n已保存变异度结果：{var_out}")
    print(f"已保存教材相似度矩阵：{sim_out}")

    # 可视化
    print("\n现在将展示两个简单的可视化图：")
    print("1）变异度 Top N 条形图；2）教材相似度热力图。关闭图窗后程序结束。\n")

    plot_variation(var_df, top_n=20)
    plot_similarity(sim_df)

    print("\n完成。")

if __name__ == "__main__":
    main()
