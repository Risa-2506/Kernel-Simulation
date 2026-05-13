from flask import Flask, render_template, jsonify, request
from core.kernel_simulator import KernelSimulator
from core.logger import Logger
from core.constants import SchedulingType

app = Flask(__name__)
simulator = KernelSimulator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    return jsonify(simulator.get_status())

@app.route('/api/step', methods=['POST'])
def step():
    simulator.step()
    return jsonify({"status": "success"})

@app.route('/api/reset', methods=['POST'])
def reset():
    simulator.reset()
    return jsonify({"status": "success"})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    s_type = data.get('type')
    quantum = int(data.get('quantum', 2))
    
    if s_type == "Priority":
        simulator.scheduler.scheduling_type = SchedulingType.PRIORITY
    else:
        simulator.scheduler.scheduling_type = SchedulingType.ROUND_ROBIN
        
    simulator.scheduler.time_quantum = quantum
    Logger.log(f"Settings updated: Mode={simulator.scheduler.scheduling_type}, Quantum={quantum}")
    return jsonify({"status": "success"})

@app.route('/api/process/create', methods=['POST'])
def create_process():
    data = request.json
    name = data.get('name', 'Process')
    prio = int(data.get('priority', 1))
    burst = int(data.get('burst', 5))
    mem = int(data.get('memory', 100))
    
    success = simulator.process_manager.create_process(name, prio, burst, mem)
    if success:
        p = simulator.process_manager.get_all_processes()[-1]
        simulator.scheduler.enqueue(p)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Insufficient memory"}), 400

# File System Routes
@app.route('/api/file/create', methods=['POST'])
def create_file():
    data = request.json
    name = data.get('name')
    content = data.get('content')
    success = simulator.file_system.create_file(name, content)
    
    # Simulate I/O if a process is running
    if success and simulator.scheduler.running_process:
        proc = simulator.scheduler.running_process
        simulator.scheduler.put_to_waiting(proc, 2, f"File Create ({name})")
        simulator.scheduler.dispatch()
        
    return jsonify({"status": "success" if success else "error"})

@app.route('/api/file/edit', methods=['POST'])
def edit_file():
    data = request.json
    name = data.get('name')
    content = data.get('content')
    success = simulator.file_system.edit_file(name, content)
    
    # Simulate I/O if a process is running
    if success and simulator.scheduler.running_process:
        proc = simulator.scheduler.running_process
        simulator.scheduler.put_to_waiting(proc, 2, f"File Write ({name})")
        simulator.scheduler.dispatch()
        
    return jsonify({"status": "success" if success else "error"})

@app.route('/api/file/delete', methods=['POST'])
def delete_file():
    name = request.json.get('name')
    success = simulator.file_system.delete_file(name)
    return jsonify({"status": "success" if success else "error"})

if __name__ == '__main__':
    # Initial setup
    simulator.process_manager.create_process("System", 5, 10, 200)
    simulator.process_manager.create_process("Shell", 2, 5, 100)
    for p in simulator.process_manager.get_all_processes():
        simulator.scheduler.enqueue(p)
    
    app.run(debug=True, port=5000)
