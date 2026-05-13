#include "KernelSimulator.h"
#include "UIManager.h"

/**
 * MINI OPERATING SYSTEM KERNEL SIMULATOR
 * --------------------------------------
 * A modular simulation of OS core subsystems:
 * - Process Management (PCB, States)
 * - Memory Management (First Fit Allocation)
 * - CPU Scheduling (Round Robin)
 * - File System (Inode structure)
 * - Event Logging
 * 
 * Architecture:
 * main -> UIManager -> KernelSimulator (Orchestrator) -> Subsystems
 */

int main() {
    // Initialize the kernel orchestrator
    KernelSimulator kernel;
    
    // Initialize and run the UI
    UIManager ui(kernel);
    ui.run();
    
    return 0;
}
