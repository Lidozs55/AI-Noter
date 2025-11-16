"""
性能监控工具
监控系统运行状态和性能指标
"""
import time
import psutil
import json
from datetime import datetime
from pathlib import Path


class PerformanceMonitor:
    """性能监控器"""
    
    def __init__(self):
        self.metrics = []
        self.log_file = Path('./performance.log')
    
    def get_cpu_usage(self):
        """获取 CPU 使用率"""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self):
        """获取内存使用率"""
        memory = psutil.virtual_memory()
        return {
            'percent': memory.percent,
            'used': memory.used / (1024**3),  # GB
            'total': memory.total / (1024**3)
        }
    
    def get_disk_usage(self):
        """获取磁盘使用率"""
        disk = psutil.disk_usage('/')
        return {
            'percent': disk.percent,
            'used': disk.used / (1024**3),  # GB
            'total': disk.total / (1024**3)
        }
    
    def get_data_size(self):
        """获取数据目录大小"""
        data_dir = Path('./data')
        total_size = 0
        
        if data_dir.exists():
            for file in data_dir.rglob('*'):
                if file.is_file():
                    total_size += file.stat().st_size
        
        return total_size / (1024**2)  # MB
    
    def collect_metrics(self):
        """收集性能指标"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_usage': self.get_cpu_usage(),
            'memory_usage': self.get_memory_usage(),
            'disk_usage': self.get_disk_usage(),
            'data_size_mb': self.get_data_size()
        }
        
        self.metrics.append(metrics)
        return metrics
    
    def print_report(self):
        """打印性能报告"""
        if not self.metrics:
            print("暂无数据")
            return
        
        latest = self.metrics[-1]
        
        print("\n" + "="*60)
        print("  性能监控报告")
        print("="*60)
        print(f"\n时间: {latest['timestamp']}")
        print(f"CPU 使用率: {latest['cpu_usage']:.1f}%")
        print(f"内存使用: {latest['memory_usage']['used']:.2f}GB / {latest['memory_usage']['total']:.2f}GB ({latest['memory_usage']['percent']:.1f}%)")
        print(f"磁盘使用: {latest['disk_usage']['used']:.2f}GB / {latest['disk_usage']['total']:.2f}GB ({latest['disk_usage']['percent']:.1f}%)")
        print(f"数据大小: {latest['data_size_mb']:.2f}MB")
        print("="*60 + "\n")
    
    def save_metrics(self):
        """保存指标到文件"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.metrics, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    monitor = PerformanceMonitor()
    print("正在收集性能指标...")
    
    for i in range(5):
        monitor.collect_metrics()
        print(f"已收集 {i+1}/5 条数据...")
        time.sleep(1)
    
    monitor.print_report()
    monitor.save_metrics()
    print("✅ 性能数据已保存到 performance.log")
