import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import jieba
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
plt.rcParams['font.sans-serif'] = ['SimHei']  
plt.rcParams['axes.unicode_minus'] = False     

def fetch_and_save_data():
    print("🚀 正在安全抓取百度实时热搜...")
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.select('div[class*="category-wrap"]')
        
        if not items:
            items = soup.find_all('div', {'class': lambda x: x and 'content' in x.lower()})

        data_list = []
        for item in items:
            try:
                title_el = item.select_one('div[class*="c-single-text-ellipsis"]')
                heat_el = item.select_one('div[class*="hot-index"]')
                
                if title_el and heat_el:
                    title = title_el.text.strip()
                    heat_str = heat_el.text.strip().replace(',', '') 
                    data_list.append({
                        "排名": len(data_list) + 1,
                        "标题": title, 
                        "搜索热度": int(heat_str)
                    })
            except Exception:
                continue
            
            if len(data_list) >= 15: break 

        if not data_list:
            print("⚠️ 未能解析到数据，请检查网络或联系开发者更新选择器。")
            return None

        df = pd.DataFrame(data_list)
        
        file_name = 'baidu_hot_search_dataset.csv'
        df.to_csv(file_name, index=False, encoding='utf-8-sig')
        print(f"✅ 数据已成功保存至: {os.getcwd()}\\{file_name}")
        
        return df

    except Exception as e:
        print(f"❌ 运行异常: {e}")
        return None

def visualize_data(df):
    if df is None or df.empty:
        print("💡 没有数据可供可视化分析。")
        return

    fig = plt.figure(figsize=(16, 9))
    fig.patch.set_facecolor('#f5f5f5') 

    ax1 = fig.add_subplot(1, 2, 1)
    df_sorted = df.sort_values('搜索热度', ascending=True) 
    
    color_map = plt.cm.get_cmap('Blues_r')
    colors = color_map([i/len(df_sorted) for i in range(len(df_sorted))])
    
    bars = ax1.barh(df_sorted['标题'], df_sorted['搜索热度'], color=colors, edgecolor='white')
    
    ax1.set_title("今日百度热搜 Top 15 指数榜单", fontsize=18, fontweight='bold', pad=20)
    ax1.set_xlabel("搜索热度指数 (Search Index)", fontsize=12)
    ax1.tick_params(axis='y', labelsize=11)
    
    for bar in bars:
        width = bar.get_width()
        ax1.text(width + (width*0.02), bar.get_y() + bar.get_height()/2, 
                 f'{int(width):,}', va='center', fontsize=10, color='#333', fontweight='500')
    
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)

    ax2 = fig.add_subplot(1, 2, 2)
    all_titles = " ".join(df['标题'].tolist())
    words = [w for w in jieba.cut(all_titles) if len(w) > 1] 
    processed_text = " ".join(words)
    
    try:
        wc = WordCloud(
            font_path='simhei.ttf', 
            background_color='white',
            width=1000, height=1000,
            max_words=100,
            colormap='viridis',
            contour_width=1,
            contour_color='steelblue'
        ).generate(processed_text)
        
        ax2.imshow(wc, interpolation="bilinear")
        ax2.axis("off")
        ax2.set_title("热搜关键词云 (语义权重分析)", fontsize=18, fontweight='bold', pad=20)
    except Exception as e:
        ax2.text(0.5, 0.5, f"词云生成失败\n请检查字体路径\n{e}", ha='center', va='center')
        ax2.axis("off")
    
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    print("✨ 分析完成！正在弹出可视化窗口...")
    plt.show()

if __name__ == "__main__":
    df_data = fetch_and_save_data()
    if df_data is not None:
        visualize_data(df_data)