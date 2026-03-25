# 🏦 Banking System Project (CSCI 3060U)

## 👥 Team Members
- Mansi Kandoi (100821953)  
- Sneh Patel (100950609)  
- Jolly Soni (100876863)  


## 📖 Project Overview
This project is a **file-based Banking System** developed for CSCI 3060U.  
It simulates real-world banking operations using two main components:

- **Front End** → ATM-style interface for performing transactions  
- **Back End** → Batch processor that updates account records  

The project follows an Agile development approach, where each phase focuses on 
requirements, design, implementation, testing, and integration.

## Features

Front End:
- Login (Standard/Admin)
- Deposit, Withdrawal, Transfer
- Pay Bills
- Create/Delete Accounts (Admin)
- Disable Accounts (Admin)
- Change Plan (Admin)
- Logout (generates transaction file)

Back End:
- Processes transaction files
- Updates master account records
- Applies transaction fees
- Enforces constraints and logs errors

## Project Structure

.vscode/  
Phase1/  
Phase2/  
Phase3/  
Phase4/  
Phase5/ (in progress)

## How to Run

Clone the repository:
git clone <your-repo-link>  
cd <repo-name>  

Run Front End:
python frontend.py <input_file>  

Run Back End:
python backend.py <master_file> <transaction_file>  

Run Tests:
pytest  

## Testing and Quality Assurance
- Continuous testing across all phases  
- Unit testing using pytest  
- Input/output file validation  
- Error handling for invalid transactions  
- Constraint validation and failure reporting  

The Front End handles invalid input without crashing.  
The Back End enforces rules and logs errors clearly.

## Development Phases
- Phase 1: Requirements and Planning  
- Phase 2: Design  
- Phase 3: Implementation  
- Phase 4: Testing  
- Phase 5: Integration and Finalization (in progress)

## Notes
- Console-based application  
- Uses text files for input/output  
- Focus on correctness, validation, and reliability  
