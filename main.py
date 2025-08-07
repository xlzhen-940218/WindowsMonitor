import psutil
import socket
import platform
import time
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request

# --- 初始化 ---
app = Flask(__name__)

# 全局变量用于计算实时网速
last_net_io = psutil.net_io_counters()
last_time = time.time()


# --- 数据收集函数 ---
def collect_system_info():
    """收集系统基本信息 (仅在启动时收集一次)"""
    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
    }


def collect_performance_data():
    """收集实时性能数据"""
    global last_net_io, last_time

    # --- 网络实时速度 ---
    current_time = time.time()
    current_net_io = psutil.net_io_counters()
    time_delta = current_time - last_time

    # 防止除以零
    if time_delta == 0:
        upload_speed = 0
        download_speed = 0
    else:
        upload_speed = (current_net_io.bytes_sent - last_net_io.bytes_sent) / time_delta
        download_speed = (current_net_io.bytes_recv - last_net_io.bytes_recv) / time_delta

    # 更新记录
    last_time = current_time
    last_net_io = current_net_io

    # --- CPU ---
    cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
    cpu_total_percent = sum(cpu_percent_per_core) / len(cpu_percent_per_core)
    # 获取占用率最高的4个核心 (索引, 百分比)
    top_4_cores = sorted(enumerate(cpu_percent_per_core), key=lambda x: x[1], reverse=True)[:4]

    # --- 磁盘 (C, D, E, F) ---
    disk_info = []
    target_drives = {"C", "D", "E", "F"}
    for partition in psutil.disk_partitions():
        # Windows下盘符通常是 C:\, D:\ 等
        drive_letter = partition.device.replace(':\\', '')
        if drive_letter in target_drives:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    "drive": drive_letter,
                    "total": usage.total,
                    "used": usage.used,
                    "percent": usage.percent
                })
            except Exception:
                continue  # 忽略光驱等无法访问的盘符

    # --- 进程 (Top 10) ---
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
        try:
            # 确保数据有效
            proc.info['cpu_percent']
            proc.info['memory_percent']
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    top_processes = sorted(processes, key=lambda p: p['memory_percent'], reverse=True)

    return {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "cpu": {
            "total_percent": cpu_total_percent,
            "top_cores": top_4_cores  # 新增: Top 4 核心数据
        },
        "memory": {
            "percent": psutil.virtual_memory().percent
        },
        "disks": disk_info,  # 修改: 磁盘列表
        "network": {
            "upload_speed": upload_speed,  # 新增: 上传速度
            "download_speed": download_speed  # 新增: 下载速度
        },
        "processes": top_processes
    }


# --- API 路由 ---
@app.route('/')
def index():
    """提供前端HTML页面"""
    return send_from_directory('.', 'index.html')

# --- API 路由 ---
@app.route('/white')
def white_index():
    """提供前端HTML页面"""
    return send_from_directory('.', 'white_index.html')

# --- API 路由 ---
@app.route('/cool')
def cool_index():
    """提供前端HTML页面"""
    return send_from_directory('.', 'cool.html')


@app.route('/api/data')
def get_data():
    """提供JSON格式的系统数据"""
    return jsonify(collect_performance_data())


@app.route('/api/kill_process', methods=['POST'])
def kill_process_route():
    """结束进程的API端点"""
    data = request.json
    pid = data.get('pid')
    if pid is None:
        return jsonify({"success": False, "message": "PID not provided"}), 400

    try:
        p = psutil.Process(pid)
        p.terminate()  # or p.kill() for a more forceful termination
        return jsonify({"success": True, "message": f"Process {pid} terminated."})
    except psutil.NoSuchProcess:
        return jsonify({"success": False, "message": f"Process with PID {pid} not found."}), 404
    except psutil.AccessDenied:
        return jsonify({"success": False,
                        "message": f"Access denied to terminate process {pid}. Try running the script as an administrator."}), 403
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    print("服务器正在启动...")
    print("请以管理员身份运行此脚本，以便拥有结束进程的权限。")
    print("在浏览器中访问 http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)