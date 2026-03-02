#!/usr/bin/env python3
"""
공급단 명칭 통일 패치 스크립트
사용법: python3 patch_supply.py app.py
"""
import sys, re, ast

def apply(src):
    # A. supply 정규화
    OLD_A = "        if 'supply' in df.columns:\n            df['supply'] = df['supply'].replace({'':\'<NA>\','nan':'<NA>\'})"
    NEW_A = """        if 'supply' in df.columns:
            SUPPLY_NORM = {
                '시디즈':      '시디즈(평택)', '의자내작':    '시디즈(평택)',
                '시디즈제품':  '시디즈(평택)', '시디즈평택':  '시디즈(평택)',
                '의자평택상품':'시디즈(평택)', '의자양지상품':'시디즈(평택)',
                '제품':        '시디즈(평택)', '평택의자':    '시디즈(평택)',
                'VN의자':      '베트남',       '베트남의자':  '베트남',
                '시디즈VN':    '베트남',       '시디즈vn':    '베트남',
                'FVN2':        '베트남',       '베트남상품':  '베트남',
                '의자외작':    '외주/상품',    '수입상품':    '외주/상품',
                '외주상품':    '외주/상품',    '상품':        '외주/상품',
                '진영':        '외주/상품',    '웰시트':      '외주/상품',
                '이화하이':    '외주/상품',    '웰켐':        '외주/상품',
                '한국스틸웨어':'외주/상품',    '다진':        '외주/상품',
                '에브라임':    '외주/상품',    '의자안성상품':'외주/상품',
                '의자상품':    '외주/상품',
                '': '<NA>', 'nan': '<NA>', 'NaN': '<NA>', 'None': '<NA>',
            }
            df['supply'] = df['supply'].astype(str).str.strip().replace(SUPPLY_NORM)
            _valid = {'시디즈(평택)', '베트남', '외주/상품', '<NA>'}
            df['supply'] = df['supply'].apply(lambda v: v if v in _valid else '<NA>')"""
    applied = []
    if OLD_A in src:
        src = src.replace(OLD_A, NEW_A); applied.append("A")

    # B. selectbox 고정순서
    pattern_b = r'    supply_vals\s*=\s*sorted\(\[v for v in mg_all\["supply"\]\.unique\(\).*?\]\)\n    sel_supply\s*=\s*st\.selectbox\("🏭 공급단", \["전체"\]\+supply_vals\)'
    new_b = '''    _known_supply = [\'시디즈(평택)\', \'베트남\', \'외주/상품\']
    supply_vals = [v for v in _known_supply if v in mg_all["supply"].values]
    sel_supply = st.selectbox("🏭 공급단", ["전체"] + supply_vals)'''
    new_src, n = re.subn(pattern_b, new_b, src, flags=re.DOTALL)
    if n: src = new_src; applied.append("B")

    # C. 파이차트
    OLD_C = '        sup_agg = (df_ov[~df_ov["supply"].isin(["<NA>","nan","","None"])]\n                   .groupby("supply")["forecast"].sum().reset_index())'
    if OLD_C in src:
        src = src.replace(OLD_C, '        sup_agg = (df_ov[df_ov["supply"] != "<NA>"]\n                   .groupby("supply")["forecast"].sum().reset_index())')
        applied.append("C")

    # D. 미분류
    OLD_D = '        display_det["supply"] = display_det["supply"].replace({"<NA>":"—"})'
    if OLD_D in src:
        src = src.replace(OLD_D, '        display_det["supply"] = display_det["supply"].replace({"<NA>":"미분류"})')
        applied.append("D")

    return src, applied

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "app.py"
    src = open(path, encoding="utf-8").read()
    patched, applied = apply(src)
    try:
        ast.parse(patched)
    except SyntaxError as e:
        print(f"구문 오류: {e}"); sys.exit(1)
    import shutil, os
    shutil.copy(path, path + ".bak")
    open(path, "w", encoding="utf-8").write(patched)
    print(f"✅ 패치 완료: {applied}")
    print(f"   백업: {path}.bak")
