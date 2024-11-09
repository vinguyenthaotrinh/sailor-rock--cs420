import matplotlib.pyplot as plt
import numpy as np
import os

# Hàm để trích xuất dữ liệu từ file output
def extract_data(file_path):
    with open(file_path, 'r') as f:
        data = f.read().splitlines()
    
    algorithms = ['BFS', 'DFS', 'UCS', 'A*']
    metrics = {'Steps': [], 'Total cost': [], 'Node': [], 'Time': [], 'Memory': []}
    
    current_algorithm = None
    for line in data:
        if line.startswith('Algorithm'):
            current_algorithm = line.split(':')[1].strip()
        elif any(line.startswith(metric) for metric in metrics):
            metric_name = next(metric for metric in metrics if line.startswith(metric))
            value = line.split(':')[1].strip().split()[0]
            if metric_name == 'Memory':
                # Trích xuất giá trị bộ nhớ từ MB (có thể có đơn vị MB)
                value = value.replace('MB', '').strip()
            metrics[metric_name].append(float(value))
    
    return metrics

# Hàm để vẽ biểu đồ so sánh các đặc tính
def plot_comparison(test_files):
    # Lấy các dữ liệu cần thiết
    all_data = {'Steps': [], 'Total cost': [], 'Node': [], 'Time': [], 'Memory': []}
    
    for test_file in test_files:
        file_path = os.path.join('levels', test_file)
        metrics = extract_data(file_path)
        
        # Append dữ liệu của các thuật toán vào từng đặc tính
        for key in all_data:
            all_data[key].append(metrics[key])
    
    # Tạo các biểu đồ cho từng đặc tính
    for metric, values in all_data.items():
        fig, ax = plt.subplots(figsize=(12, 8))
        width = 0.2  # Chiều rộng của mỗi cột
        x_labels = [str(i+1) for i in range(12)]  # Các nhãn cho test 1 đến 12
        x_pos = np.arange(len(x_labels))  # Tọa độ các cột
        
        # Các thuật toán
        algorithms = ['BFS', 'DFS', 'UCS', 'A*']
        colors = ['blue', 'orange', 'green', 'red']
        
        # Vẽ các cột cho mỗi thuật toán
        for i, algorithm in enumerate(algorithms):
            ax.bar(x_pos + i * width, [test[i] for test in values], width, label=algorithm, color=colors[i])
        
        # Thiết lập các thông số cho biểu đồ
        ax.set_xlabel('Test')
        ax.set_ylabel(metric)
        ax.set_title(f'Comparison of {metric} for Algorithms')
        ax.set_xticks(x_pos + width * 1.5)
        ax.set_xticklabels(x_labels)
        ax.legend(title="Algorithms")
        
        # Lưu biểu đồ vào thư mục manager/
        if not os.path.exists('manager'):
            os.makedirs('manager')
        plt.savefig(f'manager/{metric.lower().replace(" ", "_")}_comparison.png', bbox_inches='tight', pad_inches=0.1)
        plt.close()

# Tạo danh sách các file output từ output-01.txt đến output-12.txt
test_files = [f'output-{str(i).zfill(2)}.txt' for i in range(1, 13)]

# Vẽ các biểu đồ
plot_comparison(test_files)
