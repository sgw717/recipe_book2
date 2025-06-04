import requests
import json
from tkinter import *

# 실제 발급받은 API 키 적용
API_KEY = "e66729cee3fc473a9f1e"

# 자취생 레시피 로드
with open("my_recipes.json", "r", encoding="utf-8") as f:
    my_recipes = json.load(f)

# 페이지 구간별 URL 정의 (1~1000까지 50개 단위)
PAGE_API_MAP = {
    "자취생 레시피": None,  # 사용자 정의
    **{
        f"{i}~{i+49}": f"http://openapi.foodsafetykorea.go.kr/api/{API_KEY}/COOKRCP01/json/{i}/{i+49}"
        for i in range(1, 1001, 50)
    }
}

# 현재 로드된 레시피 저장용 변수
page_recipes = {"자취생 레시피": my_recipes}

# GUI 생성
root = Tk()
root.title("🍱 레시피북 (페이지별)")
root.geometry("1050x600")

# 왼쪽 프레임: 페이지 선택
page_frame = Frame(root)
page_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

page_label = Label(page_frame, text="레시피 범위", font=("Arial", 12, "bold"))
page_label.pack(pady=(0, 5))

page_listbox = Listbox(page_frame, exportselection=False, font=("Arial", 12), height=20)
for page in PAGE_API_MAP.keys():
    page_listbox.insert(END, page)
page_listbox.pack()

# 검색창: 페이지 리스트박스 아래 정렬
search_label = Label(page_frame, text="🔍 레시피 검색", font=("Arial", 11))
search_label.pack(pady=(10, 2))

search_entry = Entry(page_frame, font=("Arial", 11), width=20)
search_entry.pack()

def search_recipes():
    query = search_entry.get().strip().lower()
    recipe_listbox.delete(0, END)
    output.delete(1.0, END)
    matched = []
    for page, recipes in page_recipes.items():
        if page == "자취생 레시피":
            continue  # 자취생 레시피는 검색 제외
        for r in recipes:
            title = r.get("RCP_NM", "").lower()
            if query in title:
                matched.append((page, r))

    for i, (page, r) in enumerate(matched):
        recipe_listbox.insert(END, r.get("RCP_NM", "제목 없음"))

    search_results.clear()
    search_results.extend(matched)

search_results = []
search_button = Button(page_frame, text="검색", command=search_recipes, font=("Arial", 10))
search_button.pack(pady=(2, 10))

# 가운데 프레임: 레시피 목록 + 스크롤바
recipe_frame = Frame(root)
recipe_frame.pack(side=LEFT, fill=Y, padx=10, pady=10)

scrollbar = Scrollbar(recipe_frame)
scrollbar.pack(side=RIGHT, fill=Y)

recipe_listbox = Listbox(recipe_frame, yscrollcommand=scrollbar.set, width=40, font=("Arial", 11))
recipe_listbox.pack(side=LEFT, fill=Y)
scrollbar.config(command=recipe_listbox.yview)

# 오른쪽: 레시피 상세 정보 출력창
output = Text(root, wrap=WORD, font=("Arial", 11))
output.pack(fill=BOTH, expand=True, padx=10, pady=10)

# 페이지 선택 시 API 호출 또는 사용자 정의 레시피 불러오기
def on_page_select(event):
    selection = page_listbox.curselection()
    if not selection:
        return
    page = page_listbox.get(selection[0])
    recipe_listbox.delete(0, END)
    output.delete(1.0, END)
    search_results.clear()

    if page == "자취생 레시피":
        recipes = page_recipes[page]
        for r in recipes:
            recipe_listbox.insert(END, r.get("title", "제목 없음"))
        return

    try:
        res = requests.get(PAGE_API_MAP[page])
        res.raise_for_status()
        data = res.json()
        rows = data.get('COOKRCP01', {}).get('row', [])
        page_recipes[page] = rows

        for r in rows:
            recipe_listbox.insert(END, r.get("RCP_NM", "제목 없음"))
    except Exception as e:
        recipe_listbox.insert(END, f"❌ 오류 발생: {e}")

# 레시피 선택 시 상세 정보 출력
def on_recipe_select(event):
    rec_idx = recipe_listbox.curselection()
    if not rec_idx:
        return
    idx = rec_idx[0]

    if search_results:
        page, recipe = search_results[idx]
    else:
        page_idx = page_listbox.curselection()
        if not page_idx:
            return
        page = page_listbox.get(page_idx[0])
        recipe = page_recipes.get(page, [])[idx]

    if page == "자취생 레시피":
        name = recipe.get("title", "제목 없음")
        parts = "\n".join(recipe.get("ingredients", []))
        manual = [f"{i+1}. {step}" for i, step in enumerate(recipe.get("instructions", []))]
    else:
        name = recipe.get("RCP_NM", "제목 없음")
        parts = recipe.get("RCP_PARTS_DTLS", "재료 정보 없음")
        manual = [recipe.get(f"MANUAL{str(i).zfill(2)}", "") for i in range(1, 21)]
        manual = [f"{i+1}. {m.strip()}" for i, m in enumerate(manual) if m.strip()]

    instructions = "\n".join(manual)
    output.delete(1.0, END)
    output.insert(END, f"🍽️ {name}\n\n🛒 재료:\n{parts}\n\n👩‍🍳 조리법:\n{instructions}")

# 바인딩
page_listbox.bind("<<ListboxSelect>>", on_page_select)
recipe_listbox.bind("<<ListboxSelect>>", on_recipe_select)

root.mainloop()
