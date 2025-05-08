#!/usr/bin/env python3
import json
import copy
import os
import sys

# 讀取儀表板 JSON 文件
def load_dashboard(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# 將儀表板面板按行分組
def group_panels_by_rows(dashboard):
    rows = []
    current_row = None
    
    for panel in dashboard.get('panels', []):
        if panel.get('type') == 'row':
            current_row = {
                'title': panel.get('title', 'Unnamed Row'),
                'panels': [],
                'row_panel': panel
            }
            rows.append(current_row)
        elif current_row is not None:
            current_row['panels'].append(panel)
        else:
            if not rows:
                current_row = {
                    'title': 'Default Row',
                    'panels': [],
                    'row_panel': {
                        'type': 'row',
                        'title': 'Default Row',
                        'collapsed': False
                    }
                }
                rows.append(current_row)
            current_row['panels'].append(panel)
    
    return rows

# 修改 GPU 面板使用正確的變量和實例
def modify_gpu_panel(panel):
    panel_copy = copy.deepcopy(panel)
    
    if 'targets' in panel_copy:
        for target in panel_copy.get('targets', []):
            if 'expr' in target:
                expr = target['expr']
                # 如果是 nvidia_smi 指標
                if 'nvidia_smi_' in expr:
                    # 使用 $gpu_instance 變量而不是硬編碼端口
                    if 'instance=' in expr:
                        target['expr'] = expr.replace('instance="localhost:9835"', 'instance="$gpu_instance"')
                        target['expr'] = expr.replace('instance=\'localhost:9835\'', 'instance="$gpu_instance"')
                    elif '{' in expr and 'instance=' not in expr:
                        target['expr'] = expr.replace('{', '{instance="$gpu_instance",')
                    elif '{' not in expr:
                        target['expr'] = expr.replace('nvidia_smi_', 'nvidia_smi_{instance="$gpu_instance"}')
    
    return panel_copy

# 合併儀表板
def merge_dashboards(node_dashboard, gpu_dashboard):
    # 創建新儀表板
    merged_dashboard = copy.deepcopy(node_dashboard)
    
    # 清除現有面板
    merged_dashboard['panels'] = []
    
    # 獲取行分組
    node_rows = group_panels_by_rows(node_dashboard)
    gpu_rows = group_panels_by_rows(gpu_dashboard)
    
    # 添加系統監控行
    panel_id = 1
    y_pos = 0
    
    # 首先添加 Node Exporter 摘要行
    if node_rows:
        summary_row = copy.deepcopy(node_rows[0]['row_panel'])
        summary_row['id'] = panel_id
        summary_row['gridPos'] = {'h': 1, 'w': 24, 'x': 0, 'y': y_pos}
        summary_row['title'] = '系統資源概覽'
        merged_dashboard['panels'].append(summary_row)
        panel_id += 1
        y_pos += 1
        
        # 添加該行的面板
        max_height = 0
        for panel in node_rows[0]['panels']:
            panel_copy = copy.deepcopy(panel)
            panel_copy['id'] = panel_id
            grid_pos = panel_copy.get('gridPos', {})
            grid_pos['y'] = y_pos
            panel_copy['gridPos'] = grid_pos
            merged_dashboard['panels'].append(panel_copy)
            panel_id += 1
            max_height = max(grid_pos.get('h', 8), max_height)
        
        y_pos += max_height
    
    # 添加 GPU 監控行
    gpu_row = {
        'type': 'row',
        'title': 'GPU 監控',
        'collapsed': False,
        'id': panel_id,
        'gridPos': {'h': 1, 'w': 24, 'x': 0, 'y': y_pos}
    }
    merged_dashboard['panels'].append(gpu_row)
    panel_id += 1
    y_pos += 1
    
    # 收集 GPU 相關面板
    gpu_panels = []
    for gpu_panel_row in gpu_rows:
        for panel in gpu_panel_row['panels']:
            # 檢查是否是 GPU 相關面板
            is_gpu_panel = False
            
            # 檢查標題
            if panel.get('title') and any(kw in panel.get('title', '').lower() for kw in ['gpu', 'nvidia']):
                is_gpu_panel = True
                
            # 檢查查詢
            if 'targets' in panel:
                for target in panel.get('targets', []):
                    if 'expr' in target and any(kw in target['expr'].lower() for kw in ['nvidia', 'gpu']):
                        is_gpu_panel = True
                        break
            
            if is_gpu_panel:
                gpu_panels.append(panel)
    
    # 添加 GPU 面板
    max_height = 0
    x_pos = 0
    for i, panel in enumerate(gpu_panels):
        # 修改 GPU 面板使用變量
        panel_copy = modify_gpu_panel(panel)
        panel_copy['id'] = panel_id
        
        # 調整佈局
        grid_pos = panel_copy.get('gridPos', {'h': 8, 'w': 12})
        grid_pos['y'] = y_pos
        grid_pos['x'] = x_pos
        
        # 定義面板寬度
        w = grid_pos.get('w', 12)
        if w > 12:
            w = 12
        grid_pos['w'] = w
        
        # 更新 x 坐標
        x_pos = (x_pos + w) % 24
        if x_pos == 0 and i < len(gpu_panels) - 1:
            y_pos += max_height
            max_height = 0
        
        max_height = max(grid_pos.get('h', 8), max_height)
        panel_copy['gridPos'] = grid_pos
        
        merged_dashboard['panels'].append(panel_copy)
        panel_id += 1
    
    y_pos += max_height
    
    # 添加其餘的系統監控行
    for i in range(1, len(node_rows)):
        row = node_rows[i]
        row_panel = copy.deepcopy(row['row_panel'])
        row_panel['id'] = panel_id
        row_panel['gridPos'] = {'h': 1, 'w': 24, 'x': 0, 'y': y_pos}
        merged_dashboard['panels'].append(row_panel)
        panel_id += 1
        y_pos += 1
        
        max_height = 0
        x_pos = 0
        for j, panel in enumerate(row['panels']):
            panel_copy = copy.deepcopy(panel)
            panel_copy['id'] = panel_id
            grid_pos = panel_copy.get('gridPos', {})
            
            # 調整位置
            grid_pos['y'] = y_pos
            grid_pos['x'] = x_pos
            
            # 定義面板寬度
            w = grid_pos.get('w', 12)
            if w > 12:
                w = 12
            grid_pos['w'] = w
            
            # 更新 x 坐標
            x_pos = (x_pos + w) % 24
            if x_pos == 0 and j < len(row['panels']) - 1:
                y_pos += max_height
                max_height = 0
            
            max_height = max(grid_pos.get('h', 8), max_height)
            panel_copy['gridPos'] = grid_pos
            merged_dashboard['panels'].append(panel_copy)
            panel_id += 1
        
        y_pos += max_height
    
    # 添加變量
    templating = merged_dashboard.get('templating', {})
    variables = templating.get('list', [])
    
    # 確保已有 instance 變量
    has_instance = False
    for var in variables:
        if var.get('name') == 'instance':
            has_instance = True
            break
    
    if not has_instance:
        instance_var = {
            "allValue": ".*",
            "current": {"selected": True, "text": ["All"], "value": ["$__all"]},
            "datasource": {"type": "prometheus", "uid": "Prometheus"},
            "definition": "label_values(node_uname_info, instance)",
            "hide": 0,
            "includeAll": True,
            "label": "系統節點",
            "multi": True,
            "name": "instance",
            "options": [],
            "query": {"query": "label_values(node_uname_info, instance)", "refId": "StandardVariableQuery"},
            "refresh": 1,
            "regex": "",
            "skipUrlSync": False,
            "sort": 1,
            "type": "query"
        }
        variables.append(instance_var)
    
    # 添加 GPU 實例變量
    gpu_instance_var = {
        "allValue": ".*",
        "current": {"selected": True, "text": ["localhost:9835"], "value": ["localhost:9835"]},
        "datasource": {"type": "prometheus", "uid": "Prometheus"},
        "definition": "label_values(nvidia_smi_gpu_info, instance)",
        "hide": 0,
        "includeAll": False,
        "label": "GPU 節點",
        "multi": False,
        "name": "gpu_instance",
        "options": [],
        "query": {"query": "label_values(nvidia_smi_gpu_info, instance)", "refId": "StandardVariableQuery"},
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "sort": 1,
        "type": "query"
    }
    variables.append(gpu_instance_var)
    
    # 添加 GPU UUID 變量
    gpu_var = {
        "allValue": ".*",
        "current": {"selected": True, "text": ["All"], "value": ["$__all"]},
        "datasource": {"type": "prometheus", "uid": "Prometheus"},
        "definition": "label_values(nvidia_smi_gpu_info{instance=\"$gpu_instance\"}, uuid)",
        "hide": 0,
        "includeAll": True,
        "label": "GPU",
        "multi": True,
        "name": "gpu",
        "options": [],
        "query": {"query": "label_values(nvidia_smi_gpu_info{instance=\"$gpu_instance\"}, uuid)", "refId": "StandardVariableQuery"},
        "refresh": 1,
        "regex": "",
        "skipUrlSync": False,
        "sort": 1,
        "type": "query"
    }
    variables.append(gpu_var)
    
    templating['list'] = variables
    merged_dashboard['templating'] = templating
    
    # 更新標題和描述
    merged_dashboard['title'] = '系統和 GPU 整合監控'
    merged_dashboard['description'] = '整合 Node Exporter Full 和 NVIDIA GPU 儀表板，支援多節點和多 GPU 監控'
    
    # 刪除 uid 以避免衝突
    if 'uid' in merged_dashboard:
        del merged_dashboard['uid']
    
    return merged_dashboard

def main():
    # 檔案路徑
    node_dashboard_path = '1860_rev40.json'
    gpu_dashboard_path = '14574_rev11.json'
    output_path = 'merged_dashboard.json'
    
    # 檢查檔案是否存在
    for filepath in [node_dashboard_path, gpu_dashboard_path]:
        if not os.path.exists(filepath):
            print(f"錯誤: 找不到檔案 {filepath}")
            print(f"當前目錄內容: {os.listdir('.')}")
            sys.exit(1)
    
    # 讀取儀表板
    try:
        print(f"讀取 Node Exporter 儀表板: {node_dashboard_path}")
        node_dashboard = load_dashboard(node_dashboard_path)
        print(f"讀取 GPU 儀表板: {gpu_dashboard_path}")
        gpu_dashboard = load_dashboard(gpu_dashboard_path)
        print("成功讀取兩個儀表板檔案")
    except Exception as e:
        print(f"錯誤: 無法讀取儀表板檔案: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 合併儀表板
    try:
        print("開始合併儀表板...")
        merged_dashboard = merge_dashboards(node_dashboard, gpu_dashboard)
        print("儀表板合併完成")
    except Exception as e:
        print(f"錯誤: 合併儀表板失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # 保存合併後的儀表板
    try:
        print(f"正在保存合併儀表板到: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(merged_dashboard, file, indent=2)
        print(f"合併儀表板已成功保存到: {output_path}")
    except Exception as e:
        print(f"錯誤: 無法保存合併儀表板: {e}")
        sys.exit(1)
    
    print("\n合併成功完成!")
    print("提示: 儀表板使用變量選擇 GPU 節點和 UUID，您可以在儀表板頂部選擇不同的節點和 GPU。")

if __name__ == "__main__":
    main()